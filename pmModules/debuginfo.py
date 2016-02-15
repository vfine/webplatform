"""  Display Panda job debug info </td><td>$Rev: 17120 $"""
# $Id: debuginfo.py 9690 2011-11-16 22:28:01Z fine $
from pmUtils.pmState import pmstate
from pmCore.pmModule import pmRoles
from  pmTaskBuffer.pmTaskBuffer import pmtaskbuffer as pmt
import pmUtils.pmUtils as utils
import pmUtils.Stopwatch as Stopwatch

from  pmCore.pmModule import pmModule

class debuginfo(pmModule):
   """  Display Panda job debug info </td><td>$Rev: 17120 $"""

   #______________________________________________________________________________________
   def __init__(self,name=None,parent=None,obj=None):
      pmModule.__init__(self,name,parent,obj)
      self.publishUI(self.doJson)

   #______________________________________________________________________________________      
   def doJson(self,job=None,debug=None,refresh=None):
      """ 
          Display Panda job debug info <br>
          <code>job  = The command separated list of the panda ids 
          <code>debug = the  pattern used to find the panda job id
          <code>refresh = the period in sec to refresh the page
          
      """ 
      main = {'params' : {} }
      params =  main['params']
      title = 'Job run-time debug info'
      if job != None  and job != 'None': 
         params['job'] = job
         title += " for job: %s" % job
      if refresh != None and refresh !='None' and refresh !=0 and refresh !='' : 
            params['refresh'] = refresh
      if debug != None and debug !='None': 
         params['debug'] = debug
         title += " with '*%s*' stdout " % debug
      self.publishTitle(title)
      main["method"] = "debuginfo"
      dbinfo =  pmt.debugInfo(job,debug)
      # dbinfo['rows'].append([1234,"Dummy stdout  to debug"])
      # if job == None or job == 'None': 
         # dbinfo['rows'].append([5649,"Another dummy stdout  to debug"])
      main["data"] = dbinfo
      if len(main["data"]["rows"]) <=0: params['refresh']=None
      self.publish(main)
      self.publish( "%s/%s" % (self.server().fileScriptURL(),"monitor/%s.js" % "debuginfo"),role="script")

