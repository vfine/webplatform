# $Id: hellohi.py 13701 2012-12-03 20:46:09Z fine $
# Author: Valeri Fine (fine@bnl.gov) Sept 22, 2011
from pmCore.pmModule import pmModule

class hellohi(pmModule):

   #______________________________________________________________________________________      
   def __init__(self,name=None,parent=None,obj=None):
      pmModule.__init__(self,name,parent,obj)
      self.publishMenu('Hello Word example')

      #  register UI to provide the default 'http:<hostname>/hellohi' UI
      self.publishUI(self.doQuery,role='html')
      
      #  register UI to provide : 'http:<hostname>/hellohi?_mode=hi' UI
      self.publishUI(self.doHi,role='html',alias='hi')

   #______________________________________________________________________________________      
   def doQuery(self,me='World',title='PanDA Hello Word Example'):
       """ Process the query request 
        Arguments:
            me -- the name of the person to greet otherwise 'World'
        Notes:    
           the URL: 'http:<hostname>/hellohi"        should return the page reading "Hello Word !!!
           the URL: 'http:<hostname>/hellohi?me=All" should return the page reading "Hello All !!!
       """
       self.publishPage(title=title,main="Hello %s !!!" %  me)

   #______________________________________________________________________________________      
   def doHi(self,you='Everybody',title='PanDA Hi Everybody Example'):
       """ Process the query request 
        Arguments:
           you -- the name of the person to greet otherwise 'Everybody'
        Notes:    
           the URL: 'http:<hostname>/hellohi?_mode=hi"         should return the page reading "Hi Everybody !"
           the URL: 'http:<hostname>/hellohi?_mode=hi&you=All" should return the page reading "Hi All !"
       """
       self.publishTitle(title)
       self.publishMain("Hi %s !" %  you)

from pmUtils.pmState import pmstate
#______________________________________________________________________________________      
def leftMenu(self): 
    """ Return html for inclusion in left menu """
    # This method is here for the sake of the backward compatibility
    txt = "<a href='%s/hello'>Hello Word example</a>" % self.server().branchUrl()
    return txt
