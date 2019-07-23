# FIX SORTING IN DATA TABLE
from bokeh.models import CustomJS, FactorRange
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
                              'selected_inds'],
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
                         'm_legend2',
                         'p_legend2'],
               'row_reset': ['p_table',
                             'p_data_table'],
               'column_reset': ['m_table',
                                'm_data_table'],
               'p_select': ['source',
                            'p_legend',
                            'storage',
                            'ptid',
                            'nonselect_rowbarchart',
                            'select_rowbarchart'],
               'm_select': ['source',
                            'm_legend',
                            'storage',
                            'measure',
                            'nonselect_colbarchart',
                            'select_colbarchart'],
               'p_legend': ['source',
                            'p_legend',
                            'm_legend',
                            'p_legend2',
                            'm_legend2',
                            'm_table',
                            'measure',
                            'storage',
                            'ptid',
                            'col',
                            'p_table',
                            'p_data_table'],
               'm_legend': ['source',
                            'p_legend',
                            'm_legend',
                            'p_legend2',
                            'm_legend2',
                            'ptid',
                            'storage',
                            'measure',
                            'col',
                            'm_table',
                            'm_data_table'],
               'p_legend2': ['source',
                             'p_legend',
                             'm_legend',
                             'm_legend2',
                             'p_legend2',
                             'storage',
                             'ptid',
                             'measure',
                             'col',
                             'p_table',
                             'p_data_table'],
               'm_legend2': ['source',
                             'p_legend',
                             'm_legend',
                             'p_legend2',
                             'm_legend2',
                             'storage',
                             'ptid',
                             'measure',
                             'col',
                             'm_table',
                             'm_data_table'],
               }

