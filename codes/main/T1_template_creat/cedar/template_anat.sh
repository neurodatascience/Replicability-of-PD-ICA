#!/bin/bash
DATA_NAME=(${@:1:1})
echo ${DATA_NAME}

WD_DIR=${HOME}/scratch
DATA_DIR=${WD_DIR}/${DATA_NAME}
BIDS_DIR=${DATA_DIR}_BIDS
CODE_DIR=${WD_DIR}/src
CODE_SLURM=${CODE_DIR}/template_anat.slurm
CODE_COLLECT=${CODE_DIR}/template_anat.format
CODE_SRC=template_anat.py
SUB_LIST=${CODE_DIR}/${DATA_NAME}_template_subjects.list
CON_IMG_DIR=${WD_DIR}/container_images/vincent_env_v0.0.simg

IN_DIR=${DATA_DIR}_fmriprep_anat_20.1.1/fmriprep
OUT_DIR=${DATA_DIR}_template-anat
LOG_DIR=${DATA_DIR}_template-anat.log
SLURM_LOG_DIR=${DATA_DIR}_template-anat_slurm
WORK_DIR=${DATA_DIR}_template-anat_work
echo SUBLIST:_$SUB_LIST

RUN_ID=$(tail -c 9 ${LOG_DIR})
rm fmriprep_vince-${RUN_ID}*.out
rm fmriprep_vince-${RUN_ID}*.err

rm -rf ${OUT_DIR}
rm -rf ${OUT_DIR}.zip
rm -rf ${WORK_DIR}
rm -rf ${SLURM_LOG_DIR}
rm -rf ${SLURM_LOG_DIR}.zip
#rm -rf ${SUB_LIST}

chmod +x ${CODE_SLURM}
chmod +x ${CODE_COLLECT}

if [ -d ${OUT_DIR} ];then
        echo "Outdir existed, and will be cleaned up!"
        rm -rf ${OUT_DIR}/*
else
        mkdir -p ${OUT_DIR}
        echo "Out_dir created!"
fi

if [ -d ${SLURM_LOG_DIR} ];then
        echo "Log_dir existed, and will be cleaned up!"
        rm -rf ${SLURM_LOG_DIR}/*
else
        mkdir -p ${SLURM_LOG_DIR}
        echo "Log_dir created!"
fi

## subjects list
#touch ${SUB_LIST}
#ls -d ${IN_DIR}/*/ | awk -F"/" '{print $7}'>> ${SUB_LIST}
#sed -i '1d' ${SUB_LIST}
#sed -i '/0039/d' ${SUB_LIST}
#sed -i '/0042/d' ${SUB_LIST}
#sed -i '/0044/d' ${SUB_LIST}
#sed -i '/0064/d' ${SUB_LIST}
#sed -i '/0058/d' ${SUB_LIST}
#sed -i '/0077/d' ${SUB_LIST}
#sed -i '/0080/d' ${SUB_LIST}
#sed -i '/0108/d' ${SUB_LIST}
#sed -i '/0110/d' ${SUB_LIST}

echo "T1 template input data dir: " ${IN_DIR} 
echo "T1 template output dir: " ${OUT_DIR} 
echo "T1 template SIG IMAGE dir: " ${CON_IMG_DIR} 
echo "T1 template Script dir: " ${CODE_SRC}

# Begin work section
sbatch ${CODE_SLURM} ${IN_DIR} ${OUT_DIR} ${CON_IMG_DIR} ${CODE_SRC} ${DATA_NAME}>> ${LOG_DIR}
