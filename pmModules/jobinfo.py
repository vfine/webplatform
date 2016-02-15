""" List the selected Panda Jobs """
# job.py
# Display Panda job lists and job details
# $Id: jobinfo.py 18206 2014-01-31 23:19:15Z fine $
#
import re, time, calendar, os, copy
from datetime import datetime
from itertools import izip, count
from  pmTaskBuffer.pmTaskBuffer import pmtaskbuffer as pmt
from  monitor.ErrorCodes  import errorcodes
import pmConfig.pmConfig as config
import pmUtils.pmUtils as utils
from pmUtils.pmState import pmstate
from pmCore.pmModule import pmModule
from pmCore.pmModule import pmRoles
from  monitor.nameMappings import nmap
from pmUtils.pmJobUtil import pmJobUtil as setutils

class jobinfo(pmModule):
   #______________________________________________________________________________________      
   def __init__(self,name=None,parent=None,obj=None):
      pmModule.__init__(self,name,parent,obj)
      self._description,params = utils.normalizeDbSchema(pmt,'jobsarchived4')
      self._jobParametersName = 'jobParameters'
      self._allparams = ','.join(params.keys())
      self._colNames= 'jobStatus prodUserID prodUserName nInputFiles AtlasRelease transformation \
            homepackage prodDBlock destinationDBlock destinationSE computingSite creationTime startTime endTime \
            modificationTime jobName attemptNr prodSourceLabel jobDefinitionID jobsetID taskID pilotID \
            schedulerID pilotErrorCode workingGroup creationHost parentID\
            pilotErrorDiag ddmErrorCode ddmErrorDiag jobDispatcherErrorCode jobDispatcherErrorDiag taskBufferErrorCode \
            taskBufferErrorDiag brokerageErrorCode brokerageErrorDiag exeErrorCode exeErrorDiag supErrorCode supErrorDiag \
            transExitCode currentPriority cloud countryGroup processingType VO JediTaskID'.split()
            
      self._jobSum = [
                         ['States'         , 'jobStatus']
                        ,['Users'        , 'prodUserName']
                        ,['Releases'      ,'AtlasRelease']
                        ,['Processing Types' , 'processingType']
#                       ,['Analysis Tasks' , 'destinationDBlock']   # jobtype = 'analysis'
#                       ,['Output dataset',  'destinationDBlock']   # jobtype = 'analysis'
                        ,['Job Types'       , 'prodSourceLabel']
#                        ,['Job Series'      , 'prodSeriesLabel']
#                       , ['Task ID'       , 'taskID'] # if ['prodSourceLabel'] == 'managed' and 'taskID' in job,
#                       ,['Batch system ID','batchID' ]
                       ,['Transformations', 'transformation']
#                       ,['Input dataset' , 'prodDBlock']
                        ,['Working Groups', 'workingGroup']
                        ,['Creation Hosts' , 'creationHost']
#                       ,['Packages'      , 'homepackage']  #  need constrain
                       ,['Sites'          , 'computingSite']
#                       , ['Regions'      , 'Region']
                       , ['Clouds'        , 'cloud']
                        ,['Jedi ID','JediTaskID'] 
                        ,['Jedi ID','JediTaskID'] 
#                        ,[ 'CPU Type','cpuConsumptionUnit']
 #                       ,['Analysis Tasks', 'destinationDBlock']
#                       ,['Job Priorities' , 'currentPriority' ]# need constrain 
                  ]
      self._errorFields, self._errorCodes, self._errorStages = errorcodes.getErrorCodes()
      self._extraFields= ['tostart', 'duration','endt','transfert']
      self._region4sites,self._site4regions= setutils.region4Sites(pmt)
      self._siteId, self._siteRegions,self._siteNames,self._siteNicks = pmt.getSiteInfo('region')
      ## 'publishUI' must be the last init statement  !
      # aliase
      self._alias = {'username' :'prodUserName'}
      for a in self._alias: params[a] = None
      self.publishUI(self.doJson,params=params)
    
   #______________________________________________________________________________________      
   def getSite4Region(self,regions):
      regs = None  
      if utils.isValid(regions):
         rgs = utils.parseArray(regions);
         regs = []
         for r in rgs:
            regs += self._site4regions[r]
      return regs
      
      
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
   def doJson(self,job=None,taskid=None,tstart=None,tend=None,hours=71,days=None,jobparam=None,limit=1500,summary=None,minjob=1,jobtype=None,timeField='modificationTime',plot='no',dump=None,tasktype=None,status=None,region=None,lfn=None,showcpu=None):
      """Display the job information: 
     <p>Sample queries:
     <ul>
      <li><a href='http://pandamon.cern.ch/jobinfo?tstart=2013-04-07 00:00&amp;tend=2013-04-07 00:03&amp;hours='>http://pandamon.cern.ch/jobinfo/?tstart=2011-06-07 00:00&amp;tend=2011-06-07 00:01</a>
       <li><a href='http://pandamon.cern.ch/jobinfo?tstart=2013-04-07 00:00&amp;tend=2013-04-07 00:03&amp;hours=&amp;processingType=simul'>http://pandamon.cern.ch/jobinfo/?tstart=2011-06-07 00:00&amp;tend=2011-06-07 00:01&prodUserName=borut.kersevan@ijs.si</a>
       <li><a href='http://pandamon.cern.ch/jobinfo?job=1246240909'>http://pandamon.cern.ch/jobinfo?job=1246240909</a>
      </ul>
          <hr>
          Supported query parameters are as follows:
          <table>
          <tr><td>taskid</td><td> - jobset / task id</td></tr>
          <tr><td>job</td><td> - comma separated list of jobs' PandaID</td></tr>
          <tr><td>jobtype</td><td> - select the 'jobtype' jobs: analysys, production, install, test </td></tr>
          <tr><td>tstart=None</td><td>  - start time </td></tr>
          <tr><td>tend=None</td><td>    - end time</td></tr>
          <tr><td>hours=N </td><td> - last (N hours + N days) or N hours after 'tstart'  or N hours before 'tend' </td></tr> 
          <tr><td>days=N</td><td>   - last (N hours + N days)  (see the hours parameter documentation</td></tr>
          <tr><td>lfn=</td><td>   -  Select the PanDA jobs using the files from the comma-separated lfn list </td></tr>
          <tr><td>jobparam=</td><td>The comma separated list of the <a title='Click to see the full list of the jobinfo parameters available' href='http://pandamon.cern.ch/describe?table=^JOBSARCHIVED4&doc=*'>job parameters</a>.<br> The  default should satisfy the interactive users.<br>
          One needs to customize jobparam to build his/her <a href='https://twiki.cern.ch/twiki/bin/view/PanDA/PandaPlatform#Custom_Monitoring_Client_Code'>own client</a></td></tr>
          <tr><td>limit=</d><td>   - max number of the Db records to fetch from  each job Db table. Since there are 4 tables the real number of the rows can be 4 times as many as that limit</td></tr>
          <tr><td><a title='Click to see the full list of the jobinfo parameters available' href='http://pandamon.cern.ch/describe?table=^JOBSARCHIVED4&doc=*'>PARAM</a>=value</td><td>-  comma-separated list of the value <a href ='https://twiki.cern.ch/twiki/bin/view/PanDA/PandaPlatform#API_parameter_value_format'> patterns</a> to filter the job records.<br>
          For example: <ul><li><a href='http://pandamon.cern.ch/jobinfo?processingType=simul'>http://pandamon.cern.ch/jobinfo?processingType=simul</a>
          <li> <a href='http://pandamon.cern.ch/jobinfo?limit=2&hours=4&processingType=ganga*,test'>http://pandamon.cern.ch/jobinfo?limit=2&hours=4&processingType=ganga*,test</a></ul>
          <tr><td>summary</td><td>Create the summary for the first member of the jobparam list<br>
          For example: <a href='http://pandamon.cern.ch/jobinfo?processingType=simul&jobparam=jobStatus&summary=yes'>http://pandamon.cern.ch/jobinfo?processingType=simul&jobparam=jobStatus&summary=yes</a>
          </td></tr>
          <tr><td>dump</td><td> - 'yes' - produce the flat list of job info  records suitable for CLI applications</td></tr>
          <tr><td>region</td><td> - the comma separated list of the regions </td></tr>
          <tr><td>showcpu</td><td> - 'yes' to show the CPU type used </td></tr>
          </table>
      """
