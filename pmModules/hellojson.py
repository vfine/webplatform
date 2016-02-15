# $Id: hellojson.py 14387 2013-03-01 01:07:33Z fine $
# Author: Valeri Fine (fine@bnl.gov) Sept 22, 2011
from pmCore.pmModule import pmModule
from pmCore.pmModule import pmRoles

#______________________________________________________________________________________      
class hellojson(pmModule):
   """ The simplest Panda Web Modulde to provide the UI as follows:
       the URL: 'http:<hostname>/hellojson'        should return the JQuery table reading "Good Morning Word !!!"
       the URL: 'http:<hostname>/hellojson?host=All should return the JQuery table reading "Good Morning All !!!"
       the URL: 'http:<hostname>/hellojson?me=All&title='Ciao Panda Example'&hello=Goode Day should return the page reading "Good day All !!!"
   """
   #______________________________________________________________________________________      
   def __init__(self,name=None,parent=None,obj=None):
      pmModule.__init__(self,name,parent,obj)
      self.publishUI(self.doQuery,role=pmRoles.object())
      self.publishUI(self.doScript,role=pmRoles.script() )

   #______________________________________________________________________________________      
   def doQuery(self,host='World',title='PanDA Hello Json Word Example',guest='Your Panda', hello="Good Morning"):
       """ Respond with the json structure  
         Arguments:
            host -- the name of the greeting person, otherwise 'World'
            title -- the banner
            guest -- the name of the person to greet, otherwise 'Your Panda'
            hello -- the greeting, otherwise 'Good Morning'
       """
       self.publishTitle(title)

       headers = [ " host", "guest" , "greeting" ]
       data = []
       data.append([host, guest, hello ])
       self.publishMain(main={"headers" : headers, "rows" : data },role=pmRoles.object())
   #______________________________________________________________________________________      
   def doScript(self,host='World',title='PanDA Hello Json Word Example',guest='Your Panda', hello="Good Morning"):
      func = """
         function(tag,data) {
            $(tag).html('<table cellpadding="0" cellspacing="0" border="0" class="display" id="example"></table>' );
            var hdr = [];  
            for (var h in data['headers'] ) { 
                hdr.push( {"sTitle":h } );
             };
            rows = data['rows'];
            $('#example').dataTable( { "aaData" : rows, "aoColumns":hdr,"bJQueryUI": true });
         }
      """
      self.publish(func,role=pmRoles.script() )   
   
