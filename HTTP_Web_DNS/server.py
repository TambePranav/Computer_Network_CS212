import sys
from http.server import SimpleHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
PORT = 5500


class MyHTTPRequestHandler (SimpleHTTPRequestHandler):

    def do_GET(self):

        # check if the request contained a cookie called "F00123"
        self.cookieHeader = self.headers.get('Cookie')
        if self.cookieHeader and "F00" in self.cookieHeader:
            # add some extra text to the html filJj
            if "index" in self.path:
                self.path = '/index.html'
            elif "website2" in self.path:
                self.path = '/website2.html'
            elif "j1" in self.path:
                self.path = '/j1.js'
                
         
        SimpleHTTPRequestHandler.do_GET(self)

    def end_headers(self):
        self.send_my_headers()
        SimpleHTTPRequestHandler. end_headers(self)

    def send_my_headers(self):
        self.send_header("set-Cookie", "F00123")


class ThreadingSimpleServer(ThreadingMixIn, HTTPServer):
    pass


server = ThreadingSimpleServer(('10.196.12.140', PORT), MyHTTPRequestHandler)
try:
    while 1:
        server.handle_request()
except KeyboardInterrupt:
    print('Finished. ')
