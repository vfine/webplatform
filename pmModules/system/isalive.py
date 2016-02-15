""" Confirm that the service is alive """
# $Id:$
from pmCore.pmModule import pmRoles
from pmCore.pmModule import pmModule

class isalive(pmModule):
   """ Confirm that the service is alive"""
    #______________________________________________________________________________________
   def __init__(self,name=None,parent=None,obj=None):
      pmModule.__init__(self,name,parent,obj)      
      self.publishUI(self.doJson)  
   #______________________________________________________________________________________      
   def doJson(self):
      """  Is Alive  """ 
      main  = {'isalive' : 'yes' }
      self.publish(main)
      self.publish( {'s-maxage':0,'max-age': 0}, role=pmRoles.cache())