_js = dict(box_select="""
        var len = col.data['feature'].length; 
        var inds = [];   
        var inds_in_source = source.selected.indices;
        selected_inds.data['indices'] = source.selected.indices;
        // sorts the indices found in source
        inds_in_source.sort(function(a, b){return a-b});
        var row_names = ptid.column_names;
        var col_names = measure.column_names;
        
        console.log(storage.data['p_legend_index']);

        // Multiselect: combine array of old and new indices
        if (storage.data['multiselect'] == "True") {
            var inds_in_old_source = storage.data['indices'];
            inds_in_source = inds_in_source.filter(val => !inds_in_old_source.includes(val));
        }
        // Clearing Tables
        else {
            for (a = 0; a < row_names.length; a++) {
                p_table.data[row_names[a]] = [];
            }
            for (b = 0; b < col_names.length; b++) {
                m_table.data[col_names[b]] = [];
            }
        }

        // COLUMN MODE
        if (storage.data['mode'] == "Column") {
            let reduced_inds = col_select();
            gen_barchart(m_legend, "m_colname", "total_colbar", measure, reduced_inds);
            pop_table(reduced_inds, measure, m_table);
            reset_barchart(p_legend, "total_rowbar");
        }

        // CROSS MODE
        else if (storage.data['mode'] == "Cross") {
            let row_reduced_inds = row_select();
            let col_reduced_inds = col_select();
            gen_barchart(p_legend, "p_colname", "total_rowbar", ptid, row_reduced_inds);
            gen_barchart(m_legend, "m_colname", "total_colbar", measure, col_reduced_inds);
            pop_table(row_reduced_inds, ptid, p_table);
            pop_table(col_reduced_inds, measure, m_table);
        }

        // ROW MODE
        else {
            let reduced_inds = row_select();
            gen_barchart(p_legend, "p_colname", "total_rowbar", ptid, reduced_inds);
            pop_table(reduced_inds, ptid, p_table);
            reset_barchart( m_legend, "total_colbar");
        }

        // Updating sources and emitting changes
        if (storage.data['multiselect'] == 'True') {
            source.selected.indices = inds.concat(inds_in_old_source);
            storage.data['indices'] = inds.concat(inds_in_old_source);
            storage.change.emit();
        }
        else {
            source.selected.indices = inds;
            source.change.emit();
        }
        p_legend.selected.indices = [];
        m_legend.selected.indices = [];
        source.change.emit();
        p_table.change.emit();
        p_data_table.change.emit();
        m_table.change.emit();
        m_data_table.change.emit();
        p_legend.change.emit();
        m_legend.change.emit();


// #######################################    HELPER FUNCTIONS    #####################################################
        // Populates the data table of the corresponding selection type and area selected. 
        // @param {array} inds_arr - array of minimum indices for each row
        // @param {CDS} src - metadata source (ptid/measure)
        // @param {BK model} table - BK model of datatable to be populated 
        function pop_table(inds_arr, src, table) {
            let names = src.column_names;

            console.log(names);
            for (let i = 0; i < inds_arr.length; i++) {
                let dir = inds_arr[i];
                for (let j = 0; j < names.length; j++) {
                    table.data[names[j]].push(src.data[names[j]][dir]);
                }
            }
            console.log(table.data);
            //for (let j = 0; j < names.length; j++) {
             //   console.log(names[j]+":");
            //    console.log(table.data[names[j]]);
            //}
        }

        // Function to perform a grouped select on rows selected
        // @return {array} output_array - array containing the minimum indices of the selected rows, 
        //                                to be used in further functionality. 
        function row_select() {
            let output_arr = [];
            let count = 1;
            let i = 0;
            let min_ind = inds_in_source[0];
            while (inds_in_source[i] == inds_in_source[i + 1] - 1) {
                count++;
                i++;
            }
            for (let j = 0; j < inds_in_source.length; j+=count) {
                var min_index = Math.floor(inds_in_source[j] / len) * len;
                output_arr.push(min_index / len);
                let max_index = min_index + len;
                while (min_index < max_index) {
                    inds.push(min_index);
                    min_index++;
                }
            }
            return output_arr;
        }

        // Function to perform a grouped select on columns selected
        // @return {array} output_array - array containing the minimum indices of the selected columns, 
        //                                to be used in further functionality. 
        function col_select() {
            let output_arr = [];
            let count = 0;
            let min_ind = inds_in_source[0]; 
            while (inds_in_source[count] + len > min_ind && inds_in_source[count] < min_ind + len) {
                output_arr.push(inds_in_source[count] % len);
                count++;
            }
            let selected_inds = output_arr.slice();
            for (let i = 0; i < selected_inds.length; i++) {
                while (selected_inds[i] < source.data['Feature'].length) {
                    inds.push(selected_inds[i]);
                    selected_inds[i] += len;
                }
            }
            return output_arr;
        }

        // Generates corresponding barchart
        // @param {BK model} legend - legend to reference when creating the barchart
        // @param {String} colname - metadata column name
        // @param {String} total - reference string to get total counts of respective bar
        // @param {CDS} meta_source - metadata source
        // @param {array} inds_arr - array of min inds of row/column
        function gen_barchart(legend, colname, total, meta_source, inds_arr) {
            let count_dict = {};
            // Resetting former sources
            for (let i = 0; i < legend.data['names'].length; i++) {
              count_dict[legend.data['names'][i]] = 0;
            }
            let metacol_name = storage.data[colname];
            let metacol = [];
            // count array of metadata columns
            for (let j = 0; j < inds_arr.length; j++) {
            metacol.push(meta_source.data[metacol_name][inds_arr[j]]);   
            }
            // dictionary of number of appearances for each column 
            for (let k = 0; k < metacol.length; k++) {
              let entry = metacol[k];
              count_dict[entry] = count_dict[entry] + 1;
            }
            let count_list = [];
            // converting dictionary of counts into a list of counts
            for (var key in count_dict) {
              count_list.push(count_dict[key]);
            }
            let nonselect_arr = [];
            legend.data['sel_count'] = count_list;
            // finding inverse of counts for selected, using it as basis for nonselect
            for (let ii = 0; ii < storage.data[total].length; ii++) {
              nonselect_arr.push(storage.data[total][ii] - count_list[ii]);
            }
            legend.data['nonsel_count'] = nonselect_arr;
        }   

        // Function to reset barcharts to their original state (no selections)
        // @param {CDS} legend - CDS containing label reference info (m_legend/p_legend)
        // @param {total} total - reference string to get total counts of respective bar
        function reset_barchart(legend, total) {
            legend.data['nonsel_count'] = storage.data[total];
            legend.data['sel_count'] = new Array(storage.data[total].length).fill(0);
        }
    """,
           multiselect_toggle="""
        var active = cb_obj.active;
        if (active.length == 1) {
            storage.data["multiselect"] = 'True';
            storage.data['indices'] = source.selected.indices;
        }
        else {
            storage.data["multiselect"] = 'False';
            storage.data['indices'] = [];
        }
        storage.change.emit();
    """,
           select_button="""
        storage.data['mode'] = cb_obj.value;
        storage.change.emit();
    """,

           reset="""
        storage.data['indices'] = [];
        source.selected.indices = [];
        p_legend.selected.indices = [];
        m_legend.selected.indices = [];
        p_legend2.selected.indices = [];
        m_legend2.selected.indices = [];
        p_col_names = p_table.column_names;
        for (i = 0; i < p_col_names.length; i++) {
            p_table.data[p_col_names[i]] = [];
        }
        m_col_names = m_table.column_names;
        for (i = 0; i < m_col_names.length; i++) {
            m_table.data[m_col_names[i]] = [];
        }
        m_legend.data['nonsel_count'] = storage.data['total_colbar']
        p_legend.data['nonsel_count'] = storage.data['total_rowbar']
        p_legend.data['sel_count'] = new Array(storage.data['total_rowbar'].length).fill(0);
        m_legend.data['sel_count'] = new Array(storage.data['total_colbar'].length).fill(0);
        source.change.emit();
        storage.change.emit();
        p_legend.change.emit();
        m_legend.change.emit();
        p_legend2.change.emit();
        m_legend2.change.emit();
        p_table.change.emit();
        p_data_table.change.emit();
        m_table.change.emit();
        m_data_table.change.emit();
    """,

           row_reset="""
        col_names = p_table.column_names;
        for (i = 0; i < col_names.length; i++) {
            p_table.data[col_names[i]] = [];
        }
        p_table.change.emit();
        p_data_table.change.emit();
    """,

           column_reset="""
        let col_names = m_table.column_names;
        for (i = 0; i < col_names.length; i++) {
            m_table.data[col_names[i]] = [];
        }
        m_table.change.emit();
        m_data_table.change.emit();
    """,

## OUT OF USE CHECK PLOTTING FOR NEW CALLBACK!!!
           p_select="""
        let input = cb_obj.value;
        console.log("helppp");
        alert("asdf");        
        console.log(document.querySelector("#p_leg_label b").innerText);
        document.querySelector("#y_leg_label b").innerText = "Row Legend: " + input;
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
        p_legend.change.emit();
        p_legend.data['nonsel_count'] = storage.data['total_rowbar'];
        p_legend.selected.indices = [];
        p_legend.change.emit();
        nonselect_rowbarchart.x_range.factors = p_legend.data['names'];
        select_rowbarchart.x_range.factors = p_legend.data['names'];
    """,

## OUT OF USE CHECK PLOTTING FOR NEW CALLBACK!!!
           m_select=""" 
        let input = cb_obj.value;
        console.log(document.querySelector("#x_leg_label b").innerText);
        document.querySelector("#x_leg_label b").innerText = "Column Legend: " + input;
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

    """,
        p_legend="""
        console.log("here");
        console.log(storage.data['p_legend_index']);
        console.log(p_legend.selected.indices[0]);
        
        let p_colname = storage.data['p_colname'];
        let p_colname2 = storage.data['p_colname2'];
        let m_colname = storage.data['m_colname'];
        let m_colname2 = storage.data['m_colname2'];
        let row_reduced_inds = [];
        let total_inds = [];
        let p_dict = {};
        p_dict[p_colname] = p_legend.selected.indices;
        p_dict[p_colname2] = p_legend2.selected.indices;
        let m_dict = {};
        m_dict[m_colname] = m_legend.selected.indices;
        m_dict[m_colname2] = m_legend2.selected.indices;
        let row_inds = [];
        let col_inds = [];
        if (p_legend.selected.indices[0] === storage.data['p_legend_index'][0]) {
            console.log("resetting...");
            p_legend.selected.indices = [];
            storage.data['p_legend_index'] = [];
            p_dict[p_colname] = [];
        }
        console.log("dicts");
        console.log(p_dict)
        console.log(m_dict)
        let is_row = false;
        let is_col = false;
        // If user is toggling same selection
        let p_keys = Object.keys(p_dict);
        if (p_dict[p_keys[0]].length > 0 || p_dict[p_keys[1]].length > 0) {
            is_row = true;
            storage.data['p_legend_index'] = p_legend.selected.indices;
            var row_names = ptid.column_names;
            if (row_names.indexOf("inspect") == -1 ) {
                row_names.push('inspect');
            }            
            for (a = 0; a < row_names.length; a++) {
                p_table.data[row_names[a]] = [];
            }
            // If 2 row filters active
            if (p_dict[p_keys[0]].length > 0 && p_dict[p_keys[1]].length > 0) {
                row_name = p_legend.data['names'][p_legend.selected.indices];
                row_name2 = p_legend2.data['names'][p_legend2.selected.indices];
                for (i = 0; i < ptid.data[p_colname].length; i++) {
                    if (ptid.data[p_colname][i] == row_name && ptid.data[p_colname2][i] == row_name2) {
                        row_reduced_inds.push(i);
                    }
                }
            }
            else {
                let keys = Object.keys(p_dict);
                let p_col = keys[0]
                let row_name = p_legend.data['names'][p_dict[p_col]];
                if (p_dict[p_keys[1]].length > 0) {
                    p_col = keys[1]; 
                    row_name =  p_legend2.data['names'][p_dict[p_col]];
                }
                console.log(p_col);
                for (i = 0; i < ptid.data[p_colname].length; i++) {
                    console.log(ptid.data[p_col][i])
                    console.log(p_legend.data['names'][p_dict[p_col]]);
                    if (ptid.data[p_col][i] == row_name) {
                        row_reduced_inds.push(i);
                    }
                }
            }
            console.log("row reduced inds");
            console.log(row_reduced_inds)
            var len = col.data['feature'].length;
            var indices = row_reduced_inds.map(function(x) { return x * len; });
            for (let i = 0; i < indices.length; i++) {
                var min_index = Math.floor(indices[i] / len) * len;
                var max_index = min_index + len;
                while (min_index < max_index) {
                    row_inds.push(min_index);
                    min_index++;
                }
            }
        }
        console.log("row inds")
        console.log(row_inds);
        let m_keys = Object.keys(m_dict);
        console.log(m_dict);
        if (m_dict[m_keys[0]].length > 0 || m_dict[m_keys[1]].length > 0) {
            is_col = true;
            var col_reduced_inds = [];
            storage.data['col_legend_index'] = m_legend.selected.indices;
            var col_names = measure.column_names;
            if (col_names.indexOf("inspect") == -1 ) {
                col_names.push('inspect');
            }            
            // If 2 row filters active
            if (m_dict[m_keys[0]].length > 0 && m_dict[m_keys[1]].length > 0) {
                console.log("2 row filters")
                col_name = m_legend.data['names'][m_legend.selected.indices];
                col_name2 = m_legend2.data['names'][m_legend2.selected.indices];
                for (let j = 0; j < measure.data[m_colname].length; j++) {
                    if (measure.data[m_colname][j] == col_name && measure.data[m_colname2][j] == col_name2) {
                        col_reduced_inds.push(j);
                    }
                }
            }
            else {
                let col_keys = Object.keys(m_dict);
                let m_col = col_keys[0]
                let col_name = m_legend.data['names'][m_dict[m_col]];
                    if (m_dict[m_keys[1]].length > 0) {
                        m_col = col_keys[1];
                        col_name = m_legend2.data['names'][m_dict[m_col]]; 
                    }
                    for (let k = 0; k < measure.data[m_colname].length; k++) {
                        if (measure.data[m_col][k] ==  col_name) {
                            col_reduced_inds.push(k);
                            console.log("pushing col ind");
                        }
                    }
                }
                console.log(col_reduced_inds);
            let len = col.data['feature'].length;
            let col_selected_inds = col_reduced_inds.slice();
            for (let i = 0; i < col_selected_inds.length; i++) {
                while (col_selected_inds[i] < source.data['Feature'].length) {
                    col_inds.push(col_selected_inds[i]);
                    col_selected_inds[i] += len;
                }
            }  
        }
        console.log("col_inds")
        console.log(col_inds)
        if (is_col && is_row) {
            console.log("both col and row filters, total inds:")
            console.log(row_inds)
            console.log(col_inds);
            total_inds = col_inds.filter(value => row_inds.includes(value));
            console.log(total_inds);
        }
        else {
            total_inds = row_inds.concat(col_inds);
        }
        console.log(col_inds);
        source.selected.indices = total_inds;
        console.log(source.selected.indices);
        source.change.emit();
        for (let j = 0; j < row_reduced_inds.length; j++) {
            let col = row_reduced_inds[j];
            for (let k = 0; k < row_names.length; k++) {
                p_table.data[row_names[k]].push(ptid.data[row_names[k]][col]);
            }
        }
        console.log(p_table.data);
        source.change.emit();
        console.log("final source")
        console.log(source.selected.indices);
        p_legend.change.emit();
        p_table.change.emit();
        p_data_table.change.emit();
        m_legend.change.emit();
    """,
           m_legend="""
        console.log("here");
        console.log(storage.data['m_legend_index']);
        console.log(m_legend.selected.indices[0]);
        
        let p_colname = storage.data['p_colname'];
        let p_colname2 = storage.data['p_colname2'];
        let m_colname = storage.data['m_colname'];
        let m_colname2 = storage.data['m_colname2'];
        let row_reduced_inds = [];
        let total_inds = [];
        let p_dict = {};
        p_dict[p_colname] = p_legend.selected.indices;
        p_dict[p_colname2] = p_legend2.selected.indices;
        let m_dict = {};
        m_dict[m_colname] = m_legend.selected.indices;
        m_dict[m_colname2] = m_legend2.selected.indices;
        let row_inds = [];
        let col_inds = [];
        if (m_legend.selected.indices[0] === storage.data['m_legend_index'][0]) {
            console.log("resetting...");
            m_legend.selected.indices = [];
            storage.data['m_legend_index'] = [];
            m_dict[m_colname] = [];
        }
        console.log("dicts");
        console.log(p_dict)
        console.log(m_dict)
        let is_row = false;
        let is_col = false;
        // If user is toggling same selection
        let p_keys = Object.keys(p_dict);
        if (p_dict[p_keys[0]].length > 0 || p_dict[p_keys[1]].length > 0) {
            is_row = true;
            var col_names = measure.column_names;
            if (col_names.indexOf("inspect") == -1 ) {
                col_names.push('inspect');
            }            
            // If 2 row filters active
            if (p_dict[p_keys[0]].length > 0 && p_dict[p_keys[1]].length > 0) {
                row_name = p_legend.data['names'][p_legend.selected.indices];
                row_name2 = p_legend2.data['names'][p_legend2.selected.indices];
                for (i = 0; i < ptid.data[p_colname].length; i++) {
                    if (ptid.data[p_colname][i] == row_name && ptid.data[p_colname2][i] == row_name2) {
                        row_reduced_inds.push(i);
                    }
                }
            }
            else {
                let keys = Object.keys(p_dict);
                let p_col = keys[0]
                let row_name = p_legend.data['names'][p_dict[p_col]];
                if (p_dict[p_keys[1]].length > 0) {
                    p_col = keys[1]; 
                    row_name =  p_legend2.data['names'][p_dict[p_col]];
                }
                console.log(p_col);
                for (i = 0; i < ptid.data[p_colname].length; i++) {
                    console.log(ptid.data[p_col][i])
                    console.log(p_legend.data['names'][p_dict[p_col]]);
                    if (ptid.data[p_col][i] == row_name) {
                        row_reduced_inds.push(i);
                    }
                }
            }
            console.log("row reduced inds");
            console.log(row_reduced_inds)
            var len = col.data['feature'].length;
            var indices = row_reduced_inds.map(function(x) { return x * len; });
            for (let i = 0; i < indices.length; i++) {
                var min_index = Math.floor(indices[i] / len) * len;
                var max_index = min_index + len;
                while (min_index < max_index) {
                    row_inds.push(min_index);
                    min_index++;
                }
            }
        }
        console.log("row inds")
        console.log(row_inds);
        let m_keys = Object.keys(m_dict);
        console.log(m_dict);
        if (m_dict[m_keys[0]].length > 0 || m_dict[m_keys[1]].length > 0) {
            storage.data['m_legend_index'] = m_legend.selected.indices;
            is_col = true;
            var col_reduced_inds = [];
            storage.data['col_legend_index'] = m_legend.selected.indices;
            var col_names = measure.column_names;
            if (col_names.indexOf("inspect") == -1 ) {
                col_names.push('inspect');
            }            
            // If 2 row filters active
            if (m_dict[m_keys[0]].length > 0 && m_dict[m_keys[1]].length > 0) {
                console.log("2 row filters")
                col_name = m_legend.data['names'][m_legend.selected.indices];
                col_name2 = m_legend2.data['names'][m_legend2.selected.indices];
                for (let j = 0; j < measure.data[m_colname].length; j++) {
                    if (measure.data[m_colname][j] == col_name && measure.data[m_colname2][j] == col_name2) {
                        col_reduced_inds.push(j);
                    }
                }
            }
            else {
                let col_keys = Object.keys(m_dict);
                let m_col = col_keys[0]
                let col_name = m_legend.data['names'][m_dict[m_col]];
                    if (m_dict[m_keys[1]].length > 0) {
                        m_col = col_keys[1];
                        col_name = m_legend2.data['names'][m_dict[m_col]]; 
                    }
                    for (let k = 0; k < measure.data[m_colname].length; k++) {
                        if (measure.data[m_col][k] ==  col_name) {
                            col_reduced_inds.push(k);
                            console.log("pushing col ind");
                        }
                    }
                }
                console.log(col_reduced_inds);
            let len = col.data['feature'].length;
            let col_selected_inds = col_reduced_inds.slice();
            for (let i = 0; i < col_selected_inds.length; i++) {
                while (col_selected_inds[i] < source.data['Feature'].length) {
                    col_inds.push(col_selected_inds[i]);
                    col_selected_inds[i] += len;
                }
            }  
        }
        console.log("col_inds")
        console.log(col_inds)
        if (is_col && is_row) {
            console.log("both col and row filters, total inds:")
            console.log(row_inds)
            console.log(col_inds);
            total_inds = col_inds.filter(value => row_inds.includes(value));
            console.log(total_inds);
        }
        else {
            total_inds = row_inds.concat(col_inds);
        }
        console.log(col_inds);
        source.selected.indices = total_inds;
        console.log(source.selected.indices);
        source.change.emit();
        for (let j = 0; j < col_reduced_inds.length; j++) {
            let col = col_reduced_inds[j];
            for (let k = 0; k < col_names.length; k++) {
                m_table.data[col_names[k]].push(measure.data[col_names[k]][col]);
            }
        }
        console.log(m_table.data);
        source.change.emit();
        console.log("final source")
        console.log(source.selected.indices);
        m_legend.change.emit();
        m_table.change.emit();
        m_data_table.change.emit();
    """,

        p_legend2 = """
        console.log("here");
        console.log(storage.data['p_legend_index']);
        console.log(p_legend.selected.indices[0]);
        
        let p_colname = storage.data['p_colname'];
        let p_colname2 = storage.data['p_colname2'];
        let m_colname = storage.data['m_colname'];
        let m_colname2 = storage.data['m_colname2'];
        let row_reduced_inds = [];
        let total_inds = [];
        let p_dict = {};
        p_dict[p_colname] = p_legend.selected.indices;
        p_dict[p_colname2] = p_legend2.selected.indices;
        let m_dict = {};
        m_dict[m_colname] = m_legend.selected.indices;
        m_dict[m_colname2] = m_legend2.selected.indices;
        let row_inds = [];
        let col_inds = [];
        if (p_legend2.selected.indices[0] === storage.data['p_legend2_index'][0]) {
            console.log("resetting...");
            p_legend2.selected.indices = [];
            storage.data['p_legend2_index'] = [];
            p_dict[p_colname2] = [];
        }
        console.log("dicts");
        console.log(p_dict)
        console.log(m_dict)
        let is_row = false;
        let is_col = false;
        // If user is toggling same selection
        let p_keys = Object.keys(p_dict);
        if (p_dict[p_keys[0]].length > 0 || p_dict[p_keys[1]].length > 0) {
            is_row = true;
            storage.data['p_legend2_index'] = p_legend2.selected.indices;
            var row_names = ptid.column_names;
            if (row_names.indexOf("inspect") == -1 ) {
                row_names.push('inspect');
            }            
            for (a = 0; a < row_names.length; a++) {
                p_table.data[row_names[a]] = [];
            }
            // If 2 row filters active
            if (p_dict[p_keys[0]].length > 0 && p_dict[p_keys[1]].length > 0) {
                row_name = p_legend.data['names'][p_legend.selected.indices];
                row_name2 = p_legend2.data['names'][p_legend2.selected.indices];
                for (i = 0; i < ptid.data[p_colname].length; i++) {
                    if (ptid.data[p_colname][i] == row_name && ptid.data[p_colname2][i] == row_name2) {
                        row_reduced_inds.push(i);
                    }
                }
            }
            else {
                let keys = Object.keys(p_dict);
                let p_col = keys[0]
                let row_name = p_legend.data['names'][p_dict[p_col]];
                if (p_dict[p_keys[1]].length > 0) {
                    p_col = keys[1]; 
                    row_name =  p_legend2.data['names'][p_dict[p_col]];
                }
                console.log(p_col);
                for (i = 0; i < ptid.data[p_colname].length; i++) {
                    console.log(ptid.data[p_col][i])
                    console.log(p_legend.data['names'][p_dict[p_col]]);
                    if (ptid.data[p_col][i] == row_name) {
                        row_reduced_inds.push(i);
                    }
                }
            }
            console.log("row reduced inds");
            console.log(row_reduced_inds)
            var len = col.data['feature'].length;
            var indices = row_reduced_inds.map(function(x) { return x * len; });
            for (let i = 0; i < indices.length; i++) {
                var min_index = Math.floor(indices[i] / len) * len;
                var max_index = min_index + len;
                while (min_index < max_index) {
                    row_inds.push(min_index);
                    min_index++;
                }
            }
        }
        console.log("row inds")
        console.log(row_inds);
        let m_keys = Object.keys(m_dict);
        console.log(m_dict);
        if (m_dict[m_keys[0]].length > 0 || m_dict[m_keys[1]].length > 0) {
            is_col = true;
            var col_reduced_inds = [];
            storage.data['col_legend_index'] = m_legend.selected.indices;
            var col_names = measure.column_names;
            if (col_names.indexOf("inspect") == -1 ) {
                col_names.push('inspect');
            }            
            // If 2 row filters active
            if (m_dict[m_keys[0]].length > 0 && m_dict[m_keys[1]].length > 0) {
                console.log("2 row filters")
                col_name = m_legend.data['names'][m_legend.selected.indices];
                col_name2 = m_legend2.data['names'][m_legend2.selected.indices];
                for (let j = 0; j < measure.data[m_colname].length; j++) {
                    if (measure.data[m_colname][j] == col_name && measure.data[m_colname2][j] == col_name2) {
                        col_reduced_inds.push(j);
                    }
                }
            }
            else {
                let col_keys = Object.keys(m_dict);
                let m_col = col_keys[0]
                let col_name = m_legend.data['names'][m_dict[m_col]];
                    if (m_dict[m_keys[1]].length > 0) {
                        m_col = col_keys[1];
                        col_name = m_legend2.data['names'][m_dict[m_col]]; 
                    }
                    for (let k = 0; k < measure.data[m_colname].length; k++) {
                        if (measure.data[m_col][k] ==  col_name) {
                            col_reduced_inds.push(k);
                            console.log("pushing col ind");
                        }
                    }
                }
                console.log(col_reduced_inds);
            let len = col.data['feature'].length;
            let col_selected_inds = col_reduced_inds.slice();
            for (let i = 0; i < col_selected_inds.length; i++) {
                while (col_selected_inds[i] < source.data['Feature'].length) {
                    col_inds.push(col_selected_inds[i]);
                    col_selected_inds[i] += len;
                }
            }  
        }
        console.log("col_inds")
        console.log(col_inds)
        if (is_col && is_row) {
            console.log("both col and row filters, total inds:")
            console.log(row_inds)
            console.log(col_inds);
            total_inds = col_inds.filter(value => row_inds.includes(value));
            console.log(total_inds);
        }
        else {
            total_inds = row_inds.concat(col_inds);
        }
        console.log(col_inds);
        source.selected.indices = total_inds;
        console.log(source.selected.indices);
        source.change.emit();
        for (let j = 0; j < row_reduced_inds.length; j++) {
            let col = row_reduced_inds[j];
            for (let k = 0; k < row_names.length; k++) {
                p_table.data[row_names[k]].push(ptid.data[row_names[k]][col]);
            }
        }
        console.log(p_table.data);
        source.change.emit();
        console.log("final source")
        console.log(source.selected.indices);
        p_legend2.change.emit();
        p_table.change.emit();
        p_data_table.change.emit();
        m_table.change.emit();
        """,
        m_legend2 = """
            console.log("here");
            console.log(storage.data['m_legend_index']);
            console.log(m_legend.selected.indices[0]);
            
            let p_colname = storage.data['p_colname'];
            let p_colname2 = storage.data['p_colname2'];
            let m_colname = storage.data['m_colname'];
            let m_colname2 = storage.data['m_colname2'];
            let row_reduced_inds = [];
            let total_inds = [];
            let p_dict = {};
            p_dict[p_colname] = p_legend.selected.indices;
            p_dict[p_colname2] = p_legend2.selected.indices;
            let m_dict = {};
            m_dict[m_colname] = m_legend.selected.indices;
            m_dict[m_colname2] = m_legend2.selected.indices;
            let row_inds = [];
            let col_inds = [];
            if (m_legend2.selected.indices[0] === storage.data['m_legend2_index'][0]) {
                console.log("resetting...");
                m_legend2.selected.indices = [];
                storage.data['m_legend_index2'] = [];
                m_dict[m_colname2] = [];
            }
            console.log("dicts");
            console.log(p_dict)
            console.log(m_dict)
            let is_row = false;
            let is_col = false;
            // If user is toggling same selection
            let p_keys = Object.keys(p_dict);
            if (p_dict[p_keys[0]].length > 0 || p_dict[p_keys[1]].length > 0) {
                is_row = true;
                var col_names = measure.column_names;
                if (col_names.indexOf("inspect") == -1 ) {
                    col_names.push('inspect');
                }            
                for (a = 0; a < col_names.length; a++) {
                    m_table.data[col_names[a]] = [];
                }
                // If 2 row filters active
                if (p_dict[p_keys[0]].length > 0 && p_dict[p_keys[1]].length > 0) {
                    row_name = p_legend.data['names'][p_legend.selected.indices];
                    row_name2 = p_legend2.data['names'][p_legend2.selected.indices];
                    for (i = 0; i < ptid.data[p_colname].length; i++) {
                        if (ptid.data[p_colname][i] == row_name && ptid.data[p_colname2][i] == row_name2) {
                            row_reduced_inds.push(i);
                        }
                    }
                }
                else {
                    let keys = Object.keys(p_dict);
                    let p_col = keys[0]
                    let row_name = p_legend.data['names'][p_dict[p_col]];
                    if (p_dict[p_keys[1]].length > 0) {
                        p_col = keys[1]; 
                        row_name =  p_legend2.data['names'][p_dict[p_col]];
                    }
                    console.log(p_col);
                    for (i = 0; i < ptid.data[p_colname].length; i++) {
                        console.log(ptid.data[p_col][i])
                        console.log(p_legend.data['names'][p_dict[p_col]]);
                        if (ptid.data[p_col][i] == row_name) {
                            row_reduced_inds.push(i);
                        }
                    }
                }
                console.log("row reduced inds");
                console.log(row_reduced_inds)
                var len = col.data['feature'].length;
                var indices = row_reduced_inds.map(function(x) { return x * len; });
                for (let i = 0; i < indices.length; i++) {
                    var min_index = Math.floor(indices[i] / len) * len;
                    var max_index = min_index + len;
                    while (min_index < max_index) {
                        row_inds.push(min_index);
                        min_index++;
                    }
                }
            }
            console.log("row inds")
            console.log(row_inds);
            let m_keys = Object.keys(m_dict);
            console.log(m_dict);
            if (m_dict[m_keys[0]].length > 0 || m_dict[m_keys[1]].length > 0) {
                storage.data['m_legend_index'] = m_legend.selected.indices;
                is_col = true;
                var col_reduced_inds = [];
                storage.data['col_legend_index'] = m_legend.selected.indices;
                var col_names = measure.column_names;
                if (col_names.indexOf("inspect") == -1 ) {
                    col_names.push('inspect');
                }            
                for (let b = 0; b < col_names.length; b++) {
                    m_table.data[col_names[b]] = [];
                }
                // If 2 row filters active
                if (m_dict[m_keys[0]].length > 0 && m_dict[m_keys[1]].length > 0) {
                    console.log("2 row filters")
                    col_name = m_legend.data['names'][m_legend.selected.indices];
                    col_name2 = m_legend2.data['names'][m_legend2.selected.indices];
                    for (let j = 0; j < measure.data[m_colname].length; j++) {
                        if (measure.data[m_colname][j] == col_name && measure.data[m_colname2][j] == col_name2) {
                            col_reduced_inds.push(j);
                        }
                    }
                }
                else {
                    let col_keys = Object.keys(m_dict);
                    let m_col = col_keys[0]
                    let col_name = m_legend.data['names'][m_dict[m_col]];
                        if (m_dict[m_keys[1]].length > 0) {
                            m_col = col_keys[1];
                            col_name = m_legend2.data['names'][m_dict[m_col]]; 
                        }
                        for (let k = 0; k < measure.data[m_colname].length; k++) {
                            if (measure.data[m_col][k] ==  col_name) {
                                col_reduced_inds.push(k);
                                console.log("pushing col ind");
                            }
                        }
                    }
                    console.log(col_reduced_inds);
                let len = col.data['feature'].length;
                let col_selected_inds = col_reduced_inds.slice();
                for (let i = 0; i < col_selected_inds.length; i++) {
                    while (col_selected_inds[i] < source.data['Feature'].length) {
                        col_inds.push(col_selected_inds[i]);
                        col_selected_inds[i] += len;
                    }
                }  
            }
            console.log("col_inds")
            console.log(col_inds)
            if (is_col && is_row) {
                console.log("both col and row filters, total inds:")
                console.log(row_inds)
                console.log(col_inds);
                total_inds = col_inds.filter(value => row_inds.includes(value));
                console.log(total_inds);
            }
            else {
                total_inds = row_inds.concat(col_inds);
            }
            console.log(col_inds);
            source.selected.indices = total_inds;
            for (let j = 0; j < col_reduced_inds.length; j++) {
                let col = col_reduced_inds[j];
                for (let k = 0; k < col_names.length; k++) {
                    m_table.data[col_names[k]].push(measure.data[col_names[k]][col]);
                }
            }
            console.log(m_table.data);
            source.change.emit();
            console.log("final source")
            console.log(source.selected.indices);
            m_legend2.change.emit();
            m_table.change.emit();
            m_data_table.change.emit();
""")

