# -*- coding: utf8 -*-
#!/usr/bin/env python
"""
static - A simple WSGI-based web server to serve static content.

Copyright (c) 2011  Valeri Fine <val.fine@gmail.com>
$Id: StaticWSGIServer.py 9964 2011-12-08 00:47:42Z fine $
Copyright (c) 2010  Daniel Dotsenko <dotsa@hotmail.com>
Copyright (C) 2006-2009 Luke Arno - http://lukearno.com/

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library; if not, write to:

The Free Software Foundation, Inc., 
51 Franklin Street, Fifth Floor, 
Boston, MA  02110-1301, USA.
"""

import time
import os
import email.utils
from wsgiref.headers import Headers
import mimetypes
import gzip


class StaticWSGIServer(object):
   """
   A simple WSGI-based static content server app.

   Relies on WSGIHandlerSelector for prepopulating some needed environ
   variables, cleaning up the URI, setting up default error handlers.

   Inputs:
      path_prefix (mandatory)
         String containing a file-system level path behaving as served root.

      block_size (optional)
         File reader's buffer size. Defaults to 65536.

      gzip_response (optional) (must be named arg)
         Specify if we are to detect if gzip compression is supported
         by client and gzip the output. False by default.
   """

   def __init__(self, pathprefix, block_size = 65536):
      object.__init__(self)
      self.root = pathprefix
      self.block_size = block_size
      self.gzip_response = False

   def notFoundResponse(self,start_response):
      headerbase = [('Content-Type', 'text/plain')]
      start_response("404 Not Found", headerbase)
      return [''] 

   def __call__(self, environ, start_response):
      selector_matches = (environ.get('wsgiorg.routing_args') or ([],{}))[1]
      if 'working_path' in selector_matches:
         # working_path is a custom key that I just happened to decide to use
         # for marking the portion of the URI that is palatable for static serving.
         # 'working_path' is the naselector_matchesme of a regex group fed to WSGIHandlerSelector
         path_info = ['working_path'].decode('utf8')
      else:
         path_info = environ.get('PATH_INFO', '').decode('utf8')

      # this, i hope, safely turns the relative path into OS-specific, absolute.
      full_path = os.path.abspath(os.path.join(self.root, path_info.strip('/')))

      if not os.path.isfile(full_path):
         return self.notFoundResponse(start_response)

      # try:
      if True:
         mtime = os.stat(full_path).st_mtime
         etag, last_modified =  str(mtime), email.utils.formatdate(mtime)

         headers = [
            ('Content-type', 'text/plain'),
            ('Date', email.utils.formatdate(time.time())),
            ('Last-Modified', last_modified),
            ('ETag', etag)
         ]
         headersIface = Headers(headers)

         headersIface['Content-Type'] = mimetypes.guess_type(full_path)[0] or 'application/octet-stream'

         file_like = open(full_path, 'rb')

         # i have a feeling that WSGI server is doing the un-gziping transparently ang gives the body unpacked.
         # Depending on WSGI server, response could be gziped transparently as well.
         # Will need to check, but it may be preferable to forego compression here...
         if self.gzip_response and bool( (environ.get('HTTP_ACCEPT_ENCODING') or '').find('gzip') > -1 ):
            _file_out = tempfile.SpooledTemporaryFile(max_size=327679, mode='w+b')
            _zfile = gzip.GzipFile(mode = 'wb',  fileobj = _file_out)
            file_like.seek(0)
            _zfile.write(file_like.read())
            _zfile.close()
            file_like.close()
            file_like = _file_out
            file_like.seek(0)
            headersIface['Content-Encoding'] = 'gzip'

         start_response('200 OK', headers)

         if 'wsgi.file_wrapper' in environ:
            return environ['wsgi.file_wrapper']( file_like, self.block_size )
         else:
            return iter( lambda: file_like.read(self.block_size), '' )
#      except:
#         return self.canned_handlers('not_found', environ, start_response)
