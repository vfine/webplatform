"""Monitor the Selected Tasks </td><td>$Rev: 18209 $"""
# $Id: listtasks.py 9690 2011-11-16 22:28:01Z fine $
from pmUtils.pmState import pmstate
from pmCore.pmModule import pmRoles
from  pmTaskBuffer.pmTaskBuffer import pmgrisliaskbuffer as gmt
import pmUtils.pmUtils as utils
import pmUtils.Stopwatch as Stopwatch
import monitor.taskDef_conf as taskDef_conf
from monitor.nameMappings import nmap

from  pmCore.pmModule import pmModule
import re

class listtasks1(pmModule):
   """ List the Selected Tasks </td><td>$Rev: 18209 $"""

   #______________________________________________________________________________________
   def __init__(self,name=None,parent=None,obj=None):
      pmModule.__init__(self,name,parent,obj)
      self._description =  gmt.describe('^t_task_request$')
      params = {}
      ci = utils.name2Index(self._description['header'],'column_name')
      for c in self._description['rows']:
         nm = nmap.get(c[ci])
         c[ci]  = nm
#         if 'pandaid' in  nm.lower() or 'time' in  nm.lower(): continue
         if 'pandaid' in  nm.lower(): continue
         if 'metadata' in  nm.lower(): continue
         if 'jobparameters' in  nm.lower(): continue
         params[nm] = None
      self._allparams = ','.join(params.keys())      
      
      self._tpattern = re.compile('([^\.]+)\.([^\.]+)\.([^\.]+)\.([^\.]+)\.(.*)')
      self._tagpattern = re.compile('(.*)_([^_]+)$')
      #                              SQL                    Web
      self._select = (   ('reqid',                      'Id'     )
                       , ('taskname',                   'Task_Name')
                       , ('TO_NUMBER(total_req_jobs)',  'Req_Jobs') 
                       , ('TO_NUMBER(total_done_jobs)','Done_Jobs')
                       , ('status',                     'State')
                       , ('TO_NUMBER(total_events)',    'Evnts')
                       , ('TO_NUMBER(priority)',        'Pri')
                       , ('inputdataset',               'Input')
                       )
      self._opt=     (   ('postproduction',             'post')
                       , ('grid',                       'grid')
                       , ('timestamp',                  'timestamp')
                       , ('PROJECT',                    'project' )
                       , ('dsn' ,                       'dsn')
                       , ('phys_ref',                   'phys_ref')
                       , ('prodstep',                   'step' )
                       , ('prodtag',                    'tag' )
                       , ('ctag',                       'Ctag' )
                       , ('total_avail_jobs' ,          'Avail' )
                       , ('phys_group',                 'Phys_Group' )
                       , ('comment_',                   'Note' )
                       , ('formats',                    'Formats')
                     )
      self._composite = { 'act' : 'running,pending, holding,submitting,waiting,submitted'
                         ,'bad' : 'failed,lost,aborted,obsolete,deleted'
                         ,'pas' : 'archived,finished,done'
                        }
      self._composite['good'] = ','.join( [self._composite['act'],self._composite['pas']])
      self.publishUI(self.doJson,params=params)

   #______________________________________________________________________________________      
   def parseTaskName(self, taskName):
      """ Parse taskname  """
      tn = self._tpattern.match(taskName)
      if tn:
         tags = {'all': tn.group(5) }
         ts = {    'project' : tn.group(1)
                  , 'dsn'    : tn.group(2)
                  , 'physics': tn.group(3)
                  , 'stage'  : tn.group(4)
                  , 'tags'   : tags
               }
         tagsds = self._tagpattern.match(tn.group(5))
         tags['tag'] = tagsds.group(2) if tagsds else tags['all']
         return   ts       
      else: 
         return None        
   #______________________________________________________________________________________      
   def doJson(self,hours=96,tidm=None,name=None,dset=None,project=None,columns=None,phys_ref=None,step=None,tag=None,dsn=None,ctag=None,failed=None,state=None,formats=None,action=None,jobstatus=None):
      """ 
        Requested Tasks
        <ui>
        <li> <b>hours</b> - list the tasks requested for the last hours
        <li> <b>tidm</b>  - simple integer to list the tasks with the TaskId >= tidm or an explicit list of the comma separated  values of TaskIds
        <li> <b>name</b>  - The comma-separated list of the <a href='https://twiki.cern.ch/twiki/bin/view/PanDA/PandaPlatform#API_parameter_value_format'>taskname patterns</a>
        <li> <b>dset</b>  - The inputdataset  <a href='https://twiki.cern.ch/twiki/bin/view/PanDA/PandaPlatform#API_parameter_value_format'>pattern</a> )
        <li> <b>formats</b>  - The output 'formats' filter pattern (may contain the wildcard symbol '*' )
        <br> &nbsp;&nbsp;&nbsp;&nbsp; <font size=-2>Application converts all values of the "formats" filter into UPPER  case values</font>
        <li> <b>state</b> - the comma separated list of the task "state"s to filter. 
         <br> One can use the regular task's state as well as 4 "composite" states:
         <ul>
         <li> BadTask     - to fetch the the tasks in "failed,lost,aborted,obsolete,deleted"
         <li> ActiveTask  - to fetch the the tasks in "running,pending, holding,submitting,waiting,submitted"
         <li> PassiveTask - to fetch the the tasks in "archived,finished,done"
         <li> GoodTask    - to fetch the 'ActiveTask' + 'PassiveTask' tasks         
        </ul>
        <li> <b>project</b> - The project name, for example 'mc12_8TeV'(may contain the wildcard symbol '*' )
        <li> <b>columns</b>  - comma separated list of the optional columns: " post, timestamp, project, dsn, phys_ref,step,tag, grid,ctag,avail,phys_group,note,formats"
        <br>  <small><it>&nbsp;&nbsp;&nbsp; CLI (aka 'curl') and 'ajax' applications can use the 'columns=*' to fetch all available columns for the selected task requests <it></small>
        <li> <b>failed</b>-  "yes" shows the failed also. 
        <br>  =  [comma separated list] list of failed states: aborted,failed,lost,obsolete
        <br> - &failed=yes - adds all kind of the failed tasks to the table
        <br> - &failed=aborted,failed to show the list of the  aborted  and failed tasks only
        <li> <b>jobstatus</b>=None. Comma separated list of the jobs' states ("failed" - for example) to be shown for each task via the dedicated column
        <li><a title='Click to see the full list of the listtask1 parameters available' href='http://pandamon.cern.ch/describe?table=^t_task_request$&db=gmt'><b>PARAM</b></a>=value</td><td>-  comma-separated list of the <a href ='https://twiki.cern.ch/twiki/bin/view/PanDA/PandaPlatform#API_parameter_value_format'> patterns</a> to filter the job records.<br>
        <hr>
        The parameters below the line are experimental. It is  for expert only 
        <li>phys_ref = Physics_stream , for example 'McAtNloJimmy_CT10_ttbar_LeptonFilter' (may contain the wildcard symbol '*' )
        <li>step   = Production step, for example 'evgen' or 'merge'  (may contain the wildcard symbol '*' )
        <li>tag
        <li>ctag
        <li>dsn     = 5 digits Task id, for example 129934
        <li>action  = add the action button against of each selected row (for example, 'action=clonetask')
        </ul>
      """
      
      vals = self.extraValues()
      for k in vals:
           if vals[k]=='undefined': vals[k]=None
      cleanVal  = dict((k,v) for k,v in vals.iteritems() if v is not None )
      vals = cleanVal
      
      ss = []
      all = False
      verbose = False
      clmns = []
      tid = None
      try:
         clmns = columns.lower().split(',')
         if '*' in  clmns or 'all' in clmns: all = True
         if columns !=None and '*' == columns.strip():  verbose = True
      except:
         pass
      if formats != None:
         if not 'formats' in clmns:  
            clmns.append('formats')   
         formats = formats.upper()
      wrong = True
      select = '*'
      if not verbose:
         if len(clmns) >0: 
            for c in clmns: 
               wrong = True
               for s in  self._opt: 
                  if s[1].lower() ==c: 
                     wrong = False
                     break
               if wrong: raise ValueError(" Unsupported optional column name: '%s' from %s" % (c,clmns))
         for s in self._select:
           ss.append(" %s as %s" % s)
         for s in self._opt:
            if all==True or s[1].lower() in clmns: ss.append(" %s as %s" % s)
         select = ", ".join(ss)   
      # select = "reqid as Id,taskname as Task_Name,inputdataset as Input,  TO_NUMBER(total_req_jobs) as Req_Jobs,  TO_NUMBER(total_done_jobs) as Done_Jobs, TO_NUMBER(total_events) as Evnts, TO_NUMBER(priority) as Pri,grid,status as State,postproduction as Post,timestamp,PROJECT,dsn,phys_ref,prodstep as step, prodtag as tag"
      timer = Stopwatch.Stopwatch()
      try:
         dsn = "%05d" % int(dsn)
      except:
         dsn = '%s' % dsn
      vstate = []
      if state != None:   
         state = state.split(',')
         for i,s in enumerate(state):
            if   'act' in s.lower(): state[i] = self._composite['act']
            elif 'bad' in s.lower(): state[i] = self._composite['bad']
            elif 'good'in s.lower(): state[i] = self._composite['good']
            elif 'pas' in s.lower(): state[i] = self._composite['pas']
         vstate = ','.join(state)
         # remove the duplicates if any
         state = ','.join(set(vstate.split(',')))
      if tidm != None:
         tidarray = utils.parseArray(tidm)
         if len(tidarray) > 1: 
             tidm=None
             tid = tidarray
      q = gmt.listTaskRequests(tidm=tidm,hours=hours,taskname=name,dset=dset,select=select,project=project,physics=phys_ref,stage=step,tag=tag,dsn=dsn,ctag=ctag,tid=tid,failed=failed,state=state,formats=formats,conditions=vals)
      header = q['header']
      rows   = q['rows']
      iTask = utils.name2Index(header,'Task_Name')
      pr = {}
      if not all:
         for row in rows:
            tname = self.parseTaskName(row[iTask]);
            if tname == None: continue
            if not pr.has_key(tname['project']): pr[tname['project']]= {}
            physics = pr[tname['project']]
            
            if not physics.has_key(tname['physics']): physics[tname['physics']] = {}
            tag = physics[tname['physics']]
            
            if not tag.has_key(tname['tags']['tag']): tag[tname['tags']['tag']] = {}
            stage =  tag[tname['tags']['tag']]
            if not stage.has_key(tname['stage']): stage[tname['stage']] = []
            task = stage[tname['stage']]
            ts = row[0:1] + [tname['tags']['all']]+ row[2:] # skip taskname
            task.append(ts)
      main = {}
      main["method"] = 'Tasks Requests (only active requests are listed. Aborted requests are not included).'
      main['time'] = {'fetch' : "%s" % timer}
      main["tasks"] = q
      if action != None:
         main['action'] = action
      main["params"] = {'hours': hours , 'jobstatus': jobstatus}
      #main['project'] = pr # to use the 'TreeJs' in future 
      self.publishTitle('Requested Tasks')
      self.publish(main)
      self.publish( "%s/%s" % (self.server().fileScriptURL(),"taskdef/%s.js" % 'listTasks' ),role="script")
      self.publish( {'s-maxage':600,'max-age': 600}, role=pmRoles.cache())
      self.publishNav("Total : %s tasks for the last %s hours " % ( len(main['tasks']['rows']),hours))
