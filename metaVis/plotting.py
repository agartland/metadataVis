from datetime import date
from random import randint

import io
import random

from jinja2 import Template

from bokeh.embed import components
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import DataTable, DateFormatter, TableColumn
from bokeh.resources import INLINE
from bokeh.util.browser import view
from bokeh.palettes import Set3
import MetaVisLauncherConfig as config
from bokeh.transform import factor_cmap
import pandas as pd
from bokeh.plotting import Figure
from bokeh.models.widgets import Tabs, Panel, Div, TextInput
from bokeh.layouts import layout, column, widgetbox, row
from bokeh.models import (
    BasicTicker,
    BoxSelectTool,
    Button,
    CategoricalColorMapper,
    ColorBar,
    CustomJS,
    HoverTool,
    TapTool,
    LinearColorMapper,
    PrintfTickFormatter,
    Select,
    CheckboxGroup,
    FactorRange,
    DataRange1d,
    Range1d,
    RadioButtonGroup,
    WheelZoomTool
)

from metaVis import *

__all__ = ['generateLayout']


def generateLayout(sources, cbDict, rowDend, colDend):
    colors = ['#ffecb3', '#ffeda0', '#fed976', '#feb24c', '#fd8d3c', '#fc4e2a', '#e31a1c', '#bd0026', '#800026']
    data, ptid_md, measures_md = sources['data'], sources['ptid_md'], sources['measures_md']

    ptid_list = list(data.index)
    feature_list = list(data.columns)
    feature_df = pd.DataFrame(feature_list)
    feature_df.columns = ["feature"]

    factors = []
    for i in range(70):
        factors.append(str(i))

    # mapper2 = LinearColorMapper(palette=Set3[12], low=0, high=11)
    p, heatmap_mapper = _createHeatmap(cbDict=cbDict, colors=colors, sources=sources)
    x_palette = config.palette
    y_palette = config.palette

    x_colorbar, x_bar_mapper = _createColorbar(source=sources['measure'],
                                               p=p,
                                               fig_size=(815, 35),
                                               tools='xpan',
                                               rect_dim=('Feature', 0),
                                               rect_size=(1, 3),
                                               orientation='x',
                                               factors=factors,
                                               palette=x_palette)

    y_colorbar, y_bar_mapper = _createColorbar(source=sources['ptid'],
                                               p=p,
                                               fig_size=(35, 400),
                                               tools='ypan',
                                               rect_dim=(0, 'PtID'),
                                               rect_size=(3, 1),
                                               orientation='y',
                                               factors=factors,
                                               palette=y_palette)

    x_legend, x_legend_mapper = _createLegend(callback=cbDict['m_legend'],
                                              source=sources['m_legend'],
                                              factors=factors,
                                              title="Column Colorbar",
                                              palette=x_palette)

    y_legend, y_legend_mapper = _createLegend(callback=cbDict['p_legend'],
                                              source=sources['p_legend'],
                                              factors=factors,
                                              title="Row Colorbar",
                                              palette=y_palette)

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

    (row_reset_button, col_reset_button, selector,
     multiselect_toggle, reset_button, p_selector, m_selector) = _createWidgets(cbDict=cbDict, sources=sources, x_legend=x_legend, y_legend=y_legend)
    spacer = _createSpacer(p)
    row_table = column(sources['p_data_table'], widgetbox(row_reset_button, width=50))
    col_table = column(sources['m_data_table'], widgetbox(col_reset_button, width=50))
    selectors = column(widgetbox(selector, multiselect_toggle))
    legends = column(y_legend, x_legend)
    subsel_button = column(widgetbox(reset_button))

    data_tab1 = Panel(child=row_table, title="Row Table")
    data_tab2 = Panel(child=col_table, title="Col Table")
    table_tabs = Tabs(tabs=[data_tab1, data_tab2])

    select_rowbar_tab = Panel(child=sources['select_rowbarchart'], title="Selected Rows")
    nonselect_rowbar_tab = Panel(child=sources['nonselect_rowbarchart'], title="Unselected Rows")
    select_colbar_tab = Panel(child=sources['select_colbarchart'], title="Selected Cols")
    nonselect_colbar_tab = Panel(child=sources['nonselect_colbarchart'], title="Unselected Cols")

    barchart_tabs = widgetbox(Tabs(tabs=[select_rowbar_tab, nonselect_rowbar_tab, select_colbar_tab, nonselect_colbar_tab]))

    # Heatmap Density Color Selector:
    # TODO - Add default coloring if given no input
    # TODO - Better Names
    heatmap_color_buttons = [_genColorButton(i, heatmap_mapper, len(colors)) for i in range(len(colors))]

    # Heatmap MetaData Label Color Selector:
    x_legend_data = sources['m_legend'].data['names']
    x_legend_buttons = [_genLabelColorButtons(i, x_legend_mapper, x_bar_mapper,
                                              sources['xbar_mapper1'], sources['xbar_mapper2'],
                                              len(x_legend_data), x_legend_data[i]) for i in range(len(x_legend_data))]

    y_legend_data = sources['p_legend'].data['names']
    y_legend_buttons = [_genLabelColorButtons(i, y_legend_mapper, y_bar_mapper,
                                              sources['ybar_mapper1'], sources['ybar_mapper2'],
                                              len(y_legend_data), y_legend_data[i]) for i in range(len(y_legend_data))]

    # Presets
    preset_cb = CustomJS(args=dict(mapper=heatmap_mapper), code="""
        palettes = [
         ['#ffecb3','#ffeda0','#fed976','#feb24c','#fd8d3c','#fc4e2a','#e31a1c','#bd0026','#800026'],
         ["#75968f","#a5bab7","#c9d9d3","#e2e2e2","#dfccce","#ddb7b1","#cc7878","#933b41", "#550b1d"],
         ['#434268','#c19cd6','#9c9cd6','#9cc3d6','#9cd6bd','#edebaf','#edd0af','#e5c1bc','#ed6a6a']
         ]
        mapper.palette = palettes[cb_obj.active];
        mapper.change.emit();
    """)

    preset_buttons = RadioButtonGroup(labels=["Palette 1", "Palette 2", "Palette 3"], active=0)
    preset_buttons.js_on_click(preset_cb)

    # TODO: "x_color_JS"
    heatmap_color_tab = Panel(child=widgetbox(heatmap_color_buttons, width=100), title='HeatMap Colors', closable=True)
    preset_tab = Panel(child=preset_buttons, title="Presets", closable=True)
    x_legend_tab = Panel(child=widgetbox(x_legend_buttons, width=100), title='X Legend Colors', closable=True)
    y_legend_tab = Panel(child=widgetbox(y_legend_buttons, width=100), title='Y Legend Colors', closable=True)

    # LEGEND TABS DO NOT UPDATE WITH
    cust_tabs = Tabs(tabs=[heatmap_color_tab, preset_tab])

    # bar_col = column(row(sources['select_rowbarchart'],
    #                  sources['nonselect_rowbarchart']),
    #                  row(sources['select_colbarchart'],
    #                  sources['nonselect_colbarchart']))

    # INCLUDES DENDROGRAMS
    page = layout([[spacer, column(x_dendrogram, x_colorbar)], [y_dendrogram, y_colorbar, p, legends, reset_button],
                   [selectors, p_selector, m_selector],[table_tabs]])
    heatmap = layout([spacer, column(x_dendrogram, x_colorbar)], [y_dendrogram, y_colorbar, p, legends])

    template = Template("""\
    <!DOCTYPE html>
    <html lang="en">
        <head>
            <meta charset="utf-8">
            <title>MetaVis</title>
            {{ resources }}
            <script src="https://ajax.aspnetcdn.com/ajax/jQuery/jquery-3.3.1.min.js"></script>
            <link href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.0/css/bootstrap.min.css" rel="stylesheet" id="bootstrap-css">
            <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.0/js/bootstrap.min.js"></script>
            <link rel="stylesheet" href="bootstrap/header.css">
            <link rel="stylesheet" href="bootstrap/sidebar.css">
            <link rel="stylesheet" href="bootstrap/sidemenu.css">
            <script src="bootstrap/sidebar.js"></script>
            <script src="bootstrap/sidemenu.js"></script>
            <script src="bootstrap/header.js"></script>
        </head>
        <body>
        <nav id="header" class="navbar navbar-fixed-top">
            <div id="header-container" class="container navbar-container">
                <nav class="navbar navbar-fixed-left navbar-minimal animate" role="navigation">
                        <div class="navbar-toggler animate">
                            <span class="menu-icon"></span>
                        </div>
                        <ul class=" navbar-menu animate">
                            <li>
                                <div class="container2">
                                <div class="panel panel-default">
                                    <div class="panel-heading panel-collapse-clickable" data-toggle="collapse" data-parent="#accordion" href="#filterPanel">
                                        <h4 class="panel-title">
                                            Color Palette
                                            <span class="pull-right">
                                                <i class="glyphicon glyphicon-chevron-down"></i>
                                            </span>
                                        </h4>
                                    </div>
                                    <div id="filterPanel" class="panel-collapse panel-collapse collapse">
                                        <div class="panel-body">
                                            {{ plot_div.colors }}
                                        </div>
                                    </div>
                                </div>
                                </div>
                            </li>
                            <li>
                                <div class="container2">
                                    <div class="panel panel-default">
                                        <div class="panel-heading panel-collapse-clickable" data-toggle="collapse" data-parent="#accordion" href="#filterPanel2">
                                            <h4 class="panel-title">
                                                Histograms
                                                <span class="pull-right">
                                                    <i class="glyphicon glyphicon-chevron-down"></i>
                                                </span>
                                            </h4>
                                        </div>
                                        <div id="filterPanel2" class="panel-collapse panel-collapse collapse">
                                            <div class="panel-body">
                                                {{ plot_div.bars }}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </li>
                        </ul>
                </nav>
                <div class="navbar-header">
                    <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#navbar" aria-expanded="false" aria-controls="navbar">
                        <span class="sr-only">Toggle navigation</span>
                        <span class="icon-bar"></span>
                        <span class="icon-bar"></span>
                        <span class="icon-bar"></span>
                    </button>
                    <a id="brand" class="navbar-brand" href="#">MetaVis: <span id="brand-span">Interactive Exploratory Visualizations</span> </a>
                </div>
                <div id="navbar" class="collapse navbar-collapse">
                    <ul class="nav navbar-nav">
                        <li class="active"><a href="#">Home</a></li>
                        <li><a href="#tutorial">Tutorial</a></li>
                        <li><a href="#contact">Contact</a></li>
                    </ul>
                </div><!-- /.nav-collapse -->
            </div><!-- /.container -->
        </nav><!-- /.navbar -->
        {{ plot_div.page }}
        <footer>
            <p>(c) 2018 Michael Zhao, All Rights Reserved. Visualizations provided by <a style="color:#0a93a6; text-decoration:none;" href="https://bokeh.pydata.org/en/latest/"> Bokeh</a></p>
        </footer>
        {{ plot_script }}


        </body>
    </html>
    """)

    resources = INLINE.render()

    script, div = components({'page': page, 'colors': cust_tabs, 'bars': barchart_tabs})

    html = template.render(resources=resources,
                           plot_script=script,
                           plot_div=div)

    filename = 'MetaVis.html'

    with io.open(filename, mode='w', encoding='utf-8') as f:
        f.write(html)

    with open('bootstrap/headercss.txt', 'r') as myfile:
        headercss = myfile.read()
    with open('bootstrap/headerjs.txt', 'r') as myfile:
        headerjs = myfile.read()
    with open('bootstrap/introjs.txt', 'r') as myfile:
        introjs = myfile.read()
    with open('bootstrap/introcss.txt', 'r') as myfile:
        introcss = myfile.read()
    with open('bootstrap/sidebarcss.txt', 'r') as myfile:
        sidebarcss = myfile.read()
    with open('bootstrap/sidebarjs.txt', 'r') as myfile:
        sidebarjs = myfile.read()
    with open('bootstrap/stepcss.txt', 'r') as myfile:
        stepcss = myfile.read()
    with open('bootstrap/stepjs.txt', 'r') as myfile:
        stepjs = myfile.read()
    with open('bootstrap/sidemenucss.txt', 'r') as myfile:
        sidemenucss = myfile.read()
    with open('bootstrap/sidemenujs.txt', 'r') as myfile:
        sidemenujs = myfile.read()

    template2 = Template("""\
    <!DOCTYPE html>
    <html lang="en">
        <head>
            <meta charset="utf-8">
            <title>MetaVis</title>
            {{ resources }}
            <script src="https://ajax.aspnetcdn.com/ajax/jQuery/jquery-3.3.1.min.js"></script>
            <link href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.0/css/bootstrap.min.css" rel="stylesheet" id="bootstrap-css">
            <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.0/js/bootstrap.min.js"></script>
            <style> {{ bootstrap.headercss }} </style>
            <style> {{ bootstrap.sidebarcss }} </style>
            <style> {{ bootstrap.sidemenucss }} </style>
            <style> {{ bootstrap.introcss }} </style>
            <style> {{ bootstrap.stepcss }} </style>
            <script> {{ bootstrap.introjs }} </script>
            <script> {{ bootstrap.sidemenujs }} </script>
            <script> {{ bootstrap.sidebarjs }} </script>
            <script> {{ bootstrap.headerjs }} </script>
            <script> {{ bootstrap.stepjs }} </script>
        </head>
        <body>
        <nav id="header" class="navbar navbar-fixed-top">
            <div id="header-container" class="container navbar-container">
                <nav class="navbar navbar-fixed-left navbar-minimal animate" role="navigation">
                    <div class="navbar-toggler animate">
                        <span class="menu-icon"></span>
                    </div>
                    <ul class=" navbar-menu animate">
                        <li>
                            <div class="container2">
                            <div class="panel panel-default">
                                <div class="panel-heading panel-collapse-clickable" data-toggle="collapse" data-parent="#accordion" href="#filterPanel">
                                    <h4 class="panel-title">
                                        Color Palette
                                        <span class="pull-right">
                                            <i class="glyphicon glyphicon-chevron-down"></i>
                                        </span>
                                    </h4>
                                </div>
                                <div id="filterPanel" class="panel-collapse panel-collapse collapse">
                                    <div class="panel-body">
                                        {{ plot_div.colors }}
                                    </div>
                                </div>
                            </div>
                            </div>
                        </li>
                        <li>
                            <div class="container2">
                                <div class="panel panel-default">
                                    <div class="panel-heading panel-collapse-clickable" data-toggle="collapse" data-parent="#accordion" href="#filterPanel2">
                                        <h4 class="panel-title">
                                            Histograms
                                            <span class="pull-right">
                                                <i class="glyphicon glyphicon-chevron-down"></i>
                                            </span>
                                        </h4>
                                    </div>
                                    <div id="filterPanel2" class="panel-collapse panel-collapse collapse">
                                        <div class="panel-body">
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </li>
                    </ul>
                </nav>
                <div class="navbar-header">
                    <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#navbar" aria-expanded="false" aria-controls="navbar">
                        <span class="sr-only">Toggle navigation</span>
                        <span class="icon-bar"></span>
                        <span class="icon-bar"></span>
                        <span class="icon-bar"></span>
                    </button>
                    <a id="brand" class="navbar-brand" href="#">MetaVis: <span id="brand-span">Interactive Exploratory Visualizations</span> </a>
                </div>
                <div id="navbar" class="collapse navbar-collapse">
                    <ul class="nav navbar-nav">
                        <li class="active"><a href="#">Home</a></li>
                        <li><a href='javascript:;' onclick="startIntro();" id="tut"s>Tutorial</a></li>
                        <li><a href="#contact">Contact</a></li>
                        <li><a href="#javascript:;" onclick="toggleHints();">Toggle Tips</a></li>
                    </ul>
                </div><!-- /.nav-collapse -->
            </div><!-- /.container -->
        </nav><!-- /.navbar -->
        <section class='wrapper'> 
            <div id=spacer> </div>
            <div class='col-flex'>
                <div id="x_dend">
                    {{ plot_div.x_dend }}
                </div>
                <div id="x_color">
                    {{ plot_div.x_color }}
                </div>
                <div class='hidden overlay' id='color-q' onclick="step('7');"> 
                    <span class="tooltiptext">Colorbars</span>
                </div>
            </div>
        </section>
        <section class='wrapper'>
            <div class='hidden overlay' id='dend-q' onclick="step('13');"> 
                <span class="tooltiptext">Dendrograms</span>
            </div>
            <div id="y_dend"> 
                {{ plot_div.y_dend }}
            </div>
            <div id="y_color">
                {{ plot_div.y_color }}
            </div>
            <div class='hidden overlay' id='heatmap-q' onclick="step('2');">
                <span class="tooltiptext">Heatmap</span>
            </div>
            <div id="heatmap"> 
                {{ plot_div.heatmap }}
            </div>
            <div class='col-flex' id='legs'>
                <div id='y_leg'>
                    {{ plot_div.y_leg }}
                </div>
                <div id='x_leg'>
                    {{ plot_div.x_leg }}
                </div>  
                <div class='hidden overlay' id='leg-q'onclick="step('10');"> 
                    <span class="tooltiptext">Legends</span>
                </div>
            </div>
        </section>
        <section class='wrapper'> 
            <div id='selectors'>
                {{ plot_div.selectors }}
            </div>
            <div id='meta-select'>
                <div id='p_selector'>
                    {{ plot_div.p_selector }}
                </div>
                <div id='m_selector'>
                    {{ plot_div.m_selector }}
                </div>
            </div>
            <div id='reset'>
                {{ plot_div.reset }}
            </div>
            <div class='hidden overlay' id='sel-q' onclick="step('3');"> 
                <span class="tooltiptext">Selectors</span>
            </div>
        </section>
        <section class="wrapper">
            <div class='hidden overlay' id='table-q' onclick="step('15');"> 
                <span class="tooltiptext">Data Tables</span>
            </div>
            <div id='table-tabs'>
                {{ plot_div.table_tabs }}
            </div>
            <div class='hidden overlay' id='bar-q' onclick="step('16');"> 
                <span class="tooltiptext">Histograms</span>
            </div>
            <div id='bar-tabs'>
                {{ plot_div.bar_tabs }}
            </div>
        </section>
        <div style="background-color:lightblue;display:none;width:100px;height:100px" id='temp'> 
        </div>
        <footer>
            <p>(c) 2018 Michael Zhao, All Rights Reserved. Visualizations provided by <a style="color:#0a93a6; text-decoration:none;" href="https://bokeh.pydata.org/en/latest/"> Bokeh</a></p>
        </footer>
        {{ plot_script }}
    
    
        </body>
    </html>
    """)

    resources2 = INLINE.render()

    heatmap = layout([spacer, column(x_dendrogram, x_colorbar)], [y_dendrogram, y_colorbar, p, legends])


    script2, div2 = components({'heatmap': p, 'y_color': y_colorbar, 'y_dend': y_dendrogram, 'x_dend': x_dendrogram,
                                'x_leg': x_legend, 'y_leg': y_legend, 'selectors': selectors, 'p_selector': p_selector,
                                'm_selector': m_selector, 'reset': reset_button, 'bar_tabs': barchart_tabs,
                                'table_tabs': table_tabs, 'x_color': x_colorbar, 'colors': cust_tabs})

    bootstrap = {'headercss': headercss, 'headerjs': headerjs, 'introjs': introjs, 'introcss': introcss,
                 'sidebarcss': sidebarcss, 'sidebarjs': sidebarjs, 'stepjs': stepjs, 'stepcss': stepcss,
                 'sidemenujs': sidemenujs, 'sidemenucss': sidemenucss}

    html = template2.render(resources=resources2,
                           plot_script=script2,
                           plot_div=div2,
                           bootstrap=bootstrap)

    filename2 = 'MetaVis.html'

    with io.open(filename2, mode='w', encoding='utf-8') as g:
        g.write(html)

    # view(filename2)

    # DOES NOT INCLUDE DENDROGRAMS
    # page = layout([[div], [column(x_colorbar)], [y_colorbar, p, legends],
    #               [selectors, p_selector, m_selector, button_bar], [barchart_tabs, table_tabs]])

    # return page
    return html


