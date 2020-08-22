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

def DataGraberRun(sub_list, DATA_DIR, TMPT):
    import nipype.interfaces.io as nio
    ds = nio.DataGrabber(infields=['subject_id', 'subject_id'])
    ds.inputs.base_directory = DATA_DIR # database
    ds.inputs.template = TMPT # from cwd
    ds.inputs.subject_id = sub_list
    ds.inputs.sort_filelist = True
    res = ds.run()
    return res

def get_args():
    import argparse
    parser = argparse.ArgumentParser(description='Input of pamameters: ')
    parser.add_argument('--data',   type=str, default = '/data')
    parser.add_argument('--output', type=str, default = '/output')
    parser.add_argument('--sub_list',   type=str, default = '/output/subjects.list')
    parser.add_argument('--nprocs', type=int, default = 2)
    args = parser.parse_args()
    return args
    
def main(DATA_DIR, OUT_DIR, SUB_LIST, N_PROCESS):
    """Entry point"""
    from niflow.nipype1.workflows.smri.ants import antsRegistrationTemplateBuildSingleIterationWF
    """1. input images"""
    out_dir = OUT_DIR
    if not os.path.exists(OUT_DIR):
        os.makedirs(out_dir)

    with open(SUB_LIST, 'r') as f_sub:
        sub_list = f_sub.readlines()
    sub_list = [x[0:-1] for x in sub_list]
    print(len(sub_list), ' subjects included: ', sub_list)

    TMPT='%s/anat/%s_desc-preproc_T1w.nii.gz'
    res_T1 = DataGraberRun(sub_list, DATA_DIR, TMPT)
    T1_file_list = res_T1.outputs.outfiles
    print('Subject T1 files: ', T1_file_list)
    # configure workflow
    registrationImageTypes = ['T1']
    interpolationMapping = {'labelmap':'NearestNeighbor', 'FLAIR':'WindowedSinc', 'T1': 'Linear'}
    tbuilder = pe.Workflow(name="antsRegistrationTemplateBuilder")
    tbuilder.base_dir = out_dir
    InitialTemplateInputs = [(isinstance(x_file, str) and x_file) or x_file[0] for x_file in T1_file_list]
    ListOfImagesDictionaries = [{'T1': FP} for FP in InitialTemplateInputs]
    print("T1 files: ", ListOfImagesDictionaries, len(ListOfImagesDictionaries))
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
    tbuilder.connect(buildTemplateIteration1, 'outputspec.template', buildTemplateIteration2, 'inputspec.fixed_image')
    tbuilder.connect(datasource, 'ListOfImagesDictionaries', buildTemplateIteration2, 'inputspec.ListOfImagesDictionaries')
    tbuilder.connect(datasource, 'registrationImageTypes', buildTemplateIteration2, 'inputspec.registrationImageTypes')
    tbuilder.connect(datasource, 'interpolationMapping', buildTemplateIteration2, 'inputspec.interpolationMapping')

    # data Sink
    datasink = pe.Node(nio.DataSink(), name="datasink")
    datasink.inputs.base_directory = os.path.join(out_dir, "results")
    tbuilder.connect(buildTemplateIteration2, 'outputspec.template', datasink,
    'PrimaryTemplate')
    tbuilder.connect(buildTemplateIteration2, 'outputspec.passive_deformed_templates', datasink,
    'PassiveTemplate')
    tbuilder.connect(initAvg, 'output_average_image', datasink, 'PreRegisterAverage')
    tbuilder.config['execution']['crashfile_format'] = 'txt'
    #run
    try:
        tbuilder.run(plugin='MultiProc', plugin_args={'n_procs':N_PROCESS})
    except(RuntimeError) as err:
        print("RuntimeError:", err)
    else:
        raise
    
if __name__ == '__main__':
    args=get_args()
    DATA_DIR=args.data;     OUT_DIR=args.output
    SUB_LIST=args.sub_list; N_PROCESS=args.nprocs
    print("The input data folder: ", DATA_DIR, type(DATA_DIR))
    print("The output data folder: ", OUT_DIR, type(OUT_DIR) )
    print("The subject list: ",      SUB_LIST, type(SUB_LIST))
    main(DATA_DIR, OUT_DIR, SUB_LIST, N_PROCESS)
