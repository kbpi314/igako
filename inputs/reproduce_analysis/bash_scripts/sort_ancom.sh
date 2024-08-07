#!/bin/bash

pwd=$(pwd)

basedir=/home/matt/lab_analysis/cerutti-presentation/reproduce_analysis/

python scripts/single-dataframe-operations.py -t $basedir/inputs -o $basedir/sorted -to int-sort -c clr

