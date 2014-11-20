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

class ConcatenateException(PivotEngineException):
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
  #  print("filters", filters)
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

def _concat_data_frames(data_frames_dict):
    from pandas import concat
    from pandas import MultiIndex
    from itertools import product

    value_tuples = data_frames_dict.keys()
    df_list = data_frames_dict.values()
    nr_columns = df_list[0].shape[1]
    for df in df_list:
        if df.shape[1] != nr_columns:
            raise ConcatenateException("Can't concatenate data frames: number of columns doesn't match")

    concatenated = None
    for column_idx in xrange(nr_columns):
        if concatenated is None:
            #bootstrap with first columns of each data frame
            concatenated = concat([df.iloc[:, column_idx] for df in df_list], axis=1)
        else:
            #add new chunks to the already concatenated part
            new_chunk = concat([df.iloc[:, column_idx] for df in df_list], axis=1)
            concatenated = concat([concatenated, new_chunk], axis=1)
    displayed_column_names = [value_tuple[1] for value_tuple in value_tuples]
    # and now...
    # ..
    # evil silence :>
    # l1=[(1,2),(3,4)]
    # l2=(9,0)
    # we want to get this: l3 = [(1, 2, 9), (1, 2, 0), (3, 4, 9), (3, 4, 0)]
    l1 = df_list[0].columns
    l2 = displayed_column_names
    if isinstance(l1[0], tuple):
    # l1=[(1,2),(3,4)]
    # l2=(9,0)
    # we want to get this: l3 = [(1, 2, 9), (1, 2, 0), (3, 4, 9), (3, 4, 0)]
        l3 = [(l1e[0], l1e[1], l2e) for l1e in l1 for l2e in l2]
    elif isinstance(l1[0], str):
    # l1=[1,4]
    # l2=(9,0)
    # we want to get this: l3 = [(1, 9), (1, 0), (4, 9), (4, 0)]
        l3 = [(l1e, l2e) for l1e in l1 for l2e in l2] 
    print(type(l1[0]))
    print(l1)
    print(l2)
    print(l3)
    concatenated.columns = MultiIndex.from_tuples(l3)
    return concatenated


def column_to_hex(data_frame, column_name):
    if column_name in data_frame.columns:
        data_frame[column_name] = data_frame[column_name].apply(lambda number: '0x%X' % number)

def pivot(data_frames_dict, column_tuples, row_tuples, displayed_value_tuples, filters, ret, div_on_top=False, aggfunc=None):
    """ Returns a pivoted data frame

    data_frames_dict: a dictionary with csv paths as keys and Pandas.DataFrame as values
    column_tuples: ordered list of tuples (csv_path, name_of_chosen_column)
    row_tuples: ordered list of tuples (csv_path, name_of_chosen_column)
    """
    from collections import OrderedDict
    if aggfunc is None:
        aggfunc = 'sum'
    output_data_frames = OrderedDict()
    # make list of needed columns
    second_elem = lambda tup: tup[1]
    row_names = [second_elem(row_tup) for row_tup in row_tuples]
    column_names = [second_elem(row_tup) for row_tup in column_tuples]
    # all_columns = row_names + column_names

    fitlered_data_frames = _apply_filters(data_frames_dict, filters)

    # for each displayed dimension create a data frame, then merge them before displaying
    for displayed_value_tuple in displayed_value_tuples:
        csv_path, displayed_column_name = displayed_value_tuple

        df_column_dict = defaultdict(set)
        df_column_dict[csv_path].add(displayed_column_name)
        for csv_path, column_name in column_tuples:
            df_column_dict[csv_path].add(column_name)
        for csv_path, row_name in row_tuples:
            df_column_dict[csv_path].add(row_name)
        for csv_path, merit_name in displayed_value_tuples:
            df_column_dict[csv_path].add(merit_name)

        # if columns from different tables -> join on the columns with the same
        # name
        needed_data_frames = df_column_dict.keys()
        if len(needed_data_frames) > 1:
            data_frame = _merge(fitlered_data_frames, df_column_dict)
        else:
            data_frame = fitlered_data_frames[df_column_dict.keys()[0]].reset_index()

        chosen_columns = reduce(lambda x, y: x.union(y), df_column_dict.values())
       # data_frame.to_csv("./merged.csv")

        try:
            data_frame_with_dropped_columns = _drop(data_frame=data_frame,
                                                    chosen_columns=chosen_columns)
        except Exception, e:
            raise DropException(str(e))

        column_to_hex(data_frame, 'bb')
        column_to_hex(data_frame, 'bb.1')

        from pandas.tools.pivot import pivot_table
        data_frame = pivot_table(data_frame_with_dropped_columns,
                              values=displayed_column_name,
                              rows=row_names,
                              cols=column_names,
                              fill_value=0,
                              aggfunc=aggfunc)
        output_data_frames[displayed_value_tuple] = data_frame
        print(data_frame)
        print("\n\n")
    # obscure way of returning values though input arguments
    # it makes running this method in a separate thread much easier
    if len(output_data_frames) == 1:
        ret[0] = output_data_frames.values()[0]
    else:
        ret[0] = _concat_data_frames(output_data_frames)
        #ret[0] = output_data_frames.values()[0]
    