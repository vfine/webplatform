"""
State information for pandamon instance
"""

import re, os, sys, logging
import Stopwatch
import pmConfig.pmConfig as config
import pmUtils as utils

class pmState:

    # Server configuration
    startup = True
    dev = False
    debugmode = False
    bypass = False  # bypass parameter security check
    instanceName = ''
    host = ''
    port = ''
    url= config.pandamon['url']
    logging.info('URL is %s' % url)
    print "pmState: 21. url=", url
    baseurl = ''
    jobarchive = 'SimpleDB'
    pandadir = None
    # get pandadir from the python path
    pat = re.compile('(.*)/pandamon$')
    for d in sys.path:
        mat = pat.match(d)
        if mat:
            pandadir = mat.group(1)
            break
    # User info
    userName = ''
    VO = ''
    DN = ''
    VOMS = []

    # query parameters
    script = ''
    path = ''
    query = ''
    # module is specified by <context>/<module> or if <context> is absent, defaults to pandamon, and module defaults to home
    context = 'pandamon'
    module = 'home'
    moduleHandle = {}
    params = {}
    timer = None

    # presentation parameters
    navmain = ''
    navright = ''
    titleleft = ''
    errorReport = ''
    windowTitle = 'PanDA Monitor'
    nGoogleVisualizations = ''
    bookmark = ''

    def __init__(self):
      self.host = os.environ.get("PANDAMON_HOST")
      try:
          self.port = int(os.environ.get("PANDAMON_PORT"))
      except:
         self.port = 80
      if self.port != 80:
         self.baseurl = "%s:%s" % ( self.host, self.port )
      else:
         self.baseurl = self.host

      self.instanceName = 'apache'

    # Panda configuration data
    def getModule(self,modname):
      """ Find, load, return the requested module """
      mhandle = None
      mfile = "%s/pandamon/pmModules/%s.py" % ( self.pandadir, modname )
      if os.path.exists(mfile):
         mpath = os.path.dirname(mfile)
         pythonpath = sys.path
         if not mpath in pythonpath:
            # Add the path of this module to pythonpath
            sys.path.append(mpath)
         mhandle = __import__(modname)
         if mhandle == None: raise ValueError(mfile)
      else:
         raise ValueError("%s" % utils.reportWarning('Module %s not found under %s name ' % (modname, mfile)) )
      return mhandle

    def initForQuery(self, urlquery):
        self.params = {}
        self.timer = Stopwatch.Stopwatch()
        self.navmain = ''
        self.errorReport = ''
        self.windowTitle = 'PanDA Monitor: %s' % self.script
        self.nGoogleVisualizations = 0
        # checkString bypass 'off' by default
        self.bypass = False

        if urlquery.find('?') >= 0:
            self.query = urlquery[urlquery.find('?')+1:]
            self.path = urlquery[:urlquery.find('?')]
            if self.query == '/': self.query = ''
            if self.query == 'isAlive': return ('yes', 'text')
        else:
            self.query = ''
            self.path = urlquery
        if self.path[-1:] == '/': self.path = self.path[:-1]

    def setModule(self):
        """get the context and module names"""
        self.context = 'pandamon'
        self.module = 'home'
        if len(self.path) > 0:
            p = self.path.replace('/query','')
            tokens = p.split('/')
            if tokens[-1] in config.contexts.keys():
                # context specified without module. Use default.
                self.context = tokens[-1]
                self.module = config.contexts[self.context]
            elif tokens[-2] in config.contexts.keys():
                # both context and module are specified
                self.context = tokens[-2]
                self.module = tokens[-1]
            elif re.match('^[a-zA-Z0-9_\-]+$',tokens[-2]):
                # looks like a context, treat as a context
                self.context = tokens[-2]
                self.module = tokens[-1]
            else:
                # module only is specified for default context.
                self.module = tokens[-1]
        if 'MODULE' in self.params: self.module = self.params['MODULE']
        logging.info("Context/Module set to %s/%s" % (self.context, self.module))

    def setParams(self, pars):
        self.callback = None
        self.params = {}
        for p in pars:
            self.params[p.upper()] = pars[p]
        if 'VO' in self.params:
            self.VO = self.params['VO'].upper()
        elif 'CALLBACK' in self.params:
           self.callback = self.params['CALLBACK']
           del self.params['CALLBACK']
        else:
            self.VO = 'aaaa'

import threading
pandaStates = {}
statesDictLock = threading.RLock()
            
def pmstate():
   t = threading.currentThread()
   statesDictLock.acquire()
   pmsrv = pandaStates.get(t)
   if pmsrv==None: 
      pmsrv = pmState()
      pandaStates[t] = pmsrv
   #print "--->states<--- thread %s:/%s total: %s server %s " %(os.getpid(),t,len(pandaStates),pmsrv) 
   statesDictLock.release()
   return pmsrv
   

## unused (so far) stuff from the old monitor:
class junk:

    oracleDBs = {}
    currentOracleDB = ''
    currentOracleDBID = ''
    currentCursor = 0
    cursorType = 'list'
    errorReport = ''
    sortOn = ''
    sortReverse = False
    nGoogleVisualizations = 0
    _xPlot = re.compile('[0-9]+')

    nmaxhrs = 24 * 15 # Maximum depth of queries into job tables
    fullQuery = ''
    fromIP = ''
    urlQuery = ''
    redirect = ''
    queryParams = {}
    userName = ''
    windowTitle = ''
    navmain = ''
    navright = '&nbsp;'
    titleleft = '&nbsp;'
    jobStates = ('defined', 'assigned', 'waiting', 'activated', 'running', 'transferring',
                 'holding', 'finished', 'failed', 'cancelled')
    nocachemark = False  # Set to true to avoid setting cache usage marker (for auto cache update)
    reload = False # force cache reload (for auto cache update)

    dsRepository = {}
    dsLocations = {}
    dsCategories = {}

    cloudList = []
    cloudInfoDict = {}
    cloudInfoDict1 = {}

    dbs = {}
    dbids = {}
    dbid_current = ''
    cursors = {}
    dictcursors = {}
    oraclecursors = {}
    lrcdbs = {}
    lrccursors = {}

    errorFields = []
    errorCodes = {}
    errorStages = {}

    bypass = bool(1)
    
    _layoutPattern = re.compile('\s*([0-9])+\s*x?\s*([0-9]*\s*)')
