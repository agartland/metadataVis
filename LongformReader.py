import pandas as pd
import sys
import os.path as op
from bisect import bisect_left
import numpy as np
import random
#from bokeh.io import show, output_file
#from bokeh.models import TableColumn, DataTable, ColumnDataSource, CustomJS
#from bokeh.layouts import layout
#from bokeh.models.widgets import MultiSelect, Dropdown


# DATAFRAME CONFIGURATION:
def _generateWideform(uniquerow_str, uniquecol_str, value_str, row_str, col_str, longform_df):

    # Row Metadata Table
    unique_rows = [x.strip() for x in (uniquerow_str + ", " + row_str).split(',')]
    rowmeta_index = '|'.join(unique_rows)
    rowmeta_columns = [x.strip() for x in row_str.split(',')]

    # Column Metadata Table
    unique_cols = [x.strip() for x in (uniquecol_str + ", " + col_str).split(',')]
    colmeta_index = '|'.join(unique_cols)
    colmeta_columns = [x.strip() for x in col_str.split(',')]

    longform_df[rowmeta_index] = longform_df.apply(lambda r: '|'.join(r[unique_rows].astype(str)), axis=1)
    longform_df[colmeta_index] = longform_df.apply(lambda r: '|'.join(r[unique_cols].astype(str)), axis=1)
    # print(len(longform_df[colmeta_index]))

    wideform_df = longform_df.pivot_table(index=rowmeta_index, columns=colmeta_index, values=value_str)
    # print(len(wideform_df.columns.values))
    # print(wideform_df.columns.values[:15])
    # print(longform_df[colmeta_index].head(15))
    ids = list(range(1, wideform_df.shape[0] + 1))
    id_list = ['id-{0}'.format(i) for i in ids]
    rowmeta_dict = {}
    lf_col_names = list(longform_df.columns.values)
    for entry in unique_rows:
        if entry in lf_col_names:
            rowmeta_dict[entry] = longform_df[entry]
    ptid_md = pd.DataFrame(data=rowmeta_dict,
                           columns=rowmeta_dict.keys())
    ptid_md = ptid_md.drop_duplicates()

    colmeta_dict = {colmeta_index: longform_df[colmeta_index]}
    for entry in unique_cols:
        colmeta_dict[entry] = longform_df[entry]
    measure_md = pd.DataFrame(data=colmeta_dict,
                              columns=colmeta_dict.keys())
    measure_md = measure_md.drop_duplicates()
    #print(wideform_df.columns.values[:15])
    wideform_df = wideform_df.reindex(measure_md[colmeta_index], axis=1)
    try:
        ptid_md['id'] = id_list
        ptid_md.set_index("id", inplace=True)
    except ValueError:
        print("Index row not unique")
        return "Index row not unique", None, None
    if measure_md.shape[0] != wideform_df.shape[1]:
        print("Index column not unique")
        print(measure_md.shape[0])
        print(wideform_df.shape[1])
        return "Index column not unique", None, None

    measure_md.set_index(colmeta_index, inplace=True)
    wideform_df['id'] = id_list
    wideform_df.set_index("id", inplace=True)

    return wideform_df, ptid_md, measure_md



def _handleRX(ex_rowmeta_cols, ptid_md, base_rows, rx):
    rx_col_names = list(rx.columns.values)
    for col in rx_col_names:
        if (base_rows.lower() == col.lower()) & (base_rows != col):
            rx.rename(columns={col: base_rows}, inplace=True)
    if '-' in rx[base_rows][0]:
        rx[base_rows] = rx[base_rows].str.replace('-', '')

    rx_subset_cols = []
    for entry in ex_rowmeta_cols:
        if entry in rx_col_names:
            rx_subset_cols.append(entry)
    rx_subset_cols.append(base_rows)
    rx_subset = rx[rx_subset_cols]
    ptid_md = pd.merge(ptid_md, rx_subset, on='ptid', how='inner')
    return ptid_md


# def binary_search(a, x, lo=0, hi=None):  # can't use a to specify default for hi
#     hi = hi if hi is not None else len(a)  # hi defaults to len(a)
#     pos = bisect_left(a, x, lo, hi)  # find insertion position
#     return (pos if pos != hi & a[pos] == x else -1)  # don't walk off the end
#

if __name__ == '__main__':
    if len(sys.argv) > 1:
        homeParam = sys.argv[1]
    else:
        homeParam = 'mzWork'

    homeFolders = dict(mzWork='C:/Users/mzhao/Documents',
                       afgWork='A:/gitrepo')
    home = homeFolders[homeParam]

    longform_df = pd.read_csv(op.join(home, 'metadataVis', 'data', 'e097lum_gt_resp_p.csv'))

    rx = pd.read_csv(op.join(home, 'metadataVis', 'data', 'rx_v2.csv'))

    wideform_df, ptid_md, measure_md = _generateWideform('ptid, visitno', 'isotype, antigen', 'delta', 'response', 'dilution, testdt', longform_df)
    print(longform_df['delta'].count())
    print(wideform_df.count().sum().sum())
    wideform_df.to_csv('data/wideforma.csv')
    ptid_md.to_csv('data/ptida.csv')
    measure_md.to_csv('data/measurea.csv')

# for i in wideform_df.index:
#     if i ==
#         ptid_indices

# print(wideform_df)
# print(ptid_md)
# print(measure_md)


