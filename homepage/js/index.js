var colnames = {};
var data = [];

$(document).ready(function() {
      if(isAPIAvailable()) {
        $('#lfFile').bind('change', handleFileSelect);
      }
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
        for (let i = 0; i < arr[0].length; i++) {
            let val = arr[0][i];
            colnames[val] = i;
            let opt1 = document.createElement('option');
            opt1.value = val;
            opt1.innerText = val;
            document.getElementById('rowindex').appendChild(opt1);
            let opt2 = opt1.cloneNode(true);
            document.getElementById('colindex').appendChild(opt2)
        }
        $('#rowindex').multipleSelect({
            selectAll: false,
            multiple: true,
            multipleWidth: 120,
            countSelected: false,
            placeholder: "Choose columns that make the samples unique",
            filter: true
        });
        $('#colindex').multipleSelect({
            selectAll: false,
            multiple: true,
            multipleWidth: 120,
            placeholder: "Choose columns that make the measures unique",
            countSelected: false,
            filter: true
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
    if (col_selected_inds.length > 0) {
        let colMetaCandidates = indexCol(col_selected_inds, "Column");
        genMetaList(colMetaCandidates, "colmeta");
        document.getElementById("colmeta-cont").classList.remove("hidden");
    }
    document.getElementById('myModal').style.display = 'block';
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
    article.id = header;
    let head = document.createElement("h4");
    head.innerText = "Possible " + header + " Metadata Candidates";
    article.appendChild(head);
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
        inner_cont.appendChild(select)
        inner_cont.appendChild(tab)
        article.appendChild(inner_cont);
        article.appendChild(text);
    }
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
    article.appendChild(selectAll)
    article.appendChild(txt);
    cont.appendChild(article);
    if (header === "Row") {
        article.appendChild(document.createElement("hr"));
    }
}

function checkMetadata(index) {
    let candidates = {};
    let count = dropDuplicates(index).length;
    console.log(count)
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
