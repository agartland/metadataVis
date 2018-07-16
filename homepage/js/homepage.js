"use strict";

(function() {
  window.onload = function(){
    let ics = document.querySelector("form input[name='ics']");
    let bama = document.querySelector("form input[name='bama']");
    let dataStrings = document.querySelectorAll("form input[type='text']")
    bama.onclick = function() {
      dataStrings[0].value = 'ptid, feature, pctpos_pos';
      dataStrings[1].value = 'labid, samp_ord, rx_code, rx';
      dataStrings[2].value = 'tcellsub, cytokine, antigen' ;
    }
    ics.onclick = function() {
      dataStrings[0].value = 'ptid, feature, pctpos_pos';
      dataStrings[1].value = 'labid, samp_ord, rx_code, rx, pub_id';
      dataStrings[2].value = 'tcellsub, cytokine, antigen' ;
    }
  }
})();
