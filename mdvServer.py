from __future__ import print_function
from twisted.web import server, resource, static
from twisted.internet import reactor, endpoints, task, threads
from twisted.internet.defer import Deferred
import cgi
import argparse
from StringIO import StringIO
import pandas as pd
from twisted.web.util import Redirect
from twisted.web.util import redirectTo
from twisted.python import log

from example_server_plot import exampleVis

def _prepArgs(request):
    kwargs = {}
    for k,v in request.args.iteritems():
        if k.find('File') >= 0:
            sio = StringIO(request.args[k][0])
            tmp = pd.read_csv(sio, index_col=0)
            kwargs[k.replace('File', '')] = tmp
    if 'static' in request.args:
        kwargs['static'] = True
    if 'standardize' in request.args:
        kwargs['standardize'] = True
    kwargs['metric'] = request.args['metric'][0]
    kwargs['method'] = request.args['method'][0]
    html = exampleVis(**kwargs)
    print(html[:100])
    request.write(html.encode('utf-8'))
    return request

class FileUpload(resource.Resource):
    isLeaf = True
    def render_GET(self, request):
        return redirectHome.render(request)

    def _delayedPOSTRender(self, request):
        #request.write("\n\n\nUpload complete.</body></html>")
        request.finish()

    def render_POST(self, request):
        #request.write('<html><body>')
        d = threads.deferToThread(_prepArgs, request)
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

redirectHome = Redirect('home')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Start metadataVis web server.')
    parser.add_argument('--port', metavar='PORT', type=int, default=5097)
    args = parser.parse_args()

    root = RootResource()
    root.putChild('home', static.File('./homepage'))
    root.putChild('viz', FileUpload())
    
    site = server.Site(root)
    reactor.listenTCP(args.port, site)
    reactor.run()
