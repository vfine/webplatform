#!/usr/local/bin/python
# $Id: pmModule.py 9426 2011-10-22 10:51:06Z fine $
from pmObject import pmObject

import sys,os
import inspect
import urlparse
import cgi
import urllib
from datetime import datetime
import time

from pmUtils.Stopwatch import Stopwatch
from pmUtils import pmUtils as utils

""" Base class for all Panda Modules  """
class pmRoles:
   _roleJson   = "json"
   _roleHtml   = "html"
   _roleScript = "script"
   _roleParams = "params"
   _roleExtra  = "extra"   
   _roleTiming = "timing"
   _roleObject = "object"
   _roleCacheControl = "cache"
   _roles = (_roleJson,_roleHtml,_roleScript,_roleParams,_roleExtra,_roleTiming,_roleCacheControl, _roleObject)
   @classmethod
   def json(cls):   return  cls._roleJson
   @classmethod
   def html(cls):   return  cls._roleHtml
   @classmethod
   def script(cls): return  cls._roleScript
   @classmethod
   def params(cls): return  cls._roleParams
   @classmethod
   def extra(cls):  return  cls._roleExtra
   @classmethod
   def timing(cls):  return  cls._roleTiming
   @classmethod
   def cache(cls):  return  cls._roleCacheControl
   @classmethod
   def object(cls): return  cls.json() # transition cls._roleObject

class pmModule(pmObject):
   _moduleFile = os.path.join(__file__.rpartition('/')[0].rsplit('/',1)[0],'pmModules')

   #______________________________________________________________________________________      
   def __init__(self,name=None,parent=None,obj=None,server=None, config=None):
      self._moduleTimers = {}
      self._moduleTimers['total'] = Stopwatch()
      self._moduleTimers['UI']    = Stopwatch(False)
      self._server  = server
      self._rootDir = ".ui"
      self._roleDir = "%s/%s" % (self._rootDir, ".role")
      self._role = pmRoles.object()
      self._moduleDir = '.module'
      self._config = config
      self._defaultJs = """
            function(tag,data) { 
                  var defout = "<pre>\n" + JSON.stringify(data, undefined, 2) + "\n" + "</pre>\n";
                  $(tag).html(defout);
            } """
      if parent != None: parent = parent.mkdir(self._moduleDir);
      pmObject.__init__(self,name,parent,obj)
