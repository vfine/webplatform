"""Get log file extracts</td><td>$Rev: 17117 $"""
# Author: Valeri Fine 10/19/2013, (fine@bnl.gov)
from  pmTaskBuffer.pmTaskBuffer import pmtaskbuffer as pmt
import pmUtils.pmUtils as utils
from pmCore.pmModule import pmModule
from pmCore.pmModule import pmRoles

class joblogs(pmModule):
   #______________________________________________________________________________________      
   def __init__(self,name=None,parent=None,obj=None):
      pmModule.__init__(self,name,parent,obj)
      self.publishUI(self.doJson)
   #______________________________________________________________________________________      
   def doJson(self,pandaid):
      """Get log file extracts:
     <p>Get log file extracts:
      <p>  Supported query parameters are as follows:
          <table>
          <tr><td>pandaid</td><td>The list of the comma-separated PanDA job Ids'</td></tr>
          </table>
      """
      logs = pmt.getJobLogInfo(pandaid)
      main =  {}
      if len(logs['rows']) >0:   main["data"] = logs;
      self.publish(main);
      self.publish( {'s-maxage':4000,'max-age':4000}, role=pmRoles.cache())
      self.publish( "%s/%s" % ( self.server().fileScriptURL(),"monitor/%s.js" % "joblogs" ),role=pmRoles.script())

 