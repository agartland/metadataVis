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
import numpy as np

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
        error += "\n\tGiven: " + sys.argv[5]
        error += "\n\tExpected: [-euclidean | -correlation]"
    elif (sys.argv[7] != '-complete'
        and sys.argv[7] != '-single'
        and sys.argv[7] != '-ward'
        and sys.argv[7] != '-average'):
        error = "Error: Unexpected 6th argument"
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
        na_df = pd.DataFrame(na_inds, columns="NA Value Indices")
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

kwargs['metric'] = str(sys.argv[6].replace('-', ''))
kwargs['method'] = str(sys.argv[7].replace('-', ''))
kwargs['standardize'] = '-standardize' in sys.argv
kwargs['impute'] = '-impute' in sys.argv

has_error, err_html = _errorDisplay(kwargs['data'], kwargs['row_md'], kwargs['col_md'])
if (has_error):
    ret_map = err_html
else:
    ret_map = gen_heatmap_html(**kwargs)
    if(ret_map['error'] is not None):
        _write_to_error(ret_map['error'])