"""============================================================================================"""


def _createWidgets(cbDict, sources, x_legend, y_legend):
    # Defining Buttons
    data, ptid_md, measures_md = sources['data'], sources['ptid_md'], sources['measures_md']
    row_reset_button = Button(label="Reset", callback=cbDict['row_reset'], button_type='danger')
    col_reset_button = Button(label="Reset", callback=cbDict['column_reset'], button_type='danger')
    selector = Select(title="Selection Type", value="Cross", options=["Cross", "Row", "Column"],
                      callback=cbDict['select_button'])
    multiselect_toggle = CheckboxGroup(labels=["multiselect"], callback=cbDict['multiselect_toggle'])
    reset_button = Button(label="Reset", callback=cbDict['reset'], button_type='danger', width=100)
    p_selector = Select(title="Choose row metadata", options=list(ptid_md)[1:], callback=CustomJS(args=dict(y_legend=y_legend, source=sources['source'], p_legend=sources['p_legend'],
                                            storage=sources['storage'], ptid=sources['ptid'], nonselect_rowbarchart=sources['nonselect_rowbarchart'],
                                            select_rowbarchart=sources['select_rowbarchart']), code='''
        y_legend.reset.emit();
        let input = cb_obj.value;
        storage.data['p_colname'] = input;
        let new_row = ptid.data[input];
        var factor_dict = {};
        var count = -1;
        var freq = {};
        var key_array = [];
        for (i = 0; i < new_row.length; i++) {
            var entry = new_row[i];
            if (!(factor_dict.hasOwnProperty(entry))) {
                count++;
                factor_dict[entry] = count;
                freq[entry] = 1;
            }
            else {
                freq[entry] = freq[entry] + 1;
            }
            key_array.push(factor_dict[entry]);
        }
        ptid.data['inspect'] = key_array.map(String);
        ptid.change.emit();
        freq_list = [];
        for (var key in freq) {
            freq_list.push(freq[key]);
        }            
        storage.data['total_rowbar'] = freq_list;        
        p_legend.data['factors'] = [];
        p_legend.data['names'] = [];
        let names = [];
        let factors = [];
        for (entry in factor_dict) {
            names.push(entry);
            factors.push(factor_dict[entry].toString());
        }
        let sel_count = new Array(freq_list.length).fill(0);
        p_legend.data = {'factors': factors, 'names': names, 'nonsel_count': freq_list, 'sel_count': sel_count};
        console.log(p_legend.data);
        p_legend.change.emit();
        p_legend.data['nonsel_count'] = storage.data['total_rowbar'];
        p_legend.selected.indices = [];
        p_legend.change.emit();
        nonselect_rowbarchart.x_range.factors = p_legend.data['names'];
        select_rowbarchart.x_range.factors = p_legend.data['names'];
    '''), width=175)
    m_selector = Select(title="Choose column metadata", options=list(measures_md)[1:], callback=CustomJS(args=dict(x_legend=x_legend, source=sources['source'], p_legend=sources['p_legend'],
                                            storage=sources['storage'], measure=sources['measure'], col=sources['col'], m_table=sources['m_table'],
                                            m_data_table=sources['m_data_table'], m_legend=sources['m_legend'], nonselect_colbarchart=sources['nonselect_colbarchart'],
                                            select_colbarchart=sources['select_colbarchart']), code='''
        x_legend.reset.emit();
        let input = cb_obj.value;
        storage.data['m_colname'] = input;
        let new_row = measure.data[input];
        var factor_dict = {};
        var count = -1;
        var freq = {};
        var key_array = [];
        for (i = 0; i < new_row.length; i++) {
            var entry = new_row[i];
            if (!(factor_dict.hasOwnProperty(entry))) {
                count++;
                factor_dict[entry] = count;
                freq[entry] = 1;
            }
            else {
                freq[entry] = freq[entry] + 1;
            }
            key_array.push(factor_dict[entry]);
        }
        measure.data['inspect'] = key_array.map(String);
        measure.change.emit();
        freq_list = [];
        for (var key in freq) {
            freq_list.push(freq[key]);
        }
        storage.data['total_colbar'] = freq_list;
        m_legend.data['factors'] = [];
        m_legend.data['names'] = [];
        let names = [];
        let factors = [];
        for (entry in factor_dict) {
            names.push(entry);
            factors.push(factor_dict[entry].toString());
        }
        console.log(m_legend.data);
        let sel_count = new Array(freq_list.length).fill(0);
        m_legend.data = {'factors': factors, 'names': names, 'nonsel_count': freq_list, 'sel_count': sel_count};
        console.log(m_legend.data);
        m_legend.change.emit();
        console.log(m_legend.data['factors']);
        m_legend.data['nonsel_count'] = storage.data['total_colbar'];
        m_legend.selected.indices = [];
        m_legend.change.emit();
        nonselect_colbarchart.x_range.factors = m_legend.data['names'];
        select_colbarchart.x_range.factors = m_legend.data['names'];
                                            '''), width=175)

    return row_reset_button, col_reset_button, selector, multiselect_toggle, reset_button, p_selector, m_selector


