from bokeh.palettes import Set3
from bokeh.transform import factor_cmap
import pandas as pd
from bokeh.plotting import Figure
from bokeh.models.widgets import Tabs, Panel, Div
from bokeh.layouts import layout, column, widgetbox, row
from bokeh.models import (
    HoverTool,
    BoxSelectTool,
    TapTool,
    LinearColorMapper,
    BasicTicker,
    PrintfTickFormatter,
    ColorBar,
    Button,
    Select,
    CheckboxGroup,
    FactorRange,
    CategoricalColorMapper,
    WheelZoomTool,
)

from metaVis import *

__all__ = ['generateLayout']

def generateLayout(sources, cbDict, rowDend, colDend):
    colors =['#ffecb3','#ffeda0','#fed976','#feb24c','#fd8d3c','#fc4e2a','#e31a1c','#bd0026','#800026']
    data, ptid_md, measures_md = sources['data'], sources['ptid_md'], sources['measures_md']

    ptid_list = list(data.index)
    feature_list = list(data.columns)
    feature_df = pd.DataFrame(feature_list)
    feature_df.columns = ["feature"]

    factors = []
    for i in range(12):
        factors.append(str(i))

    mapper2 = LinearColorMapper(palette=Set3[12], low=0, high=11)
    p = _createHeatmap(cbDict=cbDict, colors=colors, sources=sources)

    div = Div(text="""<font face="helvetica" size="20">MetaVis</font>""",
              width=200, height=50)

    x_colorbar = _createColorbar(source=sources['measure'],
                                 p=p,
                                 fig_size=(815, 35),
                                 tools='xpan',
                                 rect_dim=('Feature', 0),
                                 rect_size=(1, 3),
                                 orientation='x',
                                 factors=factors)

    y_colorbar = _createColorbar(source=sources['ptid'],
                                 p=p,
                                 fig_size=(35, 400),
                                 tools='ypan',
                                 rect_dim=(0, 'PtID'),
                                 rect_size=(3, 1),
                                 orientation='y',
                                 factors=factors)

    x_legend = _createLegend(callback=cbDict['m_legend'],
                             source=sources['m_legend'],
                             mapper=mapper2,
                             factors=factors)

    y_legend = _createLegend(callback=cbDict['p_legend'],
                             source=sources['p_legend'],
                             mapper=mapper2,
                             factors=factors)

    y_dendrogram = _createDendrogram(rowDend,
                                     size=(400, 75),
                                     p=p,
                                     list=ptid_list,
                                     orientation='vertical')
    x_dendrogram = _createDendrogram(colDend,
                                     size=(150, 815),
                                     p=p,
                                     list=feature_list,
                                     orientation='horizontal')



    test = Figure(x_range = p.x_range, y_range = (1, 10), plot_width=1000, plot_height=250)
    test.line(1, 2, line_width=100)
    test.line(2, 5)




    (row_reset_button, col_reset_button, selector,
    multiselect_toggle, reset_button, p_selector, m_selector) = _createWidgets(cbDict=cbDict, sources=sources)
    spacer = _createSpacer(p)
    row_table = column(sources['p_data_table'], widgetbox(row_reset_button, width=50))
    col_table = column(sources['m_data_table'], widgetbox(col_reset_button, width=50))
    selectors = column(widgetbox(selector, multiselect_toggle))
    legends = column(y_legend, x_legend)
    button_bar = column(widgetbox(reset_button))
    tab1 = Panel(child=row_table, title="RowTable")
    tab2 = Panel(child=col_table, title="ColTable")
    tabs = Tabs(tabs=[tab1, tab2])
    bar_col = column(row(sources['select_rowbarchart'],
                     sources['nonselect_rowbarchart']),
                     row(sources['select_colbarchart'],
                     sources['nonselect_colbarchart']))
    #DOES NOT INCLUDE DENDROGRAMS
    page = layout([[div], [spacer, column(x_dendrogram, x_colorbar)], [y_dendrogram, y_colorbar, p, legends],
                  [selectors, p_selector, m_selector, button_bar], [bar_col, tabs]])

    # DOES NOT INCLUDE DENDROGRAMS
    # page = layout([[div], [column(x_colorbar)], [y_colorbar, p, legends],
    #               [selectors, p_selector, m_selector, button_bar], [bar_col, tabs]])

    return page

"""============================================================================================"""


