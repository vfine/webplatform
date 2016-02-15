from pmUtils.pmState import pmstate
from pmCore.pmModule import pmModule
from pmCore.pmModule import pmRoles
import pmUtils.pmUtils as utils

class status(pmModule):

   #______________________________________________________________________________________      
   def __init__(self,name=None,parent=None,obj=None):
      pmModule.__init__(self,name,parent,obj)
      self.publishUI(self.doQuery)
      self.publishUI(self.doScript,role=pmRoles.script())
   #______________________________________________________________________________________      
   def doQuery(self,jobtype=None):
      main = {'dash':'dash'}
      self.publishTitle("Dashboard")
      self.publish({'s-maxage':600,'max-age': 600 }, role=pmRoles.cache())
      self.publish(main)
   #______________________________________________________________________________________      
   def doScript(self,jobtype=None):
      status = ''
      scriptstat = ''
      if jobtype==None:
         status = 'States'
         jobtype = ''
      else: 
         status = jobtype[0].upper() + jobtype[1:]
         jobtype =",jobtype:'%s'" % jobtype
         scriptstat = " maininfo['jobtype']='%s';" %  jobtype
      script = """
        function db(tg,maindata) { 
            var maininfo = { };
            %(scriptstat)s
            return views().showPandaJobStatus(tg,maininfo);
        }
      """ % {'jobtype':jobtype,'status': status , 'scriptstat': scriptstat} 
      self.publish(script,role=pmRoles.script())
      self.publish({'s-maxage':0,'max-age': 0 }, role=pmRoles.cache())
   
  