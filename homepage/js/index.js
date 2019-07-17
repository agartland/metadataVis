var colnames = {};
var data = [];
var indices = [];

$(document).ready(function() {
      if(isAPIAvailable()) {
        $('#lfFile').bind('change', handleFileSelect);
      }
      var file_input_index = 0;
        $('input[type=file]').each(function() {
            file_input_index++;
            $(this).wrap('<div style="display:flex;align-items:center" id="file_input_container_'+file_input_index+'"></div>');
            $(this).after('<span class="clear" onclick="reset_html(\'file_input_container_'+file_input_index+'\')"> X </span>');
        });
    });

    function isAPIAvailable() {
      // Check for the various File API support.
      if (window.File && window.FileReader && window.FileList && window.Blob) {
        // Great success! All the File APIs are supported.
        return true;
      } else {
        // source: File API availability - http://caniuse.com/#feat=fileapi
        // source: <output> availability - http://html5doctor.com/the-output-element/
        document.writeln('The HTML5 APIs used in this form are only available in the following browsers:<br />');
        // 6.0 File API & 13.0 <output>
        document.writeln(' - Google Chrome: 13.0 or later<br />');
        // 3.6 File API & 6.0 <output>
        document.writeln(' - Mozilla Firefox: 6.0 or later<br />');
        // 10.0 File API & 10.0 <output>
        document.writeln(' - Internet Explorer: Not supported (partial support expected in 10.0)<br />');
        // ? File API & 5.1 <output>
        document.writeln(' - Safari: Not supported<br />');
        // ? File API & 9.2 <output>
        document.writeln(' - Opera: Not supported');
        return false;
      }
    }

    function handleFileSelect(evt) {
      var files = evt.target.files; // FileList object
      var file = files[0];

      // read the file metadata
      var output = ''
          output += '<span style="font-weight:bold;">' + escape(file.name) + '</span><br />\n';
          output += ' - FileType: ' + (file.type || 'n/a') + '<br />\n';
          output += ' - FileSize: ' + file.size + ' bytes<br />\n';
          output += ' - LastModified: ' + (file.lastModifiedDate ? file.lastModifiedDate.toLocaleDateString() : 'n/a') + '<br />\n';

      // read the file contents
      processFile(file);
    }

    function processFile(file) {
      var reader = new FileReader();
      reader.readAsText(file);
      reader.onload = function(event){
        var csv = event.target.result;
        var arr = $.csv.toArrays(csv);
        colnames = {};
        document.getElementById('rowindex').innerHTML = '';
        document.getElementById('colindex').innerHTML = '';
        document.getElementById('row-modal-index').innerHTML = '';
        document.getElementById('col-modal-index').innerHTML = '';
        document.getElementById('value').innerHTML = '';
        document.getElementById('value-modal').innerHTML = '';
        indices = [];
        document.getElementById("warning").style.display = "none";
        document.getElementById("rowmeta-cont").classList.add("hidden");
        document.getElementById("colmeta-cont").classList.add("hidden");

        for (let i = 0; i < arr[0].length; i++) {
            let val = arr[0][i];
            colnames[val] = i;
            let opt1 = document.createElement('option');
            opt1.value = val;
            opt1.innerText = val;
            document.getElementById('rowindex').appendChild(opt1);
            let opt2 = opt1.cloneNode(true);
            document.getElementById('colindex').appendChild(opt2);
            let opt3 = opt1.cloneNode(true);
            document.getElementById('row-modal-index').appendChild(opt3);
            let opt4 = opt1.cloneNode(true);
            document.getElementById('col-modal-index').appendChild(opt4);
        }

        $('#row-modal-index').multipleSelect({
            selectAll: false,
            multiple: true,
            multipleWidth: 120,
            countSelected: false,
            maxHeight: 400,
            placeholder: "Choose columns that make the samples unique",
            filter: true,
            onClick: function(view) {
                if (view.checked) {
                    indices.push(view.label);
                }
                else {
                    for (let i = 0; i < indices.length; i++){
                       if (indices[i] === view.label) {
                         indices.splice(i, 1);
                         break;
                       }
                    }
                }
                dataCapture(view);
            }
        });
        $('#col-modal-index').multipleSelect({
            selectAll: false,
            multiple: true,
            multipleWidth: 120,
            maxHeight: 400,
            placeholder: "Choose columns that make the measures unique",
            countSelected: false,
            filter: true,
            onClick: function(view) {
                if (view.checked) {
                    indices.push(view.label);
                }
                else {
                    for (let i = 0; i < indices.length; i++){
                       if (indices[i] === view.label) {
                         indices.splice(i, 1);
                         break;
                       }
                    }
                }
                dataCapture(view);
            }
        });
        $('#rowindex').multipleSelect({
            selectAll: false,
            multiple: true,
            multipleWidth: 120,
            placeholder: "Choose columns that make the samples unique",
            countSelected: false,
            filter: true,
            onClick: function(view) {
                if (view.checked) {
                    indices.push(view.label);
                }
                else {
                    for (let i = 0; i < indices.length; i++){
                       if (indices[i] === view.label) {
                         indices.splice(i, 1);
                         break;
                       }
                    }
                }
                dataCapture(view);
                document.getElementById("rowmeta-cont").classList.add("hidden");
                document.getElementById("colmeta-cont").classList.add("hidden");
            }
        });
        $('#colindex').multipleSelect({
            selectAll: false,
            multiple: true,
            multipleWidth: 120,
            placeholder: "Choose columns that make the measures unique",
            countSelected: false,
            filter: true,
            onClick: function(view) {
                if (view.checked) {
                    indices.push(view.label);
                }
                else {
                    for (let i = 0; i < indices.length; i++){
                       if (indices[i] === view.label) {
                         indices.splice(i, 1);
                         break;
                       }
                    }
                }
                dataCapture(view);
                document.getElementById("rowmeta-cont").classList.add("hidden");
                document.getElementById("colmeta-cont").classList.add("hidden");
            }
        });
        document.getElementById('colnames').classList.remove('hidden');
        document.getElementById('metabutton').onclick = function() {
            introspectData();
        }
        // transposes 2D array from arrays of rows to arrays of columns
        data = arr[0].map(function(col, i){
        return arr.map(function(row){
            return row[i];
        });
        });
        var modal = document.getElementById('indexModal');
        document.getElementById("count").innerText = 0;
        document.getElementById("total").innerText = data[0].length;
        document.getElementById("info").style.color = "red";
        document.getElementById("success").innerText = "";
        modal.style.display = "block";
    }
}

