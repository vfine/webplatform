""" List the selected Panda JEDI Tasks (see: https://twiki.cern.ch/twiki/bin/viewauth/AtlasComputing/PandaJEDI ) </td><td>$Rev: 17889 $"""
# Display Panda JEDI task list and task details
# $Id$
# https://indico.cern.ch/conferenceDisplay.py?confId=284579
#
import re, time, calendar, os, copy
from datetime import datetime
from itertools import izip, count
from  pmTaskBuffer.pmTaskBuffer import pmtaskbuffer as jmt
# from  pmTaskBuffer.pmTaskBuffer import pmjeditaskBuffer as jmt
from  monitor.ErrorCodes  import errorcodes
import pmUtils.pmUtils as utils
from pmUtils.pmState import pmstate
from pmCore.pmModule import pmModule
from pmCore.pmModule import pmRoles
from monitor.nameMappings import nmap
from pmUtils.pmJobUtil import pmJobUtil as setutils

class taskinfo(pmModule):
   #______________________________________________________________________________________      
   def __init__(self,name=None,parent=None,obj=None):
      pmModule.__init__(self,name,parent,obj)
      self._description,params = utils.normalizeDbSchema(jmt,'JEDI_Tasks')
      self._allparams = ','.join(params.keys())
      self._colNames= 'status username  transUses transPath  \
            startTime endTime \
            modificationTime taskname taskType prodSourceLabel \
            workingGroup site \
            errorDialog currentPriority cloud processingType wallTime VO'.split()
            
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
      self._extraFields= ['tostart', 'duration','endt','transfert']
      ## 'publishUI' must be the last init statement  !
      self._jobinfo = self.factory("jobinfo",None,self.parentModule() )
      self._jobinfoactive = False
      if params == None: params = {}
      params.update({'nFiles':None,'nFilesUsed':None,'nFilesFailed':None})
      self.publishUI(self.doJson,params=params)
    
   #______________________________________________________________________________________      
   def doJson(self,task=None,tstart=None,tend=None,hours=None,days=3,taskparam=None,limit=1500,summary=None,minjob=0,tasktype=None,timeField='modificationTime',dump='yes'):
      """ Display the task information: 
     <p>Sample queries:
     <ul>
      <li><a href='http://pandamon.cern.ch/jedi/taskinfo?tstart=2013-04-07 00:00&amp;tend=2013-04-07 00:03&amp;hours='>http://pandamon.cern.ch/jedi/taskinfo?tstart=2011-06-07 00:00&amp;tend=2011-06-07 00:01</a>
       <li><a href='http://pandamon.cern.ch/jedi/taskinfo?tstart=2013-04-07 00:00&amp;tend=2013-04-07 00:03&amp;hours=&amp;processingType=simul'>http://pandamon.cern.ch/jedi/taskinfo?tstart=2011-06-07 00:00&amp;tend=2011-06-07 00:01&username=borut.kersevan@ijs.si</a>
       <li><a href='http://pandamon.cern.ch/jedi/taskinfo?task=763'>http://pandamon.cern.ch/jedi/taskinfo?task=763</a>
      </ul>
          <hr>
          Supported query parameters are as follows:
          <table>
          <tr><td>task</td><td> - comma separated list of the task JediTaskID's</td></tr>
          <tr><td>tasktype</td><td> - select the 'tasktype' jobs: analysys, prod, install, test </td></tr>
          <tr><td>tstart=None</td><td>  - start time </td></tr>
          <tr><td>tend=None</td><td>    - end time</td></tr>
          <tr><td>hours=N </td><td> - last (N hours + N days) or N hours after 'tstart'  or N hours before 'tend' </td></tr> 
          <tr><td>days=N</td><td>   - last (N hours + N days)  (see the hours parameter documentation</td></tr>
          <tr><td>taskparam=</td><td>The comma separated list of the <a title='Click to see the full list of the taskinfo parameters available' href='http://pandamon.cern.ch/describe?table=^JEDI_TASKS&doc=*'>task parameters</a>.<br> The  default should satisfied the interactive users.<br>
          One needs to customize taskparam to build his/her <a href='https://twiki.cern.ch/twiki/bin/view/PanDA/PandaPlatform#Custom_Monitoring_Client_Code'>own client</a></td></tr>
          <tr><td>limit=</d><td>   - max number of the Db records to fetch from  each job Db table. Since there 4 tables the real number of the rows can be 4 times as many as that limit</td></tr>
          <tr><td><a title='Click to see the full list of the taskinfo parameters available' href='http://pandamon.cern.ch/describe?table=^JEDI_TASKS&doc=*'>PARAM</a>=value</td><td>-  comma-separated list of the value <a href ='https://twiki.cern.ch/twiki/bin/view/PanDA/PandaPlatform#API_parameter_value_format'> patterns</a> to filter the job records.<br>
          For example: <ul><li><a href='http://pandamon.cern.ch/jedi/taskinfo?processingType=simul'>http://pandamon.cern.ch/jedi/taskinfo?processingType=simul</a>
          <li> <a href='http://pandamon.cern.ch/jedi/taskinfo?limit=2&hours=4&processingType=ganga*,test'>http://pandamon.cern.ch/jedi/taskinfo?limit=2&hours=4&processingType=ganga*,test</a></ul>
          <tr><td>summary</td><td>Create the summary for the first member of the taskparam list<br>
          For example: <a href='http://pandamon.cern.ch/jedi/taskinfo?processingType=simul&taskparam=status&summary=yes'>http://pandamon.cern.ch/jedi/taskinfo?processingType=simul&taskparam=status&summary=yes</a>
          </td></tr>
          <tr><td>dump</td><td> - 'yes' - produce the flat list of the task info  records suitable for CLI applications</td></tr>
          </table>
      """
      if taskparam == None or taskparam=='undefined':
         tsks = utils.parseArray(task)
         if task != None and len(tsks) == 1: 
            taskparam = None
         else:
            taskparam = 'JediTaskID,status,username,nFiles,nFilesUsed,nFilesFailed,transUses,transPath,modificationTime,taskname'
      if tstart=='undefined': tstart = None
      if tend=='undefined': tend = None
      self._jobinfoactive = False
      if utils.isFilled(summary) and taskparam=='JediTaskID':
         self._jobinfoactive = True
         timemap = ['jobparam=JediTaskID','summary=true','limit=','jobtype=all']
         if days != None:   timemap += ['days=%s' % days] 
         if hours != None:  timemap += ['hours=%s' % hours] 
         if tstart != None: timemap += ['tstart=%s' % tstart] 
         if tend != None:   timemap += ['tend=%s' % tend] 
         timemap = '&'.join(timemap)
         self._jobinfo.callUI(timemap);
         # self.publish(self._jobinfo, pmRoles.publisher() ) 
         return
