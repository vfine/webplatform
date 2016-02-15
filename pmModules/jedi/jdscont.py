"""  Display the Jedi Dataset Contents </td><td>$Rev: 16745 $"""
# $Id: helloora.py 13701 2012-12-03 20:46:09Z fine $

from pmCore.pmModule import pmRoles
from  pmTaskBuffer.pmTaskBuffer import pmtaskbuffer as pmt
import pmUtils.pmUtils as utils
from  pmCore.pmModule import pmModule
 
class jdscont(pmModule):

    #______________________________________________________________________________________
   def __init__(self,name=None,parent=None,obj=None):
      pmModule.__init__(self,name,parent,obj)
      self._description,params = utils.normalizeDbSchema(pmt,'JEDI_Dataset_Contents')
      self.publishUI(self.doJson,params=params)
   
   #______________________________________________________________________________________      
   def doJson(self, tstart=None,tend=None,hours=None,days=None,dsparam=None,limit=None):
      """ 
          Jedi Dataset contents<br/>
          <table>
          <tr><td>tstart=None</td><td>  - start time </td></tr>
          <tr><td>tend=None</td><td>    - end time</td></tr>
          <tr><td>hours=N </td><td> - last (N hours + N days) or N hours after 'tstart'  or N hours before 'tend' </td></tr> 
          <tr><td>days=N</td><td>   - last (N hours + N days)  (see the hours parameter documentation</td></tr>
          <tr><td>dsparam=</td><td>The comma separated list of the <a title='Click to see the full list of the jdscont parameters available' href='http://pandamon.cern.ch/describe?table=^JEDI_Dataset_Contents&doc=*'>task parameters</a>.<br> The  default should satisfied the interactive users.<br>
          One needs to customize dsparam to build his/her <a href='https://twiki.cern.ch/twiki/bin/view/PanDA/PandaPlatform#Custom_Monitoring_Client_Code'>own client</a></td></tr>
          <tr><td><a title='Click to see the full list of the taskinfo parameters available' href='http://pandamon.cern.ch/describe?table=^JEDI_Dataset_Contents&doc=*'>PARAM</a>=value</td><td>-  comma-separated list of the value <a href ='https://twiki.cern.ch/twiki/bin/view/PanDA/PandaPlatform#API_parameter_value_format'> patterns</a> to filter the job records.<br>
          </table>   
      """
      title=''
      vals = self.extraValues()
      cleanVal  = dict((k,v) for k,v in vals.iteritems() if v is not None )
      conditions = cleanVal
      title='JEDI Datasets Contents'
      if dsparam == None: dsparam = ' JEDITASKID, DATASETID, FILEID, CREATIONDATE, LFN, GUID, TYPE, STATUS, FSIZE, CHECKSUM, SCOPE  '
      tasks = pmt.getJediDSAtt(dsid=None, taskparams=dsparam, conditions=conditions, hours=hours, tstart=tstart, tend=tend, days=days,table='ATLAS_PANDA.JEDI_Dataset_Contents',field='creationdate',limit=limit)
      main = {'header':[], 'data':None}
      header = tasks['header'] 
      rows = tasks['rows'] 
      if len(rows) >0:
         main['header'] = header
         main['data']=rows
      self.publish(main)
      self.publishTitle('%s table' % title )
      self.publish( "%s/%s" % ( self.server().fileScriptURL(),"jedi/%s.js" % "jtab" ),role=pmRoles.script() )
