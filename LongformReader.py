import pandas as pd
import sys
import os.path as op
import random
from bokeh.io import show, output_file
from bokeh.models import TableColumn, DataTable, ColumnDataSource, CustomJS
from bokeh.layouts import layout
from bokeh.models.widgets import MultiSelect, Dropdown


'''// helper function
function addIfMissing(array, value) {
    var found = false;
    for(var i = 0; i < array.length; i++)
        if(array[i] === value)
            return array;
    array.push(value);
    return array;
}

function restructure(input) {
    var output = [], headerX = [], headerY = [], xCoor, yCoor;

    // first create non-repeating headers
    headerX.push(input[0][0]);
    headerY.push(input[0][0]);
    for(var i = 1; i < input.length; i++)
        headerX = addIfMissing(headerX, input[i][0]), headerY = addIfMissing(headerY, input[i][1]);

    // put headers into output array
    for(var i = 0; i < headerX.length; i++)
        output.push([headerX[i]]);
    output[0] = headerY;

    // find correct headers on both axes and input data
    for(var i = 1; i < input.length; i++) {
        for(var k = 1; k < headerX.length; k++)
            if(output[k][0] == input[i][0])
                xCoor = k;
        for(var j = 1; j < headerY.length; j++)
            if(output[0][j] == input[i][1])
                yCoor = j;
        output[xCoor][yCoor] = input[i][2];
    }

    return output;
}

'''


# Test DataSet
# ptid = [1, 1, 2, 2, 3, 3, 4, 4, 5, 5]
# measure = ["Blue", "Red", "Blue", "Red", "Blue", "Red", "Blue", "Red", "Blue", "Red"]
# measuremeta = ["A", "B", "A", "B", "A", "B", "A", "B", "A", "B"]
# ptidmeta = ["Male", "Male", "Female", "Female", "Female", "Female", "Male", "Male", "Male", "Male"]
# value = random.sample(range(100), 10)
# d = {'PtID': ptid, 'PatientMD': ptidmeta, 'Measure': measure, 'MeasureMD': measuremeta, 'Value': value}
#
# test_longform_df = pd.DataFrame(data=d, columns=['PtID', 'PatientMD', 'Measure', 'MeasureMD', 'Value'])
#
#
# print(test_longform_df)
#
# test_wideform_df = test_longform_df.pivot_table(index='PtID', columns='Measure', values='Value')
#
# test_ptid_md = pd.DataFrame(data={'PtID': test_longform_df['PtID'], 'Metadata': test_longform_df['PatientMD']}, columns=['PtID', 'Metadata'])
# test_ptid_md = test_ptid_md.drop_duplicates()
#
# test_measure_md = pd.DataFrame(data={'Measure': test_longform_df['Measure'], 'Metadata': test_longform_df['MeasureMD']}, columns=['Measure', 'Metadata'])
# test_measure_md = test_measure_md.drop_duplicates()
#
# print(test_wideform_df)
# print(test_measure_md)
# print(test_ptid_md)

if len(sys.argv) > 1:
    homeParam = sys.argv[1]
else:
    homeParam = 'mzWork'

homeFolders = dict(mzWork='C:/Users/mihuz/Documents',
                   afgWork='A:/gitrepo')
home = homeFolders[homeParam]

longform_df = pd.read_csv(op.join(home, 'metadataVis', 'data', 'e097fcm_fh_39_single_resp_p.csv'))

# DATAFRAME CONFIGURATION:

# Base Data
base_rows = 'ptid'
base_columns = 'Measure'
base_values = "pctpos_pos"

# Row Metadata Table
rowmeta_index = base_rows
rowmeta_columns = ['labid', 'samp_ord']

# Column Metadata Table
colmeta_index = base_columns
colmeta_columns = ['tcellsub', 'cytokine', 'antigen']

def _generateWideform(longform_df):

    longform_df["Measure"] = longform_df['tcellsub'] + '_' + longform_df['cytokine'] + '_' + longform_df['antigen']

    wideform_df = longform_df.pivot_table(index=base_rows, columns=base_columns, values=base_values)

    rowmeta_dict = {rowmeta_index: longform_df[rowmeta_index]}
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

    return wideform_df, ptid_md, measure_md

# print(wideform_df)
# print(ptid_md)
# print(measure_md)

# wideform_df.to_csv(op.join(home, 'metadataVis', 'data', 'wideform_test.csv'))
# ptid_md.to_csv(op.join(home, 'metadataVis', 'data', 'wideform_ptidmd_test.csv'))
# measure_md.to_csv(op.join(home, 'metadataVis', 'data', 'wideform_measuremd_test.csv'))






