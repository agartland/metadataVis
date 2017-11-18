# https://github.com/bokeh/bokeh/issues/5701
# https://groups.google.com/a/continuum.io/forum/#!searchin/bokeh/selected/bokeh/ft2U4nX4fVo/srBMki9FAQAJ
import pandas as pd
import sys
import os.path as op
from bokeh.io import show, output_file
from metaVis import *


if len(sys.argv) > 1:
    homeParam = sys.argv[1]
else:
    homeParam = 'mzWork'

homeFolders = dict(mzWork='C:/Users/mihuz/Documents',
                   afgWork='A:/gitrepo')
home = homeFolders[homeParam]

# Importing files as dataframes

data = pd.read_csv(op.join(home, 'metadataVis', 'data', 'IR_levels144.csv'), index_col=0)
measures_md = pd.read_csv(op.join(home, 'metadataVis', 'data', 'metacols144.csv'), index_col=0)
ptid_md = pd.read_csv(op.join(home, 'metadataVis', 'data', 'metarows144.csv'), index_col=0)


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

layout = generateLayout(sources, cbDict, rowDend, colDend)

output_file('HeatmapMetaVis.html', title='HeatmapMetaVis')
show(layout)

