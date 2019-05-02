from twisted.web import server, resource, static
from twisted.internet import reactor, endpoints, task, threads
from twisted.internet.defer import Deferred
from twisted.web.util import Redirect
from twisted.web.util import redirectTo
from twisted.python import log

from io import StringIO
import io
import os.path as op
import argparse
#import pandas as pd
import tempfile, os, sys
import subprocess
import shutil
import pandas as pd
from jinja2 import Environment, FileSystemLoader, select_autoescape
import numpy as np
import logging




import MetaVisLauncherConfig as config
from HeatmapMetaVis import gen_heatmap_html, error_check
import MetaVisLauncherConstants as constants
from LongformReader import _generateWideform


logger = logging.getLogger('spam_application')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('spam.log')
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


# TODO - Popup if file upload is empty; popup for errors
# Must call _cleanup_tmp before returning
def _handleMetaVis(request):
    tmpdirname = config.tmp_dir
    if not os.path.exists(tmpdirname):
        os.makedirs(tmpdirname)

    launcher_args = _prepArgs(request)
    args = [config.python3_path] + launcher_args
    _launchMetaVis(launcher_args)
    # Check for and handle errors
    if os.path.exists(os.path.join(config.error_dir, config.error_file)):
        error_file = open(os.path.join(config.error_dir, config.error_file), "r")
        error = error_file.read()
        error_file.close()
        request.write(error)
        return _clean_and_return(request)

    output_file = open(os.path.join(tmpdirname, config.output_file), "r")
    res_html = output_file.read()
    output_file.close()
    res_html = res_html.encode('utf-8')
    request.write(res_html)
    return _clean_and_return(request)

def _processLongform(request):

    sio_longform = StringIO(request.args[b'longformFile'][0].decode("UTF-8"))
    longform = pd.read_csv(sio_longform)
    rx = None
    unique_rows = request.args[b'rowIndex']
    unique_cols = request.args[b'colIndex']
    value_str = request.args[b'value'][0]
    rowmeta_columns = request.args[b'rowMeta']
    colmeta_columns = request.args[b'colMeta']
    data, row_md, col_md = _generateWideform(unique_rows_b=unique_rows, unique_cols_b=unique_cols,
                                             value_str_b=value_str, rowmeta_columns_b=rowmeta_columns, colmeta_columns_b=colmeta_columns,
                                             longform_df=longform)
    return data, row_md, col_md

def _prepArgs(request):
    # See Py3MetaVisLauncher.py for format
    tmpdirname = config.tmp_dir
    launcher_args = [''] * constants.REQ_ARG_NUM
    launcher_args[0] = config.launcher
    launcher_args[1] = tmpdirname
    for k, v in request.args.items():
        print(type(k))
        print(type(v))
        if (k.find(b'File') >= 0) & (request.args[k][0] != ''):
            if k == b'longformFile':
                logger.info("found longform")
                data, row_md, col_md = _processLongform(request)
                data.to_csv(os.path.join(tmpdirname, "data.csv"))
                row_md.to_csv(os.path.join(tmpdirname, "row_md.csv"))
                col_md.to_csv(os.path.join(tmpdirname, "col_md.csv"))
                launcher_args[2] = 'data'
                launcher_args[3] = 'row_md'
                launcher_args[4] = 'col_md'
                launcher_args[5] = None
                break
            else:
                filename = k.replace(b'File', b'').decode("UTF-8")
                logger.info("hello: " + filename)
                with open(os.path.join(tmpdirname, filename + '.csv'), 'wb') as tmpFile:
                    tmpFile.write(request.args[k][0])
                if k == b'dataFile':
                    launcher_args[2] = filename
                elif k == b'row_mdFile':
                    launcher_args[3] = filename
                elif k == b'col_mdFile':
                    launcher_args[4] = filename
                elif k == b'raw_dataFile':
                    if len(request.args[k][0]) > 0:
                        print(request.args[k][0])
                        launcher_args[5] = filename
    launcher_args[6] = '-' + str(request.args[b'metric'][0])
    launcher_args[7] = '-' + str(request.args[b'method'][0])
    if 'standardize' in request.args:
        launcher_args.append('-standardize')
    if 'impute' in request.args:
        launcher_args.append('-impute')
    if 'static' in request.args:
        launcher_args.append('-static')
    return launcher_args

def usage():
    return constants.USAGE

def _write_to_error(error):
    if not op.exists(config.error_dir):
        os.makedirs(config.error_dir)
    error_file = open(op.join(config.error_dir, config.error_file), 'w')
    error_file.write(error)
    error_file.close()

