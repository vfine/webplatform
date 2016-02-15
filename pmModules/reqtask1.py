""" Generic Task Request """
# $Id: reqtask1.py 9690 2011-11-16 22:28:01Z fine $
# Display DB status and stats
from pmUtils.pmState import pmstate
from pmCore.pmModule import pmRoles
from  pmTaskBuffer.pmTaskBuffer import pmgrisliaskbuffer as gmt
import pmUtils.pmUtils as utils
import pmUtils.Stopwatch as Stopwatch
import monitor.taskDef_conf as taskDef_conf

from  pmCore.pmModule import pmModule

class reqtask1(pmModule):
   """ Generic Task Request """

   #______________________________________________________________________________________
   def __init__(self,name=None,parent=None,obj=None):
      pmModule.__init__(self,name,parent,obj)
      self.publishUI(self.doJson)
   #______________________________________________________________________________________
   def taskVersion(self,trfv):
   #
   # trfv     - transformation version
   # tversion - task version
      junk = trfv.split('.')
      version = 'v'
      for j in (junk) :
        try:
         if int(j) < 10 :
           version += "%02d"%int(j)
         else :
           version += "%d"%j
        except:
          version += "%s"%j
      return version

   #______________________________________________________________________________________
   def getLastDefinedDatasets(self,hours) :
      dbt= gmt.getLastDefinedDatasets(hours,False)
      tasks= dbt['rows']
      taskname = ''
      dataset =''
      ntrf    =''
      trfv    =''
      email   =''
      timestamp = 0
      if tasks != None and len(tasks) > 0:
         taskname = tasks[0][0]
         trf      = tasks[0][1]
         trfv     = tasks[0][2]
         formats  = tasks[0][3]
         email    = tasks[0][4]
         timestamp= tasks[0][6]
         if taskname.find('.reco') >= 0 :
            junk = taskname.split('.')
            dataset = "%s.%s.%s"%(junk[0],junk[1],junk[2])
            junk = trf.split('.')
            dataset += ".%s"%junk[1]
            if junk[1] == 'evgen' :
               ntrf = 'csc.simul.trf'
            elif junk[1] == 'simul' :
               ntrf = 'csc.reco.trf'
            elif junk[1] == 'pythia' or junk[1] == 'spgun' :
               ntrf = 'csc.simul.trf'
            junk = formats.split('.')
            dataset += ".%s"%junk[0].lower()
            version = self.taskVersion(trfv)
            dataset += ".%s"%version
         else :
          # special case last request was 'reco' - repeat it
            dataset = tasks[0][5]
            ntrf    = trf

      return {'dataset': dataset,'ntrf': ntrf,'trfv':trfv,'email': email,'timestamp':timestamp}

   #______________________________________________________________________________________      
   def doMain(self,hours):
      main = {}
      timer = Stopwatch.Stopwatch()
      tasks= self.getLastDefinedDatasets(hours)
      main = {}
      main["method"] = 'reqtask1'
      main["tasks"] = tasks
      main["taskDef"] = { 'name'   : sorted(taskDef_conf.projects['name'])
                         ,'jobs'   : taskDef_conf.trfs['jobs']
                         ,'version': taskDef_conf.swversion['version'] 
                        }
      main['time'] = {'fetch' : "%s" % timer}
      self.publish(main)

   #______________________________________________________________________________________      
   def doJson(self,hours=6):
      """ 
        Select Parameters For Task Request
      """ 
      self.publishTitle(' Select Parameters For Task Request')
      self.doMain(hours)
      self.publish( "%s/%s" % (self.server().fileScriptURL(),"taskdef/%s.js" % 'reqtask1' ),role="script")
      self.publish( {'s-maxage':600,'max-age': 600}, role=pmRoles.cache())

def leftMenu():
    """ Return html for inclusion in left menu """
    #Temporary to preserve the backward compatibility 
    txt = "<a href='%s/reqtask1'>Task Request</a>" % self.server().branchUrl()
    return txt
