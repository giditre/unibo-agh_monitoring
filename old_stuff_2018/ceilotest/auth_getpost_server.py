#!/usr/bin/env python3
 
"""Simple HTTP Server With Upload.

This module builds on BaseHTTPServer by implementing the standard GET
and HEAD requests in a fairly straightforward manner.

see: https://gist.github.com/UniIsland/3346170
"""
 
 
__version__ = "0.1"
__all__ = ["SimpleHTTPRequestHandler"]
__author__ = "bones7456"
__home_page__ = "http://li2z.cn/"
 
import os
import posixpath
import http.server
import urllib.request, urllib.parse, urllib.error
import cgi
import shutil
import mimetypes
import re
from io import BytesIO

import base64
import json

from time import strftime, gmtime
from socket import gethostname
 
class SimpleHTTPRequestHandler(http.server.BaseHTTPRequestHandler):
 
    """Simple HTTP request handler with GET/HEAD/POST commands.

    This serves files from the current directory and any of its
    subdirectories.  The MIME type for files is determined by
    calling the .guess_type() method. And can reveive file uploaded
    by client.

    The GET/HEAD/POST requests are identical except that the HEAD
    request omits the actual contents of the file.

    """
 
    server_version = "SimpleHTTPWithUpload/" + __version__ 

    def do_HEAD(self):
        """Serve a HEAD request."""
        f = self.send_head()
        if f:
            f.close()

    def do_AUTHHEAD(self):
        self.send_response(401)
        self.send_header('WWW-Authenticate', 'Basic realm="Demo Realm"')
        #self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_GET(self):
        """Serve a GET request."""

        key = self.server.get_auth_key()

        if self.headers.get('Authorization') == 'Basic ' + str(key):

            if self.path in ['/', '/index.html']:
              if args.cmd:
                print('Running command: ' + args.cmd)
                os.system(args.cmd)
              print('Refresh index.html')
              self.server.build_index(self.server.served_dir)

            f = self.send_head()
            if f:
                self.copyfile(f, self.wfile)
                f.close()
        
        else:
          # Wrong authentication (either bad method or bad credentials)
          # Present frontpage with user authentication
          self.do_AUTHHEAD()

          response = {
              'success': False,
              'error': 'Wrong authentication'
          }
          self.wfile.write(bytes(json.dumps(response), 'utf-8'))
 
    def do_POST(self):
        """Serve a POST request."""

        if not self.server.post_enabled:
          # POST requests are NOT enabled
          response = {
              'success': False,
              'error': 'POST requests are NOT enabled.'
          }
          self.wfile.write(bytes(json.dumps(response), 'utf-8'))
        
        else:
  
          key = self.server.get_auth_key()
  
          ''' Present frontpage with user authentication. '''
          if self.headers.get('Authorization') == None:
              self.do_AUTHHEAD()
  
              response = {
                  'success': False,
                  'error': 'No auth header received'
              }
  
              self.wfile.write(bytes(json.dumps(response), 'utf-8'))        
  
          elif self.headers.get('Authorization') == 'Basic ' + str(key):
   
            r, info = self.deal_post_data()
            print((r, info, "by: ", self.client_address))
            f = BytesIO()
            f.write(b'<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">')
            f.write(b"<html>\n<title>Upload Result Page</title>\n")
            f.write(b"<body>\n<h2>Upload Result Page</h2>\n")
            f.write(b"<hr>\n")
            if r:
                f.write(b"<strong>Success:</strong>")
            else:
                f.write(b"<strong>Failed:</strong>")
            f.write(info.encode())
            f.write(("<br><a href=\"%s\">back</a>" % self.headers['referer']).encode())
            f.write(b"<hr><small>Powerd By: bones7456, check new version at ")
            f.write(b"<a href=\"http://li2z.cn/?s=SimpleHTTPServerWithUpload\">")
            f.write(b"here</a>.</small></body>\n</html>\n")
            length = f.tell()
            f.seek(0)
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.send_header("Content-Length", str(length))
            self.end_headers()
            if f:
                self.copyfile(f, self.wfile)
                f.close()
          else:
            # Wrong authentication (either bad method or bad credentials)
            response = {
                'success': False,
                'error': 'Wrong authentication'
            }
            self.wfile.write(bytes(json.dumps(response), 'utf-8'))
        
    def deal_post_data(self):
        content_type = self.headers['content-type']
        if not content_type:
            return (False, "Content-Type header doesn't contain boundary")
        boundary = content_type.split("=")[1].encode()
        remainbytes = int(self.headers['content-length'])
        line = self.rfile.readline()
        remainbytes -= len(line)
        if not boundary in line:
            return (False, "Content NOT begin with boundary")
        line = self.rfile.readline()
        remainbytes -= len(line)
        fn = re.findall(r'Content-Disposition.*name="file"; filename="(.*)"', line.decode())
        if not fn:
            return (False, "Can't find out file name...")
        path = self.translate_path(self.path)
        fn = os.path.join(path, fn[0])
        line = self.rfile.readline()
        remainbytes -= len(line)
        line = self.rfile.readline()
        remainbytes -= len(line)
        try:
            out = open(fn, 'wb')
        except IOError:
            return (False, "Can't create file to write, do you have permission to write?")
                
        preline = self.rfile.readline()
        remainbytes -= len(preline)
        while remainbytes > 0:
            line = self.rfile.readline()
            remainbytes -= len(line)
            if boundary in line:
                preline = preline[0:-1]
                if preline.endswith(b'\r'):
                    preline = preline[0:-1]
                out.write(preline)
                out.close()
                return (True, "File '%s' upload success!" % fn)
            else:
                out.write(preline)
                preline = line
        return (False, "Unexpect Ends of data.")
 
    def send_head(self):
        """Common code for GET and HEAD commands.

        This sends the response code and MIME headers.

        Return value is either a file object (which has to be copied
        to the outputfile by the caller unless the command was HEAD,
        and must be closed by the caller under all circumstances), or
        None, in which case the caller has nothing further to do.

        """
        path = self.translate_path(self.path)
        f = None
        if os.path.isdir(path):
            if not self.path.endswith('/'):
                # redirect browser - doing basically what apache does
                self.send_response(301)
                self.send_header("Location", self.path + "/")
                self.end_headers()
                return None
            for index in "index.html", "index.htm":
                index = os.path.join(path, index)
                if os.path.exists(index):
                    path = index
                    break
            else:
                return self.list_directory(path)
        ctype = self.guess_type(path)
        try:
            # Always read in binary mode. Opening files in text mode may cause
            # newline translations, making the actual size of the content
            # transmitted *less* than the content-length!
            f = open(path, 'rb')
        except IOError:
            self.send_error(404, "File not found")
            return None
        self.send_response(200)
        self.send_header("Content-type", ctype)
        fs = os.fstat(f.fileno())
        self.send_header("Content-Length", str(fs[6]))
        self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
        self.end_headers()
        return f
 
    def list_directory(self, path):
        """Helper to produce a directory listing (absent index.html).

        Return value is either a file object, or None (indicating an
        error).  In either case, the headers are sent, making the
        interface the same as for send_head().

        """
        try:
            list = os.listdir(path)
        except os.error:
            self.send_error(404, "No permission to list directory")
            return None
        list.sort(key=lambda a: a.lower())
        f = BytesIO()
        displaypath = cgi.escape(urllib.parse.unquote(self.path))
        f.write(b'<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">')
        f.write(("<html>\n<title>Directory listing for %s</title>\n" % displaypath).encode())
        f.write(("<body>\n<h2>Directory listing for %s</h2>\n" % displaypath).encode())
        f.write(b"<hr>\n")
        f.write(b"<form ENCTYPE=\"multipart/form-data\" method=\"post\">")
        f.write(b"<input name=\"file\" type=\"file\"/>")
        f.write(b"<input type=\"submit\" value=\"upload\"/></form>\n")
        f.write(b"<hr>\n<ul>\n")
        for name in list:
            fullname = os.path.join(path, name)
            displayname = linkname = name
            # Append / for directories or @ for symbolic links
            if os.path.isdir(fullname):
                displayname = name + "/"
                linkname = name + "/"
            if os.path.islink(fullname):
                displayname = name + "@"
                # Note: a link to a directory displays with @ and links with /
            f.write(('<li><a href="%s">%s</a>\n'
                    % (urllib.parse.quote(linkname), cgi.escape(displayname))).encode())
        f.write(b"</ul>\n<hr>\n</body>\n</html>\n")
        length = f.tell()
        f.seek(0)
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-Length", str(length))
        self.end_headers()
        return f
 
    def translate_path(self, path):
        """Translate a /-separated PATH to the local filename syntax.

        Components that mean special things to the local file system
        (e.g. drive or directory names) are ignored.  (XXX They should
        probably be diagnosed.)

        """
        # abandon query parameters
        path = path.split('?',1)[0]
        path = path.split('#',1)[0]
        path = posixpath.normpath(urllib.parse.unquote(path))
        words = path.split('/')
        words = [_f for _f in words if _f]
        path = os.getcwd()
        for word in words:
            drive, word = os.path.splitdrive(word)
            head, word = os.path.split(word)
            if word in (os.curdir, os.pardir): continue
            path = os.path.join(path, word)
        return path
 
    def copyfile(self, source, outputfile):
        """Copy all data between two file objects.

        The SOURCE argument is a file object open for reading
        (or anything with a read() method) and the DESTINATION
        argument is a file object open for writing (or
        anything with a write() method).

        The only reason for overriding this would be to change
        the block size or perhaps to replace newlines by CRLF
        -- note however that this the default server uses this
        to copy binary data as well.

        """
        shutil.copyfileobj(source, outputfile)
 
    def guess_type(self, path):
        """Guess the type of a file.

        Argument is a PATH (a filename).

        Return value is a string of the form type/subtype,
        usable for a MIME Content-type header.

        The default implementation looks the file's extension
        up in the table self.extensions_map, using application/octet-stream
        as a default; however it would be permissible (if
        slow) to look inside the data to make a better guess.

        """
 
        base, ext = posixpath.splitext(path)
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        ext = ext.lower()
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        else:
            return self.extensions_map['']
 
    if not mimetypes.inited:
        mimetypes.init() # try to read system mime.types
    extensions_map = mimetypes.types_map.copy()
    extensions_map.update({
        '': 'application/octet-stream', # Default
        '.py': 'text/plain',
        '.c': 'text/plain',
        '.h': 'text/plain',
        })

