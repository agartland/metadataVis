# FIX SORTING IN DATA TABLE
from bokeh.models import CustomJS
from metaVis import *

__all__ = ['initCallbacks']


def initCallbacks(sources):
    """Initialize all the CustomJS callbacks

    Parameter
    ---------
    sources : dict
        Contains all the bokeh.ColumnDataSources for the callbacks. Keys are
        names of the sources.

    Return
    ------
    out : dict
        Dictionary with keys for each callback."""

    cbDict = {}
    for srcKey, reqs in _reqSources.items():
        cbDict[srcKey] = CustomJS(args={srcName: sources[srcName] for srcName in reqs},
                       code=_js[srcKey])
    return cbDict

_reqSources = {'box_select': ['source',
                              'col',
                              'ptid',
                              'p_table',
                              'm_table',
                              'p_data_table',
                              'm_data_table',
                              'storage',
                              'p_legend',
                              'm_legend',
                              'measure',
                              'select_rowbar',
                              'nonselect_rowbar',
                              'select_colbar',
                              'nonselect_colbar'
                              ],
               'multiselect_toggle': ['source',
                                      'storage'
                                     ],
               'select_button': ['storage'
                                ],
               'reset': ['source',
                         'storage',
                         'p_legend',
                         'm_legend',
                         'p_table',
                         'm_table',
                         'p_data_table',
                         'm_data_table',
                         'select_rowbar',
                         'nonselect_rowbar',
                         'select_colbar',
                         'nonselect_colbar'],
               'row_reset': ['p_table',
                             'p_data_table'],
               'column_reset': ['m_table',
                             'm_data_table'],
               'p_select': ['source',
                            'p_legend',
                            'storage',
                            'ptid',
                            'nonselect_rowbar',
                            'row_xrange'],
               'm_select': ['source',
                            'm_legend',
                            'storage',
                            'measure',
                            'nonselect_colbar',
                            'col_xrange'],
               'p_legend': ['source',
                            'p_legend',
                            'storage',
                            'ptid',
                            'col',
                            'p_table',
                            'p_data_table',
                            'm_legend'],
               'm_legend': ['source',
                            'p_legend',
                            'storage',
                            'measure',
                            'col',
                            'm_table',
                            'm_data_table',
                            'm_legend']
               }