def _createHeatmap(cbDict, colors, sources):
    # Defining tools/colors
    df, data = sources['df'], sources['data']
    feature_list = list(data.columns)
    ptid = list(data.index)
    box_select = BoxSelectTool(callback=cbDict['box_select'])
    TOOLS = "hover,save,pan,box_zoom,reset,zoom_in,zoom_out"
    mapper = LinearColorMapper(palette=colors, low=df.rate.min(), high=df.rate.max())
    color = {'field': 'rate', 'transform': mapper}

    # Creating heatmap figure
    p = Figure(x_range=FactorRange(factors=feature_list, bounds='auto'),
               y_range=FactorRange(factors=list(reversed(ptid)), bounds='auto'), plot_width=900, plot_height=400,
               tools=[TOOLS, box_select], active_drag=box_select, logo=None,
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
        ('Patient ID ', '@PtID'),
        ('Feature: ', '@Feature'),
        ('rate', '@rate')
    ]

    # Creating individual rectangle glyphs for heatmap
    p.rect(x="Feature", y="PtID", width=1, height=1,
           source=sources['source'],
           fill_color=color,
           line_color=None,
           selection_fill_color=color,
           selection_line_color="black",
           selection_line_alpha=0.2,
           nonselection_line_color=None,
           nonselection_fill_alpha=0,
           nonselection_fill_color=color,
           )
    return p, mapper