class CustomHTTPServer(http.server.HTTPServer):
    key = ''

    def __init__(self, address, handlerClass=SimpleHTTPRequestHandler, post_enabled=False):
        super().__init__(address, handlerClass)
        # define served directory
        self.served_dir = os.path.dirname(os.path.abspath(__file__))
        self.server_info = gethostname() + ' ' + self.served_dir
        self.post_enabled = post_enabled
        # print('HTTP server ' + self.server_info + ' at http://' + str(address[0]) + ':' + str(address[1]), end='\n\n')
        print('HTTP server {} at http://{}:{} - serving {} requests'.format(self.server_info, address[0], address[1], 'GET' if not post_enabled else 'GET/POST'),  end='\n\n')

    def set_auth(self, username, password):
        self.key = base64.b64encode(bytes('%s:%s' % (username, password), 'utf-8')).decode('ascii')

    def get_auth_key(self):
        return self.key 

    def build_index(self, startpath):

      def bytes2human(n_bytes, step=1024, prec=1):
        '''
        Convert size in bytes to human readable format
        '''
        # a simple check
        if n_bytes < 0:
            print('Error: n_bytes ' + str(n_bytes) + ' cannot be negative')
        # convert n_bytes to float
        n_bytes = float(n_bytes)
        # unit will be empty if number is in bytes, or it will be K, M G, T
        unit = ''
        # if remaining n_bytes is larger than step, divide and set larger unit
        # last n_bytes and unit will be the displayed value
        if (n_bytes / step) >= 1:
            n_bytes /= step
            unit = 'K'
        if (n_bytes / step) >= 1:
            n_bytes /= step
            unit = 'M'
        if (n_bytes / step) >= 1:
            n_bytes /= step
            unit = 'G'
        if (n_bytes / step) >= 1:
            n_bytes /= step
            unit = 'T'
        # round n_bytes to requested precision
        n_bytes = round(n_bytes, prec)
        # return formatted string
        return '{: >6} {:1}'.format(str(n_bytes), unit)

      with open(self.served_dir + '/index.html', 'w') as index:
        # build index page, starting from headers with styles
        index.write("""<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
          <html>
          <head>
            <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
            <title>""" + self.server_info + """</title>
            <style type="text/css">
             <!--
             BODY { font-family : ariel, monospace, sans-serif; }
             P { font-weight: normal; font-family : ariel, monospace, sans-serif; color: black; background-color: transparent;}
             B { font-weight: bold; font-size: 150%; color: #cc0000; background-color: transparent;}
             A:visited { font-weight : normal; text-decoration : none; background-color : transparent; margin : 0px 0px 0px 0px; padding : 0px 0px 0px 0px; display: inline; }
             A:link    { font-weight : normal; text-decoration : none; margin : 0px 0px 0px 0px; padding : 0px 0px 0px 0px; display: inline; }
             A:hover   { color : #000000; font-weight : normal; text-decoration : underline; background-color : yellow; margin : 0px 0px 0px 0px; padding : 0px 0px 0px 0px; display: inline; }
             A:active  { color : #000000; font-weight: normal; background-color : transparent; margin : 0px 0px 0px 0px; padding : 0px 0px 0px 0px; display: inline; }
             .VERSION { font-size: small; font-family : arial, sans-serif; }
             .NORM  { color: black;  background-color: transparent;}
             .FIFO  { color: purple; background-color: transparent;}
             .CHAR  { color: yellow; background-color: transparent;}
             .DIR   { color: blue;   background-color: transparent;}
             .BLOCK { color: yellow; background-color: transparent;}
             .LINK  { color: aqua;   background-color: transparent;}
             .SOCK  { color: fuchsia;background-color: transparent;}
             .EXEC  { color: green;  background-color: transparent;}
             -->
            </style>
          </head>
          <body>""")
        # scan all folders and subfolders, and add a list of href'd files, in HTML format
        for root, dirs, files in os.walk(startpath):
          # write header for current folder
          index.write('<b>' + str(root) + '</b><br><br>\n')
          for f in sorted(files):
              # file size in human readable format
              size = bytes2human(os.stat(root + '/' + f).st_size)
              # modified date and time in human readable format
              mod = strftime("%d %b %Y %H:%M", gmtime(int(os.stat(root + '/' + f).st_mtime)))
              # field combining size and last mod time, formatted for tidiness
              # &nbsp; is the HTML tag that prints a visible (and indivisible) blank space
              info = '[ {:>7} | {:<} ] '.format(size, mod).replace(' ', '&nbsp;')
              # build path for the hyperlink for the current file
              href = root.replace(self.served_dir, '') + '/' + f
              # build line in HTML format for the (linked) current file
              href_f = '<a href="{}">{}</a>'.format(href, f)
              # write the entry line in the HTML page
              index.write('{} {: <18}<br>\n'.format(info, href_f))
          index.write('<br>\n')
        index.write('</body>\n</html>\n')
 
if __name__ == '__main__':
  import argparse

  parser = argparse.ArgumentParser()

  parser.add_argument("ip", help="server IP address", nargs='?', default='127.0.0.1')
  parser.add_argument("port", help="server TCP port", nargs='?', default='8000')
  parser.add_argument("user", help="server username", nargs='?', default='demo')
  parser.add_argument("pw", help="server password", nargs='?', default='demo')
  parser.add_argument("-P", "--post", help="enable POST requests (WARNING: DANGEROUS)", action="store_true")
  parser.add_argument("--cmd", help="bash command to be run before refreshing index.html")
  
  args = parser.parse_args()

  # store and print parsed arguments
  print('Information from arguments...')
  print('...server IP: ' + args.ip)
  print('...server port: ' + args.port)
  print('...server user: ' + args.user)
  print('...server password: ' + args.pw)
  print('...POST requests are {}'.format('ENABLED' if args.post else 'DISABLED'))
  if args.cmd:
    print('...command to be run before index refresh: ' + args.cmd)
  print('\n')

  server = CustomHTTPServer((args.ip, int(args.port)), post_enabled=True if args.post else False)
  server.set_auth(args.user, args.pw)
  server.serve_forever()

