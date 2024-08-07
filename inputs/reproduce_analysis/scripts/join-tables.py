#!/usr/bin/env python3

import click
import numpy as np
import pandas as pd
from pathlib import Path
from modules.pandas_utils import read_tsv_into_dataframe, filter_by_col_val, sort_df, normalize_df, multiindex_from_index
from modules.map_file_utils import merge_map_files
from scipy.stats import zscore
from skbio.stats.composition import alr, clr


__author__ = "The Clemente Lab"
__copyright__ = "Copyright (c) 2021 The Clemente Lab"
__credits__ = ["Jose C. Clemente, Matthew Stapylton"]
__license__ = "GPL"
__version__ = "0.1-dev"
__maintainer__ = "Matthew Stapylton"
__email__ = "mkstapylton@gmail.com"


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.version_option(version='0.1')
@click.option('-n', '--combined_table_name',
              help="Path to first mapping file.")
@click.option('-fx', '--fix',
              is_flag=True,
              help="Path to first mapping file.")
@click.option('-m', '--map_file_path',
              help="Path to first dataframe file, columns of interest added to second dataframe.")
@click.option('-t', '--taxa_path',
              help="columns of interest will be added to this dataframe from the first using a dataframe join")
@click.option('-c1', '--map_join_col',
              default='',
              help="Name of first join column")
@click.option('-c2', '--taxa_join_col',
              default='',
              help="Path to second mapping file.")
@click.option('-j', '--join_direction',
              required=False,
              default='left',
              help="left, right, outer, inner or cross")
@click.option('-c', '--id_col',
              required=False,
              help="ID column, if passed, set it as first column of resulting map file.")
@click.option('-i2', '--id_col2',
              required=False,
              help="ID column, if passed, set it as first column of resulting map file.")
@click.option('-ac', '--additional_cols',
              required=False,
              help="additional columns to get from other table, if all is passed then we join the entire dataframe\n\
              e.x. -ac 'col1_name' -ac 'col2_name'")
@click.option('-dc', '--drop_cols',
              is_flag=True,
              required=False,
              help="columns to drop")
@click.option('-o', '--output_folder',
              help="Output folder for combined mapping file")
@click.option('-f', '--fill_na',
              is_flag=True,
              default=False,
              help="Output folder for combined mapping file")
@click.option('-fs', '--filter_stmt',
              is_flag=True,
              help="Output folder for combined mapping file")
@click.option('-rf', '--row_filters',
              multiple=True,
              default=[],
              help='Filter out rows that pattern match passed strings:\n\
              -rf column1,filter_val -rf col2,filter_val')
@click.option('-tf', '--transform',
              is_flag=True,
              help='transform second dataframe to match first')
@click.option('-rf', '--row_filters',
              multiple=True,
              default=[],
              help='Filter out rows that pattern match passed strings:\n\
              -rf column0,filter_val -rf col2,filter_val')
@click.option('-i', '--isolate_sample_name',
              is_flag=True,
              help="if True, isolates the sample name in the join column of the second mapping file.\
              Often it'll be part of a longer string: sample_name_L01_other_info, and we just want the first part\
              to join with")
@click.option('-no', '--normalize',
              is_flag=True,
              help="if True, normalize the final dataframe by dividing by column sums.")
def join_tables(combined_table_name, map_file_path, taxa_path, map_join_col, taxa_join_col,
                drop_cols, id_col, id_col2, additional_cols, output_folder, join_direction,
                fill_na, row_filters, filter_stmt, isolate_sample_name, transform, normalize, fix):
    """
    Combines two tsv mapping files through a left-outer join.
    The map_join_col is the join column from the first mapping file.
    The taxa_join_col is the join column from the second mapping file.

    id_co is supplied, will be set as the first column in the resulting mapping file.
    fill_nan if set to true, will replace NAN values that may result from a one to many join between mapping files.
    row_filters are row,value pairs used to filter the rows of the resulting mapping file.
    transform indicates that the second dataframe should be transformed before merging.
    """
    if map_file_path is not None:
        #map_df = read_tsv_into_dataframe(map_file_path, file_type='multi_header')
        map_df = read_tsv_into_dataframe(map_file_path)


    if taxa_path is not None:
        #taxa_df = read_tsv_into_dataframe(taxa_path, file_type='multi_header')
        taxa_df = read_tsv_into_dataframe(taxa_path)

        # if set, normalize the otu table
        if normalize:
            #taxa_df = normalize_df(taxa_df, taxa_df.columns[0])

            taxa_df.set_index(taxa_df.columns[0], inplace=True)

            taxa_df = taxa_df + 1
            taxa_df = taxa_df.apply(clr)
            taxa_df = taxa_df.apply(zscore)
            taxa_df.reset_index(inplace=True)

        # since taxa tables will often have sample names as columns, we may need to transform
        # only do so if the desired join column is not already in the columns, otherwise transform after merging
        if transform and taxa_join_col not in taxa_df.columns:
            df_transformed = True
            taxa_df.set_index(taxa_df.columns[0], inplace=True)
            taxa_df = taxa_df.T
            taxa_df.reset_index(inplace=True)
        else:
             df_transformed = False

        # sometimes sample names will be something like sampleID_something_not_useful
        # in that case grab just the sample_name for joining
        if isolate_sample_name:
             taxa_df[taxa_join_col] = taxa_df[taxa_join_col].str.split('_', expand=True)[0]

        # join the tables
        if map_join_col and taxa_join_col:
             new_df = merge_map_files(taxa_df, map_df, map_join_col, taxa_join_col, join_direction, additional_cols)

    else:
        new_df = map_df

    # when doing a one to many join, we may want to fill rows of nan values from the last non-nan value.
    if fill_na:
        new_df = new_df.replace('nan', np.NaN)
        new_df = new_df.fillna(method='ffill', axis=0)

    # option to filter combined table
    if filter_stmt:
        new_df = filter_by_col_val(new_df, row_filters, method='filter_stmt')

    # place id_columns first, sort
    # TODO: this code could be better
    if id_col:
        if id_col2:
            new_df.set_index(id_col2, inplace=True)
            new_df.reset_index(inplace=True)
        new_df.set_index(id_col, inplace=True)
        new_df.reset_index(inplace=True)
        new_df = sort_df(new_df, column=id_col, ascending=True)
        new_df.set_index(new_df.columns[0], inplace=True)
        new_df = new_df.T
        new_df.reset_index(inplace=True)

    # transform only if we didn't do it before merging
    # df = df.drop('id', errors='ignore')

    #if transform:
    #    new_df.set_index(new_df.columns[0], inplace=True)
    #    new_df = new_df.T
    #    new_df.reset_index(inplace=True)

    write_maps_to_tsv(new_df, output_folder, map_file_path, taxa_path, f'{combined_table_name}.tsv')


def write_maps_to_tsv(df, output_path, first_input_path, second_input_path, combined_table_name):
    """
    Write_dataframe_to_tsv() writes a dataframe to a folder as a tsv file.
    """
    df_path = Path(output_path) / Path(combined_table_name)
    df.to_csv((str(df_path)), index=None, header=True, sep='\t')


if __name__ == '__main__':
    join_tables()
