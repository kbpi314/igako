#!/usr/bin/env python3

import pandas as pd
import numpy as np
from pathlib import Path


def read_tsv_into_dataframe(df_path, file_type='', delim="\t"):
    """
    From a path to a tsv file, the function loads the file to a pandas dataframe.
    """
    if file_type == 'qiime':
        df = pd.read_csv(df_path, sep=delim, skiprows=[1], header=[0])
    elif file_type == 'multi_header':
        df = pd.read_csv(df_path, sep=delim, header=[0, 1])
    elif file_type == 'feature_table':
        df = pd.read_csv(df_path, sep=delim, skiprows=1, index_col='#OTU ID')
    elif file_type == 'taxonomy_file':
        df = pd.read_csv(df_path, sep=delim, index_col='taxonomy_target_level')
    #elif file_type == 'irep':
    #    df = pd.read_csv(df_path, sep=delim, skiprows=1)
    elif file_type == 'reader_file':
        table_name = str(Path(df_path).stem)
        if 'Coloc' in table_name:
            table_name = table_name.replace('_ORG.tif_Coloc_Results', '')
            df = pd.read_csv(df_path, sep=delim, names=['reader_field', table_name])
        elif 'nuclei' in table_name:
            df = pd.read_csv(df_path, sep=delim)
    elif file_type == '':
        df = pd.read_csv(df_path, sep=delim)
    else:
        raise ValueError(f'invalid file type: {file_type}')

    return df


def write_dataframe_to_tsv(df, file_name, output_path=None):
    """
    Write_dataframe_to_tsv() writes a dataframe to a folder as a tsv file.
    """
    if output_path is None:
        df_path = file_name
    else:
        output_folder = Path(output_path)
        if not output_folder.exists():
            output_folder.mkdir(parents=True)
        df_path = output_folder / Path(file_name)
    df.to_csv((str(df_path)), index=None, header=True, sep='\t')


def drop_empty_rows(df, set_index=True):
    """
    Drop rows of all zeroes from the dataframe.
    """
    # Get a list of empty rows and then drop any row on the list from the dataframe.
    empty_rows = get_empty_rows(df, set_index)
    if empty_rows:

        if set_index:
            df.set_index(df.columns[0], inplace=True)
        df.drop(index=empty_rows, inplace=True)

        if set_index:
            df.reset_index(inplace=True)
    return df


def get_empty_rows(df, set_index=True):
    """
    Checks if any row of a dataframe contains only zeroes.
    """
    empty_rows = []
    temp_df = df.copy(deep=True)

    if set_index:
        temp_df.set_index(df.columns[0], inplace=True)

    temp_df = temp_df.T

    for series in temp_df.items():
        # Check if there are any rows that don't have at least one non-zero entry.
        if not series[1].any(axis=None):
            empty_rows.append(series[0])

    return empty_rows


def filter_by_col_val(df, filter_args, method='filter_stmt', split_char=','):
    """
    Filters a dataframe per values of specified column(s).
    Filter args are passed in a list
    column:filter-value pairs can be separated by a comma in a single list entry, if so...
    an AND condition is placed between them
    Separate column:filter-value pairs in the passed list will have an OR condition placed between them
    If this seems needlessly confusing, I challenge you to design something better on the fly to accomplish the same!

    df: dataframe to filter
    filter_args: list of column:filter-value pairs.
    split_char: comma by default, used to split list entries that are combined in an AND statement.

    method: filter_like uses pandas like filter, pretty inflexible but can also be used to filter columns...
    filter_stmt is basically you give this function a bunch of filter arguments and we build a string of ANDs and ORs...
    separated by the column,filter_value pairs to filter the dataframe by
    """
    # Outer string is used to build the OR conditions between filter conditions
    # columnX == 1 or columnX == 2
    outer_string = ""
    for i, cfilter in enumerate(filter_args):

        filter_vals = cfilter.split(split_char)
        # Filter string is used to build out the AND conditions between columns and their filter values
        # columnX == 1 and columnY == 2
        filter_string = ""

        for j, fval in enumerate(filter_vals):

            filter_col, filter_val = fval.split(':')

            if method == 'filter_like':
                df.set_index(filter_col, inplace=True)
                df = df.filter(like=filter_val, axis='index')
                df.reset_index(inplace=True)
            elif method == 'filter_stmt':

                # add quotes to non-numeric filter values
                if not filter_val.startswith('"') and not filter_val.replace('.', '').isnumeric():
                    filter_val = f'"{filter_val}"'

                # Filter by AND and OR statements
                # ColumnX == 1 AND ColumnY == 1 OR ColumnX == 2 AND ColumnY == 2
                if j == 0:
                    filter_string += f'(df["{filter_col}"]=={filter_val})'
                else:
                    filter_string += f' & (df["{filter_col}"]=={filter_val})'

        if method == 'filter_stmt':
            if i == 0:
                outer_string += f'({filter_string})'
            else:
                outer_string += f' | ({filter_string})'
            if len(filter_args) == i + 1:
                x = outer_string
                df = df[eval(x)]

    return df


