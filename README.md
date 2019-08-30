## metaVis

An integrated data upload and interactive heatmap visualization tool built for exploratory data analysis and introspection.

metaVis is a heatmap visualization tool that enables users to interactively interface with their data that centers around the inclusion of "metadata"
\- supplementary information behind each data point that characterizes and contextualizes it.
metaVis comprises two main components: a server and web portal that provides flexible data upload and the heatmap visualization tool itself in the form of a generated standalone html file.
The metaVis visualization tool is meant to enable scientists and researchers to more easily visualize their datasets, recontextualize and gain a wider perspective
of their data through the integration of "metadata," and interactively perform exploratory data analysis. metaVis is primarily built on the _[bokeh](https://bokeh.pydata.org/en/latest/)_ and _[twisted](https://twistedmatrix.com/trac/)_ packages as the visualization and server backend.

- https://bokeh.pydata.org/en/latest/
- https://twistedmatrix.com/trac/

## Installation
The package is compatible with Python 3.6 and can be cloned or installed directly through github or PyPI.

To install latest version from github:
```bash
pip install git+https://github.com/agartland/metadataVis.git
```

To install latest version from PyPI:
```bash
pip install "metaVis"
```

To install a specific version from PyPI:
```bash
pip install "metaVis==1.0"
```

## Usage: Running a metaVis server locally
1) Navigate to the directory 'metadataVis' in a bash shell or cmd

2) Run the following command:
```bash
python MetaVisServer.py
```

3) Navigate your browser to [localhost:5097](localhost:5097)
