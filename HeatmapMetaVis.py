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
import numpy as np
import logging

logger = logging.getLogger('spam_application')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('spam2.log')
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
    if metric[-1] == "'":
        metric = metric[2: -1]
        method = method[2: -1]

    logger.info(type(metric))
    logger.info(metric)
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
    data_colnames = list(data.columns.values)
    data_rownames = list(data.index)
    rowmd_names = list(row_md.index)
    colmd_names = list(col_md.index)
    env = Environment(
        loader=FileSystemLoader('templates'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template("error.html")
    # html = template.render(tables=[data.to_html(), row_md.to_html(), col_md.to_html()], titles=['na', 'Base Data', 'Row Metadata', 'Column Metadata'])
    count_err, count_loc, base_count, meta_count = _checkCounts(data, row_md, col_md)
    html = ""
    has_error = False
    if count_err is True:
        has_error = True
        print(count_err)
        message = "Error: There are mismatched counts between your metadata and your base data. "
        if count_loc == 'col':
            message += "Your base data has " + str(data.shape[1]) + " columns but your Column Metadata has " + str(col_md.shape[0]) + " entries."
            data_col_df = pd.DataFrame({"Columns from data": data_colnames})
            colmd_df = pd.DataFrame({"Columns from Col Metadata": colmd_names})
            html = template.render(title="Mismatched column counts", message=message, tables=[data_col_df.to_html(), colmd_df.to_html()],
                                   titles=['na', "Columns from Data", "Columns from Column Metadata"])
        if count_loc == 'row':
            message += "Your base data has " + str(data.shape[0]) + " rows but your Row Metadata has " + str(row_md.shape[0]) + " entries."
            data_row_df = pd.DataFrame({"Rows from data": data_rownames})
            rowmd_df = pd.DataFrame({"Columns from Row Metadata": rowmd_names})
            html = template.render(title="Mismatched row counts", message=message, tables=[data_row_df.to_html(), rowmd_df.to_html()],
                                   titles=['na', "Rows from Data", "Columns from Row Metadata"])
    na_err, data_na = _checkNA(data)
    if na_err is True:
        has_error = True
        message = "Error: Your Base Data table contains " + str(len(data_na[0])) + " NA values. "
        if (len(data_na[0]) > 20):
            print(data_na[0][:20])
            na_inds = ["({}, {})".format(b_, a_) for a_, b_ in zip(data_na[0][:20], data_na[1][:20])]
            print(na_inds)
            message += "The indices of the first 20 are shown below."
        else:
            na_inds = ["({}, {})".format(b_, a_) for a_, b_ in zip(data_na[0], data_na[1])]
        na_df = pd.DataFrame(na_inds)
        html = template.render(title="Data contains NA Values", message=message,
                               tables=[na_df.to_html()],
                               titles=['na', "Data Indices with NA Values"])
    name_err, name_loc = _checkNames(data_colnames, data_rownames, rowmd_names, colmd_names)
    if name_err is True:
        has_error = True
        if name_loc == 'col':
            diffs = (list(set(data_colnames) - set(colmd_names)))
            if len(diffs) == 0:
                message = "Error: The ordering of the column names in the base dataset do not match the ordering of the entries in the Column Metadata."
                html = template.render(title="Misnamed column names", message=message)
            else:
                basecol_comparison = []
                metacol_diffs = []
                for i in range(min(20, len(data_colnames))):
                    if data_colnames[i] != colmd_names[i]:
                        metacol_diffs.append(colmd_names[i])
                        basecol_comparison.append(data_colnames[i])
                data_col_df = pd.DataFrame({"Columns from data": basecol_comparison})
                colmd_df = pd.DataFrame({"Misnamed Entries from Column Metadata": metacol_diffs})
                message = "Error: The column names in the base dataset do not match the entries in the Column Metadata. (Showing a max of 20 entries)"
                html = template.render(title="Misnamed column names", message=message,
                                       tables=[data_col_df.to_html(), colmd_df.to_html()],
                                       titles=['na', "Columns from Data", "Misnamed Entries from Column Metadata"])
        if name_loc == 'row':
            diffs = (list(set(data_rownames) - set(rowmd_names)))
            print(diffs)
            if len(diffs) == 0:
                message = "Error: The ordering of the row names in the base dataset do not match the ordering of the entries in the Row Metadata."
                html = template.render(title="Misnamed column names", message=message)
            else:
                baserow_comparison = []
                metarow_diffs = []
                for i in range(min(20, len(data_rownames))):
                    if data_rownames[i] != rowmd_names[i]:
                        metarow_diffs.append(rowmd_names[i])
                        baserow_comparison.append(data_rownames[i])
                data_row_df = pd.DataFrame({"Rows from data": baserow_comparison})
                rowmd_df = pd.DataFrame({"Misnamed Entries from Row Metadata": metarow_diffs})
                message = "Error: The row names in the base dataset do not match the entries in the Row Metadata. (Showing a max of 20 entries)"
                html = template.render(title="Misnamed row names", message=message,
                                       tables=[data_row_df.to_html(), rowmd_df.to_html()],
                                       titles=['na', "Rows from Data", "Misnamed Entries from Row Metadata"])
    return has_error, html


def _checkCounts(data, row_md, col_md):
    row_count = data.shape[0]
    col_count = data.shape[1]
    rowmeta_count = row_md.shape[0]
    colmeta_count = col_md.shape[0]
    if (row_count != rowmeta_count):
        return True, "row", row_count, rowmeta_count
    if (col_count != colmeta_count):
        return True, "col", col_count, colmeta_count
    return False, "", 0, 0

def _checkNA(data):
    data_na_inds = np.where(np.asanyarray(np.isnan(data)))
    print(data_na_inds)
    if len(data_na_inds[0]) > 0:
        return True, data_na_inds
    return False, None

def _checkNames(data_colnames, data_rownames, rowmd_names, colmd_names):
    if data_colnames != colmd_names:
        return True, "col"
    elif data_rownames != rowmd_names:
        return True, "row"
    return False, ""

if __name__ == '__main__':
    if len(sys.argv) > 1:
        homeParam = sys.argv[1]
    else:
        homeParam = 'mzWork'

    homeFolders = dict(mzWork='C:/Users/mihuz/Documents',
                       afgWork='A:/gitrepo')
    home = homeFolders[homeParam]

    # Importing files as dataframes
    #
    data = pd.read_csv(op.join(home, 'metadataVis', 'data/test_data/misnamed_indices', 'MetaViz-responsesNA.csv'), index_col=0)
    measures_md = pd.read_csv(op.join(home, 'metadataVis', 'data/test_data/misnamed_indices', 'MetaViz-metacols.csv'), index_col=0)
    ptid_md = pd.read_csv(op.join(home, 'metadataVis', 'data/test_data/misnamed_indices', 'MetaViz-metarows-mis.csv'), index_col=0)
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
    else:
        with io.open('MetaVisError.html', mode='w', encoding='utf-8') as g:
            g.write(err_html)

        view('MetaVisError.html')
        print(isError)