#      aa = self.publishMenu()
   #______________________________________________________________________________________      
   def parentModule(self):
      p = self.parent()
      try:
         if not isinstance(p, pmModule): p = p.parent()
      except:
         pass
      return p
   #______________________________________________________________________________________      
   def config(self,newconfig=None):
      if newconfig: self._config=newconfig
      c = self._config
      if c == None:
         try: 
           c = self.parentModule().config()
         except: 
           pass
      return c
   #______________________________________________________________________________________      
   def server(self,newserver=None):
      if newserver: self._server = newserver
      s = self._server
      if s == None:
         try: 
            s = self.parentModule().server()
         except: 
            pass
      return s

   #______________________________________________________________________________________      
   def defaultJs(self):
      return self._defaultJs
   #______________________________________________________________________________________      
   def publishMenu(self,title=None):
      return self.publish({self.objectName():"menu URL"},'.menu','menu')

   #______________________________________________________________________________________      
   def makeDocUI(self, object,label=None):
      """ Create the documentation for the UI """
      className = ''
      for name, obj in inspect.getmembers(object):
         if name == 'im_class': 
            className = obj.__name__
            break
      if label != None:   className = className +"."+label       
      odoc = '<div class="ui-widget">'
      doc = inspect.getdoc(object)
      (args, varargs, keywords, defaults) = inspect.getargspec(object)
      module = className
      ndef = len(defaults) if defaults else 0
      largs = len(args) if args else 0
      iDfl = largs - ndef
      pars = ''
      sep = ''
      for i,arg in enumerate(args):
         if arg == 'self': continue
         pars +=  "%s%s" % (sep, arg)
         if sep == "": sep = '&#38'
         if i >= iDfl: pars += "=%s" % defaults[i-iDfl]
      url = "%(host)s/%(module)s"  % { 'host': self.server().host() , 'module' : module }
      if pars != '': 
         url += "?%s" % pars
      odoc += '<span class="ui-corner-all ui-widget ui-widget-header"><b>Module: %s</b></span>' % module
      if doc != None and doc != '':
         odoc += ": %s"  %doc
      if url != '':
         src = "<a title='One may omit the default values' href='%(url)s'>%(url)s</a>" % { 'url' : url } 
         odoc += """<hr><b title='The default values of the API parameters are shown.'>API:</b><br><a href='http://curl.haxx.se/docs/manpage.html'>curl</a> --compressed  %(url)s
                 """ % { 'url' : src.replace('=None','=') } 
      odoc += "</div>"
      return odoc

   #______________________________________________________________________________________      
   def makeHelpUI(self,f,publish=True):
      """ Create and publish  if needed the document for the 'f' object """
      h = self.makeDocUI(f)
      if publish:
         self.publishHelp(h) 
      return h

   #______________________________________________________________________________________      
   def starting(self):
      pass
   #______________________________________________________________________________________      
   def finishing(self):
      pass
   #______________________________________________________________________________________      
   def modules(self):
      return self[self._moduleDir]
      
   #______________________________________________________________________________________      
   def module(self,name):
      mods = self.modules()
      if mods != None:
         mods = mods[name]
      return mods

   #______________________________________________________________________________________      
   def role(self):
      return  self._role
   #______________________________________________________________________________________      
   def setRole(self,role):
      oldRole = self.role()
      self._role=role
      return  self.role()

   #______________________________________________________________________________________      
   def doScript(self):
      """ provides the javascript function to client-site data rendering 
        function(tag, data) { . . . }
        where tag - is the HTML tag (strinng in css notation) the data is to be rendered into
              data - the data structure , the fucttion should render
         The default version assume the data is the "HTML" string to fill the innHTML
         of the tag provided         
      """         
      deffunc = self.defaultJs()
      self.publish(deffunc,'main','script')
      return deffunc

   #______________________________________________________________________________________      
   def doJson(self):
      return self.doQuery()
   #______________________________________________________________________________________      
   def extraParams(self):
      e = self["%s/%s" % (self._roleDir, pmRoles.params())]
      if e!= None: e = e.cargo()
      return e
   #______________________________________________________________________________________      
   def extraValues(self):
      e = self["%s/%s" % (self._roleDir, pmRoles.extra())]
      if e!= None: e = e.cargo()
      return e
   #______________________________________________________________________________________      
   def extraValuesFilled(self,alias=None):
      vals = self.extraValues()
      cleanVal  = dict((k,v) for k,v in vals.iteritems() if v is not None )
      if cleanVal != None and len(cleanVal.keys()) >= 1: vals = cleanVal
      else: vals = None
      if vals != None and alias != None:
         for a in alias:
            if vals.has_key(a): 
               vals[alias[a]]= vals[a]
               del vals[a]
      return vals

   #______________________________________________________________________________________      
   def ui(self, aaaaa, bbbb="ui_bbbb"):
      print "Dummy test ----  ui(aaaaa=%s, bbbb=%s,params=%s)"% (aaaaa, bbbb,self.extraValues())
   #______________________________________________________________________________________      
   def doQuery(self):
      raise ValueError("  Module defines no doQuery method ")
      return None
   #______________________________________________________________________________________      
   def publishUI(self,method,role=pmRoles.object(),alias='default',params={}):
      """ 
          Publish the user interface method by name  to play the role provided 
          use alias='default' to mark the method to be default.
          One can extent the method interface with the extra params
      """
      try:
         func = method
         if isinstance(method,str):            
            func = self.__getattribute__(method)
         if alias == None:
            alias= func.func_name
            self.mkdir("%s/%s/%s" % (self._roleDir, role,alias)).setCargo(func)
         else:   
            self.mkdir("%s/%s/%s" % (self._roleDir, role,alias)).setCargo(func)
            self.mkdir("%s/%s/%s" % (self._roleDir, role,func.func_name)).setCargo(func)
         if params and len(params) > 0:
            self.mkdir("%s/%s" % (self._roleDir, pmRoles.params())).setCargo(params)
         #self.ls()
      except:
         raise ValueError("unknown method %s" % method)

   #______________________________________________________________________________________      
   def param(self,prm):
      p =  None
      if prm != None and prm != '':
         p = prm
         if prm.strip().isdigit():
            p = int(prm.strip())
         else:
            p = prm.strip()
            if len(p) > 2:
               if p[0]=="'" and p[-1]=="'":
                  p = prm.lstrip().lstrip("'").rstrip().rstrip("'")
                  pass
               else: 
                  p = prm.strip()
      return p

   #______________________________________________________________________________________      
   def param2Args(self,params,keyonly=True):
      """ Convert the list of the URL ampersand separated parameteres to the python argument list """
      values = []
      keys   = {}
      syskeys = {}
      extraValue = {}
      extra = self.extraParams()
      if extra: extraValue = extra.copy()
      semicolon = False
      if ";" in params and '&' in params: 
         # http://stackoverflow.com/questions/5158565/why-does-pythons-urlparse-parse-qs-split-arguments-on-semicolon 
         w3c = """
            ';' is equivalent to '&'
             W3C recommends that all web servers support semicolon separators in the place of ampersand separators.
             http://www.w3.org/TR/1999/REC-html401-19991224/appendix/notes.html#h-B.2.2
         """
         params = params.replace(';',',,,')
         print utils.lineInfo(),"params <%s> contains the ';', %s" %(params,w3c) 
         semicolon = True
      try:
         for (v,k) in cgi.parse_qs(params,True).iteritems(): 
            # print " 163 ", v,k,params
            if len(k) != 1: raise SyntaxError("Ambiguous values %s of the '%s' URL parameters" % (k,v) )
            kpar = k[0]
            if semicolon: kpar= k[0].replace(",,,",";")
            var = v.strip()
            if var[0] == "_":
               syskeys[var] = self.param(kpar)
            elif extra and  extra.has_key(var):
               extraValue[var] = self.param(kpar)
            else:
                keys[var] = self.param(kpar)
      except:
         raise
         pass
      self.debug("%s from %s " % ( (values,keys,syskeys), params ))
      self.debug(" keys=<%s>  syskeys=<%s>" %  (urllib.urlencode(keys),urllib.urlencode(syskeys)))
      return (values,keys,syskeys,extraValue)

   #______________________________________________________________________________________      
   def getParams(self,method,role):
      """ return UI method by name or alias """
      func = None
      try:
         r = self["%s/%s/%s" % (self._roleDir, role, method)]
         # print " 148 ", r,(self._roleDir, role, method)
         # self.ls()
         if r != None: func = r.cargo()
      except:
         pass
      return func

   #______________________________________________________________________________________      
   def getUI(self,method,role):
      """ return UI method by name or alias """
      func = None
      try:
         r = self["%s/%s/%s" % (self._roleDir, role, method)]
         #print " 176 ", r,(self._roleDir, role, method)
         # self.ls()
         if r != None: func = r.cargo()
      except:
         pass
      if func == None and method == 'default' and role == pmRoles.script(): func = self.doScript  
      return func

   #______________________________________________________________________________________      
   def callUI(self,urlparams,role=pmRoles.object(), method=None):
      """ execute the registered method with the Url parameters """
      (values, keys,syskeys,extra) = self.param2Args(urlparams)
      if method == None or method == '': 
         method = syskeys.get('_mode','default')
      f = self.getUI(method,role)
      if f == None and self.isRoleObject(role):
         " There is no 'json', try html instead "
         f = self.callUI(urlparams,pmRoles.html(), method)
      else:
         mt = self._moduleTimers.get(method,{})
         mtr =  mt.get(role, Stopwatch())
         mtr.start()
         # print " 215 callUI ", urlparams, method , " <-------------------", extra
         if extra and len(extra) > 0: 
             self.mkdir("%s/%s" % (self._roleDir, pmRoles.extra())).setCargo(extra)
         if keys.has_key('callback'): del keys['callback']
         try:
            f(**keys)
         except:
            mtr.stop()   
            if f != None:
               # print utils.lineInfo(), f, keys, mtr,role
               self.error("invocation of <%s(%s)> at %s failed %s" % (f.func_name, keys, mtr,role) )
               raise
            else:
              raise ValueError("An invocation of &lt;%s&gt; to call &lt;%s&gt; method with the &lt;%s&gt; role failed" % (urlparams, method,role) )
         mtr.stop()
         if self.isRoleObject(role):
            self.publish(mtr,role=pmRoles.timing())
      return f
   #______________________________________________________________________________________      
   def isRoleJson(self,role):
      return role==pmRoles.json()
   #______________________________________________________________________________________      
   def isRoleObject(self,role):
      return role==pmRoles.object()
   #______________________________________________________________________________________      
   def unpublish(self, dir=".pub",location=None,role=None):
      """ Unpublish the data and return it to the caller """
      pub = self.empty(dir,location,role)
      return pub.cargo() if  pub else None
   #______________________________________________________________________________________      
   def empty(self, dir=".pub",location=None,role=None):
      """ Remove all published data """
      if dir:
         folder = dir
         if location:
            folder += "/%s" % location
            if role:
               folder += "/%s" %  role
      pub =  self[folder]
      if pub: pub.setParent(None) 
      return pub   
   #______________________________________________________________________________________      
   def publish(self, data,location='main',role=pmRoles.object()):
      place = None
      if data != None:
         place = self.mkdir(".pub/%(location)s/%(role)s" % {"location" : location , "role" : role } )
         if isinstance(data,Stopwatch) and role==pmRoles.timing():
            data = { "timestamp" : time.time() ,"cpu" : int(data.cpuTime()*1000), "real" : int(1000*data.realTime()), "slice" : data.counter, "unit" : "msec"}           
         place.setCargo(data)
      return place
   #______________________________________________________________________________________      
   def publishTitle(self, title,role=pmRoles.html()):
      self.publish(title,"title",role)
   #______________________________________________________________________________________      
   def publishNav(self, nav,role=pmRoles.html()):
      self.publish(nav,"nav",role)
   #______________________________________________________________________________________      
   def publishMain(self, main,role=pmRoles.html()):
      self.publish(main,"main",role)
   #______________________________________________________________________________________      
   def publishHelp(self, help, helpid="navhelp", role=pmRoles.html()):
      self.publish(help,helpid,role)
   #______________________________________________________________________________________      
   def publishFooter(self, footer='',footerid="foot", role=pmRoles.html()):
      """HTML page footer"""
      htmlstr = ""
      if footer == '' or footer==None:
         version = "Code $Rev: 18379 $"
         version = version.replace('$','')
         footer = version
      htmlstr += "<br> &nbsp; &nbsp; Module: %s" % ( self.objectName() )
      htmlstr += "<br> &nbsp; &nbsp; Page created %s" % datetime.utcnow().strftime("%m-%d %H:%M:%S")
      htmlstr += " by %s. " %  self.server().username()
      try:
         timing = self.findChild(pmRoles.timing()).cargo()
         real = timing['real']/1000.0
         cpu = timing['cpu']/1000.0
         htmlstr += " To produce this page our server spent: Real time %.2f sec, CP time %.2f sec " %  (real, cpu)
      except:
         pass
      if footer != '': htmlstr += "<br> &nbsp; &nbsp; %s" % footer
      htmlstr += "<br> &nbsp; &nbsp; Host: %s %s:%s (thread=%s) " % (self.server().host(), self.server().getppid(), self.server().getpid(),self.server().threadId() )
      htmlstr += """
         <br> &nbsp; &nbsp; <a href='https://savannah.cern.ch/bugs/?func=additem&group=panda'>Report a problem</a>
              &nbsp; &nbsp; <a href='mailto:hn-atlas-dist-analysis-help@cern.ch'>Email list for help</a>
         <br> &nbsp; &nbsp; <a href='mailto:atlas-adc-pandamon-support@cern.ch'>Webmaster</a></div>
      """
      self.publish(htmlstr,footerid,role)
   #______________________________________________________________________________________      
   def publishPage(self, title=None,nav=None,main=None, role=pmRoles.html()):
      self.publishTitle(title,role)
      self.publishNav(nav,role)
      self.publishMain(main,role)

   #______________________________________________________________________________________      
   def cached(self):
      """ return the CacheContol role if present rols
      """
      cache = None
      pub = self[".pub"]
      for it in pub:
         if it.hasCargo(): 
            role = it
            if role.objectName()== pmRoles.cache():
               cache =  role.cargo()
               break
      return cache
   #______________________________________________________________________________________      
   def published(self):
      """ 
          Output:
         { "id" : location , role : data } 
      """
      pubarray = None
      pub = self[".pub"]
      if pub:
         locations = {}
         system = {'host': self.server().serverHost() }
         json = None
         for it in pub:
            if it.hasCargo(): 
               role = it
               if role.objectName()== pmRoles.timing():
                  system[role.objectName()] = role.cargo()
                  continue
               location = role.parent()
               locname = location.objectName()
               if not locations.has_key(locname):
                  locations[locname] = {"id": locname}
               ldict = locations[locname]
               ldict[role.objectName()] = it.cargo()
               if self.isRoleObject(role.objectName()) and locname=="main":
                  json = it.cargo()
               if False:
                  # new version 2012.11.29. see tasks/clonetask use case
                  if self.isRoleObject(role.objectName()) and locname=="main":                  
                     json =  ldict[role.objectName()]
                     if type(json) != dict:
                         ldict[role.objectName()] = {'data': json}
                         json = ldict[role.objectName()]
         if json != None and len(system) >0: # publish system into json
            json["_system"] =  system
         for layout in locations:
            if pubarray == None: pubarray = []
            pubarray.append(locations[layout])
      return pubarray

   #______________________________________________________________________________________ 
   def splitPublsihed(self,published):
      locations=None
      if published:
         locations = {}
         for frame in published:
            id = None
            value = None
            for (k,field) in frame.iteritems():
               if k == "id":
                  id = field
               else:
                  value = {k : field }
            if id != None:      
              locations[id] = value
      return locations
      
   #______________________________________________________________________________________ 
   def wrapScript(self,handlerResponse):
      """ Prepare the user function to ship """
      page = ''
      function = ''
      lr = len(handlerResponse)
      # print " pmMain: 51 ", lr, handlerResponse
      if lr == 0:
         """ default function to render plain HTML data """
         function = self.defaultJs()
      else:
         function = handlerResponse
      if function == None:
         function = self.defaultJs()
      """ Wrap the user's function into the  framework script """      
      page = """
      {  
       var f = %s;
       var pm = $('body').data('Pm'); 
       el = pm._topElement; 
       el.Log('New Function Arrived:' + f); 
       el._render = f; 
       el.Log('Function Accepted for ' + el.Id() + ' ' +  el._render );
       }
      """  % function
      page = page.replace("\n","");
      return page
   #______________________________________________________________________________________      
   def isValid(self,params,exceptions=None):
      """ Check whether the extra parameters are valid """
      if params != None:
         p = utils.parseArray(params)
         ex = self.extraParams()
         for nxp in p:
            if exceptions != None and nxp in exceptions: continue
            if ex == None or not nxp in ex: raise ValueError("Unexpected module parameter : '%s' from : \n\t '%s' \n" % ( nxp,"'\n\t'".join( sorted(ex.keys())) ))
      return True

   #______________________________________________________________________________________________________________
   @classmethod
   def timeValue(cls,str):
    """ Parse time string into time value """
    res = None
    if len(tstr) == 10:
        res = datetime.strptime(tstr,'%Y-%m-%d')
    elif len(tstr) == 13:
        res = datetime.strptime(tstr,'%Y-%m-%d %H')
    elif len(tstr) == 16:
        res = datetime.strptime(tstr,'%Y-%m-%d %H:%M')
    elif len(tstr) >= 19:
        res = datetime.strptime(tstr[:18],'%Y-%m-%d %H:%M:%S')
    else:
        raise ValueError('%s:  time length %s not parseable: %s' % ( utils.lineInfo(), len(tstr), tstr ))
    return res

   #______________________________________________________________________________________________________________
   def prepareTime(self, days, hours=None, tstart=None, tend=None):
      """ 
          Generate start / from datime and duration
      if (hours != None or days!=None) and tstart !=None and tend!=None: 
         raise ValueError("Ambiguous time range input 2 parameteres are allowed. All 3 or 4 have been provided: days=%(days)s, hours=%(hours)s, tstart=%(tstart)s, tend=%(tend)s" %{ 'days': days, 'hours' : hours,'tstart': tstart, 'tend':tend } )
      if tstart != None:
         starttime = tstart if isinstance(tstart,datetime) else self.timeValue(tstart)
         if hours != None:
            endtime = starttime + datetime.timedelta(hours=hours)
      if tend != None:
         endtime = tend  if isinstance(tend,datetime) else self.timeValue(tend)
         if hours != None:
            endtime = endtime - datetime.timedelta(hours=hours)
      if tstart == None and tend == None:
         tstart = datetime.datetime.utcnow() - datetime.timedelta(hours=hours)
      """   
      pass

        
