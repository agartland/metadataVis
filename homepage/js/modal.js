
      // Get the modal
      var indexModal = document.getElementById('indexModal');

      // Get the button that opens the modal
      // Get the <span> element that closes the modal
      var indexSpan = document.getElementById('close-modal1');

      // When the user clicks on <span> (x), close the modal
      indexSpan.onclick = function() {
          reflectChanges("row-modal-index", "rowindex");
          reflectChanges("col-modal-index", "colindex");
          if (document.getElementById("success").innerText == "") {
              warning.style.display = "block";
              warning.innerText = "Warning! " + document.getElementById("info").innerText;  
          }
          indexModal.style.display = "none";
          popValueModal();
      }

      // When the user clicks anywhere outside of the modal, close it
      window.onclick = function(event) {
          if (event.target.className == 'modal') {
              if (event.target.id == "metaModal") {
                  populateTabs("Row", "rowmeta");
                  populateTabs("Column", "colmeta");
                  event.target.style.display = "none";
              }
          }
      }

    // Get the modal
    var metaModal = document.getElementById('metaModal');

    // Get the button that opens the modal
    var btn = document.getElementById("metabutton");

    // Get the <span> element that closes the modal
    var metaSpan = document.getElementById("close-modal2");
    var metaExit = document.getElementById("next3");


    // When the user clicks the button, open the modal
    btn.onclick = function() {
        metaModal.style.display = "block";
    }

    // When the user clicks on <span> (x), close the modal
    metaSpan.onclick = function() {
        populateTabs("Row", "rowmeta");
        populateTabs("Column", "colmeta");
        metaModal.style.display = "none";
    }

    metaExit.onclick = function() {
        populateTabs("Row", "rowmeta");
        populateTabs("Column", "colmeta");
        metaModal.style.display = "none";
    }

    var bamaButton = document.getElementById("preset-bama");
    bamaButton.onclick = bamaPreset;

    // Get the modal
    var valueModal = document.getElementById('valueModal');

    // Get the button that opens the modal
    var next1 = document.getElementById("next1");

    // Get the <span> element that closes the modal
    var valueSpan = document.getElementById("close-modal3");

    // When the user clicks the button, open the modal
    next1.onclick = function() {
        reflectChanges("row-modal-index", "rowindex");
        reflectChanges("col-modal-index", "colindex");
        if (parseInt(document.getElementById("count").innerText) != parseInt(document.getElementById("total").innerText)) {
            alert("You have not supplied enough columns to your row/column indices to make a MetaVis visualization!");
            let warning = document.getElementById("warning");
            warning.style.display = "block";
            warning.innerText = "Warning! " + document.getElementById("info").innerText;
        }
        indexModal.style.display = "none";
        popValueModal();
        reflectChanges("value-modal", "value")  
        valueModal.style.display = "block";
    }

    var next2 = document.getElementById("next2");
    next2.onclick = function() {
        reflectChanges("value-modal", "value")  
        valueModal.style.display = "none";
        introspectData();
        metaModal.style.display = "block";
    }

    // When the user clicks on <span> (x), close the modal
    valueSpan.onclick = function() {
        valueModal.style.display = "none";
    }

    function populateTabs(header, select) {
        if ($("#rowindex").multipleSelect("getSelects").length > 0 && $("#colindex").multipleSelect("getSelects").length > 0) {
            let boxes = document.querySelectorAll("#" + header + " .cbox");
            let arr = [];
            for (let i = 0; i < boxes.length; i++) {
                if (boxes[i].checked) {
                    arr.push(boxes[i].value);
                }
            }['ptid', 'visitno']
            console.log(arr)
            $("#" + select).multipleSelect("setSelects", arr);
        }
        else if (header == "Row"){
            // alert("Please select both a row and column index!");
        }
    }
    function reflectChanges(modal, select) {
        console.log($("#" + modal).multipleSelect("getSelects"))
        $("#" + select).multipleSelect("setSelects", $("#" + modal).multipleSelect("getSelects"));
    }

    function bamaPreset() {
        popValueModal();
        console.log($("#value").multipleSelect("getSelects"));
        $("#rowindex").multipleSelect("setSelects", ['ptid', 'visitno']);
        $("#colindex").multipleSelect("setSelects", ['isotype', 'antigen']);
        $("#value").multipleSelect("setSelects", ['delta']);
        console.log($("#value").multipleSelect("getSelects"));
        indexModal.style.display = "none";
    }