def _createSubsel(colors, sources, mapper):
    # Defining tools/colors
    color = {'field': 'rate', 'transform': mapper}
    TOOLS = "hover,save,pan,box_zoom,reset,zoom_in,zoom_out"

    # Creating heatmap figure
    subsel_chart = Figure(x_range=sources['subsel_source'].data['features'],
               y_range=sources['subsel_source'].data['ptids'], plot_width=900, plot_height=400,
               tools=[TOOLS], logo=None,
               toolbar_location='right', toolbar_sticky=False)

    # Adjusting plot details
    subsel_chart.grid.grid_line_color = None
    subsel_chart.min_border = 0
    subsel_chart.outline_line_color = None
    subsel_chart.axis.visible = False

    # Adding colorbar
    color_bar = ColorBar(color_mapper=mapper, major_label_text_font_size="5pt",
                         ticker=BasicTicker(desired_num_ticks=len(colors)),
                         formatter=PrintfTickFormatter(format="%f"),
                         label_standoff=1, border_line_color=None, location=(0, 0))

    subsel_chart.add_layout(color_bar, 'right')

    # Adding hover functionality
    subsel_chart.select_one(HoverTool).tooltips = [
        ('Patient ID and Feature', '@PtID, @Feature'),
        ('rate', '@rate')
    ]

    # Creating individual rectangle glyphs for heatmap
    subsel_chart.rect(x="features", y="ptids", width=1, height=1,
           source=sources['subsel_source'],
           fill_color=color,
           line_color=None,
           selection_fill_color=color,
           selection_line_color="black",
           selection_line_alpha=0.2,
           nonselection_line_color=None,
           nonselection_fill_alpha=0,
           nonselection_fill_color=color,
           )
    sources['subsel_chart'] = subsel_chart
    return subsel_chart


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
    dendrogram.outline_line_color = 'navy'
    dendrogram.outline_line_alpha = 0.1
    dendrogram.outline_line_width = 5
    dendrogram.axis.major_tick_line_color = None
    dendrogram.axis.minor_tick_line_color = None
    dendrogram.min_border = 0
    dendrogram.axis.major_label_standoff = 0
    dendrogram.axis.axis_line_color = None
    dendrogram.background_fill_color = 'white'
    dendrogram.grid.grid_line_color = None
    dendrogram.xaxis.major_label_text_font_size = '0pt'
    dendrogram.axis.visible = False
    name = 0

    if orientation == 'vertical':
        # PERFORMANCE BOTTLENECK PLEASE FIX
        for xlist, ylist in zip(dend['dcoord'], dend['icoord']):
            name += 1
            line = dendrogram.line(xlist, ylist, color='black', selection_color='black', nonselection_color='black',
                            selection_line_alpha=1, nonselection_line_alpha=1, hover_line_color='red', name="line")
        # OLD MULTILINE CODE
        # dendrogram.multi_line(dend['dcoord'], dend['icoord'], color='black',
        # selection_color='black', nonselection_color='black',
        # selection_line_alpha=1, nonselection_line_alpha=1)
    elif orientation == 'horizontal':
        # PERFORMANCE BOTTLENECK PLEASE FIX
        for xlist, ylist in zip(dend['icoord'], dend['dcoord']):
            name += 1
            line = dendrogram.line(xlist, ylist, color='black', selection_color='black', nonselection_color='black',
                            selection_line_alpha=1, nonselection_line_alpha=1, hover_line_color='red', name="line")

        # OLD MULTILINE CODE
        # dendrogram.multi_line(dend['icoord'], dend['dcoord'], color='black',
        # selection_color='black', nonselection_color='black',
        # selection_line_alpha=1, nonselection_line_alpha=1)
    callback = CustomJS(args=dict(), code="""
        console.log(cb_obj);
    """)
    dendrogram.add_tools(TapTool())
    return dendrogram


