#!/bin/bash

inputdir=/home/matt/lab_analysis/cerutti-presentation/
basedir=/home/matt/lab_analysis/cerutti-presentation/reproduce_analysis
mapname=$inputdir/qiime_mapping_file.tsv

outputdir=$inputdir/reproduce_analysis/heatmap

mkdir $outputdir


# example input
python scripts/double-heatmap.py -n colon_top10_asv -p $basedir/heatmap-20-asvs.tsv -fs 160 100 -s 8 -tl 'Colon MB' -rtx -o $outputdir -hc 'RdBu_r'

# Can run this only after editing the file, removing merge artifacts 
# python scripts/double-heatmap.py -n colon_top10_asv -p $basedir/taxonomy-matched/top_10_asvs_taxonomy.tsv -fs 160 100 -s 8 -tl 'Colon MB' -rtx -o $outputdir -hc 'RdBu_r'
