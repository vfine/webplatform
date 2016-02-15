# $Id: pd2ptest.py 9290 2011-10-07 03:12:24Z fine $
# Author: Valeri Fine (fine@bnl.gov) Sept 22, 2011
from pmCore.pmModule import pmModule
from pmCore.pmModule import pmRoles
import pmUtils.pmUtils as utils

#______________________________________________________________________________________      
class pd2ptest(pmModule):
   """ The simplest Panda Web Module to provide the UI as follows:
       the URL: 'http:<hostname>/pd2ptest'
       the URL: 'http:<hostname>/pd2ptest&scloud=CA'
   """
   #______________________________________________________________________________________      
   def __init__(self,name=None,parent=None,obj=None):
      pmModule.__init__(self,name,parent,obj)

      self.publishUI(self.doQuery,role=pmRoles.json())
      self.publishUI(self.doScript,role=pmRoles.script())
      self.publishUI(self.doQuery2,role=pmRoles.json(),alias="site")
      self.publishUI(self.doScript2,role=pmRoles.script(),alias="site")

   #______________________________________________________________________________________      
   def doQuery(self,cloud='ALL',style='table'):
       """ Show PD2P test application 
         <h2 class='ui-corner-all ui-widget ui-widget-header'>Arguments:</<h2>
         <ul>
           <li>cloud  -- the cloud name or "ALL"
           <li>style  -- the rendering stryle
           </ul>
       """
       self.publishTitle("Pd2p data for %s cloud " % cloud)
       data = {  "cloud" : cloud
                , "points" : [[336,23],[1323,34], [459,0] ,[789,0],[404,0],[10,0],[35,0],[2,0], [74,0], [4,0]]
                , 'style': style }
       self.publishMain(main=data,role=pmRoles.json())
   #______________________________________________________________________________________      
   def doQuery2(self,site='ALL',style='table'):
       """ Process the query request 
         Arguments:
            site  -- the site name
       """
       self.publishTitle("Pd2p data for %s site " % site)
       data = {   "cloud" : site
                , "points" : [[336,23],[1323,34], [459,0] ,[789,0],[404,0],[10,0],[35,0],[2,0], [74,0], [4,0]]
                , 'style': style }
       self.publishMain(main=data,role=pmRoles.json())

   #______________________________________________________________________________________      
   def doScript2(self,site='ALL',style='table'):
      """ Reuse the doScript with another  parameters: 'site' instead of "cloud' """
      self.doScript(site,style)
   #______________________________________________________________________________________      
   def doScript(self,cloud='ALL',style='table'):
      func = """
         function(tag,data) {
            $(tag).empty();
            var points = data.points;
            if ( data.style == 'table') {
               $(tag).html('<table cellpadding="0" cellspacing="0" border="0" id="example"></table>' );
               var h = ["data points"];  
               var hdr = [];
               hdr.push( {"sTitle":h } );
               hdr.push( {"sTitle":h } );
               rows = data['points'];
               $('#example').dataTable( { "aaData" : rows, "aoColumns":hdr ,"bJQueryUI": true });
            } else {
               $(tag).html(" <b>  Unknown presentation style:" +  data.style + "</b>" );
            }
         }
      """
      self.publish(func,role=pmRoles.script())   
   