_js = dict(box_select="""
        var inds_in_source = source.selected['1d'].indices;
        // sorts the indices found in source
        inds_in_source.sort(function(a, b){return a-b});
        console.log(inds_in_source);
        var row_names = ptid.column_names;
        var col_names = measure.column_names;
        if (storage.data['multiselect'] == "True") {
            var inds_in_old_source = storage.data['indices'];
            inds_in_source = inds_in_source.filter(val => !inds_in_old_source.includes(val));
        }
        // Clearing Tables
        else {
            for (a = 0; a < row_names.length - 1; a++) {
                p_table.data[row_names[a]] = [];
            }
            for (b = 0; b < col_names.length - 1; b++) {
                m_table.data[col_names[b]] = [];
            }
        }
        
        var len = col.data['feature'].length; 

        var inds = [];

        // COLUMN MODE
        
        if (storage.data['mode'] == "Column") {
            var reduced_inds = [];
            var count = 0;
            var min_ind = inds_in_source[0]; 
            while (inds_in_source[count] + len > min_ind && inds_in_source[count] < min_ind + len) {
                reduced_inds.push(inds_in_source[count] % len);
                count++;
            }
            selected_inds = reduced_inds.slice();
            for ( j = 0; j < selected_inds.length; j++) {
                while (selected_inds[j] < source.data['Feature'].length) {
                    inds.push(selected_inds[j]);
                    selected_inds[j] += len;
                }
            }
            
            // Bar Chart
            var count_dict = {};
            for (i = 0; i < m_legend.data['names'].length; i++) {
                count_dict[m_legend.data['names'][i]] = 0;
            }
            var metacol_name = storage.data['m_colname'];
            var metacol = [];
            for (x = 0; x < reduced_inds.length; x++) {
             metacol.push(measure.data[metacol_name][reduced_inds[x]]);   
            }
            for (a = 0; a < metacol.length; a++) {
                var entry = metacol[a];
                count_dict[entry] = count_dict[entry] + 1;
            }
            count_list = [];
            for (var key in count_dict) {
                count_list.push(count_dict[key]);
            }
            var nonselect = [];
            select_colbar.data['y'] = count_list;
            console.log("total: ", storage.data['total_colbar']);
            for (z = 0; z < storage.data['total_colbar'].length; z++) {
                nonselect.push(storage.data['total_colbar'][z] - count_list[z]);
            }
            nonselect_colbar.data['y'] = nonselect;
            select_colbar.data['x'] = m_legend.data['names'];
            nonselect_colbar.data['x'] = m_legend.data['names'];
            
            //console.log("nonselect x: ", nonselect_colbar.data['x'], "select x: ", select_colbar.data['x']);
            //console.log("nonselect y: ", nonselect_colbar.data['y'], "select y: ", select_colbar.data['y']);

            // Adding to Feature table
            for (m = 0; m < reduced_inds.length; m++) {
                var col = reduced_inds[m];
                if (m_table.data[col_names[0]].includes(measure.data[col_names[0]][col])) {
                    var duplicate = true;   
                }
                for (n = 0; n < col_names.length - 1; n++) {
                    if (!duplicate) {
                        m_table.data[col_names[n]].push(measure.data[col_names[n]][col]);
                    }
                }
                duplicate = false;
            }
            console.log("M_Table: ", m_table.data);
            // Updating all sources/data tables
            if (storage.data['multiselect'] == 'True') {
                source.selected['1d'].indices = inds.concat(inds_in_old_source);
                storage.data['indices'] = inds.concat(inds_in_old_source);
                storage.change.emit();
            }
            else {
                source.selected['1d'].indices = inds;
            }
            nonselect_colbar.change.emit();
            select_colbar.change.emit();
            source.change.emit();
            p_table.change.emit();
            m_table.change.emit();
            p_data_table.change.emit();
            m_data_table.change.emit();
        }
        
        // CROSS MODE
        else if (storage.data['mode'] == "Cross") {
            // Selecting rows
            var row_reduced_inds = [];
            var count = 1;
            var i = 0
            var min_ind = inds_in_source[0]; 
            while (inds_in_source[i] == inds_in_source[i + 1] - 1) {
                i++;
                count++;
            }
            for (k = 0; k < inds_in_source.length; k+=count) {
                var min_index = Math.floor(inds_in_source[k] / len) * len;
                row_reduced_inds.push(min_index / len);
                var max_index = min_index + len;
                while (min_index < max_index) {
                    inds.push(min_index);
                    min_index++;
                }
            }
            // Selecting columns
            var col_reduced_inds = [];
            var count = 0;
            var min_ind = inds_in_source[0]; 
            while (inds_in_source[count] + len > min_ind && inds_in_source[count] < min_ind + len) {
                col_reduced_inds.push(inds_in_source[count] % len);
                count++;
            }
            selected_inds = col_reduced_inds.slice();
            for ( j = 0; j < selected_inds.length; j++) {
                while (selected_inds[j] < source.data['Feature'].length) {
                    inds.push(selected_inds[j]);
                    selected_inds[j] += len;
                }
            }
            
            // Ptid Bar Chart
            var row_count_dict = {};
            for (i = 0; i < p_legend.data['names'].length; i++) {
                row_count_dict[p_legend.data['names'][i]] = 0;
            }
            var row_metacol_name = storage.data['p_colname'];
            var row_metacol = [];
            for (x = 0; x < row_reduced_inds.length; x++) {
             row_metacol.push(ptid.data[row_metacol_name][row_reduced_inds[x]]);   
            }
            for (a = 0; a < row_metacol.length; a++) {
                var entry = row_metacol[a];
                row_count_dict[entry] = row_count_dict[entry] + 1;
            }
            row_count_list = [];
            for (var key in row_count_dict) {
                row_count_list.push(row_count_dict[key]);
            }            
            var row_nonselect = [];
            select_rowbar.data['y'] = row_count_list;
            for (z = 0; z < storage.data['total_rowbar'].length; z++) {
                row_nonselect.push(storage.data['total_rowbar'][z] - row_count_list[z]);
            }
            nonselect_rowbar.data['y'] = row_nonselect;
            select_rowbar.data['x'] = p_legend.data['names'];
            nonselect_rowbar.data['x'] = p_legend.data['names'];
            
            console.log("nonselect x: ", nonselect_rowbar.data['x'], "select x: ", select_rowbar.data['x']);
            console.log("nonselect y: ", nonselect_rowbar.data['y'], "select y: ", select_rowbar.data['y']);
            
            
            // Measure Bar Chart
            var col_count_dict = {};
            for (i = 0; i < m_legend.data['names'].length; i++) {
                col_count_dict[m_legend.data['names'][i]] = 0;
            }
            var col_metacol_name = storage.data['m_colname'];
            var col_metacol = [];
            for (x = 0; x < col_reduced_inds.length; x++) {
             col_metacol.push(measure.data[col_metacol_name][col_reduced_inds[x]]);   
            }
            for (a = 0; a < col_metacol.length; a++) {
                var entry = col_metacol[a];
                col_count_dict[entry] = col_count_dict[entry] + 1;
            }
            col_count_list = [];
            for (var key in col_count_dict) {
                col_count_list.push(col_count_dict[key]);
            }
            var col_nonselect = [];
            select_colbar.data['y'] = col_count_list;
            for (z = 0; z < storage.data['total_colbar'].length; z++) {
                col_nonselect.push(storage.data['total_colbar'][z] - col_count_list[z]);
            }
            nonselect_colbar.data['y'] = col_nonselect;
            select_colbar.data['x'] = m_legend.data['names'];
            nonselect_colbar.data['x'] = m_legend.data['names'];
            
            console.log("nonselect x: ", nonselect_colbar.data['x'], "select x: ", select_colbar.data['x']);
            console.log("nonselect y: ", nonselect_colbar.data['y'], "select y: ", select_colbar.data['y']);
            
            
            
            // Adding to PtID table
            for (g = 0; g < row_reduced_inds.length; g++) {
                var row = row_reduced_inds[g];
                if (p_table.data[row_names[0]].includes(ptid.data[row_names[0]][row])) {
                    var duplicate = true;   
                }
                for (h = 0; h < row_names.length - 1; h++) {
                    if (!duplicate) {
                    p_table.data[row_names[h]].push(ptid.data[row_names[h]][row]);
                    }
                }
                duplicate = false;
            }
            // Adding to Feature table
            for (m = 0; m < col_reduced_inds.length; m++) {
                var col = col_reduced_inds[m];
                if (m_table.data[col_names[0]].includes(measure.data[col_names[0]][col])) {
                    var duplicate = true;   
                }
                for (n = 0; n < col_names.length - 1; n++) {
                    if (!duplicate) {
                        m_table.data[col_names[n]].push(measure.data[col_names[n]][col]);
                    }
                }
                duplicate = false;
            }
            // Updating all sources/data tables
            if (storage.data['multiselect'] == 'True') {
                source.selected['1d'].indices = inds.concat(inds_in_old_source);
                storage.data['indices'] = inds.concat(inds_in_old_source);
                storage.change.emit();
            }
            else {
                source.selected['1d'].indices = inds;
            }
            nonselect_rowbar.change.emit();
            select_rowbar.change.emit();
            select_colbar.change.emit();
            nonselect_colbar.change.emit();
            source.change.emit();
            p_table.change.emit();
            p_data_table.change.emit();
            m_table.change.emit();
            m_data_table.change.emit();
        }


        // ROW MODE
        else {
            var reduced_inds = [];
            var count = 1;
            var i = 0;
            var min_ind = inds_in_source[0];
             while (inds_in_source[i] == inds_in_source[i + 1] - 1) {
                count++;
                i++;
            }
            for (k = 0; k < inds_in_source.length; k+=count) {
                var min_index = Math.floor(inds_in_source[k] / len) * len;
                reduced_inds.push(min_index / len);
                var max_index = min_index + len;
                while (min_index < max_index) {
                    inds.push(min_index);
                    min_index++;
                }
            }
            
            var count_dict = {};
            for (i = 0; i < p_legend.data['names'].length; i++) {
                count_dict[p_legend.data['names'][i]] = 0;
            }
            console.log("count_dict", count_dict);
            console.log("inds", reduced_inds);
            var metacol_name = storage.data['p_colname'];
            var metacol = [];
            for (x = 0; x < reduced_inds.length; x++) {
             metacol.push(ptid.data[metacol_name][reduced_inds[x]]);   
            }
            console.log("metacol", metacol);
            for (a = 0; a < metacol.length; a++) {
                var entry = metacol[a];
                count_dict[entry] = count_dict[entry] + 1;
            }
            count_list = [];
            for (var key in count_dict) {
                count_list.push(count_dict[key]);
            }            
            
            console.log("total", storage.data['total_rowbar']);
            var nonselect = [];
            select_rowbar.data['y'] = count_list;
            for (z = 0; z < storage.data['total_rowbar'].length; z++) {
                nonselect.push(storage.data['total_rowbar'][z] - count_list[z]);
            }
            nonselect_rowbar.data['y'] = nonselect;
            select_rowbar.data['x'] = p_legend.data['names'];
            nonselect_rowbar.data['x'] = p_legend.data['names'];
            
            console.log("nonselect x: ", nonselect_rowbar.data['x'], "select x: ", select_rowbar.data['x']);
            console.log("nonselect y: ", nonselect_rowbar.data['y'], "select y: ", select_rowbar.data['y']);
            
                        
            
            // Adding to PtID table
            for (g = 0; g < reduced_inds.length; g++) {
                var row = reduced_inds[g];
                if (p_table.data[row_names[0]].includes(ptid.data[row_names[0]][row])) {
                    var duplicate = true;   
                }
                for (h = 0; h < row_names.length - 1; h++) {
                    if (!duplicate) {
                    p_table.data[row_names[h]].push(ptid.data[row_names[h]][row]);
                    }
                }
                duplicate = false;
            }
            if (storage.data['multiselect'] == 'True') {
                source.selected['1d'].indices = inds.concat(inds_in_old_source);
                storage.data['indices'] = inds.concat(inds_in_old_source);
                storage.change.emit();
            }
            else {
                source.selected['1d'].indices = inds;
            }
            console.log("p_table test: ");
            console.log(p_table.data);
            nonselect_rowbar.change.emit();
            select_rowbar.change.emit();
            source.change.emit();
            p_table.change.emit();
            console.log(p_data_table);
            console.log(p_data_table.data);
            m_table.change.emit();
            m_data_table.change.emit();
        }
        
        p_legend.selected['1d'].indices = [];
        m_legend.selected['1d'].indices = [];
        p_legend.change.emit();
        m_legend.change.emit();
    """,
    multiselect_toggle = """
        var active = cb_obj.active;
        if (active.length == 1) {
            storage.data["multiselect"] = 'True';
            storage.data['indices'] = source.selected['1d'].indices;
            console.log(storage.data['indices']);
        }
        else {
            storage.data["multiselect"] = 'False';
            storage.data['indices'] = [];
            console.log(storage.data['indices']);
        }
        storage.change.emit();
    """,
    select_button = """
        storage.data['mode'] = cb_obj.value;
        storage.change.emit();
    """,

    reset = """
        storage.data['indices'] = [];
        source.selected['1d'].indices = [];
        p_legend.get('selected')['1d'].indices = [];
        m_legend.get('selected')['1d'].indices = [];
        p_col_names = p_table.column_names;
        for (i = 0; i < p_col_names.length; i++) {
            p_table.data[p_col_names[i]] = [];
        }
        m_col_names = m_table.column_names;
        for (i = 0; i < m_col_names.length; i++) {
            m_table.data[m_col_names[i]] = [];
        }
        console.log(storage.data['indices']);
        nonselect_rowbar.data['x'] = p_legend.data['names']
        nonselect_rowbar.data['y'] = storage.data['total_rowbar']
        nonselect_colbar.data['x'] = m_legend.data['names']
        nonselect_colbar.data['y'] = storage.data['total_colbar']
        select_rowbar.data['x'] = [];
        select_rowbar.data['y'] = [];
        select_colbar.data['x'] = [];
        select_colbar.data['y'] = [];
        source.change.emit();
        storage.change.emit();
        p_legend.change.emit();
        m_legend.change.emit();
        p_table.change.emit();
        p_data_table.change.emit();
        nonselect_rowbar.change.emit();
        nonselect_colbar.change.emit();
        select_rowbar.change.emit();
        select_colbar.change.emit();
        m_table.change.emit();
        m_data_table.change.emit();
    """,

    row_reset = """
        col_names = p_table.column_names;
        for (i = 0; i < col_names.length; i++) {
            p_table.data[col_names[i]] = [];
        }
        p_table.change.emit();
        p_data_table.change.emit();
    """,

    column_reset = """
        col_names = m_table.column_names;
        for (i = 0; i < col_names.length; i++) {
            m_table.data[col_names[i]] = [];
        }
        m_table.change.emit();
        m_data_table.change.emit();
    """,

    p_select = """
        var input = cb_obj.value;
        storage.data['p_colname'] = input;
        ptid.data['inspect'] = ptid.data[input];
        var factor_dict = {};
        var count = -1;
        var key_array = [];
        var freq = {};
        for (i = 0; i < ptid.data['inspect'].length; i++) {
            var entry = ptid.data['inspect'][i];
            if (!(factor_dict.hasOwnProperty(entry))) {
                count++;
                factor_dict[entry] = count;
                freq[entry] = 1
            }
            else {
                freq[entry] = freq[entry] + 1;
            }
            key_array.push(factor_dict[entry]);
        }
        freq_list = [];
        for (var key in freq) {
            freq_list.push(freq[key]);
        }            
        storage.data['total_rowbar'] = freq_list;
        ptid.data['inspect'] = key_array.map(String);
        p_legend.data['factors'] = [];
        p_legend.data['names'] = [];
        for (entry in factor_dict) {
            p_legend.data['names'].push(entry);
            p_legend.data['factors'].push(factor_dict[entry].toString());
        }
        nonselect_rowbar.data['x'] = p_legend.data['names'];
        nonselect_rowbar.data['y'] = storage.data['total_rowbar'];
        row_xrange.factors = p_legend.data['names'];
        p_legend.selected['1d'].indices = [];
        ptid.change.emit();
        p_legend.change.emit();
        storage.change.emit();
        nonselect_rowbar.change.emit();
        row_xrange.change.emit();
    """,
    m_select = """
        var input = cb_obj.value;
        storage.data['m_colname'] = input;
        measure.data['inspect'] = measure.data[input];
        var factor_dict = {};
        var count = -1;
        var freq = {};
        var key_array = [];
        for (i = 0; i < measure.data['inspect'].length; i++) {
            var entry = measure.data['inspect'][i];
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
        freq_list = [];
        for (var key in freq) {
            freq_list.push(freq[key]);
        }            
        storage.data['total_colbar'] = freq_list;        
        measure.data['inspect'] = key_array.map(String);
        m_legend.data['factors'] = [];
        m_legend.data['names'] = [];
        for (entry in factor_dict) {
            m_legend.data['names'].push(entry);
            m_legend.data['factors'].push(factor_dict[entry].toString());
        }
        nonselect_colbar.data['x'] = m_legend.data['names'];
        nonselect_colbar.data['y'] = storage.data['total_colbar'];
        col_xrange.factors = m_legend.data['names'];
        m_legend.selected['1d'].indices = [];
        measure.change.emit();
        m_legend.change.emit();
        storage.change.emit();
        col_xrange.change.emit();
    """,
    p_legend = """
        if (m_legend.selected['1d'].indices.length != 0) {
            m_legend.selected['1d'].indices = [];
            m_legend.change.emit();
        }
        if (p_legend.selected['1d'].indices[0] == storage.data['p_legend_index'][0] && source.selected['1d'].indices.length != 0) {
            console.log("double tap");
            source.selected['1d'].indices = [];
            p_legend.selected['1d'].indices = [];
            // resetting p_table
            p_col_names = p_table.column_names;
            for (i = 0; i < p_col_names.length; i++) {
                p_table.data[p_col_names[i]] = [];
            }
        }
        else {
            var index = p_legend.selected['1d'].indices;
            var names = p_legend.data['names'];
            var name = names[index];
            var selected_inds = [];
            var colname = storage.data['p_colname'];
            var row_names = ptid.column_names;
            for (a = 0; a < row_names.length - 1; a++) {
                p_table.data[row_names[a]] = [];
            }
            for (i = 0; i < ptid.data[colname].length; i++) {
                if (ptid.data[colname][i] == name) {
                    selected_inds.push(i);
                }
            }
            var len = col.data['feature'].length;
            var indices = selected_inds.map(function(x) { return x * len; });
            var inds = [];
            for (i = 0; i < indices.length; i++) {
                var min_index = Math.floor(indices[i] / len) * len;
                var max_index = min_index + len;
                while (min_index < max_index) {
                    inds.push(min_index);
                    min_index++;
                }
            }
            source.selected['1d'].indices = inds;
            var sorted_inds = source.selected['1d'].indices.sort(function(a, b) {return a-b});
            min_inds = [];
            for (i = 0; i < sorted_inds.length; i=i+len) {
                min_inds.push(sorted_inds[i]);
            }
            var row_array = [];
            for (j = 0; j < min_inds.length; j++) {
                row_array.push(Math.floor(min_inds[j] / len));
            }
            // Adding to PtID table
            for (k = 0; k < row_array.length; k++) {
                var row = row_array[k];
                var row_names = ptid.column_names;
                if (p_table.data[row_names[0]].includes(ptid.data[row_names[0]][row])) {
                    var duplicate = true;   
                }
                if (!duplicate) {
                    for (g = 0; g < row_names.length - 1; g++) {
                        p_table.data[row_names[g]].push(ptid.data[row_names[g]][row]);
                    }
                }
                duplicate = false;
            }
            storage.data['p_legend_index'] = p_legend.selected['1d'].indices;
            storage.data['m_legend_index'] = [];
        }
        // Fix indices selection
        source.change.emit();
        p_legend.change.emit();
        p_table.change.emit();
        p_data_table.change.emit();
    """,
    m_legend = """
        if (p_legend.selected['1d'].indices.length != 0) {
            p_legend.selected['1d'].indices = [];
            p_legend.change.emit();
        }
        if (m_legend.selected['1d'].indices[0] == storage.data['m_legend_index'][0] && source.selected['1d'].indices.length != 0) {
            source.selected['1d'].indices = [];
            m_legend.selected['1d'].indices = [];
            m_col_names = m_table.column_names;
            for (i = 0; i < m_col_names.length; i++) {
                m_table.data[m_col_names[i]] = [];
            }
        }
        else {
            var index = m_legend.selected['1d'].indices;
            var names = m_legend.data['names'];
            var name = names[index];
            var selected_inds = [];
            var col_names = measure.column_names;
            for (b = 0; b < col_names.length - 1; b++) {
                m_table.data[col_names[b]] = [];
            }
            var colname = storage.data['m_colname'];
            for (i = 0; i < measure.data[colname].length; i++) {
                if (measure.data[colname][i] == name) {
                    selected_inds.push(i);
                }
            }
            var len = col.data['feature'].length;
            var indices = selected_inds.map(function(x) { return x * len; });
            var inds = [];
            for (j = 0; j < indices.length; j++) {
                var min_index = indices[j] / len
                while (min_index < source.data['Feature'].length) {
                    inds.push(min_index);
                    min_index += len;
                }
            }
            source.selected['1d'].indices = inds;
            var sorted_inds = source.selected['1d'].indices.sort(function(a, b) {return a-b});
            min_inds = [];
            var i = 0;
            while (sorted_inds[i] < len) {
                min_inds.push(sorted_inds[i]);
                i++;
            }
            for (j = 0; j < min_inds.length; j++) {
                var col = min_inds[j];
                for (k = 0; k < col_names.length - 1; k++) {
                    m_table.data[col_names[k]].push(measure.data[col_names[k]][col]);
                }
            duplicate = false;
            }
            storage.data['m_legend_index'] = m_legend.selected['1d'].indices;
            storage.data['p_legend_index'] = [];
        }
        m_legend.change.emit();
        m_table.change.emit();
        m_data_table.change.emit();
        source.change.emit();
    """)