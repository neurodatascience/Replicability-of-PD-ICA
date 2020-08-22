#! /usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author: Vincent (Qing Wang)
# @Date:   2020-2-14 12:00:00

"""

======================================================
Using ANTS for creating a T1 template (ITK4)
Adapted for Abbas PD datasets from niflow.nipype1 by Vincent.
======================================================
1. Libs and functions
"""
import os
import sys
import nipype.interfaces.utility as util
import nipype.interfaces.ants as ants
import nipype.interfaces.io as nio
import nipype.pipeline.engine as pe  # pypeline engine

def DataGraberRun(sub_list, RUN, BASE_DIR, TMPT):
    import nipype.interfaces.io as nio
    ds = nio.DataGrabber(infields=['subject_id', 'run'])
    ds.inputs.base_directory = BASE_DIR # database
    ds.inputs.template = TMPT # from cwd
    ds.inputs.subject_id = sub_list
    ds.inputs.run = RUN
    ds.inputs.sort_filelist = True
    res = ds.run()
    return res

def main():
    """Entry point"""
    from niflow.nipype1.workflows.smri.ants import antsRegistrationTemplateBuildSingleIterationWF

    """1. input images"""
    # folders conf
    homeDir = os.getenv("HOME")
    BASE_DIR="/home/vincent/my_study/Abbas_dataset_raw_BIDS"
    out_base_dir="~/my_study/codes/sMRI"
    #out_base_dir="/output"

    out_dir = os.path.join(out_base_dir, 'nipypeTestPath')
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    print(out_dir)
    # file import
    sub_list1 = ['FMR-001', 'FMR-096', 'VT-004', 'VT-005', 'VT-007', 'VT-008', 'VT-009', 'VT-010', 'VT-011', 'VT-015', 'VT-041']
    sub_list1 = [''.join(x.split('-')) for x in sub_list1]
    sub_list3 = ['VT006']
    RUN1=1 ;RUN3=3
    TMPT='sub-%s/anat/*_run-%d_T1w.nii.gz'
    res_T1_1 = DataGraberRun(sub_list1, RUN1, BASE_DIR, TMPT)
    res_T1_3 = DataGraberRun(sub_list3, RUN3, BASE_DIR, TMPT)
    T1_file_list = res_T1_1.outputs.outfiles+[res_T1_3.outputs.outfiles]
    print(T1_file_list, len(T1_file_list))
    # configure workflow
    registrationImageTypes = ['T1']
    interpolationMapping = {'labelmap':'NearestNeighbor',
    'FLAIR':'WindowedSinc',
    'T1': 'Linear'}
    tbuilder = pe.Workflow(name="antsRegistrationTemplateBuilder")
    tbuilder.base_dir = out_dir
    InitialTemplateInputs = T1_file_list
    ListOfImagesDictionaries = [{'T1': FP} for FP in InitialTemplateInputs]

    datasource = pe.Node(
    interface=util.IdentityInterface(fields=['InitialTemplateInputs', 'ListOfImagesDictionaries',
    'registrationImageTypes', 'interpolationMapping']), run_without_submitting=True, name='InputImages')
    datasource.inputs.InitialTemplateInputs = InitialTemplateInputs
    datasource.inputs.ListOfImagesDictionaries = ListOfImagesDictionaries
    datasource.inputs.registrationImageTypes = registrationImageTypes
    datasource.inputs.interpolationMapping = interpolationMapping
    datasource.inputs.sort_filelist = True
    # ave as the first image
    initAvg = pe.Node(interface=ants.AverageImages(), name='initAvg')
    initAvg.inputs.dimension = 3
    initAvg.inputs.normalize = True
    tbuilder.connect(datasource, "InitialTemplateInputs", initAvg, "images")
    # iter1
    buildTemplateIteration1 = antsRegistrationTemplateBuildSingleIterationWF(
    'iteration01')
    BeginANTS = buildTemplateIteration1.get_node("BeginANTS")
    tbuilder.connect(initAvg, 'output_average_image', buildTemplateIteration1, 'inputspec.fixed_image')
    tbuilder.connect(datasource, 'ListOfImagesDictionaries', buildTemplateIteration1, 'inputspec.ListOfImagesDictionaries')
    tbuilder.connect(datasource, 'registrationImageTypes', buildTemplateIteration1, 'inputspec.registrationImageTypes')
    tbuilder.connect(datasource, 'interpolationMapping', buildTemplateIteration1, 'inputspec.interpolationMapping')
    # iter2
    buildTemplateIteration2 = antsRegistrationTemplateBuildSingleIterationWF('iteration02')
    BeginANTS = buildTemplateIteration2.get_node("BeginANTS")
    tbuilder.connect(buildTemplateIteration1, 'outputspec.template',
    buildTemplateIteration2, 'inputspec.fixed_image')
    tbuilder.connect(datasource, 'ListOfImagesDictionaries',
    buildTemplateIteration2, 'inputspec.ListOfImagesDictionaries')
    tbuilder.connect(datasource, 'registrationImageTypes', buildTemplateIteration2,
    'inputspec.registrationImageTypes')
    tbuilder.connect(datasource, 'interpolationMapping', buildTemplateIteration2,
    'inputspec.interpolationMapping')
    #
    datasink = pe.Node(nio.DataSink(), name="datasink")
    datasink.inputs.base_directory = os.path.join(out_dir, "results")
    tbuilder.connect(buildTemplateIteration2, 'outputspec.template', datasink,
    'PrimaryTemplate')
    tbuilder.connect(buildTemplateIteration2, 'outputspec.passive_deformed_templates', datasink,
    'PassiveTemplate')
    tbuilder.connect(initAvg, 'output_average_image', datasink, 'PreRegisterAverage')
    tbuilder.run(plugin='MultiProc', plugin_args={'n_procs':13})
if __name__ == '__main__':
    main()
