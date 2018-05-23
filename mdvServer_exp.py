from __future__ import print_function
from twisted.web import server, resource, static
from twisted.internet import reactor, endpoints, task, threads
from twisted.internet.defer import Deferred
import cgi
import argparse
from io import StringIO
import pandas as pd
from twisted.web.util import Redirect
from twisted.web.util import redirectTo
from twisted.python import log

#from example_server_plot import exampleVis
from HeatmapMetaVis import gen_heatmap_html

# TODO - Popup if file upload is empty; popup for errors
def _prepArgs(request):
    kwargs = {}
    for k,v in request.args.iteritems():
        if k.find('File') >= 0 and request.args[k][0] != '':
            sio = StringIO(unicode(request.args[k][0]))
            if k.find('longformFile') >= 0:
                tmp = pd.read_csv(sio)
            else:
                tmp = pd.read_csv(sio, index_col=0)
            kwargs[k.replace('File', '')] = tmp
    if 'static' in request.args:
        kwargs['static'] = True
    if 'standardize' in request.args:
        kwargs['standardize'] = True
    kwargs['metric'] = request.args['metric'][0]
    kwargs['method'] = request.args['method'][0]

    #key_string = [k for k in kwargs]
    #request.write("<html>" + str(key_string) + "<body>")
    ret_map = gen_heatmap_html(**kwargs)
    if(ret_map['error'] is not None):
        # TODO - More Elegant Error Display
        request.write("<html>" + ret_map['error'] + "<body>")
        return request
    html = ret_map['heatmap_html']
    # html = exampleVis(**kwargs)
    # print(html[:100])
    # request.write(html.encode('utf-8'))
    request.write(html)
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
