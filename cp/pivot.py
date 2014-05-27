#!/usr/bin/env python

import pandas
import os
from collections import defaultdict
from PySide.QtGui import *
from PySide.QtCore import *


class PivotEngineException(Exception):
    pass

class QueryException(PivotEngineException):
    pass

class MergeException(PivotEngineException):
    pass

class DropException(PivotEngineException):
    pass


def _merge(data_frames_dict, chosen_dfs_dict):

    chosen_df_paths = chosen_dfs_dict.keys()
    chosen_columns = reduce(lambda x, y: x.union(y), chosen_dfs_dict.values())

    # iterate over all needed data frames and try to merge
    # them by a common column
    merged = data_frames_dict[chosen_df_paths[0]]
    merged = merged.reset_index()
    for df_path in chosen_df_paths[1:]:
        df = data_frames_dict[df_path]
        df = df.reset_index()
        common_columns = _find_common_columns(merged, df)

        merged = pandas.merge(merged,
                              df,
                              how="outer",
                              left_on=common_columns,
                              right_on=common_columns,
                              copy=False)
    return merged

def _drop(data_frame, chosen_columns):
    to_be_dropped = set()
    for column in data_frame.columns:
        if column not in chosen_columns:
            to_be_dropped.add(column)
    return data_frame.drop(list(to_be_dropped), axis=1) 

def _find_common_columns(df1, df2):
    df1_set = set(df1.columns)
    df2_set = set(df2.columns)
    intersec = df1_set.intersection(df2_set)
    if len(intersec) == 0:
        raise Exception(
            "No idea how to merge these tables! (no common column)")
    # elif len(intersec) > 1:
    #     raise Exception("More than two columns match!")
    return list(intersec)


def _apply_filters(data_frames_dict, filters):
    def _string_from_filter(filter_):
            query_string = "%s %s %s" % (filter_.column,
                                         filter_.condition,
                                         filter_.value)
            return query_string
    print("filters", filters)
    ret_dict = {}
    filter_dict = defaultdict(list)
    for filter_ in filters:
        filter_dict[filter_.data_frame_name].append(filter_)
    for data_frame_path, data_frame in data_frames_dict.items():
        data_frame_name = os.path.basename(data_frame_path)
        if data_frame_name in filter_dict.keys():
            filters = filter_dict[data_frame_name]
            query_strings = map(_string_from_filter, filters)
            query_string = ' and '.join(query_strings)
            ret_dict[data_frame_path] = data_frame.query(query_string)
        else:
            ret_dict[data_frame_path] = data_frame
    return ret_dict

def column_to_hex(data_frame, column_name):
    if column_name in data_frame.columns:
        data_frame[column_name] = data_frame[column_name].apply(lambda number: '0x%X' % number)

def pivot(data_frames_dict, column_tuples, row_tuples, displayed_value, filters, aggfunc=None):
    """ Returns a pivoted data frame

    data_frames_dict: a dictionary with csv paths as keys and Pandas.DataFrame as values
    column_tuples: ordered list of tuples (csv_path, name_of_chosen_column)
    row_tuples: ordered list of tuples (csv_path, name_of_chosen_column)
    """
    if aggfunc is None:
        aggfunc = 'sum'
    # make list of needed columns
    second_elem = lambda tup: tup[1]
    row_names = [second_elem(row_tup) for row_tup in row_tuples]
    column_names = [second_elem(row_tup) for row_tup in column_tuples]
    # all_columns = row_names + column_names

    data_frames_dict = _apply_filters(data_frames_dict, filters)

    df_column_dict = defaultdict(set)
    for csv_path, column_name in column_tuples:
        df_column_dict[csv_path].add(column_name)
    for csv_path, row_name in row_tuples:
        df_column_dict[csv_path].add(row_name)
    df_column_dict[displayed_value[0]].add(displayed_value[1])

    # if columns from different tables -> join on the columns with the same
    # name
    needed_data_frames = df_column_dict.keys()
    if len(needed_data_frames) > 1:
        data_frame = _merge(data_frames_dict, df_column_dict)
    else:
        data_frame = data_frames_dict[df_column_dict.keys()[0]].reset_index()

    chosen_columns = reduce(lambda x, y: x.union(y), df_column_dict.values())
   # data_frame.to_csv("./merged.csv")

    try:
        data_frame = _drop(data_frame=data_frame,
                           chosen_columns=chosen_columns)
    except Exception, e:
        raise DropException(str(e))

    column_to_hex(data_frame, 'bb')
    column_to_hex(data_frame, 'bb.1')

    from pandas.tools.pivot import pivot_table
    data_frame = pivot_table(data_frame,
                          values=displayed_value[1],
                          rows=row_names,
                          cols=column_names,
                          fill_value=0,
                          aggfunc=aggfunc)
    print(data_frame)
    return data_frame