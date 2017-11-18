from __future__ import print_function
from twisted.web import server, resource, static
from twisted.internet import reactor, endpoints, task, threads
from twisted.internet.defer import Deferred
import cgi
import argparse
from StringIO import StringIO
import pandas as pd

from example_server_plot import exampleVis

uploadFormHTML = """
<html>
<body>
<form action="/upload" enctype="multipart/form-data" method="post">
    Data: <input type="file" name="dataFile"><br/>
    Row metadata: <input type="file" name="row_mdFile"><br/>
    Column metadata: <input type="file" name="col_mdFile"><br/>
    Render static image: <input type='checkbox' name='makeStatic' value='static'></br>
    <input type="submit" value="submit">
</form>
</body>
</html>
"""

singleUploadFormHTML = """
<html>
<body>
<form action="/upload" enctype="multipart/form-data" method="post">
    Data: <input type="file" name="dataFile"><br/>
    <input type="submit" value="submit">
</form>
</body>
</html>
"""
class HelloWorld(resource.Resource):
    isLeaf = True
    def render(self, request):
        # print(request)
        return '<html> Hello world! </html>'

class BasicForm(resource.Resource):
    isLeaf = True
    def render_GET(self, request):
        return '<html><body><form method="POST"><input name="the-field" type="text" /></form></body></html>'
    def render_POST(self, request):
        return '<html><body>You submitted: %s</body></html>' % (cgi.escape(request.args["the-field"][0]),)

def _prepArgs(request):
    kwargs = {}
    for k,v in request.args.iteritems():
        if k.find('File') >= 0:
            sio = StringIO(request.args[k][0])
            kwargs[k.replace('File', '')] = pd.read_csv(sio)
    if 'makeStatic' in request.args:
        kwargs['makeStatic'] = True
    html = exampleVis(**kwargs)
    request.write(html.encode('utf-8'))
    return request

class FileUpload(resource.Resource):
    isLeaf = True
    def render_GET(self, request):
        return uploadFormHTML

    def _delayedPOSTRender(self, request):
        #request.write("\n\n\nUpload complete.</body></html>")
        request.finish()

    def render_POST(self, request):
        #request.write('<html><body>')
        d = threads.deferToThread(_prepArgs, request)
        d.addCallback(self._delayedPOSTRender)
        return server.NOT_DONE_YET

class RootResource(resource.Resource):
    isLeaf = False
    def getChild(self, name, request):
        if name == '':
            return self
        return resource.Resource.getChild(self, name, request)
    def render_GET(self, request):
        return '<html><body>ROOT</body></html>'

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Start metadataVis web server.')
    parser.add_argument('--port', metavar='PORT', type=int, default=8080)
    args = parser.parse_args()

    root = RootResource()
    root.putChild('form', BasicForm())
    root.putChild('hello', HelloWorld())
    root.putChild('upload', FileUpload())
    
    site = server.Site(root)
    reactor.listenTCP(args.port, site)
    reactor.run()
