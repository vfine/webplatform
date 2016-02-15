""" Invoke the PanDA Server TaskBuffer API """
# $Id: taskBuffer.py 15860 2013-06-12 22:13:47Z fine $
# Display DB status and stats
from pmUtils.pmState import pmstate
from pmCore.pmModule import pmRoles
from  pmTaskBuffer.pmTaskBuffer import pmtaskbuffer as pmt
try:
   from  pmTaskBuffer.pmTaskBuffer import pmgrisliaskbuffer as gmt
except:
   pass
try:
    from  pmTaskBuffer.pmTaskBuffer import pmjeditaskBuffer as jmt
except:
   pass
import pmUtils.pmUtils as utils
import pmUtils.Stopwatch as Stopwatch
from datetime import datetime

from  pmCore.pmModule import pmModule

class taskBuffer(pmModule):

    #______________________________________________________________________________________
   def __init__(self,name=None,parent=None,obj=None):
      pmModule.__init__(self,name,parent,obj)
      self.publishUI(self.doJson)
      self._doc = None
   #______________________________________________________________________________________      
   def doMain(self,method,params,db):
      main = {}
      method = method.strip()
      api = method.replace("()","")
      if params == None: 
         params = ''
      elif params!='':
         if method=='getFullJobStatus':
            api='fullJobStatus' # rename to eliminate the 'side effect'
            if not isinstance(params, int):
               params=params.lstrip('[').rstrip(']')
            params = "[%s]" % params
         elif method=='getScriptOfflineRunning':
            params = int(params)
         elif method=='describe':
            params = "'%s'" % params
         else:
            params = "%s" % params
      if method.find('(') >=0 and method[-1]==')':
         api = method
         self._doc = method[:method.find('(')]
      else:
         self._doc = api
         api = "%s(%s)" % (api, params)

      timer = Stopwatch.Stopwatch()
      tasks=eval('%s.%s' % (db,api))
      main["buffer"] = {}
      main["buffer"]["method"] = method.replace("()","")
      main["buffer"]["params"] = params
      main["buffer"]["type"] = isinstance(tasks,str)
      main["buffer"]["data"] = tasks
      
      main['time'] = {'fetch' : "%s" % timer}

      self.publish(main)
   #______________________________________________________________________________________      
   def makeDocUI(self,object):
      h = self.server().host()
      m = pmModule.makeDocUI(self,object)
      if self._doc != None:
         # self._doc = self._doc.replace("(","").replace(")","")
         d =  eval('pmt.%s' % (self._doc)) 
         m += '<hr>'
         m += pmModule.makeDocUI(self,d,self._doc)
         pass 
      return m
   #______________________________________________________________________________________      
   def doJson(self,method="getAssigningTask",params='',db='pmt'):
      """ 
          Invoke the arbitrary method of <a href="https://svnweb.cern.ch/trac/panda/browser/panda-server/current/pandaserver/taskbuffer/TaskBuffer.py">TaskBuffer</a> class <br>
          <code>method = "getAssigningTask"</code><br>
          <code>method = "getNumUserSubscriptions"</code><br>
          <code>method = "getSiteList"</code>  ... etc <br>
          <code>params = the comma separated list of the parameters to be passed to the method defined by 'method' parameter</code>
      """ 
      self._doc = None
      self._db = db
      self.publishTitle('Panda TaskBuffer')
      timer = Stopwatch.Stopwatch()
      self.doMain(method,params,db)
      self.publishNav('The TaskBuffer from CERN: "%s:%s".  "%s"' % ( method , params, timer ) ) # I know the cyber security will be mad ;-) VF.
      sc = {"getAssigningTask" : "getAssigningTask"
           ,"getPledgeResourceRatio": "getPledgeResourceRatio"
           ,"getScriptOfflineRunning": "getScriptOfflineRunning"
           ,"getFullJobStatus":"getFullJobStatus"
           ,"fullJobStatus"  :"getFullJobStatus"
           ,"getUsers"       : "getUsers"
           ,'getMembers'     : "tbTable"
           ,'getSiteInfo'    : "getSiteInfo"
           ,'getSnapshot'    : "tbTable"
           ,'getCloudSummary': "tbTable"
           ,'getSiteSummary' : "tbTable"
           ,'getCloudList'   : "getCloudList"
           ,"getMCShares"    : "getMCShares"
           ,'getCloudConfig' : "tbTable"
           ,'getCloudSites'  : "tbTable"
           ,'getjobparam'    : "getjobparam"
           ,'getUserActivity': "tbTable"
           ,'wnList'         : "tbTable"
           ,'diskUsage'      : "tbTable"
           ,'debugInfo'      : "tbTable"
           ,'corruptFiles'   : "tbTable"
           ,'getVCloudSummary': "tbTable"
           ,'jobParams'      : "tbTable"
           ,'schedCfg'       : "tbTable"
           ,'getLastDefinedDataset': "tbTable"
           ,'getTaskMaxLength': "tbTable"
           ,'listTaskRequests': "tbTable"
           ,'getUserSubs'  : "tbTable"
           ,'pandatabs'    : "tbTable"
           ,'pandacols'    : "tbTable"
           ,'countReleases': "tbTable"
           ,'getLogInfo'   : "tbTable"
           ,'getJobsAtt'   : "tbTable"
           ,'getErrorCount': "tbTable"
           ,'getJediTaskAtt': "tbTable"
           ,'getJediDSAtt' : "tbTable"
           ,'describe'     : "describe"
      }
      f = 'default'
      for m in sc:
          if m in method: 
            f = sc[m]
            break
      self.publish( "%s/%s" % (self.server().fileScriptURL(),"taskBuffer/%s.js" % f ),role="script")
      cache = { 
                  "getMCShares": {'s-maxage':90000,'max-age': 90000 }
                 ,"getJediTaskAtt": {'s-maxage':900,'max-age': 900 }
              }
      c =  cache.get( method );
      if c: self.publish(c, role=pmRoles.cache())

def leftMenu():
    """ Return html for inclusion in left menu """
    #Temporary to preserve the backward compatibility 
    txt = "<a href='%s/taskBuffer'>Hello Panda TaskBuffer</a>" % self.server().branchUrl()
    return txt
