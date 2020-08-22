#!/bin/bash
#SBATCH --job-name=mriqc_vince
#SBATCH --time=3:00:00
#SBATCH --account=rpp-aevans-ab
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=12GB
#SBATCH --array=1-57
# Outputs ----------------------------------
#SBATCH -o %x-%A-%a_%j.out
#SBATCH -e %x-%A-%a_%j.err
#SBATCH --mail-user=vincent.w.qing@gmail.com
#SBATCH --mail-type=ALL
# ------------------------------------------
DATA_DIR=(${@:1:1})
OUT_DIR=(${@:2:1})
SUB_LIST=(${@:3:1})
CON_IMG_DIR=(${@:4:1})
MRIQC_WORK_DIR=(${@:5:1})

echo DATA_DIR: ${DATA_DIR} 
echo OUT_DIR: ${OUT_DIR}
echo SUBJECT_List: ${SUB_LIST}
echo CON_IMG_DIR: ${CON_IMG_DIR}
echo MRIQC_WORK_DIR: ${MRIQC_WORK_DIR}
TEMPLATEFLOW_HOST_HOME=$HOME/scratch/templateflow
export SINGULARITYENV_TEMPLATEFLOW_HOME="/templateflow"
# Begin work section
SUB_STR=$(sed -n "${SLURM_ARRAY_TASK_ID}p" ${SUB_LIST})
echo ${SUB_STR}
SUB_ID="$(cut -d'-' -f2 <<<${SUB_STR})"
MRIQC_HOME=mriqc_home_${SUB_ID}
mkdir -p ${MRIQC_HOME}
echo "Slurm task ID: " ${SLURM_ARRAY_TASK_ID} "SUBJECT_ID: " ${SUB_ID} "SUBJECT_HOME: " ${MRIQC_HOME}


#module load singularity/3.5
#singularity cache clean -f --name mriqc_v0.15.2
unset PYTHONPATH
singularity run -B ${MRIQC_HOME}:/home/mriqc --home /home/mriqc --cleanenv \
        -B ${DATA_DIR}:/data:ro \
        -B ${OUT_DIR}:/out \
        -B ${MRIQC_WORK_DIR}:/mriqc_work \
        -B ${TEMPLATEFLOW_HOST_HOME}:${SINGULARITYENV_TEMPLATEFLOW_HOME} \
        ${CON_IMG_DIR} /data /out participant \
        --participant-label ${SUB_ID} -w /mriqc_work --session-id 1 --ica --no-sub --verbose-reports
rm -rf ${MRIQC_HOME}
