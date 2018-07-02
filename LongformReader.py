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

def _generateWideform(longform_df, rx=None):
    base_rows = 'ptid'
    base_columns = 'Feature'
    base_values = 'pctpos_pos'

    # Row Metadata Table
    rowmeta_index = base_rows
    rowmeta_columns = ['labid', 'samp_ord']

    # Column Metadata Table
    colmeta_index = base_columns
    colmeta_columns = ['tcellsub', 'cytokine', 'antigen']

    id = list(range(1, 76))
    id_list = ['id-{0}'.format(i) for i in id]

    longform_df['ptid'] = longform_df['ptid'].astype(str)
    longform_df['ptid'] = longform_df['ptid'].str[:-2]

    longform_df["Feature"] = longform_df['tcellsub'] + '_' + longform_df['cytokine'] + '_' + longform_df['antigen']

    wideform_df = longform_df.pivot_table(index=base_rows, columns=base_columns, values=base_values)

    rowmeta_dict = {rowmeta_index: longform_df[rowmeta_index]}
    for entry in rowmeta_columns:
        rowmeta_dict[entry] = longform_df[entry]

    if (rx is not None):
        ptid_md = pd.DataFrame(data=rowmeta_dict,
                           columns=rowmeta_dict.keys())
        ptid_md = ptid_md.drop_duplicates()
    else:
        ptid_md = _generatePtidMetadata(wideform_df, id_list, rx)

    colmeta_dict = {colmeta_index: longform_df[colmeta_index]}
    for entry in colmeta_columns:
        colmeta_dict[entry] = longform_df[entry]
    measure_md = pd.DataFrame(data=colmeta_dict,
                              columns=colmeta_dict.keys())
    measure_md = measure_md.drop_duplicates()
    measure_md.set_index("Feature", inplace=True)
    wideform_df['id'] = id_list
    wideform_df.set_index("id", inplace=True)

    return wideform_df, ptid_md, measure_md


def _generatePtidMetadata(wideform_df, id_list, rx=None):

    def binary_search(a, x, lo=0, hi=None):  # can't use a to specify default for hi
        hi = hi if hi is not None else len(a)  # hi defaults to len(a)
        pos = bisect_left(a, x, lo, hi)  # find insertion position
        return (pos if pos != hi and a[pos] == x else -1)  # don't walk off the end

    # if (rx):
    rx.rename(columns={'Ptid': 'TruePtID'}, inplace=True)
    rx['TruePtID'] = rx['TruePtID'].str.replace('-', '')

    ptid_indices = []

    for i in range(0, wideform_df.index.size):
        ind = binary_search(rx['TruePtID'].values, wideform_df.index.values[i])
        if ind != -1:
            ptid_indices.append(ind)

    rx_md = rx.iloc[ptid_indices]
    rx_md['PtID'] = id_list
    rx_md.set_index('PtID', inplace=True)
    return rx_md


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


# for i in wideform_df.index:
#     if i ==
#         ptid_indices

#print(wideform_df)
# print(ptid_md)
# print(measure_md)
#
