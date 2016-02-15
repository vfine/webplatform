""" Display Tthe PanDA Users Info """
#  $Id$
#
import re, os
from datetime import datetime, timedelta

import pmConfig.pmConfig as config
import pmUtils.pmUtils as utils
from  pmCore.pmModule import pmModule
from  pmTaskBuffer.pmTaskBuffer import pmtaskbuffer as pmt
from operator import itemgetter, attrgetter

class listusers(pmModule):

   #______________________________________________________________________________________      
   def __init__(self,name=None,parent=None,obj=None):
      pmModule.__init__(self,name,parent,obj)
      self.publishUI(self.doJson)
   #______________________________________________________________________________________      
   def makeTop(self,users,top):
      return sorted(users, key=itemgetter(*top), reverse=True)
   #______________________________________________________________________________________      
   def doJson(self,hours=None,days=180,tstart=None,tend=None,PRODUSERNAME=None,top='CPUA7', topsize=0,name=None):
      """ Get the list of the users
          <ul>
          <li> hours = use the last hours 
          <li> days = use the last days 
          <li> PRODUSERNAME or name - the comma separated pattern to select the list of the users.
          <li> topsize - the size of the top list 
          <br> = 0 - all users are shown
          <li> top - the comma separated list to select top users using 'top' columns. 
             <ul>
                <li> 'nJobsA' - the number  of the jobs
                <li> 'CPUA1' - Personal the CPU used for the last 24 hours
                <li> 'CPUA7' - Personal Cpu used for the last 7 days
                <li> 'CPUP1'- Group the CPU used for the last 24 hours
                <li> 'CPUP7'- Group Cpu used for the last 7 days
            </ul>
            The order of the column names defines the default sorting.
            <br>For example: top='cpua7,nJobsA'    creates the table sorted by "7 days " cpu and by "number of the jobs"
            <br> the parameter is essential for CLI (aka 'curl'/'ajax') clients. The Web Browser user can override the default by clicking onto the column header 
          </ul>
      """
      if days == None: days = 0
      if hours == None: hours = 0
      main = {"buffer":{  "params" : {'hours' : days*24+hours }
                        , "method" : 'getUsers' 
                        , "type"   :  False
                       }
             }
      columns="name,njobsa,cpua1,cpua7,latestjob"
      if topsize==0 or topsize==None:  columns="name,njobsa,latestjob,cpua1,cpua7,cpup1,cpup7,scriptcache"
      elif 'pup' in top.lower():
            columns="name,njobsa,cpup1,cpup7,latestjob,scriptcache"
      if PRODUSERNAME == None: PRODUSERNAME = name
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
      iCpua1 = utils.name2Index(header,"cpua1") 
      iCpua7 = utils.name2Index(header,"cpua7") 
      iCpup1 = utils.name2Index(header,"cpup1") 
      iCpup7 = utils.name2Index(header,"cpup7") 

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
         if  topsize > 0 and diffdays  > 7 :
            # exclude the old users from the count
            if iCpua1 >=0: u[iCpua1] = 0;
            if iCpua7 >=0: u[iCpua7] = 0;
            if iCpup1 >=0: u[iCpup1] = 0;
            if iCpup1 >=0: u[iCpup7] = 0;
                      
      if topsize > 0 and top != None:
         vtop = top.split(",")
         iTop = tuple( utils.name2Index(header,t) for t in vtop)
         users = self.makeTop(users,iTop)[:topsize]
         main["buffer"]["top"] = { 'top' :  top, 'size' : topsize  }
         njobsa = 0
         cpua1  = 0
         cpua7  = 0
         cpup1  = 0
         cpup7  = 0
         finalusers = []
         for u in users:
            nxtp = u[iNJobs]
            if nxtp == None: continue
            njobsa+= nxtp
            cpu = 0
            if iCpua1 >=0: 
               cpua1 += u[iCpua1]
               cpu += u[iCpua1]
            if iCpua7 >=0: 
               cpua7 += u[iCpua7]
               cpu += u[iCpua7]
            if iCpup1 >=0: 
               cpup1 += u[iCpup1]
               cpu += u[iCpup1]
            if iCpup7 >=0: 
               cpup7 += u[iCpup7]
               cpu += u[iCpup7]
            if cpu >0:
               njobsa+= nxtp
               finalusers.append(u)
         users =  finalusers     

      main["buffer"]["data"] = {'header' : header,'rows' : users }
      main["buffer"]["totaljobs"] = jobpertime
      if topsize > 0:
         if iCpua1>=0 or iCpua7 >=0:
            main["buffer"]["totaltop"] = {'njobsa' :njobsa,'cpua1':cpua1, 'cpua7': cpua7 }
         else:    
            main["buffer"]["totaltop"] = {'njobsa' :njobsa,'cpup1':cpup1, 'cpup7': cpup7 }
      main["buffer"]["recent"] = recent
      
      self.publishTitle(title)
      self.publish(main)
      self.publish( "%s/%s" % (self.server().fileScriptURL(),"taskBuffer/%s.js" % "getUsers"),role="script")
      return