#______________________________________________________________________________________
   @classmethod      
   def factory(cls,modname=None,name=None,parent=None,obj=None,server=None, config=None,fileonly=False):
      """ Find, load, return the requested module """
      mhandle = None
      hMethod = None
      mfile = os.path.join(cls._moduleFile, "%s.py" % modname )
      mname = modname.rpartition('/')[2].strip()
      if not os.path.exists(mfile):
         mfile = os.path.join( cls._moduleFile,'..','pmModules','%s.py' % modname)
      if os.path.exists(mfile):
         mpath = os.path.dirname(mfile)
         pythonpath = sys.path
         if not mpath in pythonpath:
         #   Add the path of this module to pythonpath
            sys.path.append(mpath)
         if parent:
           hMethod = parent.module(mname)
         if not isinstance(hMethod,pmModule):
            mhandle = __import__(mname)
            if mhandle == None: raise ValueError(mfile)
            hMethod  = None
      else:
         raise ValueError("%s" % utils.reportWarning('Module %s not found under %s  ' % ( modname, mfile.replace(cls._moduleFile,'') ) ) )
      if mhandle:
         if fileonly: hMethod = mhandle
         else:
            cl = mhandle.__dict__[mname]
            if name==None: name=mname
            hMethod = cl(name=name,parent=parent,obj=obj)
            hMethod.server(server);
            hMethod.config(config);
      return hMethod

