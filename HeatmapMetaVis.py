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

data = pd.read_csv(op.join(home, 'metadataVis', 'data', 'IR_levels097.csv'), index_col=0)
measures_md = pd.read_csv(op.join(home, 'metadataVis', 'data', 'metacols097.csv'), index_col=0)
ptid_md = pd.read_csv(op.join(home, 'metadataVis', 'data', 'metarows097.csv'), index_col=0)
# data = pd.read_csv(op.join(home, 'metadataVis', 'data', 'wideform_test.csv'), index_col=0)
# measures_md = pd.read_csv(op.join(home, 'metadataVis', 'data', 'wideform_measuremd_test.csv'), index_col=0)
# ptid_md = pd.read_csv(op.join(home, 'metadataVis', 'data', 'wideform_ptidmd_test.csv'), index_col=0)

# ERROR CHECKING
data_colnames = list(data.columns.values)
data_rownames = list(data.index)
ptid_names = list(ptid_md.index)
measures_names = list(measures_md.index)

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

layout = generateLayout(sources, cbDict, rowDend, colDend)

output_file('HeatmapMetaVis.html', title='HeatmapMetaVis')
show(layout)

