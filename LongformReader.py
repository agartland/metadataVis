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
import time
import logging

logger = logging.getLogger('spam_application')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('spam3.log')
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)


# DATAFRAME CONFIGURATION:
def _generateWideform(unique_rows_b, unique_cols_b, value_str_b, rowmeta_columns_b, colmeta_columns_b, longform_df):
    unique_rows = []
    unique_cols = []
    value_str = value_str_b.decode('utf-8')
    rowmeta_columns = []
    colmeta_columns = []
    for byte in unique_rows_b:
        unique_rows.append(byte.decode('utf-8'))
    for byte in unique_cols_b:
        unique_cols.append(byte.decode('utf-8'))
    for byte in rowmeta_columns_b:
        rowmeta_columns.append(byte.decode('utf-8'))
    for byte in colmeta_columns_b:
        colmeta_columns.append(byte.decode('utf-8'))
    logger.info(unique_rows)
    logger.info(unique_cols)
    logger.info(value_str)
    logger.info(rowmeta_columns)
    logger.info(colmeta_columns)
    logger.info(longform_df.shape)
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
    #unique_rows = [x.strip() for x in (uniquerow_str + ", " + row_str).split(',')]
    rowmeta_index = "RowIndex"

    # Column Metadata Table
    #unique_cols = [x.strip() for x in (uniquecol_str + ", " + col_str).split(',')]
    colmeta_index = 'Measure'
    st1 = time.time()
    longform_df[rowmeta_index] = longform_df.apply(lambda r: '|'.join(r[unique_rows].astype(str)), axis=1)
    longform_df[colmeta_index] = longform_df.apply(lambda r: '|'.join(r[unique_cols].astype(str)), axis=1)
    st2 = time.time()
    print("apply: " + str(st2 - st1))
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
    wideform_df.to_csv('data/wideformc.csv')
    end = time.time()
    # print(len(wideform_df.columns.values))
    # print(wideform_df.columns.values[:15])
    # print(longform_df[colmeta_index].head(15))
    ids = list(range(1, wideform_df.shape[0] + 1))
    id_list = ['id-{0}'.format(i) for i in ids]
    rowmeta_dict = {'index': longform_df[rowmeta_index]}
    lf_col_names = list(wideform_df.columns.values)
    print(lf_col_names)
    for entry in rowmeta_columns:
        rowmeta_dict[entry] = longform_df[entry]
    ptid_md = pd.DataFrame(data=rowmeta_dict,
                           columns=rowmeta_dict.keys())
    ptid_md = ptid_md.drop_duplicates()
    ptid_md.set_index('index', inplace=True)
    print(ptid_md.index)
    print(wideform_df.index)
    ptid_md = ptid_md.loc[list(wideform_df.index)]
    print(ptid_md.index)
    ptid_md.to_csv('data/ptidc.csv')
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
    measure_md = measure_md.reindex(wideform_df.columns.values)
    wideform_df['id'] = id_list
    wideform_df.set_index("id", inplace=True)
    logger.info(ptid_md.index)
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

    homeFolders = dict(mzWork='C:/Users/mihuz/Documents',
                       afgWork='A:/gitrepo')
    home = homeFolders[homeParam]

    s1 = time.time()

    longform_df = pd.read_csv(op.join(home, 'metadataVis', 'data', 'immune_response_data.csv'))

    s2 = time.time()

    print("upload: " + str(s1 - s1))
    wideform_df, ptid_md, measure_md = _generateWideform([b'ptid'], [b'tcellsub'], b'pctpos_adj', [b'samp_ord', b'visitno'], [b'tcellsub', b'antigen'], longform_df)
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


