#!/bin/env python
"""
Panda monitor main routine
$Id: pmMain.py 14824 2013-04-03 19:15:49Z fine $
"""
import os, sys, re, time, commands
import email.utils
from wsgiref.headers import Headers
from datetime import datetime, timedelta

import threading

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

import BaseHTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler
if not "." in sys.path: sys.path.append('.')
try:
   from pmConfig import pmConfig as config
   from pmUtils import pmUtils as utils
   from pmServer.pmHandler import pmHandler
   from pmUtils.pmState import pmstate
   from pandalogger.PandaLogger import PandaLogger
except:
    print sys.path
    raise
_logger = PandaLogger().getLogger('pmMain')

def toLog(str,req):
    tmpstr = "ps h -p %s -o pcpu,pmem,cputime" % (os.getpid())
    tmplist = tmpstr.split()
    _logger.debug("%s %s: ppid=%s pid=%s cpu=%s%% mem=%s%% query=%s client=%s" % \
            (str, datetime.utcnow(), os.getppid(), os.getpid(), tmplist[0], tmplist[1], req.unparsed_uri, req.get_remote_host()))
    return

def mmCode(format):
   mmcode = {    'json'   : 'application/json'
               , 'script' : 'application/javascript'
               , 'html'   : 'text/html'
               , 'default': 'text/html'
             }
   return   mmcode.get(format,"text/html")

#___________________________________________________________________________________
from PandaWSGIServer import PandaWSGIServer 
class PandaMonWSGIServer(PandaWSGIServer):

   #___________________________________________________________________
   def __init__(self, staticServer= None): 
      PandaWSGIServer.__init__(self,staticServer)
      self._requesthandler = pmHandler(server=self,config=config)

   #___________________________________________________________________
   def __call__(self, environ, start_response):
      """ Process GET queries """
      self.setEnviron(environ)
      if self.method() == "GET" or  self.method() == "POST":
         # self.server().branchUrl() = self.assmemblerUrl('host')
         pmstate().script = self.script()
         pmstate().dev = True  # Standalone version is dev
         print "=== pmMain 88  pandamon query <%s> thread=%s  static = %s " %  (self.path(), threading.currentThread(), self._staticServer)
         # self.show()
         # print "----COOKIES ---- <%s> " % self.cookie()
         
         static = self.static( environ, start_response) 
         if static: return static
         requesthandler = self._requesthandler
         requesthandler.starting()
         ( page, format,cached ) = requesthandler.do_GET()
         requesthandler.finishing()
         
         tmptmptime = datetime.utcnow()
         courseness = 10
         mindiff = tmptmptime.minute - int( tmptmptime.minute / courseness ) * courseness
         someminutes = timedelta( minutes=mindiff )
         lastmodtime = tmptmptime - someminutes

         expireminutes = timedelta( minutes=5 )
         expiretime = tmptmptime + expireminutes

         # http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html 
         headers = [
           ('Content-type' , 'text/plain'),
           ('Date'         , email.utils.formatdate(time.time())),
#           ("Last-Modified", lastmodtime.strftime("%a, %d %b %Y %H:%M:00 GMT") ),
#           ("Expires"      , expiretime.strftime("%a, %d %b %Y %H:%M:%S GMT") ),
         ]
         try:
            if cached == None: cached = timedelta(seconds=300)
            if isinstance(cached,timedelta) :
               headers.append(('Cache-Control', 's-maxage=%s' % 0 ))  # for varnish
               headers.append(('Cache-Control', 'max-age=%s' % cached.seconds)) # for the client
            elif isinstance(cached,str):
               headers.append(('Cache-Control', '%s' % cached)) 
            else:
               for c,v  in cached.iteritems():
                  headers.append(('Cache-Control', '%s=%s' % (c,v)))
         except:
             raise ValueError("Wrong cache control value %s ", cached )
         headersIface = Headers(headers)
         headersIface['Content-type']=mmCode(format)
         start_response('200 OK', headers)
      else:
         raise ValueError("Can not process the client %s request yet" % self.environ('REQUEST_METHOD'))
      return [page]
        
if __name__ == '__main__':
    pmstate().instanceName = 'dev'
    debugmode = True
    if pmstate().host == 'localhost':
        # URLs will be built using localhost, but server runs against real host
        host = commands.getoutput('/bin/hostname')
    else:
        host = pmstate().host
    if len(sys.argv) > 1 and sys.argv[1] == 'local':
        myinstance = 'local' 
    else:
        myinstance = ''
    print "Running Panda monitor daemon at http://%s:%s" % (host, int(pmstate().port))
    # wgsi_server(host, int(pmstate().port))
    httpd = BaseHTTPServer.HTTPServer((host, int(pmstate().port)), PythonHTTPHandler)
    httpd.serve_forever()       
