from __future__ import print_function
from twisted.web import server, resource, static
from twisted.internet import reactor, endpoints, task, threads
from twisted.internet.defer import Deferred
from twisted.web.util import Redirect
from twisted.web.util import redirectTo
from twisted.python import log

from io import StringIO
import argparse
#import pandas as pd
import tempfile, os, sys
import subprocess
import shutil
import pandas as pd

import MetaVisLauncherConfig as config
import MetaVisLauncherConstants as constants
from LongformReader import _generateWideform


# TODO - Popup if file upload is empty; popup for errors
# Must call _cleanup_tmp before returning
def _handleMetaVis(request):
    tmpdirname = config.tmp_dir
    if not os.path.exists(tmpdirname):
        os.makedirs(tmpdirname)

    launcher_args = _prepArgs(request)
    args = [config.python3_path] + launcher_args
    return_code = subprocess.call(args)

    if return_code != 0:
        request.write("Sorry, your files could not be processed at this time.")
        return _clean_and_return(request)
        
    # Check for and handle errors
    if os.path.exists(os.path.join(config.error_dir, config.error_file)):
        error_file = open(os.path.join(config.error_dir, config.error_file), "r")
        error = error_file.read()
        error_file.close()
        request.write(error)
        return _clean_and_return(request)

    output_file = open(os.path.join(tmpdirname, config.output_file), "r")
    res_html = output_file.read()
    output_file.close()

    request.write(res_html)
    return _clean_and_return(request)

def _processLongform(request):
    sio_longform = StringIO(request.args['longformFile'][0].decode("UTF-8"))
    longform = pd.read_csv(sio_longform)
    rx = None
    if request.args['rxFile'][0]:
        sio_rx = StringIO(request.args['rxFile'][0].decode("UTF-8"))
        rx = pd.read_csv(sio_rx)
    base_str = request.args['baseStr'][0]
    row_str = request.args['rowStr'][0]
    col_str = request.args['colStr'][0]
    data, row_md, col_md = _generateWideform(base_str=base_str, row_str=row_str, col_str=col_str, longform_df=longform,
                                                                             rx=rx)
    return data, row_md, col_md

def _prepArgs(request):
    # See Py3MetaVisLauncher.py for format
    tmpdirname = config.tmp_dir
    launcher_args = [''] * constants.REQ_ARG_NUM
    launcher_args[0] = config.launcher
    launcher_args[1] = tmpdirname

    for k,v in request.args.iteritems():
        if (k.find('File') >= 0) & (request.args[k][0] != ''):
            if k == 'longformFile':
                data, row_md, col_md = _processLongform(request)
                data.to_csv(os.path.join(tmpdirname, 'data.csv'))
                row_md.to_csv(os.path.join(tmpdirname, 'row_md.csv'))
                col_md.to_csv(os.path.join(tmpdirname, 'col_md.csv'))
                launcher_args[2] = 'data'
                launcher_args[3] = 'row_md'
                launcher_args[4] = 'col_md'
            else:
                filename = str(k.replace('File', ''))
                with open(os.path.join(tmpdirname, filename + '.csv'), 'w') as tmpFile:
                    tmpFile.write(request.args[k][0])
                if k == 'dataFile':
                    launcher_args[2] = filename
                elif k == 'row_mdFile':
                    launcher_args[3] = filename
                else: # k == 'col_mdFile'
                    launcher_args[4] = filename
    launcher_args[5] = '-' + str(request.args['metric'][0])
    launcher_args[6] = '-' + str(request.args['method'][0])
    if 'standardize' in request.args:
        launcher_args.append('-standardize')
    if 'impute' in request.args:
        launcher_args.append('-impute')
    if 'static' in request.args:
        launcher_args.append('-static')
    return launcher_args

class FileUpload(resource.Resource):
    isLeaf = True
    def render_GET(self, request):
        return redirectHome.render(request)

    def _delayedPOSTRender(self, request):
        request.finish()

    def render_POST(self, request):
        d = threads.deferToThread(_handleMetaVis, request)
        d.addCallback(self._delayedPOSTRender)
        d.addErrback(log.err)
        return server.NOT_DONE_YET

class RootResource(resource.Resource):
    isLeaf = False
    def getChild(self, name, request):
        if name == '':
            return self
        return resource.Resource.getChild(self, name, request)
    def render_GET(self, request):
        return redirectHome.render(request)

def _clean_and_return(request):
    _cleanup_tmp()
    return request

def _cleanup_tmp():
    if os.path.exists(config.tmp_dir):
        shutil.rmtree(config.tmp_dir)

def _check_ver():
    if sys.version_info[0] != 2:
        raise Exception("MetaVisServer must be launched with python 2")

redirectHome = Redirect('home')

if __name__ == '__main__':
    _check_ver()
    parser = argparse.ArgumentParser(description='Start metadataVis web server.')
    parser.add_argument('--port', metavar='PORT', type=int, default=5097)
    args = parser.parse_args()

    root = RootResource()
    root.putChild('home', static.File('./homepage'))
    root.putChild('viz', FileUpload())

    site = server.Site(root)
    reactor.listenTCP(args.port, site)
    reactor.run()