#       % { 'url' : self.server().branchUrl() }
      if job=='undefined': job=None
      if limit=='undefined': limit=None
      if summary=='undefined': summary=None
      if jobparam=='undefined': jobparam=None
      if tstart=='undefined': tstart=None
      if tend=='undefined': tend=None
      if tasktype=='prod' : jobtype='production'
      if jobtype=='null': jobtype=None
      if jobparam == None: 
         if job != None:
            jobparam = self._allparams
         else:  
            jobparam = ','.join(self._colNames)
      if timeField == None or timeField=='undefined' or timeField=='': timeField ='modificationTime'
      if self.isValid(jobparam):
         self.publish(self.doJobs(job,tstart=tstart,tend=tend,hours=hours,days=days,jobparam=jobparam,limit=limit,field=timeField,jobtype=jobtype,summary=summary,minjob=minjob,dump=dump,region=region,lfn=lfn,showcpu=showcpu))
         self.publish( "%s/%s" % (self.server().fileScriptURL(),"jobInfoRender.js"),role=pmRoles.script() ) 
         self.publish({'s-maxage':600,'max-age': 600 }, role=pmRoles.cache())
      else:
         title = 'Job data '
         if utils.isFilled(job):
            hours=None
            days=None
            title += " %s " % job
         if days != None:
            title += ' for %.2f day' % float(days)
            if days>1: title+="s"
         if hours != None: 
            if days == None: title += " for "
            title += ' %d hour' % int(hours)
            if hours>1: title+="s"
         self.publishTitle( title )
   #______________________________________________________________________________________      
   def doJobs(self,pandaid=None,params=None,jobparam=None, table=None, hours=None, tstart=None, tend=None, field='modificationTime', days=None,format=None,jobtype=None,testsite=None,limit=1500,summary=None,minjob=1,dump=None,region=None,lfn=None,showcpu=None):
    ## Perform the query
       main = {}
       errorcolcheck = False
       selection = '*'
       vals = self.extraValuesFilled(self._alias)
       
       title = 'PanDA Job(s)'
       if utils.isFilled(pandaid):
         hours=None
         days=None
         title += " %s " % pandaid
       if days != None:
         title += ' for %.2f Day' % float(days)
         if days>1: title+="s"
       if hours != None: 
         if days == None: title += " for "
         title += ' %d Hour' % int(hours)
         if hours>1: title+="s"

       if vals != None:
         for k in vals.keys():
           if vals[k]=='undefined': vals[k]=None
           elif  vals[k] != None and k.lower() == 'jobstatus' and  (vals[k].lower().find('prerun') >=0 or vals[k].lower().find('finishing') >=0 or vals[k].lower().find('unassigned') >=0 or vals[k].lower().find('retried')>=0 ) :
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
         cleanVal  = dict((k,v) for k,v in vals.iteritems() if v is not None )
         vals = cleanVal
       if vals == None: vals = {}
       nav = ''
       certificate = None
       certusr  = None
       try:
         cert = self.server().certificate()
         if cert != None:
            certusr = pmt.cleanUserID(cert)
            main['ceruser'] = certusr
       except:
         pass
       if vals.get('prodUserName') == 'auto' and certusr !=None:
             if cert != None: vals['prodUserName'] = certusr
       for v in vals:
         nav += "<b>%s</b>=%s " %(v,vals[v]) 
       # nav += "<span id=linkjobid  stule='display:inline'></span>"
       # nav +="<script>$(document).ready(function(){$('#linkjobid').html(utils().linkJobs(s.cloud,jobtype"
       # nav += jobtype if jobtype!=None else "undefined"
       # nav += ", s.jobStatus, " 
       # nav += "%d" % hours if hours!=None else "undefined" 
       # nav += ", s.computingSite,'Classic Page' ))});</script>";
       if not utils.isFilled(summary):
          nav +=  "<b>%s</b>=%s " %('limit',limit) 

       self.publishNav(nav)  
       if len(vals) == 0: vals = None    
       if vals == None and jobparam ==None:
            main['Description'] = self.description()
       else:
            if lfn != None and lfn != "undefined":
               lfnselect ='pandaid,lfn'
               lfnjobs = pmt.getJobLFN(select=lfnselect,table='new',lfn=lfn,pandaid=pandaid,type='*',limit=limit)
               if lfnjobs['rows'] > 0:
                  pandaid = [ljobs[0] for ljobs in lfnjobs['rows']]
            selection = {}
            if vals != None: selection.update(vals)
            if pandaid != None: selection.update({nmap.get('pandaid') :pandaid }) 
            if region != None: selection.update({'region':region}) 
            main['Selection'] = selection
            conditions=vals
            if conditions == None: conditions = {}
            cs = conditions.get('computingSite')
            if cs == None:
               site4region = self.getSite4Region(region)
               if site4region != None and len(site4region)>0:
                  conditions['computingSite'] = site4region
            else: 
               pass # ignore the region parameter            
            if  utils.isValid(summary):
               jobtype = 'production' if jobtype == None and  jobparam.lower().find('taskid')>=0 and  jobparam.lower().find('jeditaskid')<0 else jobtype
               jobs = pmt.getJobsAtt(pandaid, jobparam, conditions, None, hours, tstart, tend, field, days,format,jobtype,testsite,None,True)
               rows = jobs['rows']
               indx = []
               if len(rows) > 30:
                  for i,r in enumerate(rows):
                     try:              
                        if r[1]>minjob: 
                           indx.append(i)
                           continue
                     except:
                        pass
                  cleanrows = [rows[i] for i in indx]
                  jobs['rows'] = cleanrows
               istatus = utils.name2Index(jobs['header'],'jobstatus')     
               if istatus != None:
                  statOrder = utils.name2Index(utils.jobStates)
                  def byStatus(a,b):
                     return statOrder[a[istatus]]-statOrder[b[istatus]]
                  jobs['rows'] = sorted(jobs['rows'], cmp=byStatus)            
            else:
               if jobparam == self._allparams and conditions.get(self._jobParametersName) == None: 
                  conditions[self._jobParametersName] = 'any'
               jobs = pmt.getJobsAtt(pandaid, 'PandaID,'+jobparam, conditions, None, hours, tstart, tend, field, days,format,jobtype,testsite,limit)
               errorcolcheck = True
            if len(jobs) > 0:
               header = [nmap.get(h) for h in jobs['header']]
               info = jobs['rows']
               main['header'] = header#  + self._extraFields
               timecols = [] 
               errdict = None
               errorcol = not errorcolcheck
               for i,h in enumerate(header):
                   if 'time' in h.lower() and 'cpuconsumptiontime' != h.lower(): timecols.append(i)
                   if not errorcol and 'error' in  h.lower(): 
                      errorcol = True
