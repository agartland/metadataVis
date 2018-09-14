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
def _generateWideform(unique_rows, unique_cols, value_str, rowmeta_columns, colmeta_columns, longform_df):
    '''
    cd A:/gitrepo/metadataVisData/data
    fn = 'e097lum_gt_resp_p.csv'
    uniquerow_str = 'ptid,visitno'
    uniquecol_str = 'isotype,antigen'
    value_str = 'delta'
    row_str, col_str = 'response','dilution,testdt'
    longform_df = pd.read_csv(fn)
    wideform_df, ptid_md, measure_md = _generateWideform(uniquerow_str, uniquecol_str, value_str, row_str, col_str, longform_df)'''

    # Row Metadata Table
    print(unique_rows)
    print(unique_cols)
    print(value_str)
    print(rowmeta_columns)
    print(colmeta_columns)
    #unique_rows = [x.strip() for x in (uniquerow_str + ", " + row_str).split(',')]
    rowmeta_index = '|'.join(unique_rows)

    # Column Metadata Table
    #unique_cols = [x.strip() for x in (uniquecol_str + ", " + col_str).split(',')]
    colmeta_index = '|'.join(unique_cols)

    longform_df[rowmeta_index] = longform_df.apply(lambda r: '|'.join(r[unique_rows].astype(str)), axis=1)
    longform_df[colmeta_index] = longform_df.apply(lambda r: '|'.join(r[unique_cols].astype(str)), axis=1)
    # print(len(longform_df[colmeta_index]))

    '''unique_rows = [x.strip() for x in (uniquerow_str).split(',')]
    unique_cols = [x.strip() for x in (uniquecol_str).split(',')]
    hDf = longform_df.set_index(unique_cols + unique_rows)[value_str].unstack(unique_cols)

    unique_rows = [x.strip() for x in (uniquerow_str + ", " + row_str).split(',')]
    unique_cols = [x.strip() for x in (uniquecol_str + ", " + col_str).split(',')]
    wdf = longform_df.set_index(unique_cols + unique_rows)[value_str].unstack(unique_cols)  
    row_metadata = wdf.index.to_frame()
    col_metadata = wdf.columns.to_frame()

    row_metadata.index = np.arange(row_metadata.shape[0])
    row_metadata = row_metadata.reset_index()'''

    wideform_df = longform_df.pivot(index=rowmeta_index, columns=colmeta_index, values=value_str)
    # print(len(wideform_df.columns.values))
    # print(wideform_df.columns.values[:15])
    # print(longform_df[colmeta_index].head(15))
    ids = list(range(1, wideform_df.shape[0] + 1))
    id_list = ['id-{0}'.format(i) for i in ids]
    rowmeta_dict = {'index': longform_df[rowmeta_index]}
    lf_col_names = list(longform_df.columns.values)
    for entry in rowmeta_columns:
        rowmeta_dict[entry] = longform_df[entry]
    ptid_md = pd.DataFrame(data=rowmeta_dict,
                           columns=rowmeta_dict.keys())
    ptid_md = ptid_md.drop_duplicates()
    colmeta_dict = {colmeta_index: longform_df[colmeta_index]}
    for entry in colmeta_columns:
        colmeta_dict[entry] = longform_df[entry]
    measure_md = pd.DataFrame(data=colmeta_dict,
                              columns=colmeta_dict.keys())
    measure_md = measure_md.drop_duplicates()

    # validity_arr1 = _validMetadata(wideform_df.shape[1], colmeta_index, longform_df)
    # err_str1 = _validityMessages(wideform_df.shape[1], validity_arr1, colmeta_index, 'column')
    # print(err_str1)

    # validity_arr2 = _validMetadata(wideform_df.shape[0], rowmeta_index, longform_df)
    # err_str2 = _validityMessages(wideform_df.shape[0], validity_arr2, rowmeta_index, 'row')
    # print(err_str2)
    try:
        ptid_md['id'] = id_list
        ptid_md.set_index("id", inplace=True)
    except ValueError:
        validity_arr = _validMetadata(wideform_df.shape[0], rowmeta_index, longform_df)
        err_str = _validityMessages(wideform_df.shape[0], validity_arr, rowmeta_index, 'row')
        print(err_str)
        return err_str, None, None
    # if measure_md.shape[0] != wideform_df.shape[1]:
    #     validity_arr = _validMetadata(wideform_df.shape[1], colmeta_index, longform_df)
    #     err_str = _validityMessages(wideform_df.shape[1], validity_arr, colmeta_index, 'column')
    #     print(err_str)
    #     return err_str, None, None

    measure_md.set_index(colmeta_index, inplace=True)
    wideform_df['id'] = id_list
    wideform_df.set_index("id", inplace=True)

    return wideform_df, ptid_md, measure_md

def _validMetadata(num, index, longform_df):
    columns = longform_df.columns.values
    candidates = []
    noncandidates = []
    for col in columns:
        d = {'index': longform_df[index]}
        d[col] = longform_df[col]
        df = pd.DataFrame(data=d, columns=d.keys())
        df = df.drop_duplicates()
        if df.shape[0] == num:
            unique = longform_df[col].unique().size
            if unique > 1:
                candidates.append("* " + col + ", " + str(unique))
            else:
                candidates.append(col + ", " + str(unique))
        else:
            noncandidates.append(col + ", " + str(df.shape[0]))
    return candidates, noncandidates

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

def _validityMessages(count, validity_arr, index, direc):
    valid_str = "Possible valid " + direc + " metadata variables for given " + direc + " index of '" + index + "' (count: " + str(count) + ") are: \n" + '\n'.join(validity_arr[0])
    invalid_str = "Invalid " + direc +" metadata variables for given " + direc + " index of '" + index + "' (count: " + str(count) + ") are: \n" + '\n'.join(validity_arr[1])
    err_str = "Index " + direc + " not unique. \n" + valid_str + "\n\n" + invalid_str
    return err_str

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

    wideform_df, ptid_md, measure_md = _generateWideform(['ptid', 'visitno'], ['isotype', 'antigen'], 'delta', ['ptid', 'visitno'], ['isotype', 'antigen', 'filedate'], longform_df)
    # print(longform_df['delta'].count())
    # print(wideform_df.count().sum().sum())
    wideform_df.to_csv('data/wideforma.csv')
    ptid_md.to_csv('data/ptida.csv')
    measure_md.to_csv('data/measurea.csv')

# for i in wideform_df.index:
#     if i ==
#         ptid_indices

# print(wideform_df)
# print(ptid_md)
# print(measure_md)


