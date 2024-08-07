#!/bin/bash
#BSUB -q premium
#BSUB -W 72:00
#BSUB -J mattS-Qiime2_0
#BSUB -P acc_MMEDS
#BSUB -n 10
#BSUB -R "span[hosts=1]"
#BSUB -R rusage[mem=10000]
#BSUB -o /sc/arion/projects/MMEDS/mmeds_server_data/studies/mattS_IgA_IgG_vaccine_response_0/Qiime2_0/colon/ancom/mattS-Qiime2_0.stdout
#BSUB -eo /sc/arion/projects/MMEDS/mmeds_server_data/studies/mattS_IgA_IgG_vaccine_response_0/Qiime2_0/colon/ancom/mattS-Qiime2_0.stderr
#BSUB -L /bin/bash

export QIIME_BSUB_OPTIONS='-q premium -P acc_MMEDS -W 2:00 -n 1 -R rusage[mem=2000]';

source ~/.bashrc;
set -e
set -o pipefail
echo $PATH
export LC_ALL=en_US.UTF-8;
ml anaconda3;
source activate qiime2-2020.8.0;
RUN_Qiime2=/sc/arion/projects/MMEDS/mmeds_server_data/studies/mattS_IgA_IgG_vaccine_response_0/Qiime2_0/colon/ancom;

qiime feature-table filter-samples --i-table $RUN_Qiime2/taxa_collapsed_merged_table.qza --m-metadata-file $RUN_Qiime2/qiime_mapping_file.tsv --o-filtered-table $RUN_Qiime2/taxa_merged_table.qza;
qiime feature-table filter-features --i-table $RUN_Qiime2/filtered_table.qza --p-min-samples 5 --p-min-frequency 20 --o-filtered-table $RUN_Qiime2/seqs_filt_table.qza;

qiime composition add-pseudocount --i-table $RUN_Qiime2/seqs_filt_table.qza --o-composition-table $RUN_Qiime2/comp_table_filt.qza;

qiime composition ancom --i-table $RUN_Qiime2/comp_table_filt.qza --m-metadata-file $RUN_Qiime2/qiime_mapping_file.tsv --m-metadata-column Strain --o-visualization $RUN_Qiime2/ancom.qzv;
