# $Id: PandaWSGIServer.py 9780 2011-11-24 03:56:34Z fine $ 
import os,pwd,thread,socket
import wsgiref.util as wu
import pmConfig.pmConfig as config
import pmUtils.pmUtils as utils
import cgi

class PandaWSGIServer(object):
   def __init__(self, staticServer= None):
      object.__init__(self)
      print " PandaWSGIServer Init" 
      self._environ = None
      self._staticServer = staticServer
      self._staticExt = ('.png','.jpg', '.gif','.js','.html','.json','.css','.ico')
      try:
         self._url = config.pandamon['url']
      except:
         self._url = None
         pass
   #___________________________________________________________________
   def config(self, key=None):
       return config
   #___________________________________________________________________
   def serverHost(self):
      hostname = socket.gethostbyaddr(socket.gethostname())
      return hostname
   #___________________________________________________________________
   def setEnviron(self, env):
      self._environ = env.copy()
      return self
   #___________________________________________________________________
   def staticExt(self):
      return self._staticExt
   #___________________________________________________________________
   def environ(self,key=None,dflt=None):
      if key == None:
         return self._environ
      else:
         return self._environ.get(key,dflt);
   #___________________________________________________________________
   def protected(self):
      """ reture whether the commication is protected """
      return self.ssl('PROTOCOL') != None or self.http('ADFS_LOGIN') != None
   #___________________________________________________________________
   def ssl(self,key):
      return self.environ('SSL_'+key.replace("-","_").upper());
   #___________________________________________________________________
   def http(self,key):
      return self.environ('HTTP_'+key.replace("-","_").upper());
   #___________________________________________________________________
   def mode(self):
      accept = self.httpAccept()
      mode = 'html'
      if accept != None and len(accept) >0:
         if self.cli() or accept.find('application/json') >=0:
            mode = 'json'
         elif  accept.find('application/javascript')>=0: 
            q = self.query()
            if q != None and q.find('callback=') >=0:
               mode = 'json'
            else:
               mode = 'script'
         else:  
            mode = 'html'
      return mode
   #___________________________________________________________________
   def length(self):
      l = 0;
      try: 
        l = int(self.environ('CONTENT_LENGTH', '0'))
      except:
         pass
      return l
   #___________________________________________________________________
   def method(self):
      return self.environ('REQUEST_METHOD')

   #___________________________________________________________________
   def post(self):
      """ get the POST file if any """
      fp = None;
      if self.method().lower() == 'post': 
        fp = self.environ('wsgi.input')
      return fp
   #___________________________________________________________________
   def query(self,key=None):
      fp = self.post() 
      qry = None
      if fp != None:
         qry = fp.readline().decode()
      else:
         qry = self.environ('QUERY_STRING')
      return qry
   #___________________________________________________________________
   def host(self,port=False,hostonly=None):
      u = self.environ('HTTP_HOST')
      if u == None: u = self.environ('SERVER_NAME')
      if hostonly == None:
         u = self.urlschema()  + "://" + u
         if port:
            try:
               p = int(self.port())
               if p !=  80:
                  u = "%s:%s" % (u,p)
            except:
               pass
      return u
   #___________________________________________________________________
   def branchUrl(self):
      s = self.script()
      if self._url:
         b = self.branch()
         if b != '': s = "%s/~%s" % (self._url,b )
      return s
 #___________________________________________________________________
   def appgroup(self):
      # return the group name of the server instance if any
      # the group name is the first portion of the SCRIPT_NAME
      # with the "~" as its first symbol followed by the the "application group name" if  any
      return self.environ('mod_wsgi.application_group')
      
   #___________________________________________________________________
   def branch(self):
      # return the branch name of the server instance if any
      # the branch name is the first portion of the SCRIPT_NAME
      # with the "~" as its first symbol followed by the the "branch name" if  any
      branch = ''
      try:
         script = self.script(absolute=False).split('/',1)
         if script[0][0]=='~': branch = script[0][1:]
      except:
         pass
      return branch

   #___________________________________________________________________
   def fileURL(self,fileType=''):
      """ URL to access the static content like images, Javascript files  etc"""
      vers = self.version(host=True)
      url = vers.get('version','')
      # if url != '': url = "~%s" % url
      fileurl = "%s/static/%s" % (url, fileType)
      print " pmUtils.142 --------->  ", fileurl, fileType, vers
      return fileurl

   #___________________________________________________________________
   def fileImageURL(self):
     return self.fileURL("images")

   #___________________________________________________________________
   def fileScriptURL(self):
     return self.fileURL("js")

   #___________________________________________________________________
   def fileScriptCSS(self):
     return self.fileURL("css")
   #___________________________________________________________________
   def version(self,host=None):
      """ return {version :version, pathname:pathname, application:application } """
      scriptName = self.script().split('/')
      scriptURL  = self.script('URL').split('/')
      # print " PandaWSGIServer:160 ", scriptURL, self.script('URL'),self.script('URI'),self.script(),self.environ()
      version     = {}
      pathname    = None
      application = None
      lscript =  len(scriptURL) 
      if lscript > 1:
         if len(scriptURL[1]) > 1 and scriptName[-1] == scriptURL[1] and scriptURL[1][0]=='~': 
            version['version'] = scriptURL[1][1:] if host == None else "//%s/~%s" % (self.host(hostonly=True),scriptURL[1][1:])
            s = scriptURL[0:1]
            if lscript>2:  
               s+=scriptURL[2:]
               if len(s)>2:
                  version['pathname'] = '/'.join(s[:-2])
         version['application'] = scriptURL[-1]
         # print  "  --> PandaWSGIServer:175 ", version
      return version
   #___________________________________________________________________
   def script(self,key='NAME',absolute=True):
      """ key = URL | FILENAME | URI | URL | NAME 
          absolute=False - remove the leading "/"
      """
      k = key.upper()
      r = self.environ('SCRIPT_'+k);
      if k in ("URL","NAME")  and self.environ('SCRIPT_NAME'):
        # special legacy case
        r = r.replace('/pandamon/query','').replace('/pandamon/script','')
      if not absolute and len(r) > 0 and r[0]=='/': 
         if len(r) > 1: r = r[1:]
         else: r = ''
      return r

   #___________________________________________________________________
   def port(self):
      return self.environ('SERVER_PORT')
   #___________________________________________________________________
   def urlschema(self):
      return self.environ('wsgi.url_scheme')

   #___________________________________________________________________
   def show(self,other=None):
      import pprint
      pprint.pprint (self.environ() )
      if other: pprint.pprint (self.environ() )

   #___________________________________________________________________
   def client(self):
      client = self.environ('REMOTE_ADDR')
      x_client = self.environ('HTTP_X_FORWARDED_FOR')
      if x_client != None and x_client != '': client = x_client
      return client

   #___________________________________________________________________
   def path(self):
      return self.environ('PATH_INFO')

   #___________________________________________________________________
   def jsonp(self):
      q = self.query()
      if q != None:
        return q.find('callback=')>=0 and self.mode() == 'json'
      return False  

   #___________________________________________________________________
   def cli(self):
      a= self.httpAccept()
      return a == 'text/plain' or a == "*/*"
   #___________________________________________________________________
   def user(self):
      """ Return the client user name from the client's certificate or CERN SSO """
      u = None
      if self.protected():
         u = self.http('ADFS_FULLNAME')
         if u == None:
            u = self.ssl('CLIENT_S_DN_CN')
      return u
         
   #___________________________________________________________________
   def certificate(self):
      u = None
      if self.protected():
         u = self.ssl('CLIENT_S_DN')
      return u
   #___________________________________________________________________
   def email(self):
      u = None
      if self.protected():
         u = self.http('ADFS_EMAIL')
      return u
   #___________________________________________________________________
   def username(self):
     """ return the username the Web server is working under """
     return pwd.getpwuid(os.getuid())[0]

   #___________________________________________________________________
   def cookie(self):
      import Cookie 
      ask = "COOKIE"   
      cook = self.http(ask)
      c = None
      if cook != None and cook.strip() != '':
          c = Cookie.SimpleCookie()
          c.load(cook)
      return c
   #___________________________________________________________________
   def httpAccept(self,key=None):
      ask = "Accept"
      if key: ask += "-%s" % key
      return self.http(ask)

   #___________________________________________________________________
   def __call__(self, environ, start_response):
      """ Process GET queries """
      raise ValueError("Undefined wsgi applcation")
      
   #________________________________________________________________________
   def threadId(self):
      return thread.get_ident();
   #________________________________________________________________________
   def getppid(self):
      return  os.getppid()

   #________________________________________________________________________
   def getpid(self):
      return  os.getpid()

   #________________________________________________________________________
   def assmemblerUrl(self,option='full',env=None):
      # full  - recreate the full URL
      # host  - recreate the host
      # query - recreate the query 
      from urllib import quote
      environ =  env if env != None else self.environ()
      url = ""
      if option != 'query':
         url += environ['wsgi.url_scheme']+'://'

         if environ.get('HTTP_HOST'):
            url += environ['HTTP_HOST']
         else:
            url += environ['SERVER_NAME']

            if environ['wsgi.url_scheme'] == 'https':
                 if environ['SERVER_PORT'] != '443':
                    url += ':' + environ['SERVER_PORT']
            else:
                 if environ['SERVER_PORT'] != '80':
                    url += ':' + environ['SERVER_PORT']
      if option == 'full' or option == 'host':
         url += quote(environ.get('SCRIPT_NAME', ''))
      if option == 'full'  or option == 'query':
         url += quote(environ.get('PATH_INFO', ''))
      if option == 'full' or option == 'query':
         q= self.query();
         if utils.isValid(q):
             url += '?' + q
      return url             
   #___________________________________________________________________
   def static(self, environ, start_response):
      """ Process the static files """
      path =  self.environ('PATH_INFO')
      if  self._staticServer and path != '/favicon.ico':
         (file,ext) = os.path.splitext(path)
         if ext in self.staticExt() and os.path.isfile(os.path.realpath(self._staticServer.root) + path):
            return self._staticServer(environ, start_response)
      return None
   #___________________________________________________________________
   @staticmethod
   def urisplit(uri):
      """
      Basic URI Parser according to STD66 aka RFC3986
      >>> urisplit("scheme://authority/path?query#fragment")
      ('scheme', 'authority', 'path', 'query', 'fragment')
      """
      # regex straight from STD 66 section B
      regex = '^(([^:/?#]+):)?(//([^/?#]*))?([^?#]*)(\?([^#]*))?(#(.*))?'
      p = re.match(regex, uri).groups()
      scheme, authority, path, query, fragment = p[1], p[3], p[4], p[6], p[8]
      #if not path: path = None
      return (scheme, authority, path, query, fragment)
      