function popValueModal() {
    let optgrp1 = document.createElement('optgroup');
    optgrp1.label = "Potential Suggestions";
    let optgrp2 = document.createElement('optgroup');
    optgrp2.label = "Others";
    for (let i = 0; i < Object.keys(colnames).length; i++) {
        let total = data[i].length;
        let uniq = dropDuplicates(data[i]).length;
        let opt = document.createElement("option");
        opt.value = data[i][0];
        opt.innerText = data[i][0];
        if (uniq / total > 0.5) {
            optgrp1.appendChild(opt);
        }
        else {
            optgrp2.appendChild(opt);
        }
    }
    console.log("hello")
    document.getElementById("value-modal").appendChild(optgrp1);
    document.getElementById("value-modal").appendChild(optgrp2);
    let value = document.getElementById('value');
    value.appendChild(optgrp1.cloneNode(true));
    value.appendChild(optgrp2.cloneNode(true));
    $("#value-modal").multipleSelect({
        placeholder: "Choose a column to supply heatmap values",
        multiple: true,
        multipleWidth: 120,
        single: true,
    })
    $("#value").multipleSelect({
        placeholder: "Choose a column to supply heatmap values",
        multiple: true,
        multipleWidth: 120,
        single: true,
    })
    $("#value").multipleSelect("refresh");
}

function dataCapture() {
    console.log(indices);
    let index = data[colnames[indices[0]]];
    for (let i = 1; i < indices.length; i++) {
        index = mergeCols(index, data[colnames[indices[i]]])
    }
    index = dropDuplicates(index);
    document.getElementById("count").innerText = index.length;
    if (document.getElementById("indexModal").style.display == "block") {
        document.getElementById("warning").style.display = "none";
    }
    if (index.length == data[0].length) {
        document.getElementById("info").style.color = "green";
        document.getElementById("success").innerText = "Success!";
        document.getElementById("warning").innerText = "Success! You have encapsulated all " + data[0].length + " data points!";
        document.getElementById("warning").style.color = "green";
    }
    else {
        document.getElementById("info").style.color = "red";
        document.getElementById("warning").style.color = "red";
        document.getElementById("success").innerText = "";

        if (document.getElementById("indexModal").style.display == "none") {
            document.getElementById("warning").style.display = "block";
        }
        document.getElementById("warning").innerText = "Warning! " + document.getElementById("info").innerText;
    }
}

