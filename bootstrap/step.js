var steps = [
              {
                 // 0
                 intro: "<p> Welcome to MetaVis! </p> MetaVis is an interactive visualization tool that allows you to explore data in deeper and more intuitive ways."+
                 " We hope that MetaVis can help provide a more effective interace to identify patterns, understand relationships, and interrogate data." +
                 "<br /> <br /> To these ends, MetaVis has many functionalities and tools to help streamline the experience.",
              },
              {
                  // 1
                 element: '#heatmap',
                 intro: 'This is the base heatmap visualization created by MetaVis. Some notable features are:'+
                 '<ul><li>Ability to hover over each cell to view more detailed information</li><li>Responsive functionality combined with auxillary tools</li>'+
                 '<li>Selection by row, column, or both</li><li>Supplemental Toolbar<ul><li>Pan</li><li>Zoom Tools</li><li>Save as PNG</li><li>Reset Viewport</li></ul></ul>',
                 position: 'right'
              },
              {
                  // 2
                 element: '#y_color',
                 intro: 'This is the responsive colorbar that corresponds to patient metadata.',
                 position: 'right'
              },
              {
                  // 3
                 element: '#x_color',
                 intro: 'This is the responsive colorbar that corresponds to feature metadata.'+
                 ' These colorbars change dynamically based on whichever type of metadata is selected. ',
                 position: 'right'
              },
              {
                  // 4
                 element: '#y_leg',
                 intro: 'This is the legend corresponding to the patient metadata colorbar.',
                 position: 'right'
              },
              {
                  // 5
                 element: '#x_leg',
                 intro: 'This is the legend corresopnding to the feature metadata colorbar. Clicking on these colors selects those corresponding rows/columns in the heatmap. Try it out!',
                 position: 'right'
              },
              {
                  // 6
                 element: '#y_dend',
                 intro: 'These are the dendrograms for the heatmap.',
                 position: 'right'
              },
              {
                  // 7
                 element: '#x_dend',
                 intro: 'Upon adjusting the zoom of the heatmap, these dendrograms also have the ability to zoom in and out.',
                 position: 'right'
              },
              {
                  // 8
                 element: '#selectors',
                 intro: 'This dropdown allows you to choose between selecting both rows and columns upon box select, just rows, or just columns.',
                 position: 'right'
              },
              {
                  // 9
                 element: '#p_selector',
                 intro: 'This selector allow you to choose which patient metadata category you want visualized in the colorbars and histograms.',
                 position: 'right'
              },
              {
                  // 10
                 element: '#m_selector',
                 intro: 'Same for the feature selector!',
                 position: 'right'
              },
              {
                  // 11
                 element: '#reset',
                 intro: 'The Reset button clears all selections on the heatmap and empties the data table.',
                 position: 'right'
              },
              {
                  // 12
                 element: '#table-tabs',
                 intro: 'These data tables reflect the selected rows or columns in the heatmap.',
                 position: 'right'
              },
              {
                  // 13
                 element: '#bar-tabs',
                 intro: 'This set of 4 histograms represents the number of selected/unselected rows or columns for a given metadata category.',
                 position: 'right'
              },
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
      exitOnOverlayClick: false,
      showStepNumbers: false,
      keyboardNavigation: true

    });
  intro.start();
  intro.goToStep(temp);
}