def _createWidgets(cbDict, sources):
    # Defining Buttons
    data, ptid_md, measures_md = sources['data'], sources['ptid_md'], sources['measures_md']
    row_reset_button = Button(label="Reset", callback=cbDict['row_reset'], button_type='danger')
    col_reset_button = Button(label="Reset", callback=cbDict['column_reset'], button_type='danger')
    selector = Select(title="Selection Type", value="Cross", options=["Cross", "Row", "Column"],
                      callback=cbDict['select_button'])
    multiselect_toggle = CheckboxGroup(labels=["multiselect"], callback=cbDict['multiselect_toggle'])
    reset_button = Button(label="Reset", callback=cbDict['reset'], button_type='danger', width=100)

    p_select_opt = list(ptid_md)[1:]
    p_select_opt.insert(0, "")
    m_select_opt = list(measures_md)[1:]
    m_select_opt.insert(0, "")
    p_selector = Select(title="Choose row metadata", options=list(ptid_md)[1:], callback=cbDict['p_select'], width=175)
    m_selector = Select(title="Choose column metadata", options=list(measures_md)[1:], callback=cbDict['m_select'], width=175)

    return row_reset_button, col_reset_button, selector, multiselect_toggle, reset_button, p_selector, m_selector


def _createHeatmap(cbDict, colors, sources):
# Defining tools/colors
    df, data = sources['df'], sources['data']
    feature_list = list(data.columns)
    ptid = list(data.index)
    box_select = BoxSelectTool(callback=cbDict['box_select'])
    TOOLS = "hover,save,pan,box_zoom,wheel_zoom,reset,zoom_in,zoom_out"
    mapper = LinearColorMapper(palette=colors, low=df.rate.min(), high=df.rate.max())
    color = {'field': 'rate', 'transform': mapper}

    # Creating heatmap figure
    p = Figure(x_range=FactorRange(factors=feature_list, bounds='auto'),
               y_range=FactorRange(factors=list(reversed(ptid)), bounds='auto'), plot_width=900, plot_height=400,
               tools=[TOOLS, box_select], active_drag=box_select, active_scroll="wheel_zoom",
               toolbar_location='right', toolbar_sticky=False)

    # Adjusting plot details
    p.grid.grid_line_color = None
    p.min_border = 0
    p.outline_line_color = None
    p.axis.visible = False

    # Adding colorbar
    color_bar = ColorBar(color_mapper=mapper, major_label_text_font_size="5pt",
                         ticker=BasicTicker(desired_num_ticks=len(colors)),
                         formatter=PrintfTickFormatter(format="%f"),
                         label_standoff=1, border_line_color=None, location=(0, 0))
    p.add_layout(color_bar, 'right')

    # Adding hover functionality
    p.select_one(HoverTool).tooltips = [
        ('Patient ID and Feature', '@PtID, @Feature'),
        ('rate', '@rate')
    ]

    # Creating individual rectangle glyphs for heatmap
    p.rect(x="Feature", y="PtID", width=1, height=1,
           source=sources['source'],
           fill_color=color,
           line_color=None,
           selection_fill_color=color,
           selection_line_color=None,
           nonselection_line_color=None,
           nonselection_fill_alpha=0.5,
           nonselection_fill_color=color,
           )
    return p