def _createColorbar(source, p, fig_size, tools, rect_dim, rect_size, orientation, factors, palette):
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

    mapper_dict = factor_cmap('inspect', palette=palette, factors=factors)

    colorbar.rect(source=source, x=rect_dim[0], y=rect_dim[1], width=rect_size[0], height=rect_size[1], line_color=None,
                  fill_color=mapper_dict,
                  selection_fill_color=mapper_dict,
                  nonselection_fill_color=mapper_dict,
                  selection_fill_alpha=1, nonselection_fill_alpha=1, selection_line_alpha=0
                  )
    return colorbar, mapper_dict['transform']


def _createLegend(callback, source, factors, title, palette):
    legend_tap = TapTool(callback=callback)
    legend = Figure(x_range=(-0.25, 3), y_range=Range1d(7, -1, bounds=(-1, None)), plot_height=200, plot_width=200,
                    tools=[legend_tap, 'ywheel_pan', 'ypan'],
                    active_scroll='ywheel_pan')
    legend.toolbar_location = None
    legend.min_border = 0
    legend.grid.grid_line_color = None
    legend.axis.visible = False
    legend.outline_line_color = 'navy'
    legend.outline_line_alpha = 0.1
    legend.outline_line_width = 5
    legend.title.text_font = "times"
    mapper_dict = factor_cmap('factors', palette=palette, factors=factors)

    legend.text(source=source, x=0.3, y='factors', text_font_size='9pt', text='names', y_offset=7,
                selection_text_alpha=1.3, nonselection_text_alpha=0.75)
    legend.rect(source=source, x=0, y='factors', width=0.3, height=0.5, line_color='black',
                fill_color=mapper_dict,
                selection_fill_color=mapper_dict,
                nonselection_fill_color=mapper_dict,
                selection_fill_alpha=1,
                nonselection_fill_alpha=0.75,
                selection_line_color='black'
                )

    return legend, mapper_dict['transform']


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


