import sklearn
import numpy as np
from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.spatial.distance import squareform, pdist
import pandas as pd
from bokeh.models import TableColumn, DataTable, ColumnDataSource
from bokeh.plotting import Figure
from metaVis import *

__all__ = ['imputeNA',
           'clusterData',
           'filterData',
           'standardizeData',
           'initSources']

def initSources(data, ptid_md, measures_md):
    df = pd.DataFrame(data.stack(), columns=['rate']).reset_index()
    df.columns = ['PtID', 'Feature', 'rate']
    feature_list = list(data.columns)
    feature_df = pd.DataFrame(feature_list)
    feature_df.columns = ["feature"]
    p_default = list(ptid_md)[1]
    m_default = list(measures_md)[1]

    likely_continuous = []
    for var in [c for c in ptid_md.columns if not c in ['PtID']]:
        print(var)
        if type(ptid_md[var][0]) != str and 1. * ptid_md[var].nunique() / ptid_md[var].count() > 0.1:
            likely_continuous.append(var)

    for var in likely_continuous:
        print(likely_continuous)
        print(var)
        ptid_md[var] = pd.qcut(ptid_md[var], 3, labels=["Low", 'Medium', 'High']).astype(str)

    likely_continuous = []
    for var in [c for c in measures_md.columns if not c in ['Feature']]:
        if type(measures_md[var][0]) != str and 1. * measures_md[var].nunique() / measures_md[var].count() > 0.4:
            likely_continuous.append(var)

    for var in likely_continuous:
        measures_md[var] = pd.qcut(measures_md[var], 3, labels=["Low", 'Medium', 'High']).astype(str)

    sources = {}
    sources['source'] = ColumnDataSource(df)
    sources['ptid'] = ColumnDataSource(ptid_md)
    sources['ptid'].data['inspect'] = sources['ptid'].data[p_default]
    sources['measure'] = ColumnDataSource(measures_md)
    sources['measure'].data['inspect'] = sources['measure'].data[m_default]

    """Move to storage source?"""
    sources['col'] = ColumnDataSource(feature_df)
    sources['p_table'] = ColumnDataSource(data={feat: [] for feat in list(ptid_md)})
    sources['m_table'] = ColumnDataSource(data={feat: [] for feat in list(measures_md)})
    sources['storage'] = ColumnDataSource(data=dict(PtID=sources['ptid'].data['PtID'], Feature=sources['measure'].data['Feature'],
                                                mode=['Cross'], indices=[], multiselect=['False'],
                                                s_rowbar=[], s_colbar=[], total_rowbar=[], total_colbar=[],
                                                p_colname=[p_default], m_colname=[m_default],
                                                p_legend_index=[], m_legend_index=[]))
    sources['p_legend'] = ColumnDataSource(data=dict(factors=[], names=[]))
    sources['m_legend'] = ColumnDataSource(data=dict(factors=[], names=[]))

    sources['ptid'], sources['p_legend'], sources['storage'].data['total_rowbar'] = initSupplementSources(sources['ptid'], sources['p_legend'])
    sources['measure'], sources['m_legend'], sources['storage'].data['total_colbar'] = initSupplementSources(sources['measure'], sources['m_legend'])

    sources['select_rowbar'] = ColumnDataSource(data=dict(x=[], y=[]))
    sources['nonselect_rowbar'] = ColumnDataSource(data=dict(x=sources['p_legend'].data['names'],
                                                             y=sources['storage'].data['total_rowbar']))
    sources['select_colbar'] = ColumnDataSource(data=dict(x=[], y=[]))
    sources['nonselect_colbar'] = ColumnDataSource(data=dict(x=sources['m_legend'].data['names'],
                                                             y=sources['storage'].data['total_colbar']))

    sources['p_data_table'] = _createTable(md=ptid_md, md_source=sources['p_table'])
    sources['m_data_table'] = _createTable(md=measures_md, md_source=sources['m_table'])
    sources['nonselect_rowbarchart'] = _createBarChart(source=sources['nonselect_rowbar'],
                                                       xrange=sources['p_legend'].data['names'],
                                                       title='Unselected Row Metadata')
    sources['row_xrange'] = sources['nonselect_rowbarchart'].x_range
    sources['select_rowbarchart'] = _createBarChart(source=sources['select_rowbar'],
                                                    xrange=sources['nonselect_rowbarchart'].x_range,
                                                    title='Selected Row Metadata')

    sources['nonselect_colbarchart'] = _createBarChart(source=sources['nonselect_colbar'],
                                                       xrange=sources['m_legend'].data['names'],
                                                       title='Unselected Column Metadata')
    sources['col_xrange'] = sources['nonselect_colbarchart'].x_range
    sources['select_colbarchart'] = _createBarChart(source=sources['select_colbar'],
                                                    xrange=sources['nonselect_colbarchart'].x_range,
                                                    title='Selected Column Metadata')
    sources['data'] = data
    sources['ptid_md'] = ptid_md
    sources['measures_md'] = measures_md
    sources['df'] = df
    return sources

def standardizeData(data, allSame=True):
    if allSame:
        mu = np.mean(data.values.ravel())
        sigma2 = np.std(data.values.ravel())
        out = (data - mu) / sigma2
    else:
        sFunc = lambda v: (v - np.mean(v)) / np.std(v)
        out = data.apply(sFunc, axis=0)

    return out

