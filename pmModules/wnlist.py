""" List The Worker Nodes </td><td>$Rev$"""
# $Id: wnlist.py 18220 2014-02-04 02:37:48Z fine $
# Author Valeri Fine (fine@bnl.gov) 
# 6/6/2012
import re, os
from datetime import datetime, timedelta

import pmConfig.pmConfig as config
import pmUtils.pmUtils as utils
from pmUtils.pmState import pmstate
from  pmCore.pmModule import pmModule
from  pmTaskBuffer.pmTaskBuffer import pmtaskbuffer as pmt
from pmCore.pmModule import pmRoles

class wnlist(pmModule):
   """ List The Worker Nodes """
   #______________________________________________________________________________________      
   def __init__(self,name=None,parent=None,obj=None):
      pmModule.__init__(self,name,parent,obj)
      
      self._jobstates = utils.jobStates
      self._lstates = len(self._jobstates)
      actIndex = utils.name2Index(self._jobstates,'activated')+1
      canIndex = utils.name2Index(self._jobstates,'cancelled')+1
      self._jobsFactoryStates = utils.parseArray(self._jobstates[:actIndex])
      self._jobsWNStates = utils.parseArray(self._jobstates[actIndex:canIndex-1])
      self._jobsCaneledStates = utils.parseArray(self._jobstates[canIndex:])
      shift = 1
      self._shift = shift
      self._ifailed =  utils.name2Index(self._jobstates,'failed')+shift
      self._itotal = self._lstates+shift
      self._ifail = 0
      self._description,params = utils.normalizeDbSchema(pmt,'jobsarchived4')
      self.publishUI(self.doQuery,params = params)
   #______________________________________________________________________________________      
   def factory(self):
       return self._jobsFactoryStates
   #______________________________________________________________________________________      
   def wn(self):
       return self._jobsWNStates
   #______________________________________________________________________________________      
   def status(self,f,w):
     return [0]*(self.total(f,w)+1)
   #______________________________________________________________________________________      
   def states(self,factory,wn):
      sts = self._jobstates
      if (factory == None and wn != None) or (factory != None and wn == None):
         if factory != None:
            sts = self.factory()
         else:
            sts = self.wn()
      return sts
   #______________________________________________________________________________________      
   def total(self,f,w):
      return len(self.states(f,w))+self._shift
   #______________________________________________________________________________________      
   def failed(self,f,w):
      ifl =  utils.name2Index(self.states(f,w),'failed')
      if ifl !=None: ifl += self._shift
      return ifl
   #______________________________________________________________________________________      
   def site (self,siteName,f,w):
      return {'nm' : siteName, 'st' : self.status(f,w),  'hosts' : [] }
   #______________________________________________________________________________________      
   def host(self, hostname,f,w):
     return {'nm' :  hostname, 'st' : self.status(f,w) }
   #______________________________________________________________________________________      
   def countFail(self,ce,w):
      f = None
      ce[self._ifail] = 100*ce[self.failed(f,w)]/ce[ self.total(f,w) ] 

   #______________________________________________________________________________________      
   def do(self,header,rows,site,hostonly,details,f,w):
      states =  self.states(f,w)
      iHost = utils.name2Index(header,'modificationhost')
      iSite = utils.name2Index(header,'computingSite')
      iStatus = utils.name2Index(header,'jobStatus')
      iJobs= utils.name2Index(header,'jobs')
      itotal = self.total(f,w)
      lrow = itotal+2
      allSitesTotal =  self.status(f,w)
      sites = []
      wnlist =  { 'st' :allSitesTotal, 'sites' : sites }
      wnlistStatus = wnlist['st']
      nxSite = {'nm': None }
      nxHost = {'nm': None }
      hostStatus = None
      hosts = {}
      hostonly = isinstance(hostonly ,str)  and hostonly.lower() == 'yes'
      sitesStat = {}
      for r in rows:
         if details != 'summary':
            siteName =  r[iSite]
            if siteName == None: siteName = 'UNDEFINED'
            if sitesStat.has_key(siteName):
               siteStatus =  sitesStat[siteName]
            else: 
               nxSite = self.site(siteName,f,w)
               siteStatus = nxSite['st']
               sites.append(nxSite)
               nxHost = {'nm' : None}
               hosts = {}
               sitesStat[siteName] = siteStatus
         host = r[iHost]
         if hostonly: host = utils.hostName(host)
         if not hosts.has_key(host): 
            nxHost  =  self.host(host,f,w)
            hostStatus = nxHost['st']
            if details and details != 'summary': nxSite['hosts'].append(nxHost)
            hosts[host] = hostStatus
         else:
            hostStatus = hosts[host]
         status = r[iStatus]
         jbs =  r[iJobs]
         istatus  =   utils.name2Index(states,status)+1
         if details and details != 'summary':
            hostStatus[istatus]       +=  jbs
            hostStatus[itotal]  +=  jbs
         if details != 'summary':
            siteStatus[istatus]       +=  jbs
            siteStatus[itotal]  +=  jbs
         wnlistStatus[istatus]     +=  jbs   
         wnlistStatus[itotal]+=  jbs
      # ---
      if f == None:
         if len(rows) > 0:
            self.countFail(wnlistStatus,w)
         wsites = wnlist['sites']   
         for c in wsites:
            self.countFail(c['st'],w)
            for h in c['hosts']:
               self.countFail(h['st'],w)
            c['hosts'] = sorted(c['hosts'], key=lambda site: site['nm'])    
      header = ['fail'] + list(states) + ['Total']
      res = {"header" : header , 'status' : wnlist}
      # print utils.lineInfo(), details ,len(hosts) 
      if details == 'summary':
         res['hosts']=len(hosts)
      return res
      
   #______________________________________________________________________________________      
   def doQuery(self,site='all',jobtype='all',days=1,hostonly='yes',plot='finished,failed',style='SB', details=None,deep='no'):
      """ Get the list of the  jobs' status per worker node for selected site for upto 3 last days
        <ol>
        <li><code>site</code> - site to get the information about or "all"
        <li><code>jobtype</code> = 'production" or " analysis" or "all"
        <li><code>days</code> - number of days we want to fetch the information for. This parameter must be less or equal 3. 
        <li><code>hostonly</code> - "yes" . "no" - means provide the information 'per CPU' rather 'per host'
        <li><code>plot</code> - the comma separated list of the <a href='https://twiki.cern.ch/twiki/bin/viewauth/Atlas/PandaShiftGuide#Job_state_definitions_in_Panda'>job status names</a> to generate the plot for 
        <li><code>style</code>  the combination of the symbols: 'H' - histogram, 'B' - bar , 'L' - line, 'P' - points, 'S' - stacked<br>
             = 'BS' - 'by default'
        <li><code>details</code> - 'yes' - provide   the status per host<br>
        <br>  = 'summary' - provide the summary only <br>
             default = 'yes' if not site == 'all' else 'no'
        <li><code>deep</code> - do not look up the "long job table" . It can be very slow.
             default = 'no'       
        <li> <b><a title='Click to see the full list of the  parameters available' href='http://pandamon.cern.ch/describe?table=^JOBSARCHIVED4&doc=*'>PARAM</a>=value</b> - comma-separated list of the value <a href ='https://twiki.cern.ch/twiki/bin/view/PanDA/PandaPlatform#API_parameter_value_format'> patterns</a> to filter the job records.
        <li><code>jobStatus</code> - it can be any comma-separated list of the Panda Jobs states patterns or / and <br>
        two 'meta' states: "factory" to list the "factory" nodes and "wn" to list the the Worker Nodes
        </ol>
      """
      vals = self.extraValuesFilled()
      if site == None: site='all'
      factory = None
      wn = None
      titletype = "PanDA"
      jobStatus = None
      if vals != None:
         jstat = vals.get('jobStatus')
         jobStatus  =  jstat
         if jstat != None:
            jstat = [x.lower() for x in utils.parseArray(jstat)]
            print utils.lineInfo(), jstat, 'factory' in jstat
            if 'factory' in jstat:
               factory = self.factory()
               jstat += factory
               titletype = "Factory"
            if 'wn' in jstat:
               wn = self.wn()
               jstat += wn
               titletype = "Worker"
            jstat = list(set(jstat))
            vals['jobStatus'] = ','.join(jstat)
      if deep == None or deep == False: deep =  'no'
      deep = not deep.lower() == 'no'
      title = ''
      hours =  (float(days))*24
      Deep = 'Deep' if deep else ''
      if float(days) > 3 and False and not deep: 
         days = 3.0
         hours = 24*days
         title = 'The List of the %s Nodes Activity for the Last %s Hours Only.' % (titletype, int(hours))
      else:
         title = 'The %s List of the %s  Nodes Activity for the %s Hours' % (Deep, titletype,int(hours)  )
         days = float(days)
      try:
        if jobtype.lower() == 'all': jobtype=None
      except:
         pass
      self.publishTitle(title)
      modes = ( 'Defined', 'Waiting', 'Active', 'Archived' )
      tables = []
      for mode in modes: tables += ['ATLAS_PANDA.jobs%s4' % mode]
      if days>3 and deep: tables += ['ATLAS_PANDAARCH.JOBSARCHIVED'] 
      q = pmt.wnList(site, jobtype, table=tables, days=days,conditions = vals)
      try:
         if details == None: 
            details = not (site == None or site == 'None' or site.lower() == 'all' or site == '*' )
         # else:
            # details = isinstance(details,str) and details.lower() == 'yes'
      except:
         details = False       
      ## Publish the result
      main = {}
      main['data'] = self.do(q['header'],q['rows'],site,hostonly,details,factory,wn)
      main['params'] = { 'jobtype': jobtype,'days': days,'site': site,'hostonly':hostonly,'jobStatus':jobStatus}
      plotpars = []
      if plot:
         for p in plot.split(","):
            if p.lower() == 'prerun' or factory != None: 
               if wn == None: plotpars += self.factory()
               if factory == None:
                  plotpars += ['pending','sent','starting']
            elif p.lower() == 'finishing' and factory == None: 
               plotpars += ['holding','transferring']
            else:
               plotpars += [p]
         main['params']['plot'] = list(set(plotpars)) # remove duplicates
      if style: main['params']['style'] = style
      self.publish(main)
      self.publishNav(' type=%s days= last %s '  % (jobtype, days ) )
      self.publish( "%s/%s" % ( self.server().fileScriptURL(),"monitor/%s.js" % "wnlist" ),role=pmRoles.script())
      self.publish( {'s-maxage':600,'max-age': 600}, role=pmRoles.cache())
    

