#! /usr/bin/env python3
# -*- coding:utf-8 -*-
# @Author: Vincent (Qing Wang)
# @Date:   2020-10-9 12:00:00
"""
======================================================
Preparing Ants folder for creating the group T1 template.
Created by Vincent.
======================================================
1. Libs and functions
"""
import os
import sys
import nipype.interfaces.utility as util

def dataGraber_sub(SUB_ID, DATA_DIR, TMPT_STR):
    import nipype.interfaces.io as nio
    import time
    t0=time.time()
    print('Grabbing files for: ', SUB_ID)
    OUT_FILE=[]
    out_len=len(TMPT_STR)
    if out_len == 0:
        print(SUB_ID+' has no files named: ', TMPT_STR)
        return OUT_FILE
    else:
        for i in range(out_len):
            TMP='%s/anat/%s_'+TMPT_STR[i]
            ds = nio.DataGrabber(infields=['subject_id', 'subject_id'])
            ds.inputs.base_directory = DATA_DIR # database
            ds.inputs.template = TMP 
            ds.inputs.subject_id = [SUB_ID]
            ds.inputs.sort_filelist = True
            res = ds.run()
            res_list = res.outputs.outfiles
            OUT_FILE.append(res_list)
        #print(SUB_ID+' files: ', OUT_FILE)
        print('dataGraber takes: ', time.time()-t0 )
        return OUT_FILE

def main(DATA_DIR, OUT_DIR, SRC_DIR):
    """1. Prepare folders """
    if not os.path.exists(OUT_DIR):
        os.makedirs(OUT_DIR)
    GROUPS=['PD','ET','NC']
    SUB_LIST=[]; AGE_LIST=[];
    """2. read images and mask images"""
    for group_name in GROUPS:
        current_group=group_name
        current_sub_list_file = SRC_DIR+'/'+current_group+'_info_ICA.list'
        # create dir for output
        current_OUT_DIR=OUT_DIR+current_group+'/'
        if not os.path.exists(current_OUT_DIR):
            os.makedirs(current_OUT_DIR)
        #read sub list
        with open(current_sub_list_file, 'r') as f_sub:
            sub_list_raw= f_sub.readlines()
        sub_list = [x[0:-1].split('\t')[0] for x in sub_list_raw] # remove 
        age_list = [x[0:-1].split('\t')[1] for x in sub_list_raw]
        SUB_LIST.append(sub_list);  AGE_LIST.append(age_list);
        N_sub=len(sub_list)
        print(N_sub, sub_list, age_list)
        DATA_DIR='/data/'+current_group
        TMPT_list=['desc-preproc_T1w.nii.gz', \
                   'desc-brain_mask.nii.gz', \
                   'space-MNI152NLin2009cAsym_desc-preproc_T1w.nii.gz', \
                   'space-MNI152NLin2009cAsym_desc-brain_mask.nii.gz'];
        print('Masking ',current_group,' group starts:')
        t0=time.time()
        for i_sub in range(0, N_sub,1):
            sub_str=sub_list[i_sub]
            res1 = dataGraber_sub(sub_str, DATA_DIR, TMPT_list)
            ind_t1 = res1[0]; ind_bm = res1[1];
            tmp_t1 = res1[2]; tmp_bm = res1[3];
            ind_masked_t1 = current_OUT_DIR+sub_str+'_'+'desc-masked_T1w.nii.gz'
            tmp_masked_t1 = current_OUT_DIR+sub_str+'_'+'space-MNI152NLin2009cAsym_desc-masked_T1w.nii.gz'
            mask_ind = fsl.ApplyMask(
                in_file=ind_t1,
                out_file=ind_masked_t1, 
                mask_file=ind_bm)
            mask_ind.run()
            mask_tmp = fsl.ApplyMask(
                in_file=tmp_t1,
                out_file=tmp_masked_t1,
                mask_file=tmp_bm)
            mask_tmp.run()
        print('Masking ',current_group,' finished in ',time.time()-t0, '\n')
        
if __name__ == '__main__':
    args=get_args()
    DATA_DIR=args.data;     OUT_DIR=args.output
    SUB_LIST=args.sub_list;
    print("The input data folder: ",  DATA_DIR, type(DATA_DIR))
    print("The output data folder: ",  OUT_DIR, type(OUT_DIR) )
    print("The subject list folder: ", SRC_DIR, type(SRC_DIR) )
    main(DATA_DIR, OUT_DIR, SRC_DIR)