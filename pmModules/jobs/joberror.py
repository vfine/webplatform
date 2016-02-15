""" List the Errors for the selected Panda Jobs  </td><td>$Rev: 18195 $"""
# job.py
# Display Panda job lists and job details
# $Id$
#
import re, time, calendar, os, copy,math
from datetime import datetime
from  pmTaskBuffer.pmTaskBuffer import pmtaskbuffer as pmt
from  monitor.ErrorCodes  import errorcodes
import pmConfig.pmConfig as config
import pmUtils.pmUtils as utils
from pmUtils.pmState import pmstate
from pmUtils.pmOracle import sqlSelect
from pmCore.pmModule import pmModule
from pmCore.pmModule import pmRoles
from  monitor.nameMappings import nmap
from  monitor.PandaHistogram import *

from pmUtils.pmJobUtil import pmJobUtil as setutils

class joberror(pmModule):
   #______________________________________________________________________________________      
   def __init__(self,name=None,parent=None,obj=None):
      pmModule.__init__(self,name,parent,obj)
      self._description,params = utils.normalizeDbSchema(pmt,'jobsarchived4')
      self._errorFields, self._errorCodes, self._errorStages = errorcodes.getErrorCodes()
      self._exitFields = errorcodes.getExitCodes()
      self._errorFields = self._errorFields + self._exitFields
      self._region4sites,self._sites4regions = setutils.region4Sites(pmt)
      ## 'publishUI' must be the last init statement  !
      self.publishUI(self.doJson,params=params)

   #______________________________________________________________________________________
   def getErrors(self,job,header,errdict):
      """ collect the unique errors to publish """
      for errcode in self._errorCodes.keys():
         errval = 0
         indx = header.get(errcode);
         if indx == None: continue
         errval = job[indx]
         if errdict!=None:
            ec = errdict.get(errcode)
            if ec!=None: 
               ev = ec.get(errval)
               if ev != None: continue
         try: 
            if errval != 0 and errval != '0' and utils.isValid(errval):
               errval = int(errval)
   
               ## set prompt to True if error code is 1178 ##
               if errval == 1178: prompt = bool(1)

               errdiag = errcode.replace('ErrorCode','ErrorDiag')
               if errcode.find('ErrorCode') > 0:
                  diagtxt = job[header[errdiag]]
               else:
                  diagtxt = ''
               if utils.isValid(diagtxt) and len(diagtxt) > 0:
                  desc = diagtxt
               elif self._errorCodes[errcode].has_key(errval):
                   desc = self._errorCodes[errcode][errval]
               else:
                  desc = "Unknown %s error code %s" % ( errcode, errval )
               errname = errcode.replace('ErrorCode','')
               errname = errname.replace('ExitCode','')
               if errdict ==None: 
                  errdict = {errcode: { errval : ( errname, desc ) }}
               else:
                  errcd = errdict.get(errcode);
                  if errcd == None: errdict[errcode] =  { errval : ( errname, desc ) }
                  else:             errcd[errval]=( errname, desc )
         except:
            incident  = "Wrong  data: %s " % utils.reportError("Unexpected value '%s' of the '%s' error code" %(errval,errcode))
            # utils.recordIncident(incident,'monalarm')
            pass
      return errdict
      
   #______________________________________________________________________________________      
   def doJson(self,jobtype=None,errorcol=None,item='taskID',hours=12,tstart=None, tend=None, days=None,timeField = None,edge=None,minerrs=3,maxplot=5,opt="sum+item",region=None):
      """Display the job error distribution: 
     <p>Sample queries:
     <ul>
      <li><a href='http://pandamon.cern.ch/joberror?tstart=2013-04-07 00:00&amp;tend=2013-04-07 00:03&amp;hours='>http://pandamon.cern.ch/joberror/?tstart=2011-06-07 00:00&amp;tend=2011-06-07 00:01</a>
       <li><a href='http://pandamon.cern.ch/joberror?tstart=2013-04-07 00:00&amp;tend=2013-04-07 00:03&amp;hours=&amp;processingType=simul'>http://pandamon.cern.ch/joberror/?tstart=2011-06-07 00:00&amp;tend=2011-06-07 00:01&prodUserName=borut.kersevan@ijs.si</a>
       <li><a href='http://pandamon.cern.ch/joberror?job=1246240909'>http://pandamon.cern.ch/joberror?job=1246240909</a>
      </ul>
          <hr>
          Supported query parameters are as follows:
          <table>
          <tr><td>item=taskID</td><td> - cloud / computingSite / jobsetID / taskID any <a title='Click to see the full list of the joberror parameters available' href='http://pandamon.cern.ch/describe?table=^JOBSARCHIVED4&doc=*'>other job paramter</a> to build the error distribution for</td></tr>\
          <tr><td>jobtype=production</td><td> - select the 'jobtype' jobs: analysys, production, install, test </td></tr>
          <tr><td>edge=None</td><td> -  parameter to sort out the rare errors. <br>By default' the edge = 4*hours/12. Use edge=0 to see all errors.
          <tr><td>minerrs=3</td><td>  - parameters to hide the plots with the number of the errors &le;<code>minerr</code> </td></tr>
          <tr><td>maxplot=5</td><td>  - Only top maxplot parameters are to be drawn onto one plot.
          <tr><td>tstart=None</td><td>  - start time </td></tr>
          <tr><td>tend=None</td><td>    - end time</td></tr>
          <tr><td>hours=N </td><td> - last (N hours + N days) or N hours after 'tstart'  or N hours before 'tend' </td></tr> 
          <tr><td>days=N</td><td>   - last (N hours + N days)  (see the hours parameter documentaion</td></tr>
          <tr><td><a title='Click to see the full list of the joberror parameters available' href='http://pandamon.cern.ch/describe?table=^JOBSARCHIVED4&doc=*'>PARAM</a>=value</td><td>-  comma-separated list of the value <a href ='https://twiki.cern.ch/twiki/bin/view/PanDA/PandaPlatform#API_parameter_value_format'> patterns</a> to filter the job records.<br>
          For example: <ul><li><a href='http://pandamon.cern.ch/jobs/joberror?processingType=simul'>http://pandamon.cern.ch/jobs/joberror?processingType=simul</a>
          <li> <a href='http://pandamon.cern.ch/jobs/joberror?hours=4&processingType=ganga*,test'>http://pandamon.cern.ch/jobs/joberror?hours=4&processingType=ganga*,test</a></ul>
          </table>
      """
