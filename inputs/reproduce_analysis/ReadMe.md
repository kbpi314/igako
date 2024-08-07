Heatmap for paper: top20 ancom ASVs

mmeds_folder: 
/sc/arion/projects/MMEDS/mmeds_server_data/studies/mattS_IgA_IgG_vaccine_response_0/Qiime2_0/colon_LM

sample type: colon
mice group: Littermates = CoHoused
Both IgAKO and WT


1. Run Ancom on MMEDs output: bash_scripts/run_ancom.sh. The final output from ancom is ancom.qzv, which is then copied to inputs. The data.tsv file is given an _10 or _20 depending how many max and min asvs we want to analyze.

2. Create the conda environment: conda env create -f conda_env.yaml. Then: source activate analysis. Lastly, edit each bash_script so that the basedir parameter matches the directory reproduce_analysis is placed in.

3. sort Ancom results, get top 10 largest and smallest ASVs (20 total): bash_scripts/sort_ancom.sh

4. Filter results to top and bottom 10 ASVs, then combine with metadata and taxonomy: bash_scripts/merge_ancom.sh

5. Edit taxonomy-matched/top_10_asvs_taxonomy.py. Remove rows of unneeded metadata. Remove any columns that aren't ancom data or the taxonomy column. Switch the top two header rows, place the taxonomy column first. The header above the taxonomy should be Sample, then Strain below it. For reference, see the file heatmap-20-asvs.tsv

6. Generate the heatmap: bash_scripts/asv_heatmap.sh
