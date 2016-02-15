""" The Cloud Summary  </td><td>$Rev$"""
# $Id: cloudsummary.py 17477 2013-11-21 19:54:33Z fine $
#
import re, os
from datetime import datetime, timedelta

import pmConfig.pmConfig as config
import pmUtils.pmUtils as utils
from pmUtils.pmState import pmstate
from  pmCore.pmModule import pmModule
from pmCore.pmModule import pmRoles
from  pmTaskBuffer.pmTaskBuffer import pmtaskbuffer as pmt
from pmUtils.pmJobUtil import pmJobUtil as setutils

class cloudsummary(pmModule):
   """ The Cloud Summary  """
   #______________________________________________________________________________________      
   def __init__(self,name=None,parent=None,obj=None):
      pmModule.__init__(self,name,parent,obj)
      self.jobstates = ('Pilots','%fail','Latest')+utils.jobStates + ('unassigned',)
      self._ALL = ' ALL'
      self.lstates = len(self.jobstates)
      self.cloudList= pmt.getCloudList()
      self.clouds = [self._ALL]
      self.clouds +=  self.cloudList.keys() + ['CMS','AMS']
      self._region4sites,self._sites4region = setutils.region4Sites(pmt)
      self._iFailed = utils.name2Index(self.jobstates,'failed')
      self._iFinished  = utils.name2Index(self.jobstates,'finished')
      self._iRation    = utils.name2Index(self.jobstates,'%fail')
      self._iPilots    = utils.name2Index(self.jobstates,'Pilots');
      self._iLatest    = utils.name2Index(self.jobstates,'Latest');

      self._jobSum = [
                         ['States'         , 'status']
                        ,['Users'        , 'username']
                        ,['Releases'      ,'transUses']
                        ,['Processing Types' , 'processingType']
#                       ,['Analysis Tasks' , 'destinationDBlock']   # tasktype = 'analysis'
#                       ,['Output Dataset',  'destinationDBlock']   # tasktype = 'analysis'
                        ,['Task Labels'       , 'prodSourceLabel']
#                       , ['Task ID'       , 'JEDITASKID']
#                       ,['Batch system ID','batchID' ]
                       ,['Transformations', 'transPath']
#                       ,['Input dataset' , 'prodDBlock']
                        ,['Working groups', 'workingGroup']
#                       ,['Creation Hosts' , 'creationHost']
#                       ,['Packages'      , 'homepackage']  #  need constrain
#                       ,['Sites'          , 'computingSite']
#                       , ['Regions'      , 'Region']
                       , ['Clouds'        , 'cloud']
                       , ['Task Types'        , 'taskType']
                       , ['Jobs','JediTaskID'] 
#                       ,['Analysis Tasks', 'destinationDBlock']
#                       ,['Task Priorities' , 'currentPriority' ]# need constrain 
                  ]
 #      self.clouds = 'ALL CA CERN DE ES FR IT ND NL RU TW UK US OSG CMS AMS'.split()
      self._description,params = utils.normalizeDbSchema(pmt,'jobsarchived4')

      self.publishUI(self.doQuery,params=params)

   #______________________________________________________________________________________      
   def doQuery(self,jobtype='production',hours=12,region=None):
      """ 
      <ul>
      <li>jobtype  - production,analysis, test
      <li>hours  - production,analysis, test      
      <li>VO - virtual organization atlas,cms
      <li>computingSite
      <li>processingType
      <li>workingGroup
      <li>prodUserName
      <li>specialHandling
      </ul>      
      """      
      if int(hours) > 24 * 3: 
            hours = 24*3
            title = 'Job summary for the last %s hours only.' % hours  # Use <a href="%s/?%s">"stats"</a> page to see all %s hours' % ( 24 * 3, utils.monURL, 'mode=sitestats', hours )
      else:
            title = 'Job summary for the past %s hours' % hours
      pars = self.extraValuesFilled()
      self.publishTitle(title)
      nav = ' <b>type</b>=%s <b>hours</b>=%s'  % (jobtype, hours )
      if pars != None:
         for tp in ['computingSite','processingType','workingGroup', 'prodUserName', 'specialHandling']:
            if pars.get(tp) !=None: 
               nav += ' <b>%s</b>=%s' % (tp,pars[tp])
      modes = ( 'Defined', 'Waiting', 'Active', 'Archived' )
      rows = []
      for mode in modes:
         q  = pmt.getCloudSummary(jobtype,pars.get('VO') if pars!=None else None,hours,extraConditions=pars,selectionFields='computingSite,processingType,workingGroup, prodUserName,specialHandling,modificationTime', tablename='ATLAS_PANDA.jobs%s4' % mode)
         if len(rows) ==0: header =  q['header']
         rows += q['rows']
      # get getCurrentSiteData
      pilotd = pmt.getCurrentSiteData()
      ### Build the jobsumd dictionary
      jobsumd     = {}
      proctyped   = {}
      workgroupd  = {}
      userd       = {}
      spechandled = {}
      item = self.clouds
      if region != None:
         item = [self._ALL] + self._sites4region.keys()
      for c in item:
         jobsumd[c] = {}
         jobsumd[c][self._ALL] = [0]*self.lstates
         if c != self._ALL :
            jobsumd[c]['status'] = self.cloudList.get(c,{'status':'unknown'})['status']
      iCloud = utils.name2Index(header,'cloud')
      iComputingSite = utils.name2Index(header,'computingSite')
      iStatus     = utils.name2Index(header,'jobStatus')
      iProctype   = utils.name2Index(header,'processingType')
      iSpechandle = utils.name2Index(header,'specialHandling')
      iWorkgroup  = utils.name2Index(header,'workingGroup')
      iUser       = utils.name2Index(header,'prodUserName')
      iCount      = utils.name2Index(header,'COUNT')
      iTime       = utils.name2Index(header,'modificationTime')
      iLatest    = self._iLatest
      def updateTime(oldt,newt):
         ol = oldt[iLatest]
         if (ol != 0 and ol<newt) or ol==0: oldt[iLatest]  = newt
      for r in rows:
         site       = r[iComputingSite]
         if site == None:
            # print "Db record doesn't define any site: %s " % r
            regn = "unassigned"
            site="unassigned"
            if region!= None: continue
            # continue
         else:
            regn = self._region4sites.get(site,'unknown')
            if region!= None and regn == 'unknown': continue
         cloud      = r[iCloud] # utils.getCloud4Site(r)          
         status     = r[iStatus]
         if status == 'cancelled' and site == 'Unknown': status = 'unassigned'
         istatus  =   utils.name2Index(self.jobstates,status)
         proctype   = r[iProctype]
         spechandle = r[iSpechandle]
         workgroup  = r[iWorkgroup]
         user       = r[iUser]
         count      = r[iCount]
         time       = r[iTime]
         if region!=None: cloud = regn
         if not cloud in jobsumd:
             print 'Unknown cloud: %s for site  %s ' % ( cloud, site)
             continue
         if not status in self.jobstates:
             print 'Unknown jobstate:', status
             continue
         if not site in jobsumd[cloud]:
            jobsumd[cloud][site] = {}
            jobsumd[cloud][site] = [0]*self.lstates
         jobsumd[cloud][site][istatus]  += count
         jobsumd[cloud][self._ALL][istatus] += count
         jobsumd[self._ALL][self._ALL][istatus] += count

         updateTime(jobsumd[cloud][site], time)
         updateTime(jobsumd[cloud][self._ALL], time)
         updateTime(jobsumd[self._ALL][self._ALL], time)
         
         proctyped[proctype]     = proctyped.get(proctype,0)     + count
         workgroupd[workgroup]   = workgroupd.get(workgroup,0)   + count
         userd[user]             = userd.get(user,0)             + count
         if spechandle != None: 
            spechandled[spechandle] = spechandled.get(spechandle,0) + count

      iFailed    = self._iFailed
      iFinished  = self._iFinished  
      iRation    = self._iRation
      iPilots    = self._iPilots
      for cloud in jobsumd:
         for site in jobsumd[cloud]:
            if site == 'status': continue
            allcloud = jobsumd[cloud][site]
            ntot = allcloud[iFailed] + allcloud[iFinished]
            psite = pilotd.get(site)
            if psite:
               nplt = pilotd[site]['updateJob']+ pilotd[site]['getJob']
               jobsumd[cloud][site][iPilots]   = nplt
               jobsumd[cloud][self._ALL][iPilots] += nplt
               jobsumd[self._ALL][self._ALL][iPilots] += nplt
            if ntot >0:
               jobsumd[cloud][site][iRation] = 100.0*allcloud[iFailed]/ntot
      
      ## Get cloud/site status
      main = {}
      main['states'] = self.jobstates      
      main['jobsumd'] = jobsumd
      if pars == None: pars = {}
      if (hours!=None): 
         pars['hours'] = hours
      if (jobtype!=None): 
         pars['jobtype'] = jobtype
      if (region!=None): 
         pars['region'] = region
         nav += '  <b>region view</a>'
      main['params'] = pars
      self.publish(main)
      self.publishNav(nav)
      self.publish( "%s/%s" % ( self.server().fileScriptURL(),"monitor/%s.js" % "cloudsummary" ),role=pmRoles.script() )
    

