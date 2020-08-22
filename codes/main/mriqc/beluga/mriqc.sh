#!/bin/bash
DATA_NAME=(${@:1:1})
echo ${DATA_NAME}

WD_DIR=${HOME}/scratch
DATA_DIR=${WD_DIR}/${DATA_NAME}
BIDS_DIR=${DATA_DIR}_BIDS
CODE_DIR=${WD_DIR}/src
CODE_SLURM=${CODE_DIR}/mriqc.slurm
CODE_COLLECT=${CODE_DIR}/mriqc.format

SUB_LIST=${WD_DIR}/${DATA_NAME}_mriqc_subjects.list
CON_IMG_DIR=${WD_DIR}/container_images/mriqc_v0.15.2.simg

OUT_DIR=${DATA_DIR}_mriqc
LOG_DIR=${DATA_DIR}_mriqc.log
SLURM_LOG_DIR=${DATA_DIR}_mriqc_slurm_log
MRIQC_WORK_DIR=${DATA_DIR}_mriqc_work


RUN_ID=$(tail -c 9 ${LOG_DIR})
rm mriqc_vince-${RUN_ID}*.out
rm mriqc_vince-${RUN_ID}*.err
rm ${SUB_LIST}
rm -rf ${OUT_DIR}.zip
rm -rf ${SLURM_LOG_DIR}
rm -rf ${SLURM_LOG_DIR}.zip
rm -rf ${LOG_DIR}


chmod +x ${CODE_SLURM}
chmod +x ${CODE_COLLECT}

awk -F"\t" '{print $1}' ${BIDS_DIR}/participants.tsv >> ${SUB_LIST}
sed -i '1d' ${SUB_LIST}

echo "Step1: subjects list created!"

if [ -d ${OUT_DIR} ];then
        echo "mriqc out dir already exists!"
	rm -rf ${OUT_DIR}/*
else
        mkdir -p ${OUT_DIR}
fi
if [ -d ${MRIQC_WORK_DIR} ];then
	echo "mriqc work dir already exists!"
	rm -rf ${MRIQC_WORK_DIR}/*
else
	mkdir -p ${MRIQC_WORK_DIR}
fi
if [ -d ${SLURM_LOG_DIR} ];then
        echo "mriqc slurm log dir already exists!"
	rm -rf ${SLURM_LOG_DIR}/*
else
        mkdir -p ${SLURM_LOG_DIR}
fi
echo "Step2: starting mriqc!"
echo DATA_DIR: ${BIDS_DIR} 
echo OUT_DIR: ${OUT_DIR}
echo SUBJECT_List: ${SUB_LIST}
echo CON_IMG_DIR: ${CON_IMG_DIR}
echo MRIQC_WORK_DIR: ${MRIQC_WORK_DIR}
sbatch ${CODE_SLURM} ${BIDS_DIR} ${OUT_DIR} ${SUB_LIST} ${CON_IMG_DIR} ${MRIQC_WORK_DIR} >> ${LOG_DIR}