def _parse_args_err(launcher_args):
    error = None
    print(launcher_args)
    if len(launcher_args) < 8:
        error = "Error: Too few arguments"
    elif(launcher_args[6] != '-euclidean' and launcher_args[6] != '-correlation'):
        error = "Error: Unexpected 6th argument"
        error += "\n\tGiven: " + launcher_args[6]
        error += "\n\tExpected: [-euclidean | -correlation]"
    elif (launcher_args[7] != '-complete'
        and launcher_args[7] != '-single'
        and launcher_args[7] != '-ward'
        and launcher_args[7] != '-average'):
        error = "Error: Unexpected 6th argument"
        error += "\n\tGiven: " + launcher_args[7]
        error += "\n\tExpected: [-complete | -single | -ward | -average]"
    for i in range(8, len(launcher_args)):
        if launcher_args[i] not in ['-standardize', '-impute', '-static']:
            error = "Error: Unexpected flag"
            error += "\n\tGiven: " + launcher_args[i]
            error += "\n\tExpected: [-standardize -impute -static]"

def _empty_prev_error():
    if op.exists(config.error_dir):
        shutil.rmtree(config.error_dir)

def _launchMetaVis(launcher_args):
    _empty_prev_error()
    _parse_args_err(launcher_args)
    kwargs = {}
    dirname = launcher_args[1]
    logger.info("launching")
    logger.info(launcher_args)
    kwargs['data'] = pd.read_csv(op.join(dirname, launcher_args[2] + '.csv'), index_col=0)
    kwargs['row_md'] = pd.read_csv(op.join(dirname, launcher_args[3] + '.csv'), index_col=0)
    kwargs['col_md'] = pd.read_csv(op.join(dirname, launcher_args[4] + '.csv'), index_col=0)
    if launcher_args[5] is not None and launcher_args[5] != "":
        kwargs['raw_data'] = pd.read_csv(op.join(dirname, launcher_args[5] + '.csv'), index_col=0)
    else:
        kwargs['raw_data'] = None

    kwargs['metric'] = str(launcher_args[6].replace('-', ''))
    kwargs['method'] = str(launcher_args[7].replace('-', ''))
    kwargs['standardize'] = '-standardize' in launcher_args
    kwargs['impute'] = '-impute' in launcher_args

    # If you want to fillNA values
    kwargs['data'].fillna(0, inplace=True)
    has_error, err_html = _errorDisplay(kwargs['data'], kwargs['row_md'], kwargs['col_md'])
    if has_error:
        logger.info("not generating html")
        with io.open(op.join(config.tmp_dir, config.output_file), mode='w', encoding='utf-8') as f:
            f.write(err_html)
    else:
        logger.info("generating html")
        ret_map = gen_heatmap_html(**kwargs)
        if (ret_map['error'] is not None):
            _write_to_error(ret_map['error'])


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
    logger.info("check counts: " + str(count_err))
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
    logger.info("check na values: " + str(na_err))
    if na_err is True:
        data.fillna(-1)
    # If we want to throw errors if they have an NA value.
    #     has_error = True
    #     message = "Error: Your Base Data table contains " + str(len(data_na[0])) + " NA values. "
    #     if (len(data_na[0]) > 20):
    #         print(data_na[0][:20])
    #         na_inds = ["({}, {})".format(b_, a_) for a_, b_ in zip(data_na[0][:20], data_na[1][:20])]
    #         print(na_inds)
    #         message += "The indices of the first 20 are shown below."
    #     else:
    #         na_inds = ["({}, {})".format(b_, a_) for a_, b_ in zip(data_na[0], data_na[1])]
    #     na_df = pd.DataFrame(na_inds)
    #     html = template.render(title="Data contains NA Values", message=message,
    #                            tables=[na_df.to_html()],
    #                            titles=['na', "Data Indices with NA Values"])
    name_err, name_loc = _checkNames(data_colnames, data_rownames, rowmd_names, colmd_names)
    logger.info("check names: " + str(name_err))
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
    logger.info("check any errors: " + str(has_error))
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

class FileUpload(resource.Resource):
    isLeaf = True
    def render_GET(self, request):
        return redirectHome.render(request)

    def _delayedPOSTRender(self, request):
        request.finish()

    def render_POST(self, request):
        d = threads.deferToThread(_handleMetaVis, request)
        d.addCallback(self._delayedPOSTRender)
        d.addErrback(log.err)
        return server.NOT_DONE_YET

class RootResource(resource.Resource):
    isLeaf = False
    def getChild(self, name, request):
        if name == '':
            return self
        return resource.Resource.getChild(self, name, request)
    def render_GET(self, request):
        return redirectHome.render(request)

def _clean_and_return(request):
    _cleanup_tmp()
    return request

def _cleanup_tmp():
    if os.path.exists(config.tmp_dir):
        shutil.rmtree(config.tmp_dir)

# def _check_ver():
    # if sys.version_info[0] != 2:
        # raise Exception("MetaVisServer must be launched with python 2")

redirectHome = Redirect(b'home')

if __name__ == '__main__':
    # _check_ver()
    parser = argparse.ArgumentParser(description='Start metadataVis web server.')
    parser.add_argument('--port', metavar='PORT', type=int, default=5097)
    args = parser.parse_args()

    root = RootResource()
    root.putChild(b'home', static.File('./homepage'))
    root.putChild(b'', Redirect(b'home'))
    root.putChild(b'viz', FileUpload())

    site = server.Site(root)
    reactor.listenTCP(args.port, site)
    reactor.run()
