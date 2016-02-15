# $Id: hello.py 13310 2012-10-26 16:03:22Z fine $
# Author: Valeri Fine (fine@bnl.gov) Sept 22, 2011
from pmCore.pmModule import pmModule 
from pmCore.pmModule import pmRoles
from datetime import datetime
from datetime import timedelta

#______________________________________________________________________________________      
class hello(pmModule):
   """ The simplest Panda Web Modulde to provide the UI as follows:
       the URL: 'http:<hostname>/hello'        should return the page reading "Hello World !!!"
       the URL: 'http:<hostname>/hello?me=All should return the page reading "Hello All !!!"
       the URL: 'http:<hostname>/hello?me=All&title='Ciao Panda Example' should return the page reading "Hello All !!!"
   """
   #______________________________________________________________________________________      
   def __init__(self,name=None,parent=None,obj=None):
      pmModule.__init__(self,name,parent,obj)
      self.publishUI(self.doQuery,role='html')

   #______________________________________________________________________________________      
   def doQuery(self,me='World',title='PanDA Hello World Example',cache=600):
      """ The simplest Panda Web Modulde to provide the UI as follows:<br>
       the URL: 'http:<hostname>/hello'        should return the page reading <b>"Hello World !!!"</b> <br>
       the URL: 'http:<hostname>/hello?me=All should return the page reading  <b>"Hello All !!!"</b><br>
       the URL: 'http:<hostname>/hello?me=All&title='Ciao Panda Example' should return the page reading  <b>"Hello All !!!</b>"<br>
       <p> Arguments:
         <ul>
            <li>me -- the name of the person to greet, otherwise 'World'
            <li>title -- the page title, otherwise 'PanDA Hello World Example'
          </ul>  
      """
      user = self.server().user()
      if user:
          if me == user: 
             me = "<h2>Hello %s%s !!! </h2>" % (me[0].upper(),me[1:])
             title = "<pre> %s \n</pre><br>Thank you for using the secure communication" % title
          else: 
             me = " <b>Sorry, %s</b>. You entered the wrong name. Please, Try again" % user
             title = "Wrong name was used"
      else: 
         me = "Hello unknown guy . Please use the secure connection to communicate me"      
         title = 'PanDA Hello World Example'
      self.publishPage(main="%s" %  me, title = title )
      self.publish(timedelta(seconds=348),role=pmRoles.cache())
      self.publish( {'s-maxage':cache,'max-age': cache}, role=pmRoles.cache())