##               # add an artificial retryID
##               header += ['retryID']
               headindx = utils.name2Index(header)
               creationtDict = {}
               histograms = {}
               prodSourceLabel = headindx.get('prodSourceLabel')
               jobStatus =  headindx.get('jobStatus')
               status4title = conditions.get('jobStatus')
               if not utils.isFilled(status4title): 
                  if len(info) == 1 and jobStatus != None: 
                     status4title = info[0][jobStatus]
               if utils.isFilled(status4title):
                  title = status4title[0].upper() + status4title[1:] + " " + title
               prodtype = 'production' in jobtype.lower() if jobtype != None else True
               taskidsum =  prodtype
               if not utils.isValid(summary) and dump !='yes':
                  jsets = setutils.factory(header,info,self._errorCodes,self._siteId,self._siteNicks)
                  main['jobset'] = jsets.jobsets()
               for r in info:
                  if not taskidsum and ((prodSourceLabel and r[prodSourceLabel] == 'managed') and prodtype ) : taskidsum = True
                  if errorcol and errorcolcheck: errdict = self.getErrors(r,headindx, errdict)
                  for t in  timecols:
                        r[t] = utils.epochTime(r[t])
##                  r += [None] # retryID
                  # row = self.jobsetTime(utils.zip(header(info[r])),creationtDict,histograms)
                  # info[r] = self.addFields(utils.zip(header(info[r])),creationtDict,histograms)