#       % { 'url' : self.server().branchUrl() }
      if task=='undefined': task=None
      if limit=='undefined': limit=None
      if summary=='undefined': summary=None
      if taskparam=='undefined': taskparam=None
      if taskparam == None: 
         if task != None:
            taskparam = self._allparams
         else:  
            taskparam = ','.join(self._colNames)
      if timeField == None or timeField=='undefined' or timeField=='': timeField ='modificationTime'
      if self.isValid(taskparam):
         self.publish(self.doTasks(task,tstart=tstart,tend=tend,hours=hours,days=days,taskparam=taskparam,limit=limit,field=timeField,tasktype=tasktype,summary=summary,minjob=minjob,dump=dump))
         self.publish( "%s/%s" % (self.server().fileScriptURL(),"jobInfoRender.js"),role=pmRoles.script() ) 
         self.publish({'s-maxage':600,'max-age': 600 }, role=pmRoles.cache())
      else:
         title = "<a href='https://twiki.cern.ch/twiki/bin/viewauth/AtlasComputing/PandaJEDI'>JEDI</a> task data "
         if utils.isFilled(task):
            hours=None
            days=None
            title += " %s " % task
         if days != None:
            title += ' for %d day' % days
            if days>1: title+="s"
         if hours != None: 
            if days == None: title += " for "
            title += ' %d hour' % hours
            if hours>1: title+="s"
         self.publishTitle( title )
      

   #______________________________________________________________________________________      
   def doTasks(self,task=None,params=None,taskparam=None, table=None, hours=None, tstart=None, tend=None, field='modificationTime', days=None,format=None,tasktype=None,testsite=None,limit=1500,summary=None,minjob=0,dump=None):
    ## Perform the query
       jeditaskid=task
       main = {'module' : 'jedi/taskinfo'}
       errorcolcheck = False
       selection = '*'
       
       title = "<a href='https://twiki.cern.ch/twiki/bin/viewauth/AtlasComputing/PandaJEDI'>JEDI</a> task data "
       if utils.isFilled(task):
         hours=None
         days=None
         title += " %s " % task
       if days != None:
         title += ' for %d day' % days
         if days>1: title+="s"
       if hours != None: 
         if days == None: title += " for "
         title += ' %d hour' % hours
         if hours>1: title+="s"
       vals = self.extraValues()
       for k in vals:
           if vals[k]=='undefined': vals[k]=None
           elif  vals[k] != None and k.lower() == 'status' and  (vals[k].lower().find('prerun') >=0 or vals[k].lower().find('finishing') >=0) :
               stvals= utils.parseArray(vals[k])
               statvals = []
               for v in stvals:
                  if v.lower() == 'prerun': 
                     statvals += ['defined','assigned','waiting','activated','pending','sent','starting']
                  elif v.lower() == 'finishing': 
                     statvals += ['holding','transferring','merging']
                  else:   
                     statvals  += [v]
                  vals[k] = ','.join(statvals)  
       cleanVal  = dict((k,v) for k,v in vals.iteritems() if v is not None )
       vals = cleanVal
       nav = ''
       try:
         if vals.get('username') == 'auto':
             if self.server().certificate() != None: val['username'] =jmt.cleanUserID(self.server().certificate())
       except:
         pass
       for v in vals:
         nav += "<b>%s</b>=%s " %(v,vals[v]) 
       if not utils.isFilled(summary):
          nav +=  "<b>%s</b>=%s " %('limit',limit) 
       self.publishNav(nav)  
       if len(vals) == 0: vals = None    
       if vals == None and taskparam ==None:
            main['Description'] = self.description()
       else:
            selection = {}
            if vals != None: selection.update(vals)
            if task != None: selection.update({nmap.get('jeditaskid') :task }) 
            main['Selection'] = selection
            conditions=vals
            try:
               if vals.get('username') == 'auto':
                   if self.server().certificate() != None: conditions['username'] =jmt.cleanUserID(self.server().certificate())
            except:
               pass
            if  utils.isValid(summary):
               tasks = jmt.getJediTaskAtt(jeditaskid, taskparam, conditions, None, hours=hours, tstart=tstart, tend=tend, days=days,tasktype=tasktype,limit=None,groupby=True)
               rows = tasks['rows']
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
                  tasks['rows'] = cleanrows
               istatus = utils.name2Index(tasks['header'],'status')
               if istatus != None:
                  statOrder = utils.name2Index(utils.jediTaskStates)
                  def byStatus(a,b):
                     try:
                        return statOrder[a[istatus]]-statOrder[b[istatus]]
                     except:
                        return -1
                  tasks['rows'] = sorted(tasks['rows'], cmp=byStatus)            
            else:
               tarr = utils.parseArray(taskparam);
               if tarr == None: tarr = []
               if not 'JediTaskID' in tarr: tarr = ['JediTaskID'] + tarr
               tasks = jmt.getJediTaskAtt(jeditaskid, ','.join(tarr), conditions, None, hours=hours, tstart=tstart, tend=tend, days=days,tasktype=tasktype,limit=limit,groupby=None)
               # errorcolcheck = True
            if len(tasks) > 0:
               header = [nmap.get(h) for h in tasks['header']]
               info = tasks['rows']   
               status = utils.name2Index(tasks['header'],'status')   
               if  status !=None and len(info) == 1: 
                  title = info[0][status][0].upper() + info[0][status][1:] + " " + title               
               main['header'] = header#  + self._extraFields
               timecols = [] 
               errdict = None
               headindx = utils.name2Index(header)
               errorcol = not errorcolcheck
               for i,h in enumerate(header):
                   if 'time' in h.lower() and 'cpuconsumptiontime' != h.lower(): timecols.append(i)
                   if not errorcol and 'error' in  h.lower(): 
                      errorcol = True
               creationtDict = {}
               histograms = {}
               prodSourceLabel = headindx.get('prodSourceLabel')
               prodtype = 'production' in tasktype.lower() if tasktype != None else True
               taskidsum =  prodtype
               if not utils.isValid(summary) and dump==None:
                  jsets = setutils.factory(header,info,self._errorCodes)
                  main['jobset'] = jsets.jobsets()
               for r in info:
                  if not taskidsum and ((prodSourceLabel and r[prodSourceLabel] == 'managed') and prodtype ) : taskidsum = True
                  if errorcol and errorcolcheck: errdict = self.getErrors(r,headindx, errdict)
                  for t in  timecols:
                        r[t] = utils.epochTime(r[t])
                  # row = self.jobsetTime(utils.zip(header(info[r])),creationtDict,histograms)
                  # info[r] = self.addFields(utils.zip(header(info[r])),creationtDict,histograms)
