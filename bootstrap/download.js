var data = source.data;
var keys = Object.keys(data).slice(0, -2);
var filename = '';
if (keys.includes("PtID")) {
  filename = 'row_metadata.csv';
}
else {
  filename = 'column_metadata.csv';
}
var filetext = keys[0];
for (let i = 1; i < keys.length; i++) {
  filetext += ", " + keys[i];
}
filetext += "\n";
console.log(filetext);
for (var j = 0; j < data[keys[0]].length; j++) {
    var currRow = [];
    for (let k = 0; k < keys.length - 1; k++) {
      var entry = data[keys[k]][j];
      if (entry == null || entry.toString() == '') {
        currRow.push(NaN);
      }
      else if (entry.toString().includes(',')) {
        currRow.push("\"" + entry + '\"');
      }
      else {
        currRow.push(entry.toString());
      }
    }
    var last = data[keys[keys.length - 1]][j];
    if (last == null) {
      currRow.push(NaN.concat('\n'));
    }
    currRow.push(last.toString().concat('\n'));
    var joined = currRow.join();
    filetext = filetext.concat(joined);
}
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
