#!/usr/bin/env python3

import pandas as pd
from modules.pandas_utils import drop_empty_rows


def merge_map_files(map1_df, map2_df, first_join_cols, second_join_cols, merge_direction='left', columns=False,
                    col_type='str'):
    """
    Combines two mapping files stored in dataframes through a left-outer join.
    first_join_col: the join column from the first mapping file. Can be a list of columns.
    second_join_col: the join column from the second mapping file. Can be a list of columns.
    merge_direction: which way to merge: left, right, outer, inner
    """
    # If we're working with a join on multiple columns
    if isinstance(first_join_cols, tuple):
        for join_col in first_join_cols:
            map1_df = map1_df.astype({join_col: col_type})
        for join_col in second_join_cols:
            map2_df = map2_df.astype({join_col: col_type})
    else:
        #map1_df = map1_df.astype({first_join_cols: col_type})
        #map2_df = map2_df.astype({second_join_cols: col_type})

        first_join_cols = [first_join_cols]
        second_join_cols = [second_join_cols]

    if columns:
        if 'all' in columns:
            df_to_merge = map2_df
        else:
            # cols_to_merge = first_join_cols + list(columns)
            cols_to_merge = second_join_cols + [columns]
            #cols_to_merge = [('Feature_ID', 'blah')] + [('Taxon', 'blah')]
            # cols_to_merge = second_join_cols.append(columns)

            #df_to_merge = map2_df[cols_to_merge]
            df_to_merge = map2_df

        #first_join_cols[0] = first_join_cols[0].strip('\"')

        #merged_map_df = pd.merge(map1_df, df_to_merge, how=merge_direction,
        #                         left_on=[('Group', 'Sample')], right_on=[('Feature_ID', 'blah')])
        merged_map_df = pd.merge(map1_df, df_to_merge, how=merge_direction,
                                 left_on=first_join_cols, right_on=second_join_cols)


    else:
        df_to_merge = map2_df[second_join_cols]

        merged_map_df = pd.merge(map1_df, df_to_merge, how=merge_direction,
                                 left_on=first_join_cols, right_on=second_join_cols)

    return merged_map_df


def filter_samples_by_mapping_file(df, map_df, filter_col, delimiter='_', set_index=True, transform=False):
    """
    Filters columns of a dataframe per a specific column in a metadata file.
    df: the dataframe we're filtering
    map_df: dataframe of the map file
    filter_col: column in the map_df we want to fill the df by
    delimeter: delimiter of the sample/column names, checks if any part matches the filter_col value.
    """
    # TODO: investigate filtering by joining to the filter column.
    if set_index:
        df.set_index(df.columns[0], inplace=True)

    if transform:
        df = df.T
    # The values we're filtering by
    samples_to_keep = map_df[filter_col].tolist()

    # The actual sample names in the passed dataframe
    sample_filter_list = []
    for col in df.columns.values.tolist():
        colname = col.split(delimiter)[0]
        if colname in samples_to_keep:
            sample_filter_list.append(col)

    df = df.filter(items=sample_filter_list, axis='columns')

    if transform:
        df = df.T

    # if set_index:
    df.reset_index(inplace=True)

    df = drop_empty_rows(df)
    return df