# Action            cleanUserID SSL_CLIENT_S_DN
               main['info'] = info
               if errorcolcheck:
                  main['errorCodes'] =  errdict 
               main['colNames']   =  sorted(header)
               main['jobsummary']= copy.copy(self._jobSum);
               if taskidsum: 
                  pass
                  # main['jobsummary'] += [['Task ID','JEDITASKID']]
               elif tasktype=='analysis':
                  pass
                  # main['jobsummary'] +=[['Analysis Tasks', 'destinationDBlock']]
       self.publishTitle( title )
       return main


   #______________________________________________________________________________________      
   def publishFooter(self, footer='',footerid="foot", role=pmRoles.html()):
      if self._jobinfoactive==True:
         self._jobinfo.publishFooter(footer,footerid, role)
      else:
         pmModule.publishFooter(self,footer,footerid, role)
   #______________________________________________________________________________________      
   def published(self):
      if self._jobinfoactive==True:
         return self._jobinfo.published()
      else:
         return pmModule.published(self) 
   #______________________________________________________________________________________      
   def cached(self):
      if self._jobinfoactive==True:
         return self._jobinfo.cached()
      else:
         return pmModule.cached(self)
   #______________________________________________________________________________________      
   def empty(self, dir=".pub",location=None,role=None):
      if self._jobinfoactive==True:
         return self._jobinfo.empty(dir,location,role)
      else:
         return pmModule.empty(self,dir,location,role)
   

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