def filterData(data, md, method='mean', params={'thresh':0.0001}):
    maxCols = 1000

    if method == 'mean':
        keepInd = data.mean(axis=0) > params['thresh']
        data = data.loc[:, keepInd]
        md = md.loc[keepInd]
    elif method == 'CV':
        pass
    elif method == 'SparsePCA':
        pass
    elif method == 'meanTopN':
        sorti = np.argsort(data.mean(axis=0).values)[:params['ncols']]
        data = data.iloc[:, sorti]
        md = md.iloc[sorti]
    elif method == 'pass':
        pass

    if data.shape[1] > maxCols:
        print('Data has more than %d dimensions (%d): performance may be poor.' % (maxCols, data.shape[1]))

    return data, md


def clusterData(data, ptid_md, measures_md, metric='euclidean', method='complete', standardize=True, impute=True):
    """
    """
    if impute:
        data = imputeNA(data)
    if standardize:
        data = standardizeData(data)

    # data.rename(columns=data.iloc[0])
    # print(metric,method)

    Z = linkage(data, metric=metric, method=method)
    rowDend = dendrogram(Z, no_plot=True)
    reorderedDf = data.iloc[rowDend['leaves']]
    data = reorderedDf

    Z2 = linkage(data.T, metric=metric, method=method)
    colDend = dendrogram(Z2, no_plot=True)
    reorderedDf2 = data.T.iloc[colDend['leaves']]
    data = reorderedDf2.T

    df_a = pd.DataFrame({'PtID': data.index})
    ptid_md = pd.merge(df_a, ptid_md, left_on='PtID', right_index=True, how='outer')
    # ptid_md.drop('index', axis=1, inplace=True)

    df_b = pd.DataFrame({'Feature': data.columns})
    measures_md = pd.merge(df_b, measures_md, left_on='Feature', right_index=True, how='outer')
    # measures_md.drop('index', axis=1, inplace=True)

    data.index.name = 'PtID'
    return data, ptid_md, measures_md, rowDend, colDend


def imputeNA(df, method='median', dropThresh=0.):
    """Impute missing values in a pd.DataFrame

    Parameters
    ----------
    df : pd.DataFrame
        Data containing missing values.
    method : str
        Method fo imputation: median, mean, sample, regression
    dropThres : float
        Threshold for dropnp.ping rows: drop rows with fewer than 90% non-nan values

    Returns
    -------
    df : pd.DataFrame
        Copy of the input data with no missing values."""

    outDf = df.dropna(axis=0, thresh=np.round(df.shape[1] * dropThresh)).copy()
    if method == 'sample':
        for col in outDf.columns:
            naInd = outDf[col].isnull()
            outDf.loc[naInd, col] = outDf.loc[~naInd, col].sample(naInd.sum(), replace=True).values
    elif method == 'mean':
        for col in outDf.columns:
            naInd = outDf[col].isnull()
            outDf.loc[naInd, col] = outDf.loc[~naInd, col].mean()
    elif method == 'median':
        for col in outDf.columns:
            naInd = outDf[col].isnull()
            outDf.loc[naInd, col] = outDf.loc[~naInd, col].median()
    elif method == 'regression':
        naInds = []
        for col in outDf.columns:
            naInd = outDf[col].isnull()
            outDf.loc[naInd, col] = outDf.loc[~naInd, col].mean()
            naInds.append(naInd)
        for naInd, col in zip(naInds, outDf.columns):
            if naInd.sum() > 0:
                otherCols = [c for c in outDf.columns if not c == col]
                mod = sklearn.linear_model.LinearRegression().fit(outDf[otherCols], outDf[col])
                outDf.loc[naInd, col] = mod.predict(outDf.loc[naInd, otherCols])
    return outDf


def initSupplementSources(metadata, legend):
    factor_dict = {}
    iterator = -1
    key_array = []
    counts = {}
    for i in range(len(metadata.data['inspect'])):
        entry = metadata.data['inspect'][i]
        if entry not in factor_dict:
            iterator += 1
            factor_dict[entry] = iterator
            counts[entry] = 1
        else:
            counts[entry] = counts[entry] + 1
        key_array.append(factor_dict[entry])
    key_array = list(map(str, key_array))
    metadata.data['inspect'] = key_array
    for entry in factor_dict:
        legend.data['names'].append(entry)
        legend.data['factors'].append(str(factor_dict[entry]))
    storage = list(counts.values())
    return metadata, legend, storage


def _createTable(md, md_source):
    col_names = list(md)
    columns = [TableColumn(field=col_names[0], title=col_names[0], width=150)]
    for i in range(1, len(col_names)):
        columns.append(TableColumn(field=col_names[i], title=col_names[i], width=100))
    data_table = DataTable(source=md_source, columns=columns, width=(len(col_names)) * 100 + 25,
                           height=280, reorderable=False)
    return data_table

def _createBarChart(source, xrange, title):
    barchart = Figure(x_range=xrange, y_range=(0, 50), plot_height=250, plot_width=250, title=title, tools="xpan, xwheel_zoom",
                      active_scroll='xwheel_zoom')

    barchart.vbar(source=source, x='x', top='y', bottom=0, fill_color="#b3de69", width=0.8)
    barchart.toolbar_location = None

    return barchart
