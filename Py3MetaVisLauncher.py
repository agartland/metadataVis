import sys
import pandas as pd
import os
import io
import os.path as op
import shutil
from jinja2 import Environment, FileSystemLoader, select_autoescape
import MetaVisLauncherConfig as config
import MetaVisLauncherConstants as constants
from HeatmapMetaVis import gen_heatmap_html, error_check

def usage():
    return constants.USAGE

def _write_to_error(error):
    if not op.exists(config.error_dir):
        os.makedirs(config.error_dir)
    error_file = open(op.join(config.error_dir, config.error_file), 'w')
    error_file.write(error)
    error_file.close()

def _handle_incorrect_input(error):
    error += "\n" + usage()
    print(error)
    _write_to_error(error)
    sys.exit()

def _parse_args():
    error = None
    print(sys.argv)
    if len(sys.argv) < 8:
        error = "Error: Too few arguments"
    elif(sys.argv[6] != '-euclidean' and sys.argv[6] != '-correlation'):
        error = "Error: Unexpected 6th argument"
        error = "\n\tGiven: " + sys.argv[5]
        error += "\n\tExpected: [-euclidean | -correlation]"
    elif (sys.argv[7] != '-complete'
        and sys.argv[7] != '-single'
        and sys.argv[7] != '-ward'
        and sys.argv[7] != '-average'):
        error =  "Error: Unexpected 6th argument"
        error += "\n\tGiven: " + sys.argv[7]
        error += "\n\tExpected: [-complete | -single | -ward | -average]"
    for i in range(8, len(sys.argv)):
        if sys.argv[i] not in ['-standardize', '-impute', '-static']:
            error = "Error: Unexpected flag"
            error += "\n\tGiven: " + sys.argv[i]
            error += "\n\tExpected: [-standardize -impute -static]"
    if (error):
        _handle_incorrect_input(error)

def _empty_prev_error():
    if op.exists(config.error_dir):
        shutil.rmtree(config.error_dir)

def _errorCheck():
    return True

def _errorDisplay(data, row_md, col_md):
    env = Environment(
        loader=FileSystemLoader('templates'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template("error.html")
    html = template.render(tables=[data.to_html(), row_md.to_html(), col_md.to_html()], titles=['na', 'Base Data', 'Row Metadata', 'Column Metadata'])
    with io.open(op.join(config.tmp_dir, config.output_file), mode='w', encoding='utf-8') as f:
        f.write(html)
    with io.open("MetaVis.html", mode='w', encoding='utf-8') as f:
        f.write(html)
    return html

def _checkCounts(data, row_md, col_md):
    row_count = data.shape[0]
    col_count = data.shape[1]
    rowmeta_count = row_md.shape[0]
    colmeta_count = col_md.shape[0]
    if (row_count != rowmeta_count):
        return false, "row"
    if (col_count != colmeta_count):
        return false, "col"
    return true, ""

def _checkNames(data, row_md, col_md):
    data_colnames = list(data.columns.values)
    data_rownames = list(data.index)
    rowmd_names = list(row_md.index)
    colmd_names = list(col_md.index)
    if (data_colnames != colmd_names):
        return false, "col"
    if (data_rownames != rowmd_names):
        return false, "row"
    return true, ""

def _checkNA(data, row_md, col_md):
    df.isnull().sum()

_empty_prev_error()
_parse_args()
kwargs = {}
dirname = sys.argv[1]
# if sys.argv[2] == '-lf':
#     #Longform
#     kwargs['longform'] = pd.read_csv(op.join(dirname, sys.argv[3] + '.csv'))
#     kwargs['rx'] =  pd.read_csv(op.join(dirname, sys.argv[4] + '.csv'))
# else:
kwargs['data'] = pd.read_csv(op.join(dirname, sys.argv[2] + '.csv'), index_col=0)
kwargs['row_md'] = pd.read_csv(op.join(dirname, sys.argv[3] + '.csv'), index_col=0)
kwargs['col_md'] = pd.read_csv(op.join(dirname, sys.argv[4] + '.csv'), index_col=0)
if sys.argv[5] != "":
    kwargs['raw_data'] = pd.read_csv(op.join(dirname, sys.argv[5] + '.csv'), index_col=0)
else:
    kwargs['raw_data'] = None

kwargs['metric'] = str(sys.argv[6].replace('-',''))
kwargs['method'] = str(sys.argv[7].replace('-',''))
kwargs['standardize'] = '-standardize' in sys.argv
kwargs['impute'] = '-impute' in sys.argv

if (_errorCheck()):
    ret_map = _errorDisplay(kwargs['data'], kwargs['row_md'], kwargs['col_md'])
else:
    ret_map = gen_heatmap_html(**kwargs)
    if(ret_map['error'] is not None):
        _write_to_error(ret_map['error'])
