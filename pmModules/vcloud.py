""" List the Virtual Clouds """
# $Id: vcloud.py 15475 2013-05-15 21:03:05Z fine $
#
import re, os
from datetime import datetime, timedelta

import pmConfig.pmConfig as config
import pmUtils.pmUtils as utils
from  pmUtils.pmState import pmstate
from  pmCore.pmModule import pmModule
from pmCore.pmModule import pmRoles
from  pmTaskBuffer.pmTaskBuffer import pmtaskbuffer as pmt

#______________________________________________________________________________________      
def leftMenu():
    """ Return html for inclusion in left menu """
    txt = "<a href='%s/vcloud'>Virtual Clouds</a>" % self.server().branchUrl()
    return txt

#______________________________________________________________________________________      
def topMenu():
    """ Return html for inclusion in top menu """
    
class vcloud(pmModule):
   """ List the Virtual Clouds """
   #______________________________________________________________________________________      
   def __init__(self,name=None,parent=None,obj=None):
      pmModule.__init__(self,name,parent,obj)
      self.jobstates = utils.jobStates
      self.lstates = len(self.jobstates)
      self.cloudList= pmt.getCloudList()
      self.clouds = ['ALL']
      self.clouds +=  self.cloudList.keys()
#      self.clouds = 'ALL CA CERN DE ES FR IT ND NL TW UK US OSG '.split()
      self.publishUI(self.doQuery)

   #______________________________________________________________________________________      
   def doQuery(self,jobtype='production',hours=24,vcloud='IAAS',testJobs=None):
      if int(hours) > 24 * 3: 
            hours = 24 * 3
            title = "ATLAS '%s' Virtualized Sites for the Last %s Hours Only." % (vcloud,hours) #  Use <a href="%s/?%s">"stats"</a> page to see all %s hours' % ( 24 * 3, utils.monURL, 'mode=sitestats', hours )
      else:
            title = "ATLAS '%s' Virtualized Sites for the last %s hours" % (vcloud,hours)
      self.publishTitle(title)
      modes = ( 'Defined', 'Waiting', 'Active', 'Archived' )
      rows = []
      t = []
      for mode in modes: t += ['ATLAS_PANDA.jobs%s4' % mode]
      q = pmt.getVCloudSummary(jobtype,hours,table=','.join(t),vcloud=vcloud,testsite=(testJobs!=None))
      header = q['header']
      rows = q['rows']
      ### Build the jobsumd dictionary
      jobsumd     = {}
      for c in ['ALL',]:
         jobsumd[c] = {}
         jobsumd[c]['ALL'] = [0]*(self.lstates+2)
         
         jobsumd[c] = {}
         jobsumd[c]['ALL'] = [0]*(self.lstates+2)
         
         
      iCloud = utils.name2Index(header,'cloud')
      iComputingSite = utils.name2Index(header,'computingSite')
      iStatus     = utils.name2Index(header,'jobStatus')
      iCount      = utils.name2Index(header,'COUNT')
      iCpu        = utils.name2Index(header,'cpuConsumptionTime')
      icpu = self.lstates
      for r in rows:
         site       = r[iComputingSite]
         if site == None:
            # print "Db record doesn't define any site: %s " % r
            if region: continue
            site="Unknown"
            # continue
         cloud      = r[iCloud] # utils.getCloud4Site(r)
         status     = r[iStatus]
         istatus  =   utils.name2Index(self.jobstates,status)
         count      = r[iCount]
         cpu        = r[iCpu]
         if not jobsumd.has_key(cloud):
            jobsumd[cloud] = {}
            jobsumd[cloud]['ALL'] = [0]*(self.lstates+1)
            if cloud != 'ALL':
               jobsumd[cloud]['status'] = self.cloudList[cloud]['status']
            if cloud == 'CERN' and vcloud == 'IAAS': # fake site for the time being
               jobsumd[cloud]['HELIX_ATOS'] = {}
               jobsumd[cloud]['HELIX_ATOS'] = [0]*(self.lstates+1)

         if not status in self.jobstates:
             print 'Unknown jobstate:', status
             continue
         if not site in jobsumd[cloud]:
             jobsumd[cloud][site] = {}
             jobsumd[cloud][site] = [0]*(self.lstates+1)
         jobsumd[cloud][site][istatus]  += count
         jobsumd[cloud]['ALL'][istatus] += count
         jobsumd['ALL']['ALL'][istatus] += count
         
         jobsumd[cloud][site][icpu]  += cpu
         jobsumd[cloud]['ALL'][icpu] += cpu
         jobsumd['ALL']['ALL'][icpu] += cpu
      
      ## Get cloud/site status
      main = {}
      main['states'] = list(self.jobstates) + ["CPU (hours)"]
      main['jobsumd'] = jobsumd
      main['params'] = {   'jobtype': jobtype,'hours': hours
                          ,'computingSite': vcloud
                          }
      if testJobs == None:
         main['params']['srcLabel'] = 'managed'
      self.publish(main)
      self.publishNav(' <b>type</b>=%s <b>hours</b>=%s <b>date:</b> %s'  % (jobtype, hours, datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')  ) )
      self.publish( "%s/%s" % ( self.server().fileScriptURL(),"monitor/%s.js" % "vcloud" ),role=pmRoles.script() )
      self.publish( {'s-maxage':340,'max-age': 200}, role=pmRoles.cache()) 
    