#       % { 'url' : self.server().branchUrl() }
      if timeField == None or timeField=='undefined' or timeField=='': timeField ='modificationTime'
      title = 'Error distribution'
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
      if True or self.isValid(errorcol):
         # print utils.lineInfo(), errorcol
         self.publish(self.doJobs(jobtype,errorcol,item,hours,tstart, tend, days,timeField,edge,minerrs,maxplot,opt,region))
         self.publish( {'s-maxage':4000,'max-age':4000}, role=pmRoles.cache())
         self.publish( "%s/%s" % (self.server().fileScriptURL(),"monitor/joberror.js"),role=pmRoles.script() )

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
   def doJobs(self, jobtype,errorcol,item,hours,tstart, tend, days,timeField,edge,minerrs,maxplot,opt,region):
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
      if vals != None:
         for k in vals:
              if  vals[k] != None and k.lower() == 'jobstatus' and  (vals[k].lower().find('prerun') >=0 or vals[k].lower().find('finishing') >=0 or vals[k].lower().find('unassigned') >=0 or vals[k].lower().find('retried')>=0) :
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
#      cleanVal  = dict((k,v) for k,v in vals.iteritems() if v is not None )
#      vals = cleanVal
      try:
         if vals.get('prodUserName') == 'auto':
            if self.server().certificate() != None: vals['prodUserName'] =pmt.cleanUserID(self.server().certificate())
      except:
         pass
      nav = ''
      condpars= []
      if vals != None:
         for v in vals:
            nav += "<b>%s</b>=%s " %(v,vals[v]) 
            if v!=item and v!='jobStatus':
               condpars += ['%s=%s' %(v,vals[v] ) ]
      if len(condpars) >0:
         condpars = '&' + '&'.join(condpars)
      else:
         condpars=''
      self.publishNav(nav)  
      if vals != None and len(vals) == 0: vals = None    
      selection = {}
      if vals != None: selection.update(vals)
      if region != None: selection.update({'region':region})
      main['Selection'] = selection
      main['hist'] = {}
      main['opt'] = {'sum':optsum,'time':opttime,'item':optitem}
      conditions=vals
      if conditions != None and conditions.get('computingSite') == None:
         site4region = self.getSite4Region(region)
         if site4region != None and len(site4region)>0:
            conditions['computingSite'] = site4region
      joberrors = pmt.getErrorCount(jobtype=jobtype,errorcol=self._errorFields,item=item,timefield='modificationTime',hours=hours,tstart=tstart,tend=tend,days=days,conditions=conditions)
      # find the time range
      # print utils.lineInfo(), self._errorFields, joberrors
      maxTime = None
      minTime = None
      resolution = 1
      for fl in joberrors:
         rows =  fl['rows']
         if len(rows) <=0: continue
         mx = self.sqlTime(rows[0][0])
         mn = self.sqlTime(rows[-1][0])
         if maxTime== None or  mx > maxTime: maxTime = mx 
         if minTime== None or mn < minTime:  minTime = mn
      titlePeriod = ''
      if hours!=None:
         titlePeriod += " for the last %s hour%s" % (hours, 's' if hours>1 else '')
      elif days != None:  
         titlePeriod += " for the last %s day%s" % (days, 's' if days>1 else '')
      else:
         if tstart!= None:
            titlePeriod += " for the from %s " %  tstart
         if tend!= None:
            titlePeriod += " for the ny  %s " %  tend
      if minTime!=None and maxTime!= None:
         minTime,maxTime= self.timeBins(minTime,maxTime,timedelta( hours=resolution))
         # print utils.lineInfo(), minTime,maxTime, joberrors
         histograms = {}
         if optsum or opttime:  histograms['all']  = {}
         if optsum:
            allerrors =  PandaNameHistogram('Total Errors '+ titlePeriod)
            histograms['all']['errors']= allerrors
         if opterr:
            itemerrors =  PandaNameHistogram('Error Distribution '+ titlePeriod)
            histograms['all']['items']= itemerrors
         if opttime: 
            alltime = PandaTimeHistogram('Errors '+ titlePeriod,minTime, maxTime,timedelta( hours=resolution) )  
            histograms['all']['time'] = alltime
         if optsum: histograms['errors'] = {}
         for i,e in enumerate(self._errorFields):
            rows =  joberrors[i]['rows']
            if len(rows) <=0: continue
            head =  joberrors[i]['header']
            if optsum:
               thisError = PandaTimeHistogram("Error: %s for all %s" % (e,item) ,minTime, maxTime,timedelta( hours=resolution) )
               histograms['errors'][e] = thisError
            hindx = utils.name2Index(head);
            iTime= hindx['TIME']
            iItem= hindx[item.upper() ]
            iTotalJobs= hindx['TOTAL_JOBS']
            iErrorcode= hindx['%sERRORCODE' % e.upper() ] if e.upper() != 'TRANSEXIT' else  hindx['%sCODE' % e.upper() ]
            def isPresent(key,value):
               incond = conditions != None and conditions.has_key(key)
               return utils.isFilled(value) and not incond
            for row in rows:
               time  = row[iTime]
               itm   = row[iItem]
               value = row[iTotalJobs]
               errorcode = row[iErrorcode]
               if optitem:
                  itkey = "%s:%s|%s" % (itm, e,errorcode)
                  if not histograms.has_key(itm): histograms[itm] = {}
                  ithists =  histograms[itm] 
                  if not ithists.has_key(itkey):
                       itlink = "<a href='http://pandamon.cern.ch/jobinfo?jobStatus=failed"
                       if e != 'transExit':
                          keycode = '%(e)sErrorCode' % {'e':e }
                          if conditions != None and not conditions.has_key(keycode):
                              itlink += '&%(keycode)s=%(code)s' %{'keycode':keycode, 'code':errorcode}
                       else:   
                          keycode = '%(e)sCode' % {'e':e }
                          if conditions != None and not conditions.has_key(keycode):
                              itlink += '&%(keycode)s=%(code)s' %{'keycode':keycode, 'code':errorcode}
                       if isPresent('jobtype',jobtype):
                           itlink += "&jobtype=%s" %  jobtype
                       if isPresent('hours',hours):
                           itlink += "&hours=%s" %  hours
                       if isPresent('tstart',tstart):
                           itlink += "&tstart=%s" %  v
                       if isPresent('tend',tend):
                           itlink += "&tend=%s" %  tend
                       if isPresent('days',days):
                           itlink += "&days=%s" %  days
                       itlink += condpars
                       itlink += "&%(itemkey)s=%(item)s'>%(item)s</a>" % {'itemkey':item, 'item' :  itm }
                       htitle = "%(item)s:<a href='http://pandamon.cern.ch/errorcodes?scope=%(scope)s&code=%(code)s'>%(scope)s|%(code)s</a>" % { 
                            'item'  : itlink
                          , 'scope' : e
                          , 'code'  : errorcode }
                       ithists[itkey] = PandaTimeHistogram(htitle ,minTime, maxTime,timedelta( hours=resolution) )
                  ithists[itkey].fill(self.sqlTime(time),value)
               # histograms[itkey]['all'].fill('%s|%s'% (e[0],errorcode),value)
               if optsum:
                  thisError.fill(self.sqlTime(time),value)
                  filbin = "%(e)s|%(code)s" % {'code'  : errorcode , 'e' : e[0] }
                  allerrors.fill(filbin,value)
               if opttime:
                  alltime.fill(self.sqlTime(time),value)
               if opterr:
                  itemerrors.fill(itm,value)
         if optsum: 
            allerrors.purge(edge)
         if opterr:
            itemerrors.purge(edge)
         if maxplot != None and maxplot>0:
            hkeys =  histograms.keys()
            for histGroup  in hkeys:
               integral = []
               grhists = histograms[histGroup]
               if not histGroup=='all':
                  for hist in grhists:
                     ntotl = grhists[hist].integral() 
                     if ntotl>= minerrs: 
                        integral.append([ntotl, hist, grhists[hist]]);
                  if len( integral ) >0:    
                     integral = sorted(integral, key=lambda entr: entr[0],reverse=True);
                     grhists = {}
                     for ih in integral[:maxplot]:
                        grhists[ih[1]]=ih[2]
                     histograms[histGroup]  = grhists
                  else:
                     del histograms[histGroup]                  
         main['hist'] = histograms
         main['opt'] = {'sum':optsum,'time':opttime,'item':optitem, 'error':opterr} 
      else:
          main['hist'] = None
      return main
 