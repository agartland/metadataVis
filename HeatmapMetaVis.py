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
from bokeh.util.browser import view
from jinja2 import Environment, FileSystemLoader, select_autoescape
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
        error += str(list(data_colnames)) + "</p>"
        return error
    return None

# Generates the heatmap html at config.tmp_dir/config.output_file
def gen_heatmap_html(data=None, row_md=None, col_md=None, raw_data=None,
                     metric='euclidean', method='complete',
                     standardize=True, impute=True):
    # TODO - Metavis currently does not work without imputing

    # if (longform is not None and rx is not None):
    #     data, row_md, col_md = _generateWideform(longform, rx)
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
    sources = initSources(data, ptid_md, measures_md, raw_data)

    cbDict = initCallbacks(sources)

    html = generateLayout(sources, cbDict, rowDend, colDend)

    with io.open(op.join(config.tmp_dir, config.output_file), mode='w', encoding='utf-8') as f:
        f.write(html)
    with io.open("MetaVis.html", mode='w', encoding='utf-8') as f:
        f.write(html)
    return ret_val

def _errorDisplay(data, row_md, col_md):
    env = Environment(
        loader=FileSystemLoader('templates'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template("error.html")
    # html = template.render(tables=[data.to_html(), row_md.to_html(), col_md.to_html()], titles=['na', 'Base Data', 'Row Metadata', 'Column Metadata'])
    count_err, loc = _checkCounts(data, row_md, col_md)
    html = ""
    if count_err is True:
        print(count_err)
        if loc == 'col':
            data_colnames = pd.DataFrame({"Columns from data": list(data.columns.values)})
            colmd_names = pd.DataFrame({"Columns from Col Metadata": list(col_md.index)})
            html = template.render(tables=[data_colnames.to_html(), colmd_names.to_html()], titles=['na', "Columns from Data", "Columns from Column Metadata"])
    return True, html


def _checkCounts(data, row_md, col_md):
    row_count = data.shape[0]
    col_count = data.shape[1]
    rowmeta_count = row_md.shape[0]
    colmeta_count = col_md.shape[0]
    if (row_count != rowmeta_count):
        return True, "row"
    if (col_count != colmeta_count):
        return True, "col"
    return False, ""

def _checkNames(data, row_md, col_md):
    data_colnames = list(data.columns.values)
    data_rownames = list(data.index)
    rowmd_names = list(row_md.index)
    colmd_names = list(col_md.index)
    if (data_colnames != colmd_names):
        return True, "col"
    if (data_rownames != rowmd_names):
        return True, "row"
    return False, ""

def _checkNA(data, row_md, col_md):
    data.isnull().sum()


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
    data = pd.read_csv(op.join(home, 'metadataVis', 'data/test_data/mismatched_counts', 'MetaViz-responsesNA.csv'), index_col=0)
    measures_md = pd.read_csv(op.join(home, 'metadataVis', 'data/test_data/mismatched_counts', 'MetaViz-metacols-mis.csv'), index_col=0)
    ptid_md = pd.read_csv(op.join(home, 'metadataVis', 'data/test_data/mismatched_counts', 'MetaViz-metarows.csv'), index_col=0)
    # raw_data = pd.read_csv(op.join(home, 'metadataVis', 'data', 'MetaViz-responses_raw.csv'), index_col=0)
    raw_data = None

    #
    # data = pd.read_csv(op.join('tmpdata', 'data.csv'), index_col=0)
    # measures_md = pd.read_csv(op.join('tmpdata', 'col_md.csv'), index_col=0)
    # ptid_md = pd.read_csv(op.join('tmpdata', 'row_md.csv'), index_col=0)
    #
    # data = pd.read_csv(op.join(home, 'metadataVis', 'data', 'wideform_test.csv'), index_col=0)
    # measures_md = pd.read_csv(op.join(home, 'metadataVis', 'data', 'wideform_measuremd_test.csv'), index_col=0)
    # ptid_md = pd.read_csv(op.join(home, 'metadataVis', 'data', 'wideform_ptidmd_test.csv'), index_col=0)

    # ERROR CHECKING
    # data_colnames = list(data.columns.values)
    # data_rownames = list(data.index)
    # ptid_names = list(ptid_md.index)
    # measures_names = list(measures_md.index)
    # print(measures_names)
    # print(data_colnames)
    # if (data.shape[1] != measures_md.shape[0]):
    #     print("Error: Number of measurements in base dataset does not match the number of measurements in the measurement metadata.")
    #     print("       Base Data: ", data.shape[1])
    #     print("       Measures Metadata: ", measures_md.shape[0])
    #     sys.exit()
    # if (data.shape[0] != ptid_md.shape[0]):
    #     print("Error: Number of PtID's in base dataset does not match the number of PtID's in the PtID metadata.")
    #     print("       Base Data: ", data.shape[0])
    #     print("       PtID's Metadata: ", ptid_md.shape[0])
    #     sys.exit()
    #
    # if ptid_names != data_rownames:
    #     print("Error: PtID's in base dataset do not match PtID's in PtID metadata.")
    #     print(set(ptid_names).symmetric_difference(data_rownames))
    #     sys.exit()
    #
    # if measures_names != data_colnames:
    #     print("Error: Measures in base dataset do not match measures in measurement metadata.")
    #     print(set(measures_names).symmetric_difference(data_colnames))
    #     sys.exit()

    # data, measures_md = filterData(data, measures_md, method='mean', params={'thresh':0.0001})
    # data, measures_md = filterData(data, measures_md, method='meanTopN', params={'ncols':50})

    # data, ptid_md = filterData(data, ptid_md, method='pass')

    isError, err_html = _errorDisplay(data, ptid_md, measures_md)
    with io.open('MetaVisError.html', mode='w', encoding='utf-8') as g:
        g.write(err_html)

    view('MetaVisError.html')
    print(isError)
    if isError is False:
        data, ptid_md, measures_md, rowDend, colDend = clusterData(data, ptid_md, measures_md,
                                             metric='euclidean',
                                             method='ward',
                                             standardize=False,
                                             impute=False)

        # Creating overall data source
        sources = initSources(data, ptid_md, measures_md, raw_data)

        cbDict = initCallbacks(sources)
        p = generateLayout(sources, cbDict, rowDend, colDend)
