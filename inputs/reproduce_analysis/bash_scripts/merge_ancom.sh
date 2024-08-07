#!/bin/bash

basedir=/home/matt/lab_analysis/cerutti-presentation/reproduce_analysis
ancomdir=$basedir/ancom/
inputdir=$basedir/inputs
mapname=$basedir/qiime_mapping_file.tsv
taxonomy=$basedir/taxonomy.tsv


outputdir1=$basedir/filtered-alr/
outputdir2=$basedir/merged-alr/
outputdir3=$basedir/taxonomy-matched/



mkdir $outputdir1
mkdir $outputdir2
mkdir $outputdir3


python scripts/join-tables.py -t $ancomdir/filt-table.tsv -m $basedir/sorted/data_10.tsv -o $outputdir1 -c1 '#OTU_ID' -c2 'id' -n 'top_10_asvs' -j 'right' -no

python scripts/join-tables.py -t $outputdir1/top_10_asvs.tsv -m $mapname -o $outputdir2 -c2 '#SampleID' -c1 'index' -c Strain -n 'top_10_asvs' -ac 'Strain' -fx -tf

python scripts/join-tables.py -t $outputdir2/top_10_asvs.tsv -m $basedir/taxonomy.tsv -o $outputdir3 -c1 'index' -c2 'Feature_ID' -n 'top_10_asvs_taxonomy' -ac 'Taxon'
