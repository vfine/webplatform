""" List the Errors for the selected Panda Jobs  </td><td>$Rev: 18196 $"""
# job.py
# Display Panda job lists and job details
# $Id$
#
import re, time, calendar, os, copy,math
from datetime import datetime
from  pmTaskBuffer.pmTaskBuffer import pmtaskbuffer as pmt
import pmConfig.pmConfig as config
import pmUtils.pmUtils as utils
from pmUtils.pmState import pmstate
from pmUtils.pmOracle import sqlSelect
from pmCore.pmModule import pmModule
from pmCore.pmModule import pmRoles
from  monitor.nameMappings import nmap
from  monitor.PandaHistogram import *
from  monitor.PilotTiming import PilotTiming
from pmUtils.pmJobUtil import pmJobUtil as setutils

class jobtiming(pmModule):
   #______________________________________________________________________________________      
   def __init__(self,name=None,parent=None,obj=None):
      pmModule.__init__(self,name,parent,obj)
      self._description,params = utils.normalizeDbSchema(pmt,'jobsarchived4',['metadata','jobparameters'])
      self._region4sites,self._sites4regions = setutils.region4Sites(pmt)
      ## 'publishUI' must be the last init statement  !
      self.publishUI(self.doJson,params=params)
     
   #______________________________________________________________________________________      
   def doJson(self,pandaid=None,jobtype=None,item=None,hours=12,tstart=None, tend=None, days=None,timeField = None,edge=None,minerrs=3,maxplot=5,opt="sum+item",region=None):
      """Display the job timing distribution: 
     <p>Sample queries:
     <ul>
      <li><a href='http://pandamon.cern.ch/jobtiming?tstart=2013-04-07 00:00&amp;tend=2013-04-07 00:03&amp;hours='>http://pandamon.cern.ch/jobtiming/?tstart=2011-06-07 00:00&amp;tend=2011-06-07 00:01</a>
       <li><a href='http://pandamon.cern.ch/jobtiming?tstart=2013-04-07 00:00&amp;tend=2013-04-07 00:03&amp;hours=&amp;processingType=simul'>http://pandamon.cern.ch/jobtiming/?tstart=2011-06-07 00:00&amp;tend=2011-06-07 00:01&prodUserName=borut.kersevan@ijs.si</a>
       <li><a href='http://pandamon.cern.ch/jobtiming?job=1246240909'>http://pandamon.cern.ch/jobtiming?job=1246240909</a>
      </ul>
          <hr>
          Supported query parameters are as follows:
          <table>
          <!--
          <tr><td>item=taskID</td><td> - cloud / computingSite / jobsetID / taskID any <a title='Click to see the full list of the jobtiming parameters available' href='http://pandamon.cern.ch/describe?table=^JOBSARCHIVED4&doc=*'>other job paramter</a> to build the error distribution for</td></tr>\
          <tr><td>jobtype=production</td><td> - select the 'jobtype' jobs: analysys, production, install, test </td></tr>
          <tr><td>edge=None</td><td> -  parameter to sort out the rare errors. <br>By default' the edge = 4*hours/12. Use edge=0 to see all errors.
          <tr><td>minerrs=3</td><td>  - parameters to hide the plots with the number of the errors &le;<code>minerr</code> </td></tr>
          <tr><td>maxplot=5</td><td>  - Only top maxplot parameters are to be drawn onto one plot.
          -->
          <tr><td>tstart=None</td><td>  - start time </td></tr>
          <tr><td>tend=None</td><td>    - end time</td></tr>
          <tr><td>hours=N </td><td> - last (N hours + N days) or N hours after 'tstart'  or N hours before 'tend' </td></tr> 
          <tr><td>days=N</td><td>   - last (N hours + N days)  (see the hours parameter documentaion</td></tr>
          <tr><td><a title='Click to see the full list of the jobtiming parameters available' href='http://pandamon.cern.ch/describe?table=^JOBSARCHIVED4&doc=*'>PARAM</a>=value</td><td>-  comma-separated list of the value <a href ='https://twiki.cern.ch/twiki/bin/view/PanDA/PandaPlatform#API_parameter_value_format'> patterns</a> to filter the job records.<br>
          For example: <ul><li><a href='http://pandamon.cern.ch/jobs/jobtiming?processingType=simul'>http://pandamon.cern.ch/jobs/jobtiming?processingType=simul</a>
          <li> <a href='http://pandamon.cern.ch/jobs/jobtiming?hours=4&processingType=ganga*,test'>http://pandamon.cern.ch/jobs/jobtiming?hours=4&processingType=ganga*,test</a></ul>
          </table>
      """
