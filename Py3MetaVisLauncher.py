import sys
import pandas as pd
import os
import os.path as op
import shutil

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
    if len(sys.argv) < 7:
        error = "Error: Too few arguments"
    elif(sys.argv[5] != '-euclidean' and sys.argv[5] != '-correlation'):
        error = "Error: Unexpected 5th argument"
        error = "\n\tGiven: " + sys.argv[5]
        error += "\n\tExpected: [-euclidean | -correlation]"
    elif (sys.argv[6] != '-complete'
        and sys.argv[6] != '-single'
        and sys.argv[6] != '-ward'
        and sys.argv[6] != '-average'):
        error = "Error: Unexpected 6th argument"
        error += "\n\tGiven: " + sys.argv[6]
        error += "\n\tExpected: [-complete | -single | -ward | -average]"
    for i in range(7, len(sys.argv)):
        if sys.argv[i] not in ['-standardize', '-impute', '-static']:
            error = "Error: Unexpected flag"
            error += "\n\tGiven: " + sys.argv[i]
            error += "\n\tExpected: [-standardize -impute -static]"
    if (error):
        _handle_incorrect_input(error)

def _empty_prev_error():
    if op.exists(config.error_dir):
        shutil.rmtree(config.error_dir)

_empty_prev_error()
_parse_args()
kwargs = {}
dirname = sys.argv[1]
if sys.argv[2] == '-lf':
    #Longform
    kwargs['longform'] = pd.read_csv(op.join(dirname, sys.argv[3] + '.csv'))
    kwargs['rx'] =  pd.read_csv(op.join(dirame, sys.argv[4] + '.csv'))
else:
    kwargs['data'] =  pd.read_csv(op.join(dirname, sys.argv[2] + '.csv'), index_col=0)
    kwargs['row_md'] = pd.read_csv(op.join(dirname, sys.argv[3] + '.csv'), index_col=0)
    kwargs['col_md'] = pd.read_csv(op.join(dirname, sys.argv[4] + '.csv'), index_col=0)

kwargs['metric'] = str(sys.argv[5].replace('-',''))
kwargs['method'] = str(sys.argv[6].replace('-',''))
kwargs['standardize'] = '-standardize' in sys.argv
kwargs['impute'] = '-impute' in sys.argv
kwargs['static'] = '-static' in sys.argv

ret_map = gen_heatmap_html(**kwargs)
if(ret_map['error'] is not None):
    _write_to_error(ret_map['error'])
