var stepnum = "0";
var steps = [
                 // 0
              {
                   intro: "<p style='text-align:center'>Welcome to the MetaVis tutorial!</p> <p style='text-align:center'>This walkthrough will provide a brief overview of the functionalities and tools that MetaVis provides.</p>"+
                   " Navigate through the walkthrough using the arrow keys. <br /> Feel free to exit out at any time to experiment with the features. The walkthrough can then"+
                   " be resumed using the <b>Resume Tutorial</b> button. <br /><br /><span style='text-align:center'><i>You can also skip to the section corresponding to each important function through the <b>Toggle Tips</b> button!<i></span>"
              },
              {
                 // 1
                 intro: "<div style='text-align:center'><p> Welcome to MetaVis! </p> MetaVis is an interactive visualization tool that allows you to explore data in deeper and more intuitive ways."+
                 " We hope that MetaVis can help provide a more effective interace to identify patterns, understand relationships, and interrogate data." +
                 "<br /> <br /> To these ends, MetaVis has many functionalities and tools to help streamline the experience.</div>",
              },
              {
                  // 2
                 element: '#heatmap',
                 intro: 'This is the base heatmap visualization created by MetaVis, which serves as its centerpoint for interactivity and functionality. Some notable features are:'+
                 '<ul><li>Hover functionality for each cell to view more detailed information</li><li>Responsive integration with auxillary tools</li>'+
                 '<li>Selection by row, column, or both</li><li>Supplemental Toolbar<ul><li>Pan</li><li>Zoom Tools</li><li>Save as PNG</li><li>Viewport Reset Tool</li></ul></ul>',
                 position: 'bottom'
              },
              {
                  // 3
                 element: '#selectors',
                 intro: '<p>This dropdown menu allows you to choose 3 different ways to select data in the heatmap.</p>'+
                 '<ul><li><b>Cross Select</b>: This is the default selection mode. Upon clicking and dragging a box on the heatmap, <b>Cross Select</b> selects data in a cross-shaped pattern, giving you information about the rows and columns of the data selected.</li>'+
                 '<li><b>Row Select</b>: This selection mode selects all the rows in the box selected region.</li>'+
                 '<li><b>Column Select</b>: This selection mode selects all the columns in the box selected region.</li>',
                 position: 'right'
              },
              {
                  // 4
                 element: '#p_selector',
                 intro: 'This dropdown menu is populated with the row metadata categories given to MetaVis.<br />'+
                 ' Changing which category is selected changes which row metadata will be visualized in the colorbars and histograms.',
                 position: 'right'
              },
              {
                  // 5
                 element: '#m_selector',
                 intro: 'This dropdown menu is populated with the column metadata categories given to MetaVis.<br />'+
                 ' Changing which category is selected changes which column metadata will be visualized in the colorbars and histograms.',
                 position: 'right'
              },
              {
                  // 5
                 element: '#export',
                 intro: 'You can export data you have selected in the heatmap to .csv!<br />' +
                 ' Pressing the Export button while in <b>Row</b>/<b>Column</b> mode will export the selected rows or columns, while exporting when in <b>Cross</b> mode will give you data from the intersection of rows and columns.',
                 position: 'right'
              },
              {
                  // 6
                 element: '#reset',
                 intro: "The Reset button clears selections on the heatmap, resets it's zoom level, and empties the data tables.",
                 position: 'right'
              },
              {
                  // 7
                 element: '#x_color',
                 intro: 'This is the responsive colorbar that corresponds to measure metadata.',
                 position: 'right'
              },
              {
                  // 8
                 element: '#y_color',
                 intro: 'This is the responsive colorbar that corresponds to sample metadata.',
                 position: 'right'
              },
              {
                 // 9
                 intro: "Changes made to either the row or column metadata selectors will dynamically update their corresponding colorbars!<br /><br />" +
                 "<p style='color: gray; font-size: 8pt;'><i> 72 colors are supported. If the metadata has more than 72 categories, the extra ones will be displayed as gray.</i></p>",
              },
              {
                  // 10
                 element: '#y_leg',
                 intro: 'This is the legend corresponding to the sample metadata colorbar.',
                 position: 'right'
              },
              {
                  // 11
                 element: '#x_leg',
                 intro: 'This is the legend corresopnding to the measure metadata colorbar.',
                 position: 'right'
              },
              {
                  // 12
                 element: '#legs',
                 intro: 'Clicking on the colored boxes will select the rows/columns in the heatmap corresponding to that metadata category. <br /> <br />'+
                 'After choosing a row category to select, you can further filter the selection by selection a column category or vice versa.',
                 position: 'right'
              },
              {
                  // 13
                 element: '#x_dend',
                 intro: 'This is the x-axis dendrogram for the heatmap.',
                 position: 'right'
              },
              {
                  // 14
                 element: '#y_dend',
                 intro: 'This is the y-axis dendrogram for the heatmap.  <br /> <br />After adjusting the zoom of the heatmap, these dendrograms also have the ability to zoom in and out.',
                 position: 'right'
              },
              {
                  // 15
                 element: '#table-tabs',
                 intro: 'These data tables reflect the selected rows or columns in the heatmap. Pressing the reset button will clear the respective table, and pressing the export button will export the table\'s contents to .csv.',
                 position: 'right'
              },
              {
                  // 16
                 element: '#bar-tabs',
                 intro: 'This set of 4 histograms represents the number of selected/unselected rows or columns for a given metadata category.',
                 position: 'right'
              },
                 // 17
              {
                 intro: "That's the end of the MetaVis guided walkthrough. I hope that MetaVis will be an effective tool for you to better visualize and interact with your data!"
              }
            ];

function startIntro(){
        var intro = introJs();
          intro.setOptions({
            steps: steps,
            showBullets: false,
            showButtons: false,
            showProgress: true,
            exitOnOverlayClick: true,
            showStepNumbers: false,
            keyboardNavigation: true
          });
          intro.start();
          intro.onexit(function(target) {
              var s = this._currentStep;
              stepnum = (parseInt(s) + 1).toString();
              if (s >= 17) {
                  document.getElementById("tut").innerText = "Tutorial";
                  s = -1;
              }
              else {
                  document.getElementById("tut").innerText = "Resume Tutorial";
              }
              stepnum = (parseInt(s) + 1).toString();
          })
          if (stepnum !== "0") {
              intro.goToStep(stepnum);
          }
      }

function toggleHints(){
    let hints = document.querySelectorAll(".overlay");
    for (let i = 0; i < hints.length; i++) {
        hints[i].classList.toggle("hidden");
    }
}

// Add  onclick="step('');" to div with tool
function step(num){
    var temp = parseInt(num);
    temp += 1;
    temp = temp.toString();
  var intro = introJs();
    intro.setOptions({
      steps: steps,
      showBullets: false,
      showButtons: false,
      showProgress: true,
      exitOnOverlayClick: true,
      showStepNumbers: false,
      keyboardNavigation: true
    });
  intro.start();
  intro.goToStep(temp);
}