function introspectData() {
    let row_selected_inds = $("#rowindex").multipleSelect("getSelects", "text");
    let col_selected_inds = $("#colindex").multipleSelect("getSelects", "text");
    if (row_selected_inds.length > 0) {
        let rowMetaCandidates = indexCol(row_selected_inds, "Row");
        genMetaList(rowMetaCandidates, "rowmeta");
        document.getElementById("rowmeta-cont").classList.remove("hidden");
    }
    else {
        let cont = document.getElementById('modal-cont');
        cont.innerHTML = '';
        let article = document.createElement('article');
        article.style.minHeight = "200px";
        let head = document.createElement("h4");
        head.innerText = "Possible Row Metadata Candidates";
        article.appendChild(head);
        let warning = document.createElement("span");
        warning.classList.add("warning");
        warning.innerText = "Error: No columns supplied for Row Indices."
        article.appendChild(warning);
        cont.appendChild(article);
    }
    if (col_selected_inds.length > 0) {
        let colMetaCandidates = indexCol(col_selected_inds, "Column");
        genMetaList(colMetaCandidates, "colmeta");
        document.getElementById("colmeta-cont").classList.remove("hidden");
    }
    else {
        let article = document.createElement('article');
        article.style.minHeight = "200px";
        let cont = document.getElementById('modal-cont');
        article.appendChild(document.createElement("hr"));
        let head = document.createElement("h4");
        head.innerText = "Possible Column Metadata Candidates";
        article.appendChild(head);
        let warning = document.createElement("span");
        warning.classList.add("warning");
        warning.innerText = "Error: No columns supplied for Column Indices."
        article.appendChild(warning);
        cont.appendChild(article);
    }
    if (row_selected_inds.length == 0 && col_selected_inds.length == 0) {
        alert("Error: Metadata cannot be generated as no row or column indices were selected!");
    }
    else {
        document.getElementById('metaModal').style.display = 'block';
    }
}

function genMetaList(candidates, list) {
    document.getElementById(list).innerHTML = '';
    for (let i = 0; i < candidates.length; i++) {
        let opt = document.createElement('option');
        opt.value = candidates[i];
        opt.innerText = candidates[i];
        document.getElementById(list).appendChild(opt);
    }
    $("#" + list).multipleSelect({
        selectAll: false,
        multiple: true,
        multipleWidth: 120,
        placeholder: "Possible metadata that can be visualized",
        countSelected: false
    });
}

function indexCol(selected_inds, header) {
    let index = data[colnames[selected_inds[0]]];
    for (let j = 1; j < selected_inds.length; j++) {
        index = mergeCols(index, data[colnames[selected_inds[j]]])
    }
    let metaDict = checkMetadata(index);
    populateModal(metaDict, header);
    console.log(metaDict)
    return(Object.keys(metaDict));
}

