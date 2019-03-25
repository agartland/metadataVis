var inds = source.selected.indices;
console.log(inds);
var confirm = true;
if (storage.data['mode'] == "Cross") {
  confirm = window.confirm("Exporting on the intersection of rows and columns. \n \n (To export just rows or just columns, set the appropriate Selection Type)");
  inds = indices.data['indices'];
}
if (confirm) {
  var data = source.data;
  console.log(inds);
  console.log(data);
  var filename = "MetaVis_subselection.csv";
  var filetext = "PtID";
  var cols = [];
  var rows = [];
  for (let ii = 0; ii < inds.length; ii++) {
      rows.push(data['PtID'][inds[ii]]);
      cols.push(data['Feature'][inds[ii]]);
  }
  console.log("rows array: " + rows);
  console.log("cols array: " + cols);
  c_unique = unique(cols);
  console.log("unique cols: " + c_unique);
  var row_dict = {};
  for (let kk = 0; kk < c_unique.length; kk++) {
      filetext += "," + c_unique[kk];
  }
  filetext += "\n";

  // Initializing dictionary with ptid rows and a set number of feature columns.
  for (var i = 0; i < rows.length; i++) {
      row_dict[rows[i]] = Array(c_unique.length + 1).fill(0);
      row_dict[rows[i]][0] = rows[i];
  }

  // console.log(filetext);
  // Iterating over selected inds and putting each rate in the appropriate row/col
  for (var j = 0; j < inds.length; j++) {
      var rate = data['rate'][inds[j]].toString();
      var row = data['PtID'][inds[j]];
      var col = c_unique.indexOf(data['Feature'][inds[j]]);
      // + 1 to accomodate for first column of ptids
      row_dict[row][col + 1] = rate;
  }
  console.log(row_dict);

  keys = Object.keys(row_dict);
  for (var jj = 0; jj < keys.length; jj++) {
    var currRow = row_dict[keys[jj]].join();
    currRow += "\n";
    filetext += currRow;
  }

  console.log(filetext);

  var blob = new Blob([filetext], { type: 'text/csv;charset=utf-8;' });
  //addresses IE
  if (navigator.msSaveBlob) {
      navigator.msSaveBlob(blob, filename);
  } else {
      var link = document.createElement("a");
      link = document.createElement('a')
      link.href = URL.createObjectURL(blob);
      link.download = filename
      link.target = "_blank";
      link.style.visibility = 'hidden';
      link.dispatchEvent(new MouseEvent('click'))
  }
}

function unique(a) {
    var temp = {};
    for (var i = 0; i < a.length; i++)
        temp[a[i]] = true;
    return Object.keys(temp);
}
