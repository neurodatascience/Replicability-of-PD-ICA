#!/bin/bash
#SBATCH -J t1_temp_vince
#SBATCH --time=48:00:00
#SBATCH --account=def-jbpoline
#SBATCH --cpus-per-task=24
#SBATCH --mem-per-cpu=6G
# Outputs ----------------------------------
#SBATCH -o %x-%A-%a_%j.out
#SBATCH -e %x-%A-%a_%j.err
#SBATCH --mail-user=vincent.w.qing@gmail.com
#SBATCH --mail-type=ALL
# ------------------------------------------

DATA_DIR=(${@:1:1})
OUT_DIR=(${@:2:1})
IMG_DIR=(${@:3:1})
SRC_FILE=(${@:4:1})
DATA_NAME=(${@:5:1})
CODE_DIR=${HOME}/scratch/src
SINGULARITY_SUB_LIST=${DATA_NAME}_template_subjects.list

singularity exec -B $HOME:/home/neuro --home /home/neuro --cleanenv \
        -B ${DATA_DIR}:/data:ro \
        -B ${OUT_DIR}:/output \
        -B ${CODES_DIR}:/codes:ro \
        ${IMG_DIR} python /codes/${SRC_FILE} --data=/data --output=/output --sub_list=/codes/${SINGULARITY_SUB_LIST} --nprocs=24
#--account=rpp-aevans-ab