# Action            cleanUserID SSL_CLIENT_S_DN
               main['info'] = info
               if errorcolcheck:
                  main['errorCodes'] =  errdict 
               main['colNames']   =  sorted(header)
               main['jobsummary']= copy.copy(self._jobSum);
               if taskidsum:
                  main['jobsummary'] += [['Task ID','taskID']]
#               print utils.lineInfo(), "===============", self._description.get("JEDITASKID"), self._description.get("JediTaskID")
#               if self._description.get("JEDITASKID") or self._description.get("JediTaskID"):
#                  main['jobsummary'] += [['Jedi ID','JediTaskID']]
               elif jobtype!='jedi':
                   main['jobsummary'] += [['Jobsets', 'jobsetID']] #  need constrain
               elif jobtype=='analysis':
                  main['jobsummary'] +=[['Analysis Tasks', 'destinationDBlock']]
               if showcpu == 'yes':
                  main['jobsummary'] +=[[ 'CPU Type','cpuConsumptionUnit']]
       self.publishTitle( title )
       return main
   #______________________________________________________________________________________      
   def description(self):
       """ Description and intro page for job search """
       params= sorted(self.extraParams().keys())
       txt = """
   <pre><font size=-1>
   Available job parameters are:
   """ % { 'url' : 'http://pandamon.cern.ch' }
       for c in params:
           txt += "<br>    %s" % c
       txt += "</font></pre>"
       return txt