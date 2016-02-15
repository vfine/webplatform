# $Id: hellohttps.py 13672 2012-11-28 21:10:16Z fine $
# Author: Valeri Fine (fine@bnl.gov) Sept 22, 2011
from pmCore.pmModule import pmModule 
from pmCore.pmModule import pmRoles
from datetime import datetime
from datetime import timedelta

#______________________________________________________________________________________      
class hellohttps(pmModule):
   """ The simplest Panda Web Module to provide the UI as follows:
       the URL: 'http:<hostname>/hellohttps'        should return the page reading "Hello World !!!"
       the URL: 'http:<hostname>/hellohttps?me=All should return the page reading "Hello All !!!"
       the URL: 'http:<hostname>/hellohttps?me=All&title='Ciao Panda Example' should return the page reading "Hello All !!!"
   """
   #______________________________________________________________________________________      
   def __init__(self,name=None,parent=None,obj=None):
      pmModule.__init__(self,name,parent,obj)
      self.publishUI(self.doQuery,role='html')

   #______________________________________________________________________________________      
   def doQuery(self,me='World',title='PanDA Hello World Example',cache=600):
      """ The simplest Panda Web Module to provide the UI as follows:<br>
       the URL: 'http:<hostname>/hellohttps'        should return the page reading <b>"Hello World !!!"</b> <br>
       the URL: 'http:<hostname>/hellohttps?me=All should return the page reading  <b>"Hello All !!!"</b><br>
       the URL: 'http:<hostname>/hellohttps?me=All&title='Ciao Panda Example' should return the page reading  <b>"Hello All !!!</b>"<br>
       <p> Arguments:
         <ul>
            <li>me -- the name of the person to greet, otherwise 'World'
            <li>title -- the page title, otherwise 'PanDA Hello World Example'
          </ul>  
      """
      env = self.server().environ()
      if env.has_key('SSL_CLIENT_CERT'): env['SSL_CLIENT_CERT'] = "The real CLIENT certificate  has been removed for the security reason;"
      if env.has_key('SSL_SERVER_CERT'): env['SSL_SERVER_CERT'] = "The real SERVER certificate  has been removed for the security reason;"
      for p in env: 
        # if 'HTTP_' in p : env[p]='[ . . . ]'
        # if 'CLIENT_' in p : env[p]='[ . . . ]'
        try:
           env[p] = env[p].replace('/var/www/html/panda','{. . .}')
        except:
           pass
      self.publishPage(main="Hello %s within %s!!! EDITED VERSION" %  (me,env), title = title )

