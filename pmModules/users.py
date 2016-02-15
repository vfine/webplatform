# users.py
# Display user info
#  $Id: users.py 13454 2012-11-08 17:54:19Z fine $
#
import re, os
from datetime import datetime, timedelta

import pmConfig.pmConfig as config
import pmUtils.pmUtils as utils
from  pmCore.pmModule import pmModule
from  pmTaskBuffer.pmTaskBuffer import pmtaskbuffer as pmt
from operator import itemgetter, attrgetter

class users(pmModule):

   #______________________________________________________________________________________      
   def __init__(self,name=None,parent=None,obj=None):
      pmModule.__init__(self,name,parent,obj)
      self.publishUI(self.doJson)
   #______________________________________________________________________________________      
   def makeTop(self,users,top):
      return sorted(users, key=itemgetter(top), reverse=True)
   #______________________________________________________________________________________      
   def doJson(self,hours=None,days=180,tstart=None,tend=None,PRODUSERNAME=None,top='nJobsA', topsize=0):
      """ Get the list of the users
          <ul>
          <li> hours = use the last hours 
          <li> days = use the last days 
          <li> topsize - the size of the top list 
          <br> = 0 - all users are shown
          <li> top - select top list using 'top' column
             <ul>
                <li> 'nJobsA' - the number  of the jobs
                <li> 'CPUA1' - Personal the CPU used for the last 24 hours
                <li> 'CPUA7' - Personal Cpu used for the last 7 days
                <li> 'CPUP1' - Group Cpu for the last 24 hours
                <li> 'CPUP7' - Group Cpu for the last 7 days
            </ul>            
          </ul>
      """
      if days == None: days = 0
      if hours == None: hours = 0
      main = {"buffer":{  "params" : {'hours' : days*24+hours }
                        , "method" : 'getUsers' 
                        , "type"   :  False
                       }
             }
      columns="name,njobsa,latestjob,cpua1,cpua7,cpup1,cpup7"
      if topsize==0 or topsize==None:  columns+=",scriptcache"
      q = pmt.getUsers(PRODUSERNAME,days*24+hours,columns=columns)
      header = q['header']
      users = q['rows']
      if PRODUSERNAME == None:
        if topsize > 0:
            title = "Recent %(topsize)d Top Panda Analysis Users" % { 'topsize' : topsize }
        else:
            title = "Recent Panda Analysis Users" 
      else:  
        title = "PanDA jobs for %s" % PRODUSERNAME
        main["buffer"]["params"]['user'] = PRODUSERNAME, 

      iNJobs = utils.name2Index(header,"njobsa") 
      iLatest = utils.name2Index(header,"latestjob") 

      jobpertime = {"anajobs" : 0, "n1000" : 0, "n10k" : 0 }
      recent = { "d3" :0, "d7" :0 , "d30" : 0, "d90" : 0, "d180" :0 }
      for u in users:
         nxtp =  u[iNJobs]
         if nxtp == None: continue
         nxtp = int(nxtp)
         if nxtp > 0 :  jobpertime["anajobs"] += nxtp 

         if nxtp > 1000:
                 jobpertime["n1000"] += 1; 
                 if nxtp > 10000:  jobpertime["n10k"] += 1
         nxtp =  u[iLatest]
         if nxtp  != None:
               diffdays = (datetime.utcnow()  - nxtp).days;
               if diffdays < 4:   recent["d3"]   += 1
               if diffdays < 8:   recent["d7"]   += 1
               if diffdays < 31:  recent["d30"]  += 1
               if diffdays < 91:  recent["d90"]  += 1
               if diffdays < 181: recent["d180"] += 1
      if topsize > 0 and top != None:
         iTop  = utils.name2Index(header,top)
         users = self.makeTop(users,iTop)[:topsize]
         main["buffer"]["top"] = { 'top' :  top, 'size' : topsize  }
         # remove thr   group 
               
      main["buffer"]["data"] = {'header' : header,'rows' : users }
      main["buffer"]["totaljobs"] = jobpertime
      main["buffer"]["recent"] = recent
      
      self.publishTitle(title)
      self.publish(main)
      self.publish( "%s/%s" % (utils.fileScriptURL(),"taskBuffer/%s.js" % "getUsers"),role="script")
      return

   def leftMenu(self):
       """ Return html for inclusion in left menu """
       txt = "<a href='%s/users'>Users</a>" % this.server().script()
       return txt

   def topMenu(self):
       """ Return html for inclusion in top menu """
       
def leftMenu():
    """ Return html for inclusion in left menu """
    txt = "<a href='%s/users'>Users</a>" % self.config().pandamon['url']
    return txt
