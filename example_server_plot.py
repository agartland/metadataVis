import numpy as np
import pandas as pd
from bokeh.plotting import figure
from bokeh.resources import CDN
import pandas as pd
import sys
import os.path as op
from bokeh.io import show
from metaVis import *
from bokeh.embed import file_html


def exampleVis(data, row_md, col_md, static=False, standardize=False, method='complete', metric='euclidean', impute=True):
    """Example entry point for a function called by the mdvServer.
    Function should take HTML form arguments as parameters and
    return the HTML.

    Parameters
    ----------
    data
    row_md
    col_md
    
    """
    # print(data.shape)
    # print(col_md.shape)
    # print(row_md.shape)
    
    # data, col_md = filterData(data, col_md, method='mean', params={'thresh': 0.0001})
    # data, measures_md = filterData(data, measures_md, method='meanTopN', params={'ncols':500})

    #data, row_md = filterData(data, row_md, method='pass')
    data, row_md, col_md, rowDend, colDend = clusterData(data,
                                                                 row_md,
                                                                 col_md,
                                                                 metric=metric,
                                                                 method=method,
                                                                 standardize=standardize,
                                                                 impute=impute)
    # Creating overall data source

    sources = initSources(data, row_md, col_md)

    cbD = initCallbacks(sources)

    layout = generateLayout(sources, cbD, rowDend, colDend)

    html = file_html(layout, resources=CDN)
    return html


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate metadataVis html.')
    parser.add_argument('--static', type=int, default=8080)
    args = parser.parse_args()

    if len(sys.argv) > 1:
        homeParam = sys.argv[1]
    else:
        homeParam = 'mzWork'

    homeFolders = dict(mzWork='C:/Users/mzhao/PycharmProjects',
                       afgWork='A:/gitrepo')
    home = homeFolders[homeParam]

    # Importing files as dataframes
    data = pd.read_csv(op.join(home, 'metadataVis', 'data', 'hvtn505_ics_24Jul2017.csv'), index_col=0)
    measures_md = pd.read_csv(op.join(home, 'metadataVis', 'data', 'hvtn505_ics_colmeta_24Jul2017.csv'))
    ptid_md = pd.read_csv(op.join(home, 'metadataVis', 'data', 'hvtn505_ics_rowmeta_24Jul2017.csv'))


    html = exampleVis(data=data, ptid_md=ptid_md, measures_md=measures_md, static=args.static)
    with open('HeatmapMetaVis.html', 'wa') as fh:
        fh.write(html)