def filter_index_by_values(df, filter_values, index=None):
    """
    Filters a dataframe per the index values of another dataframe or series.
    df: dataframe to be filtered.
    filter_values: list-like (series, index or list) of values to keep in the dataframe's index.
    """
    if index:
        index = eval(index)
        df.set_index(index, inplace=True)
    output_df = df.filter(items=filter_values, axis='index')

    if index:
        output_df.reset_index(inplace=True)
    return output_df


def replace_col_values(df, replacement_col_values):
    """
    Replace values in specified column with new values.
    replacement_col_values are a list of column,old_value,new_value triplets.
    """
    for cvalues in replacement_col_values:
        column_name, old_value, new_value = cvalues.split(',')
        df.loc[df[column_name] == old_value, column_name] = new_value

    return df


def fill_nan(df, value=0, fill_method=None):
    """
    Fill dataframe NaN values.
    fill methods include ffill, bfill that are ...
    based on the next or previous observed value while iterating over a column.
    """
    df = df.replace('nan', np.NaN)

    if fill_method is not None:
        df.fillna(method=fill_method, axis=0, inplace=True)
    else:
        df.fillna(value, axis=0, inplace=True)

    return df


def sqrt_arcsine_function(df, index):
    """
    Import a dataframe and performs an square root arcsine transformation.
    """
    if index:
        df.set_index(index, inplace=True)
    df = df.transform(lambda x: np.arcsin(np.sqrt(x)))
    if index:
        df.reset_index(inplace=True)
    return df


def sort_df(df, index=None, column=None, ascending=True):
    """
    Sorts a dataframe across both axes
    If index is passed, set it as the index to sort by.
    """
    if index:
        df = df.set_index(index)
        df = df.sort_index(axis=0)
        df = df.sort_index(axis=1)
        df = df.reset_index(index)
    if column:
        df = df.sort_values(by=column, axis=0, ascending=ascending)
    else:
        df = df.sort_index(axis=0)
        df = df.sort_index(axis=1)
    return df


def zero_one_map(df, index=None):
    """
    Maps all positive values to 1.
    :param index: Column name for taxonomic strings.
    :param df: taxa table with results from each tool.
    :return df: taxa_table of 0s and 1s.
    """
    if index is not None:
        df.set_index(index, inplace=True)

    # Map positive values to 1
    df[df > 0] = 1

    if index is not None:
        df.reset_index(index, inplace=True)
    return df


def get_column_sums(df, index=None, validate=False):
    """
    Computes the column sums for a dataframe.
    If validate is true, checks that column sums rounded in the digits place is 1.
    Otherwise, returns a pandas Series of the column sums.
    """
    df_copy = df.copy(deep=True)

    # For validation, drop empty columns because their column sum will be 0.
    if validate:
        df_copy = drop_empty_columns(df_copy, index)

    # Sum the columns and then round the resulting dataframe to account for small deviations from 1 or 100.
    if index is not None:
        df_copy.set_index(index, inplace=True)
    df_sum = df_copy.sum(axis=0)

    if validate:
        df_sum = df_sum.round(1)

        if not df_sum.subtract(1).any(axis=None):
            # The abundances are ratios.
            invalid_column_sums = False
        elif not df_sum.subtract(100).any(axis=None):
            # The abundances are percents.
            invalid_column_sums = False
        else:
            # At least one column sum is invalid.
            invalid_column_sums = True
        ret_val = invalid_column_sums
    else:
        ret_val = df_sum

    return ret_val


def drop_empty_columns(df, index):
    """
    drop columns of all zeroes from the dataframe.
    """
    if index is not None:
        df.set_index(index, inplace=True)
    df = df.loc[:, (df != 0).any(axis=0)]

    if index is not None:
        df.reset_index(index, inplace=True)
    return df


def add_df_sum_row(df, index=None, return_df=False):
    """
    Create a row of column sums, return either as a series or as a dataframe.
    """
    # get a Series of column sums for the dataframe
    df_sum = get_column_sums(df, index)

    if return_df:
        ret_val = pd.DataFrame(data=df_sum.values, index=df_sum.index, columns=['row_sum'])
    else:
        ret_val = df_sum
    return ret_val


def multiindex_from_index(df, old_col, new_col, set_multiindex=True):
    """
    Create two columns, or a new multi-index out of an old multi-index.
    Old multi-index column will be in the format: (col1), (col2)

    df: dataframe
    old_col: name of original index
    new_col: name of the new second column, or index to be created
    set_multiindex: whether to set the new columns as a multi-index
    """
    df.reset_index(inplace=True)
    df[[new_col, old_col]] = df[old_col].str.split(',', expand=True)

    df[old_col] = df[old_col].str.replace('(', '')
    df[old_col] = df[old_col].str.replace(')', '')
    df[old_col] = df[old_col].str.replace("'", '')
    df[old_col] = df[old_col].str.strip()

    df[new_col] = df[new_col].str.replace('(', '')
    df[new_col] = df[new_col].str.replace(')', '')
    df[new_col] = df[new_col].str.replace("'", '')
    df[new_col] = df[new_col].str.strip()

    if set_multiindex:
        df.set_index(old_col, inplace=True)
        df.set_index(new_col, append=True, inplace=True)

    return df


