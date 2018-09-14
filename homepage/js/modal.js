
      // Get the modal
      var modal = document.getElementById('myModal2');

      // Get the button that opens the modal
      var btn = document.getElementById("metabutton");

      // Get the <span> element that closes the modal
      var span = document.getElementsByClassName("close")[0];

      // When the user clicks the button, open the modal
      btn.onclick = function() {
          modal.style.display = "block";
      }

      // When the user clicks on <span> (x), close the modal
      span.onclick = function() {
          populateTabs("Row", "rowmeta");
          populateTabs("Column", "colmeta");
          modal.style.display = "none";
      }

      // When the user clicks anywhere outside of the modal, close it
      window.onclick = function(event) {
          if (event.target == modal) {
              populateTabs("Row", "rowmeta");
              populateTabs("Column", "colmeta");
              modal.style.display = "none";
          }
      }

      function populateTabs(header, select) {
          if ($("#rowindex").multipleSelect("getSelects").length > 0 && $("#colindex").multipleSelect("getSelects").length > 0) {
              let boxes = document.querySelectorAll("#" + header + " .cbox");
              let arr = [];
              for (let i = 0; i < boxes.length; i++) {
                  if (boxes[i].checked) {
                      arr.push(boxes[i].value);
                  }
              }
              console.log(arr)
              $("#" + select).multipleSelect("setSelects", arr);
          }
          else if (header == "Row"){
              // alert("Please select both a row and column index!");
          }

      }
