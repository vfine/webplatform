"""  List the Active Multicore Sites </td><td>$Rev: 17747 $"""
# $Id$
import re, os
from datetime import datetime, timedelta

import pmConfig.pmConfig as config
import pmUtils.pmUtils as utils
from pmUtils.pmState import pmstate
from  pmCore.pmModule import pmModule
from  pmTaskBuffer.pmTaskBuffer import pmtaskbuffer as pmt

#______________________________________________________________________________________      
def leftMenu():
    """ Return html for inclusion in left menu """
    txt = "<a href='%s/mcore'>Monitor</a>" % self.server().branchUrl()
    return txt

#______________________________________________________________________________________      
def topMenu():
    """ Return html for inclusion in top menu """
    
class mcore(pmModule):
   """  List the Active Multicore Sites </td><td>$Rev: 17747 $"""
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
   def doQuery(self,jobtype='production,test',hours=12,cores=2,vo=None,computingSite=None,processingType=None,workingGroup=None,prodUserName=None,specialHandling=None,region=False):
      if int(hours) > 24 * 3: 
            hours = 24 * 3
            title = 'Job summary from the MultiCore sites for the last %s hours only.' % hours #  Use <a href="%s/?%s">"stats"</a> page to see all %s hours' % ( 24 * 3, utils.monURL, 'mode=sitestats', hours )
      else:
            title = 'Job summary from the MultiCore sites for the last %s hours' % hours
      self.publishTitle(title)
      modes = ( 'Defined', 'Waiting', 'Active', 'Archived' )
      rows = []
      cores = cores if cores != None else 0
      for mode in modes:
         q = pmt.getCloudSummary(jobtype,vo,hours,selectionFields='computingSite,processingType,workingGroup, prodUserName,specialHandling,coreCount', tablename='ATLAS_PANDA.jobs%s4' % mode)
         if len(rows) == 0: header =  q['header']
         rows += q['rows']
      ### Build the jobsumd dictionary
      jobsumd     = {}
      proctyped   = {}
      workgroupd  = {}
      userd       = {}
      spechandled = {}
      for c in self.clouds:
         jobsumd[c] = {}
         jobsumd[c]['ALL'] = [0]*(self.lstates+1)
         if c != 'ALL':
            jobsumd[c]['status'] = self.cloudList[c]['status']
      iCloud = utils.name2Index(header,'cloud')
      print utils.lineInfo(), header
      iComputingSite = utils.name2Index(header,'computingSite')
      iStatus     = utils.name2Index(header,'jobStatus')
      iProctype   = utils.name2Index(header,'processingType')
      iSpechandle = utils.name2Index(header,'specialHandling')
      iWorkgroup  = utils.name2Index(header,'workingGroup')
      iUser       = utils.name2Index(header,'prodUserName')
      iCore       = utils.name2Index(header,'coreCount')
      iCount      = utils.name2Index(header,'COUNT')
      for r in rows:
         ncores     = r[iCore]  if  r[iCore] != None else 0
         if cores != 0 and ncores < cores: continue
         site       = r[iComputingSite]
         if site == None:
            # print "Db record doesn't define any site: %s " % r
            if region: continue
            site="Unknown"
            # continue
         cloud      = r[iCloud] # utils.getCloud4Site(r)          
         status     = r[iStatus]
         istatus  =   utils.name2Index(self.jobstates,status)
         proctype   = r[iProctype]
         spechandle = r[iSpechandle]
         workgroup  = r[iWorkgroup]
         user       = r[iUser]
         count      = r[iCount]
         if not cloud in jobsumd:
             print 'Unknown cloud: %s for site  %s ' % ( cloud, site)
             continue
         cloud = 'ALL'    
         if not status in self.jobstates:
             print 'Unknown jobstate:', status
             continue
         if not site in jobsumd[cloud]:
             jobsumd[cloud][site] = {}
             jobsumd[cloud][site] = [0]*(self.lstates+1)
             jobsumd[cloud][site][self.lstates] = ncores if ncores != None else 0
         jobsumd[cloud][site][istatus]  += count
         if cloud != 'ALL': jobsumd[cloud]['ALL'][istatus] += count
         jobsumd['ALL']['ALL'][istatus] += count
         proctyped[proctype]     = proctyped.get(proctype,0)     + count
         workgroupd[workgroup]   = workgroupd.get(workgroup,0)   + count
         userd[user]             = userd.get(user,0)             + count
         if spechandle != None: 
            spechandled[spechandle] = spechandled.get(spechandle,0) + count
      
      ## Get cloud/site status
      main = {}
      main['states'] = self.jobstates      
      main['jobsumd'] = jobsumd
      main['params'] = {   'jobtype': jobtype,'hours': hours,'vo':vo
                          ,'computingSite': computingSite
                          ,'processingType': processingType
                          ,'workingGroup':workingGroup
                          ,'prodUserName':prodUserName
                          ,'specialHandling':specialHandling
                          ,'cores' : cores
                          ,'region' : region}
      self.publish(main)
      self.publishNav(' type=%s hours=%s'  % (jobtype, hours ) )
      self.publish( "%s/%s" % ( self.server().fileScriptURL(),"monitor/%s.js" % "mcore" ),role="script")
    

