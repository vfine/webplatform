""" An Example of the Third Party Monitor Embedded Application: FAX </td><td>$Rev: 14508 $"""
# $Id: map.py 9690 2011-11-16 22:28:01Z fine $
from datetime import timedelta
from datetime import datetime
import pycurl

from pmUtils.pmState import pmstate
from pmCore.pmModule import pmRoles
import pmUtils.pmOracle as pdb
import pmUtils.pmUtils as utils
import pmUtils.Stopwatch as Stopwatch

from  pmCore.pmModule import pmModule

class map(pmModule):
   """ An Example of the Third Party Monitor Embedded Application: FAX </td><td>$Rev: 14508 $"""
   #______________________________________________________________________________________
   def __init__(self,name=None,parent=None,obj=None):
      pmModule.__init__(self,name,parent,obj)
      self.publishUI(self.doJson)
      c = pycurl.Curl()
      c.setopt(c.WRITEFUNCTION, self.bodyCallBack)
      self._curl = c
      self._sites = []
      self.reset()
   #______________________________________________________________________________________
   def reset(self):
      self._title = ''
      self._links = []
   #______________________________________________________________________________________      
   def fetchInfo(self,url,api,params=None):
      self._title = api
      if params == None:
         self._curl.setopt(self._curl.URL, '%s/%s.asp' % (url,api))
      else:
         self._curl.setopt(self._curl.URL, '%s/%s.asp?%s' % (url,api,params))
      self._curl.perform()
   
   #______________________________________________________________________________________      
   def bodyCallBack(self,buf):
      lines =  buf.split('\n')
      for l in lines:
         arr = l.split("\t")
         if len(arr) >1:
            if self._title == 'getSites':
               self._sites.append(arr);
            else:
               self._links.append(arr);  
   #______________________________________________________________________________________      
   def doJson(self,src='http://ivukotic.web.cern.ch/ivukotic/FAX',date='2012-10-16',selS='ALL',script='fax/map'):
      """ FAX configuration viewer 
      """
      self.reset()
      params = "from=%s" % date
      if selS != None: params += '&selS=%s' % selS
      self.fetchInfo(src,'getLinks',params)
      if len(self._sites) == 0:
         self.fetchInfo(src,'getSites')
      main = {'sites': self._sites, 'links': self._links,'url': src }
      self.publish(main)
      self.publishTitle('FAX configuration viewer')
      self.publishNav(' %s for "%s"  ' % ( script, params ) ) 
      self.publish( "%s/%s" % (self.server().fileScriptURL(),"%s.js" % script ),role=pmRoles.script())
      self.publish({'s-maxage':340,'max-age': 200},role=pmRoles.cache())

def leftMenu():
    """ Return html for inclusion in left menu """
    #Temporary to preserve the backward compatibility 
    txt = "<a href='%s/map'>FAX viewer </a>" % self.server().branchUrl()
    return txt
