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
                              'measure'],
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
                         'm_data_table'],
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
                            'm_legend'],
               'subsel': ['source',
                          'subsel_source',
                          'subsel_chart']
               }

_js = dict(box_select="""
        var len = col.data['feature'].length; 
        var inds = [];   
        var inds_in_source = source.selected.indices;
        // sorts the indices found in source
        inds_in_source.sort(function(a, b){return a-b});
        var row_names = ptid.column_names;
        var col_names = measure.column_names;

        // Multiselect: combine array of old and new indices
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
            for (let i = 0; i < inds_arr.length; i++) {
                let dir = inds_arr[i];
                for (let j = 0; j < names.length - 1; j++) {
                    table.data[names[j]].push(src.data[names[j]][dir]);
                }
            }
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

           p_select="""
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
    """,
           m_select=""" 
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

    """,
           p_legend="""
        if (p_legend.selected.indices[0] == storage.data['p_legend_index'][0] && source.selected.indices.length != 0) {
            source.selected.indices = [];
            p_legend.selected.indices = [];
            // resetting p_table
            let p_col_names = p_table.column_names;
            for (i = 0; i < p_col_names.length; i++) {
                p_table.data[p_col_names[i]] = [];
            }
        }
        else {
            if (storage.data['intersect'][0]) {
                console.log("resetting...");
                m_legend.selected.indices = [];
                storage.data['intersect'][0] = 0;
            }
            storage.data['p_legend_index'] = p_legend.selected.indices;
            storage.data['m_legend_index'] = [];
            var index = p_legend.selected.indices;
            var names = p_legend.data['names'];
            var name = names[index];
            var reduced_inds = [];
            var colname = storage.data['p_colname'];
            var row_names = ptid.column_names;
            for (a = 0; a < row_names.length - 1; a++) {
                p_table.data[row_names[a]] = [];
            }
            for (i = 0; i < ptid.data[colname].length; i++) {
                if (ptid.data[colname][i] == name) {
                    reduced_inds.push(i);
                }
            }
            var len = col.data['feature'].length;
            var indices = reduced_inds.map(function(x) { return x * len; });
            var inds = [];
            for (i = 0; i < indices.length; i++) {
                var min_index = Math.floor(indices[i] / len) * len;
                var max_index = min_index + len;
                while (min_index < max_index) {
                    inds.push(min_index);
                    min_index++;
                }
            }
            let intersect = [];
            // If this is a filtering selection on a m_legend select
            if (m_legend.selected.indices.length != 0) {
                intersect = inds.filter(value => -1 !== source.selected.indices.indexOf(value));
                source.selected.indices = intersect;
                storage.data['intersect'][0] = 1;
            }
            else {
                source.selected.indices = inds;      
                storage.data['intersect'][0] = 0;
            }
            for (let j = 0; j < reduced_inds.length; j++) {
                let col = reduced_inds[j];
                for (let k = 0; k < row_names.length - 1; k++) {
                    p_table.data[row_names[k]].push(ptid.data[row_names[k]][col]);
                }
            }
        }
        console.log(storage.data['intersect'][0]);
        source.change.emit();
        p_legend.change.emit();
        p_table.change.emit();
        p_data_table.change.emit();
        m_legend.change.emit();
    """,
           m_legend="""
        if (m_legend.selected.indices[0] == storage.data['m_legend_index'][0] && source.selected.indices.length != 0) {
            source.selected.indices = [];
            m_legend.selected.indices = [];
            let m_col_names = m_table.column_names;
            for (let i = 0; i < m_col_names.length; i++) {
                m_table.data[m_col_names[i]] = [];
            }
        }
        else {
            if (storage.data['intersect'][0]) {
                console.log("resetting...");
                p_legend.selected.indices = [];
                storage.data['intersect'][0] = 0;
            }
            storage.data['m_legend_index'] = m_legend.selected.indices;
            storage.data['p_legend_index'] = [];
            let index = m_legend.selected.indices;
            let names = m_legend.data['names'];
            let name = names[index];
            let reduced_inds = [];
            let inds = [];
            let col_names = measure.column_names;
            for (let b = 0; b < col_names.length - 1; b++) {
                m_table.data[col_names[b]] = [];
            }
            // Getting min indices for selected column_names
            let colname = storage.data['m_colname'];
            for (let i = 0; i < measure.data[colname].length; i++) {
                if (measure.data[colname][i] == name) {
                 reduced_inds.push(i);
                }
            }
            // Selecting the entire column from each column's min index
            let len = col.data['feature'].length;
            let selected_inds = reduced_inds.slice();
            for (let i = 0; i < selected_inds.length; i++) {
                while (selected_inds[i] < source.data['Feature'].length) {
                    inds.push(selected_inds[i]);
                    selected_inds[i] += len;
                }
            }
            let intersect = [];
            // If this is a filtering selection on a p_legend select
            if (p_legend.selected.indices.length != 0) {
                intersect = inds.filter(value => -1 !== source.selected.indices.indexOf(value));
                source.selected.indices = intersect;
                storage.data['intersect'][0] = 1;
            }
            else {
                source.selected.indices = inds;      
                storage.data['intersect'][0] = 0;
            }
            for (let j = 0; j < reduced_inds.length; j++) {
                let col = reduced_inds[j];
                for (let k = 0; k < col_names.length - 1; k++) {
                    m_table.data[col_names[k]].push(measure.data[col_names[k]][col]);
                }
            }
        }
        console.log(storage.data['intersect'][0]);
        m_legend.change.emit();
        m_table.change.emit();
        m_data_table.change.emit();
        source.change.emit();
        p_legend.change.emit();
    """,
           subsel="""
        let inds = source.selected.indices;
        console.log(inds);
        for (let i = 0; i < inds.length; i++) {
            subsel_source.data['features'].push(source.data['Feature'][[i]]);
            subsel_source.data['ptids'].push(source.data['PtID'][[i]]);
            subsel_source.data['rate'].push(source.data['rate'][[i]]);
        }
        subsel_source.change.emit();
        subsel_chart.x_range.factors = subsel_source['features'];
        subsel_chart.y_range.factors = subsel_source.data['ptids'];
    """)
