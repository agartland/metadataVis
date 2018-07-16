import pandas as pd
import sys
import os.path as op
from bisect import bisect_left
import numpy as np
import random
from bokeh.io import show, output_file
from bokeh.models import TableColumn, DataTable, ColumnDataSource, CustomJS
from bokeh.layouts import layout
from bokeh.models.widgets import MultiSelect, Dropdown


# DATAFRAME CONFIGURATION:

def _generateWideform(base_str, row_str, col_str, longform_df, rx=None):
    base_rows, base_columns, base_values = [x.strip() for x in base_str.split(',', 2)]

    # Row Metadata Table
    rowmeta_index = base_rows
    rowmeta_columns = [x.strip() for x in row_str.split(',')]
    ex_rowmeta_cols = list(rowmeta_columns)

    # Column Metadata Table
    colmeta_index = base_columns
    colmeta_columns = [x.strip() for x in col_str.split(',')]

    longform_df[base_rows] = longform_df[base_rows].astype(int).astype(str)

    longform_df[base_columns] = longform_df['tcellsub'] + '_' + longform_df['cytokine'] + '_' + longform_df['antigen']

    wideform_df = longform_df.pivot_table(index=base_rows, columns=base_columns, values=base_values)

    ids = list(range(1, wideform_df.shape[0] + 1))
    id_list = ['id-{0}'.format(i) for i in ids]

    rowmeta_dict = {rowmeta_index: longform_df[rowmeta_index]}
    lf_col_names = list(longform_df.columns.values)
    for entry in rowmeta_columns:
        if entry in lf_col_names:
            rowmeta_dict[entry] = longform_df[entry]
            ex_rowmeta_cols.remove(entry)
    ptid_md = pd.DataFrame(data=rowmeta_dict,
                           columns=rowmeta_dict.keys())
    ptid_md = ptid_md.drop_duplicates()

    if rx is not None:
        ptid_md = _handleRX(ex_rowmeta_cols, ptid_md, base_rows, rx)

    ptid_md['id'] = id_list
    ptid_md.set_index("id", inplace=True)

    colmeta_dict = {colmeta_index: longform_df[colmeta_index]}
    for entry in colmeta_columns:
        colmeta_dict[entry] = longform_df[entry]
    measure_md = pd.DataFrame(data=colmeta_dict,
                              columns=colmeta_dict.keys())
    measure_md = measure_md.drop_duplicates()
    measure_md.set_index("feature", inplace=True)
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

    homeFolders = dict(mzWork='C:/Users/mihuz/Documents',
                       afgWork='A:/gitrepo')
    home = homeFolders[homeParam]

    longform_df = pd.read_csv(op.join(home, 'metadataVis', 'data', 'e097fcm_fh_39_single_resp_p.csv'))

    rx = pd.read_csv(op.join(home, 'metadataVis', 'data', 'rx_v2.csv'))

# wideform_df, ptid_md, measure_md = _generateWideform('ptid, feature, pctpos_pos', 'labid, samp_ord, rx_code, rx', 'tcellsub, cytokine, antigen', longform_df, rx)
#
# wideform_df.to_csv('wideform123.csv')
# ptid_md.to_csv('ptid123.csv')
# measure_md.to_csv('measure123.csv')

# for i in wideform_df.index:
#     if i ==
#         ptid_indices

# print(wideform_df)
# print(ptid_md)
# print(measure_md)

