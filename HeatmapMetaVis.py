# https://github.com/bokeh/bokeh/issues/5701
# https://groups.google.com/a/continuum.io/forum/#!searchin/bokeh/selected/bokeh/ft2U4nX4fVo/srBMki9FAQAJ
import pandas as pd
import sys
import io
import os.path as op
import MetaVisLauncherConfig as config
from bokeh.io import show, output_file, save
from bokeh.embed import file_html
from bokeh.resources import CDN
from LongformReader import _generateWideform
from metaVis import *




def error_check(data, ptid_md, measures_md):
    data_colnames = list(data.columns.values)
    data_rownames = list(data.index)
    ptid_names = list(ptid_md.index)
    measures_names = list(measures_md.index)

    if (data.shape[1] != measures_md.shape[0]):
        error = "<p>Error: Number of measurements in base dataset does not match the number of measurements in the measurement metadata.</br>"
        error += "&emsp;Base Data: " + str(data.shape[1]) + "</br>"
        error += "&emsp;Measures Metadata: " + str(measures_md.shape[0])
        return error

    if (data.shape[0] != ptid_md.shape[0]):
        error = "<p>Error: Number of PtID's in base dataset does not match the number of PtID's in the PtID metadata. </br>"
        error += "&emsp;Base Data: " + str(data.shape[0]) + "</br>"
        error += "&emsp;PtID's Metadata: " + str(ptid_md.shape[0])
        error += "</p>"
        return error

    if (ptid_names != data_rownames):
        error = "<p>Error: PtID's in base dataset do not match PtID's in PtID metadata.</p>"
        print(ptid_names)
        print(data_rownames)
        return error

    if (measures_names != data_colnames):
        error = "<p>Error: Measures in base dataset do not match measures in measurement metadata. </br>"
        error += str(list(measures_names)) + "</br>"
        error += str(list(data_colnames)) + "</p"
        return error
    return None

# Generates the heatmap html at config.tmp_dir/config.output_file
def gen_heatmap_html(data=None, row_md=None, col_md=None,
                     longform=None, rx=None,
                     metric='euclidean', method='complete',
                     standardize=True, impute=True, static=False):
    # TODO - Metavis currently does not work without imputing
    impute=True

    if (longform is not None and rx is not None):
        data, row_md, col_md = _generateWideform(longform, rx)
    ret_val = {}
    ret_val['error'] = error_check(data, row_md, col_md)
    if ret_val['error'] is not None:
        return ret_val

    ptid_md = row_md
    measures_md = col_md
    # TODO - double check clusterData param handling
    data, ptid_md, measures_md, rowDend, colDend = clusterData(data, ptid_md, measures_md,
                                         metric=metric,
                                         method=method,
                                         standardize=standardize,
                                         impute=impute)
    sources = initSources(data, ptid_md, measures_md)

    cbDict = initCallbacks(sources)

    html = generateLayout(sources, cbDict, rowDend, colDend)

    with io.open(op.join(config.tmp_dir, config.output_file), mode='w', encoding='utf-8') as f:
        f.write(html)
    with io.open("MetaVis.html", mode='w', encoding='utf-8') as f:
        f.write(html)
    return ret_val


if __name__ == '__main__':
    if len(sys.argv) > 1:
        homeParam = sys.argv[1]
    else:
        homeParam = 'mzWork'

    homeFolders = dict(mzWork='C:/Users/mzhao/Documents',
                       afgWork='A:/gitrepo')
    home = homeFolders[homeParam]

    # Importing files as dataframes
    #
    data = pd.read_csv(op.join(home, 'metadataVis', 'data', 'IR_levels097.csv'), index_col=0)
    measures_md = pd.read_csv(op.join(home, 'metadataVis', 'data', 'metacols097.csv'), index_col=0)
    ptid_md = pd.read_csv(op.join(home, 'metadataVis', 'data', 'metarows097.csv'), index_col=0)

    #
    # data = pd.read_csv(op.join('tmpdata', 'data.csv'), index_col=0)
    # measures_md = pd.read_csv(op.join('tmpdata', 'col_md.csv'), index_col=0)
    # ptid_md = pd.read_csv(op.join('tmpdata', 'row_md.csv'), index_col=0)
    #
    # data = pd.read_csv(op.join(home, 'metadataVis', 'data', 'wideform_test.csv'), index_col=0)
    # measures_md = pd.read_csv(op.join(home, 'metadataVis', 'data', 'wideform_measuremd_test.csv'), index_col=0)
    # ptid_md = pd.read_csv(op.join(home, 'metadataVis', 'data', 'wideform_ptidmd_test.csv'), index_col=0)

    # ERROR CHECKING
    data_colnames = list(data.columns.values)
    data_rownames = list(data.index)
    ptid_names = list(ptid_md.index)
    measures_names = list(measures_md.index)
    print(measures_names)
    print(data_colnames)
    if (data.shape[1] != measures_md.shape[0]):
        print("Error: Number of measurements in base dataset does not match the number of measurements in the measurement metadata.")
        print("       Base Data: ", data.shape[1])
        print("       Measures Metadata: ", measures_md.shape[0])
        sys.exit()
    if (data.shape[0] != ptid_md.shape[0]):
        print("Error: Number of PtID's in base dataset does not match the number of PtID's in the PtID metadata.")
        print("       Base Data: ", data.shape[0])
        print("       PtID's Metadata: ", ptid_md.shape[0])
        sys.exit()

    if ptid_names != data_rownames:
        print("Error: PtID's in base dataset do not match PtID's in PtID metadata.")
        sys.exit()

    if measures_names != data_colnames:
        print("Error: Measures in base dataset do not match measures in measurement metadata.")
        sys.exit()

    # data, measures_md = filterData(data, measures_md, method='mean', params={'thresh':0.0001})
    # data, measures_md = filterData(data, measures_md, method='meanTopN', params={'ncols':50})

    # data, ptid_md = filterData(data, ptid_md, method='pass')


    data, ptid_md, measures_md, rowDend, colDend = clusterData(data, ptid_md, measures_md,
                                         metric='euclidean',
                                         method='ward',
                                         standardize=True,
                                         impute=True)

    # Creating overall data source
    sources = initSources(data, ptid_md, measures_md)

    cbDict = initCallbacks(sources)

    generateLayout(sources, cbDict, rowDend, colDend)
