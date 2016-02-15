"""  Display Jedi DataSet status </td><td>$Rev: 17834 $"""
# $Id: helloora.py 13701 2012-12-03 20:46:09Z fine $

from pmCore.pmModule import pmRoles
from  pmTaskBuffer.pmTaskBuffer import pmdeftbuffer as pmt
import pmUtils.pmUtils as utils
from  pmCore.pmModule import pmModule
from  monitor.nameMappings import nmap
 
class dftask(pmModule):

    #______________________________________________________________________________________
   def __init__(self,name=None,parent=None,obj=None):
      pmModule.__init__(self,name,parent,obj)
      self._description,params = utils.normalizeDbSchema(pmt,'DEFT_TASK')
      self._dfTables = { 'ATLAS_PANDA' :['DEFT_TASK','DEFT_DATASET','DEFT_JOB_TEMPLATE','DEFT_REQUEST','DEFT_META', 'DEFT_STEPEX']
                       , 'ATLAS_DEFT'  :['DEFT_META','DEFT_DATASET','T_PRODMANAGER_REQUEST_STATUS','T_TASK','T_PRODUCTION_TASK','TRIGGERS_DEBUG'
                                        ,'T_PRODMANAGER_REQUEST','T_PRODUCTION_DATASET','T_INPUT_DATASET','T_STEP_TEMPLATE']
                       }
      # self._default = 'REQID as Request, START_TIME,SUBMIT_TIME,TOTAL_DONE_JOBS, taskID as jobsetID,status, STEP_ID'.split(',') 
      self._default = 'TASK_ID as jobsetID, TASK_STATE as status,TASK_MODIFICATIONTIME as modificationTime ,TASK_TAG, TASK_PARAM'.split(',') 
      self.publishUI(self.doJson,params=params)
   
   #______________________________________________________________________________________      
   def doJson(self, tstart=None,tend=None,hours=None,days=None,dfparam=None,limit=None,table=None):
      """ 
          DEFT  TASK table<br/>
          <table>
          <tr><td>limit=None</td><td>  - the max number of the DB record to fetch </td></tr>
          <tr><td>tstart=None</td><td>  - start time </td></tr>
          <tr><td>tend=None</td><td>    - end time</td></tr>
          <tr><td>hours=N </td><td> - last (N hours + N days) or N hours after 'tstart'  or N hours before 'tend' </td></tr> 
          <tr><td>days=N</td><td>   - last (N hours + N days)  (see the hours parameter documentation</td></tr>
          <tr><td>dfparam=</td><td>The comma separated list of the <a title='Click to see the full list of the jedi dataset parameters available' href='http://pandamon.cern.ch/describe?table=^DEFT_TASK$&doc=*&db=pdf'>DEFT Task parameters</a>.<br> The  default should satisfy the interactive users.<br>
          One needs to customize dfparam to build his/her <a href='https://twiki.cern.ch/twiki/bin/view/PanDA/PandaPlatform#Custom_Monitoring_Client_Code'>own client</a></td></tr>
          <tr><td><a title='Click to see the full list of the dftask parameters available' href='http://pandamon.cern.ch/describe?table=^DEFT_TASK&doc=*&db=pdf'>PARAM</a>=value</td><td>-  comma-separated list of the value <a href ='https://twiki.cern.ch/twiki/bin/view/PanDA/PandaPlatform#API_parameter_value_format'> patterns</a> to filter the job records.<br>
          </table>   
      """
      title=''
      if table == None: table = 'DEFT_TASK'
      for own in self._dfTables:
         if table.upper() in self._dfTables[own]: 
             table = "%s.%s" %(own,table)
             break
      conditions = self.extraValuesFilled()
      title='DEFT  %s' % table
      if dfparam == None: dfparam = ','.join(self._default)
      tasks = pmt.getDefTaskAtt(dsid=None, taskparams=dfparam, conditions=conditions, hours=hours, tstart=tstart, tend=tend, days=days,limit=limit,table=table)
      main = {'header':[],'data':[]}
      header = tasks['header'] 
      rows = tasks['rows'] 
      main['header'] = []
      if len(rows) >0:
         main['header'] = [nmap.get(h) for h in header]
         main['data'] = rows 
      self.publish(main)
      self.publishTitle('%s table' % title )
      self.publish( "%s/%s" % ( self.server().fileScriptURL(),"jedi/%s.js" % "jtab" ),role=pmRoles.script() )