def normalize_df(taxa_df, index=None):
    """
    Normalizes a table by dividing by column sums.
    :param taxa_level: Column name for taxonomic strings.
    :param taxa_df: taxa table with results from each tool.
    :return taxa_df: taxa_table normalized to have column sums equal to 1.
    """
    if index:
        taxa_df.set_index(index, inplace=True)
    # divide by column sums
    column_sums = get_column_sums(taxa_df)
    taxa_df = taxa_df.div(column_sums)

    if index:
        taxa_df.reset_index(index, inplace=True)

    return taxa_df


def combine_duplicates(taxa_df, taxa_level):
    """
    taxa_df is a dataframe that is returned from Tool.combine_tool_output()
    The dataframe has species names in the first column.
    """
    return taxa_df.groupby([taxa_level]).sum().reset_index(level=0)


def convert_df_to_ratio(taxa_df, taxa_level):
    """
    Converts a dataframe to ratios that sum to 1.
    Assumes that the dataframe column sums are 100.
    """
    taxa_df.set_index(taxa_level, inplace=True)
    taxa_df = taxa_df.div(100)
    taxa_df.reset_index(taxa_level, inplace=True)

    return taxa_df


def convert_df_to_percent(taxa_df, taxa_level):
    """
    Converts a dataframe to percents that sum to 100.
    Assumes that the dataframe column sums are 1.
    """
    taxa_df.set_index(taxa_level, inplace=True)
    taxa_df = taxa_df.mul(100)
    taxa_df.reset_index(taxa_level, inplace=True)

    return taxa_df


def get_shared_samples(taxa_df1, taxa_df2, taxa_level):
    """
    Removes samples that don't exist in both taxa tables.
    """
    second_samples, first_samples = get_df_samples_diff(taxa_df1, taxa_df2)

    # Minimize dataframe differences
    taxa_df1.set_index(taxa_level, inplace=True)
    taxa_df2.set_index(taxa_level, inplace=True)
    if first_samples:
        taxa_df1 = taxa_df1.drop(columns=second_samples)

    if second_samples:
        taxa_df2 = taxa_df2.drop(columns=first_samples)

    if taxa_df1.columns.to_list() == taxa_df2.columns.to_list():
        shared_samples = taxa_df1.columns.to_list()
    else:
        shared_samples = []
    taxa_df1.reset_index(inplace=True)
    taxa_df2.reset_index(inplace=True)

    return taxa_df1, taxa_df2, shared_samples


def get_df_samples_diff(taxa_df1, taxa_df2):
    """
    Compares the columns of two dataframes and returns the difference.
    Column names are derived from a list of samples.
    Returns two lists of column names that are uniquely found in one dataframe or the other.
    """
    ensemble_table_unique_samples = taxa_df2.columns.difference(taxa_df1.columns)
    previous_table_unique_samples = taxa_df1.columns.difference(taxa_df2.columns)

    return previous_table_unique_samples.tolist(), ensemble_table_unique_samples.tolist()


def filter_taxa_table(tsv_path, output_folder, min_abundance=.1, sample_threshold=3):
    """
    filter_taxa_table() filters out species which don't meet the minimum abundance in a minimum number of samples.
    tsv_path is the path to the input tsv_file.
    min_abundance is the minimum relative abundance, which is expected to be between 0 and 1.
    sample_threshold is the minimum number of samples a species should have which meet the min_abudance to remain in...
    the dataframe.
    A filtered dataframe is printed to the terminal and written to disk per the output_folder parameter.
    """

    unfiltered_df = read_tsv_into_dataframe(tsv_path)
    unfiltered_df.set_index(unfiltered_df.columns[0], inplace=True)

    # Creating a new filtered data frame which drops the rows whose index's didn't meet the parameters.
    filtered_df = filter_df(unfiltered_df, min_abundance, sample_threshold)

    filtered_df.reset_index(inplace=True)
    return filtered_df


def filter_df(df, min_abundance, sample_threshold):
    """
    Returns a filtered dataframe per the criteria set by the passed parameters.

    Parameters:
    df (data frame): the input dataframe that will be filtered.
    min_abundance (int): the minimum abundance for a sample to pass the threshold.
    sample_threshold (int): The minimum samples needed to meet the minimum abundance.

    Returns:
    df (data frame): The filtered dataframe.
    """
    drop_rows = []

    for index, row in df.iterrows():
        passed_threshold = False
        min_abundance_counter = 0
        for sample in row:
            # Check if a sample meets the min abudance.
            if sample >= min_abundance:
                min_abundance_counter += 1
            # If the sample_threshold condition is met, break out of the loop.
            if min_abundance_counter == sample_threshold:
                passed_threshold = True
                break

        # After iterating through the row, if the sample threshold is not met, then drop the row.
        if not passed_threshold:
            drop_rows.append(index)

    # Dropping the rows whose index's are in drop_rows list.
    if drop_rows:
        df.drop(index=drop_rows, inplace=True)
    return df