#       % { 'url' : self.server().branchUrl() }
      if timeField == None or timeField=='undefined' or timeField=='': timeField ='modificationTime'
      title = "Jobs' Time Distribution"
      if days != None:
         title += ' for %d day' % days
         if days>1: title+="s"
      if hours == 'undefined' : hours=None
      if hours != None: 
         if days == None: title += " for "
         title += ' %d hour' % hours
         if hours>1: title+="s"
      self.publishTitle( title )
      duration = sqlSelect().prepareTime(hours, tstart, tend, 'modificationTime', days).times('duration')
      if edge==None:
         if duration!=None: edge = utils.total_hours(duration)/6 + 6
         else: edge = 3
      # print utils.lineInfo(), errorcol
      self.publish(self.doJobs(jobtype,item,hours,tstart, tend, days,timeField,edge,minerrs,maxplot,opt,region))
      self.publish( {'s-maxage':600,'max-age':600}, role=pmRoles.cache())
      self.publish( "%s/%s" % (self.server().fileScriptURL(),"monitor/jobtiming.js"),role=pmRoles.script() )

   #______________________________________________________________________________________      
   def sqlTime(self, dbtime):
      ''' YYMMDDhh24MI '''
      dt = '%s0' %  dbtime
      return datetime.strptime(dt,'%y%m%d%H%M')
   #______________________________________________________________________________________      
   def timeBins(cls,minTime,maxTime, resolution): 
      """ Make sure  the hist has 3 bins """
      maxTime += resolution     
      hours =  utils.total_hours(resolution)
      nbins=utils.total_hours(maxTime-minTime)/hours
      dhours2 = timedelta(hours=math.ceil(hours/2.0))
      if nbins < 3:
         maxTime += dhours2
         minTime -= dhours2
      if nbins < 2:
         maxTime += dhours2
         minTime -= dhours2
      return (minTime,maxTime)
   #______________________________________________________________________________________      
   def getSite4Region(self,regions):
      regs = None  
      if utils.isValid(regions):
         rgs = utils.parseArray(regions);
         regs = []
         for r in rgs:
            regs += self._sites4regions[r]
      return regs

   #______________________________________________________________________________________      
   def doJobs(self, jobtype,item,hours,tstart, tend, days,timeField,edge,minerrs,maxplot,opt,region):
    #items 'taskID, jobsetID, computingSite 
    ## Perform the query
      conditions = None
      main = {}
      errorcolcheck = False
      selection = '*'
      vals = self.extraValuesFilled() 
      if vals == None: vals = {}
      optsum = False
      optitem= False
      opttime= False
      opterr = False
      if utils.isFilled(opt):
         optsum  = 'sum' in opt.lower()
         optitem = 'item' in opt.lower()
         opttime = 'time' in opt.lower()
         opterr  = 'error' in opt.lower()
      if  not (optsum or  optitem or opttime): optsum=True
      for k in vals:
           if vals[k]=='undefined': vals[k]=None
           elif  vals[k] != None and k.lower() == 'jobstatus' and  (vals[k].lower().find('prerun') >=0 or vals[k].lower().find('finishing') >=0 or vals[k].lower().find('unassigned') >=0 or vals[k].lower().find('retried')>=0) :
               stvals= utils.parseArray(vals[k])
               statvals = []
               for v in stvals:
                  if v.lower() == 'prerun': 
                     statvals += ['defined','assigned','waiting','activated','pending','sent','starting']
                  elif v.lower() == 'finishing': 
                     statvals += ['holding','transferring']
                  elif v.lower() == 'unassigned':
                     vals['computingSite']='NULL'
                     statvals += ['cancelled']
                  elif v.lower() == 'retried':
                     # See the slide 3 from Tadashi: https://indico.cern.ch/getFile.py/access?contribId=13&sessionId=11&resId=0&materialId=slides&confId=119171 
                     vals['taskBufferErrorCode']=[106,107]
                     statvals += ['failed']
                  else:   
                     statvals  += [v]
                  vals[k] = ','.join(statvals)
      if not vals.has_key('jobStatus'):
          vals['jobStatus'] = ','.join(['cancelled','finished','failed'] )
      cleanVal  = dict((k,v) for k,v in vals.iteritems() if v is not None )
      vals = cleanVal
      try:
         if vals.get('prodUserName') == 'auto':
            if self.server().certificate() != None: vals['prodUserName'] =pmt.cleanUserID(self.server().certificate())
      except:
         pass
      nav = ''
      condpars= []
      for v in vals:
         nav += "<b>%s</b>=%s " %(v,vals[v]) 
         if v!=item and v!='jobStatus':
            condpars += ['%s=%s' %(v,vals[v] ) ]
      if len(condpars) >0:
         condpars = '&' + '&'.join(condpars)
      else:
         condpars=''
      self.publishNav(nav)  
      if len(vals) == 0: vals = None    
      selection = {}
      if vals != None: selection.update(vals)
      if region != None: selection.update({'region':region})
      main['Selection'] = selection
      main['hist'] = {}
      main['opt'] = {'sum':optsum,'time':opttime,'item':optitem}
      conditions=vals
      site4region = self.getSite4Region(region)
      if site4region != None and len(site4region)>0:
         cs = conditions.get('computingSite',[])
         conditions['computingSite'] = cs + site4region
      jobparam = 'pilotTiming,cpuConsumptionTime,cpuConversion'
      if item != None: jobparam += ",%s" % item
      pandaid = conditions.get('PandaID') if conditions!= None else None
      jobtimings = pmt.getJobsAtt(pandaid, jobparam,conditions, None, hours, tstart, tend, timeField, days,None,jobtype,testsite=None,limit=None)
      # find the time range
      #print utils.lineInfo(), jobtimings
      maxTime = None
      minTime = None
      resolution = 60
      iPilotTiming = utils.name2Index(jobtimings['header'],'pilotTiming')
      iCpu         = utils.name2Index(jobtimings['header'],'cpuConsumptionTime')
      iCpuFactor   = utils.name2Index(jobtimings['header'],'cpuConversion')      
      ptime = []
      cputime = []
      rows = jobtimings['rows']
      mx = {}
      mn = {}
      histograms = {}
      cpu = 'cpu'
      if len(rows) > 0:
         for job in rows:
            try: 
               t = cpu
               value = job[iCpu]*job[iCpuFactor]/3600.
               if value > 0: 
                  mx[t] = max(mx.get(t,value),value) 
                  mn[t] = min(mn.get(t,value),value) 
                  cputime.append(value)
            except:
               pass
            try:
               pilotTime = PilotTiming(job[iPilotTiming])
               for t in pilotTime:
                  pt = pilotTime[t]
                  value = pt.value/60.
                  if t in ['execute',]: value /= 60.
                  # print utils.lineInfo(),t, job,value
                  mx[t] = max(mx.get(t,value),value) 
                  mn[t] = min(mx.get(t,value),value) 
               ptime.append(pilotTime)
            except:
               pass
         for t in mx:
            h = PandaHistogram('%s distributiion' % t, 0.0, mx[t],None,resolution)
            histograms[t] = h
            if t == cpu:
               for c in cputime:                  
                  h.fill(c)
            else:
               for pilotTime in ptime: 
                  try:
                     pt = pilotTime[t]
                     value =  pt.value/60.
                     if t in ['execute',]: value /= 60.
                     h.fill( value )
                  except:
                     pass
         # exclude the empty histograms:
         for t in histograms.keys():
            if histograms[t].integral() == 0:  del histograms[t]
         main['hist'] = histograms
         main['opt'] = {'sum':optsum,'time':opttime,'item':optitem, 'error':opterr} 
      else:
         main['hist'] = None
      return main
 