#______________________________________________________________________________________      
if __name__ == '__main__':
   pmDir = __file__.rpartition('/')[0].strip()
   print pmDir
   pandadir = ['panda-common','panda-common/liveconfigparser','panda-common/pandalogger','pandamon','pandamon/pmModules']
   pythonpath = sys.path
   for dr in pandadir:
      if not dr in pythonpath:
               # Add the path of this module to pythonpath
           sys.path.append(dr)
   print sys.path        
   a = pmModule()
   a.ls()
   print "--- Panda Module Test---- " , dir (a)
   # (args, varargs, keywords, defaults)
   args = inspect.getargspec( pmModule.ui)
   print "\nags =" , args
   print "\n formt=", inspect.formatargspec(args)
   # print "\n values=", inspect.formatargvalues(args)
   # print "\n callargs", inspect.getcallargs(pmModule.ui,'ww',3)
   a.publishUI("ui")
   print " 143 Publishing . . . . "
   print " 145 Publised:\n   %s\n  %s" % (a.publish({'published' : ('staff','members')}), a.root())
   a.ls()
   p = a.published()
   print " 326 split published ", a.splitPublsihed(p)
   a.empty()
   p = a.published()
   print " 533 clean the published ", a.splitPublsihed(p)   
   a.param2Args("123&itutu& 345 & 'sdfgh' & 1.23& a=123&b='a'&c = erty & d= 123 &f= '+sssd+++' ", keyonly=False)
   a.param2Args("123&itutu& 345 & 'sdfgh' & a=123&b='a'&c = erty & d= 123 &f= ' sssd ' ", keyonly=True)
   a.param2Args("_mode=myModule&123&itutu& 345 & 'sdfgh' & a={ b=123}&b='a'&c = erty & d= 123 &f= ' sssd ' ", keyonly=True)
   print " pmModule:334 -- calling ui"
   a.callUI("aaaaa=123&bbbb=bforb ")
   print " pmModule:336 -- calling ui"
   a.callUI("_mode=ui&aaaaa=123&bbbb=bforb ")
   print " 337 --- >  ", "Expect the extra params to popup"
   params = {"First" : None, "Second" : None }
   a.publishUI("ui",alias='params', params=params)

   a.callUI("aaaaa=123&First=1",method="ui")
   a.callUI("aaaaa=123&Second=3",method="ui")
   
   b =  pmModule("b",a)
   print " 341 -- b stealing from a"
   b.ls()
   a.ls()
   c = pmModule("cModule")
   c.stealFrom(a)
   c.ls()
   a.ls()
   print " ----- try factory -----------"
   print 'file=',__file__
   home = pmModule.factory("home")
   print home
   print home.callUI('','json')

   thome = pmModule.factory("testm/thome")
   print thome
   
   try:
      a.callUI("bbbb=bforb",method="ui")
   except:
      print "\n ----------------------------"
      print "    The expected exception: "
      print " ----------------------------"
      raise
