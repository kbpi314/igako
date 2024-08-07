#!/usr/bin/env python3

import click
from pathlib import Path
import pandas as pd
from modules.pandas_utils import (
    write_dataframe_to_tsv, read_tsv_into_dataframe, sort_df, filter_by_col_val, normalize_df
)

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
@click.option('-t', '--table_path',
              required=True,
              help="Path to taxa_tables.")
@click.option('-o', '--output_folder',
              required=True,
              help="Output file for results table")
@click.option('-to', '--table_operation',
              required=True,
              help="Table operation to execute on input tables, options include:\
              sort, int-sort, wide-to-long, long-to-wide, drop-cols and filter-stmt")
@click.option('-c', '--columns',
              multiple=True,
              required=False,
              help="Column or columns of interest, to be modified or treated special")
@click.option('-oc', '--other_columns',
              required=False,
              multiple=True,
              help="Other column or columns of interest, to do something else with")
@click.option('-v1', '--value_string1',
              required=False,
              help="A string to be used in modifying the tables")
@click.option('-v2', '--value_string2',
              required=False,
              help="Another string to be used in modifying tables")
@click.option('-tf', '--transform',
              required=False,
              help="Whether to transform the output df")
def data_manipulation(table_path, output_folder, table_operation, columns, other_columns,
                      value_string1, value_string2, transform):
    """
    Generic script for any sort of table-based calculations or transformations.
    taxa_table_path: path to folder containing taxa tables
    output_folder: path for output files to be written to.

    """
    # Create output folder
    output_dir = Path(output_folder)
    if not output_dir.exists():
        output_dir.mkdir(parents=True)

    # glob datafiles
    table_files = Path(table_path).glob('*.tsv')
    for i, tsv_file in enumerate(table_files):
        df = read_tsv_into_dataframe(tsv_file)

        if 'sort' in table_operation:
            # if columns is None, uses df.sort
            # if columns is a str or list, uses df.sort_values
            if table_operation == 'int-sort':
                print('int sort')
                if type(df[columns[0]]) is str:
                    df[columns[0]] = df[columns[0]].str.replace("[^0-9]", "", regex=True)
                df = sort_df(df, column=columns[0], ascending=False)

                i = int(tsv_file.stem.split('_')[1].replace('.tsv', ''))
                i = int(i)
                df_upper = df.iloc[:i, :]

                df_lower = df.tail(i)

                df = pd.concat([df_upper, df_lower])

            else:
                df = sort_df(df, column=columns[0], ascending=True)

        elif table_operation == 'wide-to-long':
            # melt a wide format table where measurements of variables are contained to single rows
            # id_vars are columns that are left alone
            # value_vars are columns that will be unpivoted, creating row for each combination of column values.
            # var_name is new column name for created variable column
            # value_name is new column name for created value column
            df = pd.melt(df, id_vars=columns,
                         value_vars=other_columns,
                         var_name=value_string1,
                         value_name=value_string2)

        elif table_operation == 'long-to-wide':
            # pivot a long format table, where measurements of a particular variable are spread out over multiple rows
            # index is the column that will be the new pivoted dataframe index
            # columns are the column(s) whose values will become the new dataframe columns
            df = df.fillna(0)
            df = pd.pivot_table(df, index=columns, columns=other_columns)
            df.reset_index(inplace=True)

        elif table_operation == 'combine-cols':
            df['value_string1'] = f'{df[columns[0]]} {df[columns[1]]}'

        elif table_operation == 'filter-stmt':
            # Filters a dataframe by multiple column values
            # value_string1 should be column1:column1_value, column2:column2_value
            # Each row in the resulting dataframe has at least ...
            # 1 value in at least 1 column of the specified column, value pairs
            df = filter_by_col_val(df, [value_string1], method='filter_stmt')

        # finally drop columns if specified or needed by another table_operation
        elif table_operation == 'drop-cols' or table_operation == 'combine-cols':
            # drops the specified columns
            df = df.drop(columns=columns)

        elif table_operation == 'regex':
            df.set_index(df.columns[0], inplace=True)
            df = df.filter(axis = 0, regex = '[\w\s]*\|[\w\s]*\|[\w\s]*')
            df = normalize_df(df)
            df.reset_index(inplace=True)

        if transform:
            df = df.T

        table_name = str(Path(tsv_file).stem)
        write_dataframe_to_tsv(df, f'{table_name}.tsv', output_folder)


if __name__ == '__main__':
    data_manipulation()
