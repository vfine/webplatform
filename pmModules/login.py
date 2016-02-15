""" Login PANDA Monitor Server using CERN SSO  """
# $Id:$
# Author: Valeri Fine (fine@bnl.gov) Sept 22, 2011
from pmCore.pmModule import pmModule 
from pmCore.pmModule import pmRoles

#______________________________________________________________________________________      
class login(pmModule):
   """ 
   Login PANDA Monitor Server using CERN SSO 
   """
   #______________________________________________________________________________________      
   def __init__(self,name=None,parent=None,obj=None):
      pmModule.__init__(self,name,parent,obj)
      self.publishUI(self.doQuery,role=pmRoles.html())

   #______________________________________________________________________________________      
   def doQuery(self):
      """ Redirect URL to the login PANDA server 
      """
      if self.server().user() == None: raise ValueError("Login can be used  over SSL connection only")
      redirect = "<script>window.location='%s&_monlogin=1';</script>" % self.server().query()
      self.publish(redirect,role=pmRoles.html())
      self.publishTitle('Login via CERN SSO for %s' % self.server().user())
      
