""" HTTP request handler for Panda monitor """
import urllib, os
from pmUtils.pmState import pmstate
import pmUtils.pmUtils as utils
import pmUtils.pmSecurity as security
from  pmUtils.pmJsonEncoder import pmJsonEncoder
from  pmCore.pmModule import pmModule as pmModule
from  pmCore.pmModule import pmRoles
try:
    import json
except:
    import simplejson as json
#________________________________________________________________________
class pmHandler(pmModule):
    """Panda monitor HTTP request handler"""
    
    def __init__(self,name='handler',parent=None,obj=None,server=None,config=None):
      pmModule.__init__(self,name,parent,obj,server,config)
      try:
         srvname = self.config().config.frontpage['browser']
         self._browser = self.factory(srvname,parent=self)
      except:
         from pmUtils.pmBrowser import pmBrowser
         self._browser = pmBrowser(parent=self)

    #___________________________________________________________________
    def do_GET(self, urlquery=None, req=None, mode = None, cli=None):
        srv = self.server()
        if urlquery==None: urlquery = srv.assmemblerUrl('query')
        if mode == None: mode = srv.mode()
        if cli == None: cli = srv.cli()
        # self.ls()
        """ Process the GET query """
        # Set up state for this query
        pmstate().initForQuery(urlquery)
        if mode != 'html' :
           pmstate().setModule()
        else:
           pmstate().module = 'home'
        titletxt = 'pandamon'
        menuinfo = navtxt = maintxt = jsonpage = None
        mname = None
        published = None
        cached = None

        security.parseQueryString(urlquery)
#       params = security.parseQueryString(urlquery)
        # qlocation = urlquery.find('?')
        # if qlocation>=0:
           # (values,keys,syskeys,extraValue)  = self.param2Args(urlquery)
           # pmstate().setParams(keys)
           
        # if no module just show the home page
        if pmstate().module == '':
            titletxt, menuinfo, navtxt, maintxt = self._browser.frontPage()
        elif mode == 'html' :
            bp = self._browser.buildPage( mode=mode)
            self.debug("Returning the home page")
            return bp
        else:
            srvname =srv.path().strip().lstrip('/')
            if srvname=='':
               if srv.query().replace('_get=json','').strip() =='':
                  try:
                     srvname = self.config().config.frontpage['home']
                  except:
                     srvname='home'
               else:   
                  srvname = 'old'
            elif '&_old' in srv.query() : srvname = 'old'
            hMethod = self.factory(srvname,parent=self)
            if hMethod:
               params = srv.query().strip()
               p = ''
               if not srvname == 'old' and not srvname == 'login': 
                  qlocation = urlquery.find('?')
                  if qlocation>=0:
                     (values,keys,syskeys,extraValue)  = self.param2Args(urlquery[qlocation+1:])
                     pmstate().setParams(keys) 
                  p = params
               f= hMethod.callUI(p,mode)
               if cli==False and mode != 'script' and not self.server().jsonp() : 
                  hMethod.makeHelpUI(f)
                    #hMethod.publishHelp(utils.makeDocUI(f,self.server()))
                  hMethod.publishFooter()
               published = hMethod.published()
               cached = hMethod.cached()
               hMethod.empty()
            else:
                self.debug("Requested module '%s' not found" % srvname )
                # No python? Maybe there's html
                mfile = "%s/pandamon/pmModules/%s.html" % ( pmstate().pandadir, pmstate().module )
                if os.path.exists(mfile):
                    print "Got html module %s at %s" % ( pmstate().module, mfile )
                    fh = open(mfile)
                    data = fh.read()
                    fh.close()
                    mode = 'page' # Treat it as a complete web page
                    maintxt = data
                else:
                    titletxt = "Requested module '%s/%s' not found" % ( pmstate().context, pmstate().module )
            if False:   
               self.debug("------- Module %s" % pmstate().module)
               # try to load and pass control to the module
               mname = pmstate().module
               self.debug("------- getting Module  mode=%s" % ( mode))
               if '&_old' in srv.query() : mname = 'old'
               mhandle = utils.getModule(mname)
               if mode != 'html':
                  if mhandle != None:
                      pmstate().moduleHandle[mname] = mhandle
                      utils.addModule(mname)
                      cl = mhandle.__dict__[mname]
                      hMethod = cl(parent=self)
                      p = ''
                      if mname != 'old': 
                         params = urlquery.split('?',1)
                         if len(params) > 1: p = params[len(params)-1]
                      f= hMethod.callUI(p,mode)
                      if cli==False and mode != 'script' and pmstate().callback == None: 
                          hMethod.makeHelpUI(f)
                          #hMethod.publishHelp(utils.makeDocUI(f,self.server()))
                          hMethod.publishFooter()
                      published = hMethod.published()
                      cached = hMethod.cached()
                      hMethod.empty()
                      # self.info("try %s" % published)
                  else:
                      self.debug("Requested module '%s/%s' not found" % ( pmstate().context, pmstate().module ))
                      # No python? Maybe there's html
                      mfile = "%s/pandamon/pmModules/%s.html" % ( pmstate().pandadir, pmstate().module )
                      if os.path.exists(mfile):
                          print "Got html module %s at %s" % ( pmstate().module, mfile )
                          fh = open(mfile)
                          data = fh.read()
                          fh.close()
                          mode = 'page' # Treat it as a complete web page
                          maintxt = data
                      else:
                          titletxt = "Requested module '%s/%s' not found" % ( pmstate().context, pmstate().module )
               else:           
                  bp = self._browser.buildPage( mode=mode)
                  self.debug("Returning the home page")
                  return bp

        pmstate().timer.printme()
        # print "pmHandler: 85 mode=%s\n   published=   %s\ncache=%s\n" % ( mode, published,hMethod.cached()), 
        if mode in  ('json'):
            try: 
                # self.debug("--- > json %s" %  json.dumps(published))
                def default(o):
                  s = "%s" % o
                  return s
                page = ' { "pm" : %s }' %  json.dumps(published,separators=(',',':'), cls=pmJsonEncoder)
                #page = page.replace(',0,',',,').replace(',0,',',,') # compress 0s This can not pass the JSON.parser :( 
                if self.server().jsonp():
                  # wrap into JSONP format
                  page = "%(callback)s(%(page)s);" % {'callback' : pmstate().callback, 'page' : page }
            except:
               raise # ValueError(" Sorry, the module's author needs to simplify the output.\n The python 'json' module was not able to create the json representation\n for the published data: name=<%s> for module=<%s> mode=%s urlquery=%s . . . " % (mname,pmstate().module,mode,urlquery ))

            return (page,mode,cached)
        elif mode in 'script':
            # print "pmHandler: 97", published
            jscript = self.wrapScript(published[0]['script'])
            return  (jscript,mode,cached)
