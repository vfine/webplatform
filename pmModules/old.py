# $Id:$
# Author: Valeri Fine (fine@bnl.gov) Sept 22, 2011
from pmCore.pmModule import pmModule 
from pmCore.pmModule import pmRoles

#______________________________________________________________________________________      
class old(pmModule):
   """ 
   redirect the URL to the old PANDA server
   """
   #______________________________________________________________________________________      
   def __init__(self,name=None,parent=None,obj=None):
      pmModule.__init__(self,name,parent,obj)
      self.publishUI(self.doQuery,role=pmRoles.html())

   #______________________________________________________________________________________      
   def doQuery(self):
      """ Redirect URL to the old PANDA server 
          <br>Append <b><code>"&amp;_old"</code></b> to your URL query to use the <a href='http://panda.cern.ch'>old classic Panda Monitor</a> "
      """
      if self.server().query() != '' and  not '_location=menu&_class=menubar' in  self.server().query():
         redirect = "<script> window.location='http://panda.cern.ch?%s';</script>" % self.server().query().replace('&_get=json','').replace('_get=json','')
      else:
         redirect = """
            <div class=ui-widget ui-widget-content ui-cornel-all>
            <br>Append <b><code>"&amp;_old"</code></b> to your URL query to use the <a href='http://panda.cern.ch'>old classic Panda Monitor</a> 
            </div>
         """
      self.publish(redirect,role=pmRoles.html())