# PERFORMANCE BOTTLENECK PLEASE FIX
def _createDendrogram(dend, size, p, list, orientation='horizontal'):
    dend['dcoord'] = [[j * 2.5 - 0.5 for j in i] for i in dend['dcoord']]
    dend['icoord'] = [[j * 0.1 for j in i] for i in dend['icoord']]
    if orientation == 'horizontal':
        """For an X dendrogram"""
        tools = 'ypan'
        wz = WheelZoomTool(dimensions='height')
        dendrogram = Figure(y_range=(1, (8 / 5 * len(list))),
                            x_range=p.x_range,
                            plot_width=size[1],
                            plot_height=size[0],
                            tools=[tools, wz],
                            active_scroll=wz)
    elif orientation == 'vertical':
        """For a Y dendrogram"""
        tools = 'xpan'
        wz = WheelZoomTool(dimensions='width')
        dendrogram = Figure(y_range=p.y_range,
                            x_range=((5 / 4 * len(list) + 50), 1),
                            plot_width=size[1],
                            plot_height=size[0],
                            tools=[tools, wz],
                            active_scroll=wz)

    dendrogram.toolbar_location = None
    dendrogram.outline_line_color = None
    dendrogram.axis.major_tick_line_color = None
    dendrogram.axis.minor_tick_line_color = None
    dendrogram.min_border = 0
    dendrogram.axis.major_label_standoff = 0
    dendrogram.axis.axis_line_color = None
    dendrogram.background_fill_color = 'white'
    dendrogram.grid.grid_line_color = None
    dendrogram.xaxis.major_label_text_font_size = '0pt'
    dendrogram.axis.visible = False

    if orientation == 'vertical':
        # PERFORMANCE BOTTLENECK PLEASE FIX
        for xlist, ylist in zip(dend['dcoord'], dend['icoord']):
            dendrogram.line(xlist, ylist, color='black', selection_color='black', nonselection_color='black',
                              selection_line_alpha=1, nonselection_line_alpha=1)
        # OLD MULTILINE CODE
        #dendrogram.multi_line(dend['dcoord'], dend['icoord'], color='black',
                              #selection_color='black', nonselection_color='black',
                              #selection_line_alpha=1, nonselection_line_alpha=1)
    elif orientation == 'horizontal':
        # PERFORMANCE BOTTLENECK PLEASE FIX
        for xlist, ylist in zip(dend['icoord'], dend['dcoord']):
            dendrogram.line(xlist, ylist, color='black', selection_color='black', nonselection_color='black',
                              selection_line_alpha=1, nonselection_line_alpha=1)
        # OLD MULTILINE CODE
        #dendrogram.multi_line(dend['icoord'], dend['dcoord'], color='black',
                              #selection_color='black', nonselection_color='black',
                              #selection_line_alpha=1, nonselection_line_alpha=1)
    return dendrogram


def _createColorbar(source, p, fig_size, tools, rect_dim, rect_size, orientation, factors):
    if orientation == 'y':
        colorbar = Figure(
            y_range=p.y_range,
            plot_width=fig_size[0], plot_height=fig_size[1],
            tools=tools
        )

    else:
        colorbar = Figure(
            x_range=p.x_range,
            plot_width=fig_size[0], plot_height=fig_size[1],
            tools=tools
        )
    colorbar.toolbar_location = None
    colorbar.outline_line_color = None
    colorbar.min_border = 0
    colorbar.background_fill_color = 'white'
    colorbar.grid.grid_line_color = None
    colorbar.axis.visible = False

    colorbar.rect(source=source, x=rect_dim[0], y=rect_dim[1], width=rect_size[0], height=rect_size[1], line_color=None,
                  fill_color=factor_cmap('inspect', palette=Set3[12], factors=factors),
                  selection_fill_color=factor_cmap('inspect', palette=Set3[12], factors=factors),
                  nonselection_fill_color=factor_cmap('inspect', palette=Set3[12], factors=factors),
                  selection_fill_alpha=1, nonselection_fill_alpha=1, selection_line_alpha=0
                  )
    return colorbar


def _createLegend(callback, source, mapper, factors):
    legend_tap = TapTool(callback=callback)
    legend = Figure(x_range=(-0.25, 3), y_range=(-1, 7), plot_height=200, plot_width=200, tools=[legend_tap, 'ypan'])
    legend.outline_line_color = None
    legend.toolbar_location = None
    legend.min_border = 0
    legend.grid.grid_line_color = None
    legend.axis.visible = False

    legend.text(source=source, x=0.3, y='factors', text_font_size='9pt', text='names', y_offset=7,
                selection_text_alpha=1.3, nonselection_text_alpha=0.75)
    legend.rect(source=source, x=0, y='factors', width=0.3, height=0.5, line_color='black',
                fill_color=factor_cmap('factors', palette=Set3[12], factors=factors),
                selection_fill_color=factor_cmap('factors', palette=Set3[12], factors=factors),
                nonselection_fill_color=factor_cmap('factors', palette=Set3[12], factors=factors),
                selection_fill_alpha=1,
                nonselection_fill_alpha=0.75
                )
    return legend

def _createSpacer(p):
    spacer = Figure(
        x_range=p.x_range,
        plot_width=109, plot_height=10
    )
    spacer.outline_line_color = None
    spacer.toolbar_location = None
    spacer.min_border = 0
    spacer.grid.grid_line_color = None
    spacer.axis.visible = False
    return spacer
