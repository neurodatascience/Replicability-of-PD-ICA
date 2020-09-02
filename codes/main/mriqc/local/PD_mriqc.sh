#!/bin/bash
mkdir -p PD_mriqc_0.15.2
mkdir -p PD_mriqc_work
rm -r PD_mriqc_0.15.2/*
rm -r PD_mriqc_work/*
echo "" > PD_mriqc.log
echo "Start PD 43 participants QC..."
unset PYTHONPATH
singularity run -B $HOME:/home/mriqc --home /home/mriqc --cleanenv \
        -B ${HOME}/project/PD_BIDS:/data:ro \
        -B ${HOME}/project/PD_mriqc_0.15.2:/out \
        -B ${HOME}/project/PD_mriqc_work:/mriqc_work \
        -B ${HOME}/project/templateflow:/templateflow \
        ${HOME}/container_images/mriqc_v0.15.2.simg /data /out participant \
        --participant-label sub-0002 \
sub-0004 \
sub-0005 \
sub-0006 \
sub-0008 \
sub-0009 \
sub-0012 \
sub-0014 \
sub-0015 \
sub-0021 \
sub-0022 \
sub-0023 \
sub-0024 \
sub-0025 \
sub-0026 \
sub-0027 \
sub-0028 \
sub-0029 \
sub-0030 \
sub-0031 \
sub-0034 \
sub-0035 \
sub-0037 \
sub-0038 \
sub-0040 \
sub-0047 \
sub-0051 \
sub-0052 \
sub-0068 \
sub-0075 \
sub-0076 \
sub-0094 \
sub-0096 \
sub-0098 \
sub-0109 \
sub-0111 \
sub-0118 \
sub-0125 \
sub-0129 \
sub-0132 \
sub-0136 \
sub-1000 \
sub-1020 -w /mriqc_work --session-id 1 --ica --no-sub --verbose-repo --profile -vvv
echo "Start group QC..."
singularity run -B $HOME:/home/mriqc --home /home/mriqc --cleanenv \
        -B ${HOME}/project/PD_BIDS:/data:ro \
        -B ${HOME}/project/PD_mriqc_0.15.2:/out \
        -B ${HOME}/project/PD_mriqc_work:/mriqc_work \
        -B ${HOME}/project/templateflow:/templateflow \
        ${HOME}/container_images/mriqc_v0.15.2.simg /data /out group -w /mriqc_work --verbose-reports