function populateModal(metaDict, header) {
    let keys = Object.keys(metaDict);
    let cont = document.getElementById("modal-cont");
    // to reset modal
    if (header === "Row" && cont.innerHTML != null) {
        cont.innerHTML = null;
    }
    let article = document.createElement("article");
    if (header === "Column") {
        article.appendChild(document.createElement("hr"));
    }
    article.id = header;
    let head = document.createElement("h4");
    head.innerText = "Possible " + header + " Metadata Candidates";
    article.appendChild(head);
    article.style.minHeight = '200px';
    for (let i = 0; i < keys.length; i++) {
        let len = metaDict[keys[i]].length - 1
        let tab = document.createElement("div");
        let select = document.createElement("input");
        select.classList.add("cbox");
        select.value = keys[i];
        select.setAttribute("type", "checkbox");
        select.style.display = "inline";
        let inner_cont = document.createElement('div');
        tab.classList.add("expand-text");
        tab.style.display = 'inline';
        tab.setAttribute("data-toggle", "collapse");
        tab.setAttribute("data-target", "#" + keys[i]);
        tab.innerText = keys[i]+ " (" + len + " distinct categories)";
        let text = document.createElement("div");
        text.id = keys[i];
        text.classList.add("collapse");
        let list = document.createElement("ul");
        list.style.marginBottom = "0px";
        let max = Math.min(10, len + 1);
        for (let j = 1; j < max; j++) {
            let entry = document.createElement("li");
            entry.innerText = metaDict[keys[i]][j];
            list.appendChild(entry);
        }
        text.appendChild(list);
        if (metaDict[keys[i]].length > 11) {
            let span = document.createElement("span");
            span.style.fontStyle = 'italic';
            span.style.fontSize = '11px';
            span.innerText = "Displaying 10 of " + len + " distinct categories.";
            text.appendChild(span);
        }
        inner_cont.appendChild(select);
        inner_cont.appendChild(tab);
        article.appendChild(inner_cont);
        article.appendChild(text);
    }
    if (keys.length > 0) {
        let selectAll = document.createElement("input");
        selectAll.onclick = function() {
            let boxes = document.querySelectorAll("#" + header + " .cbox");
            let checked = selectAll.checked;
            for (let i = 0; i < boxes.length; i++) {
                boxes[i].checked = checked;
            }
        }
        let txt = document.createTextNode("Select All");
        selectAll.setAttribute("type", "checkbox");
        article.appendChild(selectAll);
        article.appendChild(txt);
    }
    else {
        let error = document.createElement("span");
        error.classList.add("warning");
        error.innerText = "Error: no possible metadata candidates exist for given " + header + " Indices";
        article.appendChild(error);
    }
    cont.appendChild(article);


    if ($("#rowmeta").multipleSelect("getSelects").length > 0) {
        let rowmeta_sels = $("#rowmeta").multipleSelect("getSelects", "text");
        let rowboxes = document.querySelectorAll("#Row .cbox");
        for (let i = 0; i < rowboxes.length; i++) {
            for (let j = 0; j < rowmeta_sels.length; j++) {
                if (rowboxes[i].value == rowmeta_sels[j]) {
                    rowboxes[i].checked = true;
                }
            }
        }
    }
    if ($("#colmeta").multipleSelect("getSelects").length > 0) {
        let colmeta_sels = $("#colmeta").multipleSelect("getSelects", "text");
        let colboxes = document.querySelectorAll("#Column .cbox");
        for (let k = 0; k < colboxes.length; k++) {
            for (let l = 0; l < colmeta_sels.length; l++) {
                if (colboxes[k].value == colmeta_sels[l]) {
                    colboxes[k].checked = true;
                }
            }
        }
    }
}

function checkMetadata(index) {
    let candidates = {};
    let count = dropDuplicates(index).length;
    for (let i = 0; i < data.length; i++) {
        // If we are only looking at metadata columns with at least 2 unique entries
        if (dropDuplicates(data[i]).length > 2) {
            let temp = mergeCols(index, data[i]);
            let temp2 = dropDuplicates(temp).length;
            if (temp2 == count) {
                candidates[data[i][0]] = dropDuplicates(data[i]);
            }
        }
    }
    return candidates;
}

function mergeCols(col1, col2) {
    mergedCol = [];
    for (let i = 0; i < col1.length; i++) {
        mergedCol.push(col1[i] + '|' + col2[i]);
    }
    return mergedCol;
}

function dropDuplicates(arr){
    let unique_array = Array.from(new Set(arr))
    return unique_array
}

function display(upload1, upload2) {
    document.getElementById(upload1).classList.toggle('hidden');
    if (upload1 === 'longform') {
        document.getElementById('lfFile').required = true;
        document.getElementById('dataFile').required = false;
        document.getElementById('row_mdFile').required = false;
        document.getElementById('col_mdFile').required = false;
    }
    else {
        document.getElementById('lfFile').required = false;
        document.getElementById('dataFile').required = true;
        document.getElementById('row_mdFile').required = true;
        document.getElementById('col_mdFile').required = true;
    }
    document.getElementById(upload2).classList.add('hidden');
}

function reset_html(id) {
    $('#'+id).html($('#'+id).html());
    if(isAPIAvailable()) {
      $('#lfFile').bind('change', handleFileSelect);
    }
}