# Generates JS callback for changing a color mapper
# Param:
# idx - the idx of the respective color mapper.palette to change
def _colorMapCB(idx):
    cb = """palette = mapper.palette;
            palette[""" + str(idx) + """] = cb_obj.value;
            mapper.change.emit();
         """
    return cb


def _twoColorMapCB(idx):
    cb = """let palette_1 = legend_mapper.palette;
            let palette_2 = bar_mapper.palette;
            let palette_3 = chart_mapper1.palette;
            let palette_4 = chart_mapper2.palette;
            palette_1[""" + str(idx) + """] = cb_obj.value;
            palette_2[""" + str(idx) + """] = cb_obj.value;
            palette_3[""" + str(idx) + """] = cb_obj.value;
            palette_4[""" + str(idx) + """] = cb_obj.value;
            legend_mapper.change.emit();
            bar_mapper.change.emit();
            chart_mapper1.change.emit();
            chart_mapper2.change.emit();
         """
    return cb


# Generates an input listener for dynamic coloring.
# Used for dynamic coloring of the heatmap density colors
# Param:
# idx - the idx in the mapper palette that the input listener is in charge of
# mapper - the repsective color mapper with the colors to change
# num - the total number of buttons
def _genColorButton(idx, mapper, num, placeholder=None):
    # Gives listeners in top-down order to match the order of the color bar
    cb = CustomJS(args=dict(mapper=mapper), code=_colorMapCB(num - 1 - idx))
    name = "Color " + str(idx + 1)
    if placeholder is not None:
        name = placeholder
    button = TextInput(callback=cb, placeholder=name)
    return button


def _genLabelColorButtons(idx, legend_mapper, bar_mapper, chart_mapper1, chart_mapper2, num, placeholder=None):
    cb = CustomJS(args=dict(legend_mapper=legend_mapper, bar_mapper=bar_mapper,
                            chart_mapper1=chart_mapper1, chart_mapper2=chart_mapper2),
                  code=_twoColorMapCB(idx))
    name = "Color " + str(idx + 1)
    if placeholder is not None:
        name = placeholder
    button = TextInput(callback=cb, placeholder=name)
    return button
