# $Id: hellojsonp.py 9690 2011-11-16 22:28:01Z fine $
#  Test JSONP communication

from pmUtils.pmState import pmstate
from pmCore.pmModule import pmRoles
import pmUtils.pmUtils as utils
import pmUtils.Stopwatch as Stopwatch

from  pmCore.pmModule import pmModule

class hellojsonp(pmModule):
    #______________________________________________________________________________________
   def __init__(self,name=None,parent=None,obj=None):
      pmModule.__init__(self,name,parent,obj)
      self.publishUI(self.doJson)      
   # ,atlas-nightlies-browser.cern.ch
   #______________________________________________________________________________________      
   def doJson(self,hosts='atlascloud.org,pandamon-eu.atlascloud.org,atlas-nightlies-browser.cern.ch,pandamon.cern.ch,atlascloud.org,pandamon-eu.atlascloud.org,pandamon.cern.ch,atlas-nightlies-browser.cern.ch',query='helloora',params=None):
      """ 
          Demonstrate the concurrent cross domain communication via <a href='http://en.wikipedia.org/wiki/JSONP'>JSONP</a> format
          <ul>
          <li><code>hosts</code> =  the list of hosts to communicate
          <li><code>query</code> =  the query to be sent to all hosts 
          <li><code>params</code>=  to be attached to the URL query
          </ul>
      """ 
      self.publishTitle('Hello JSONP cross domain communication.')
      hosts = "%s,%s" % (hosts,hosts)
      h = "%s" % hosts
      vr = h.split(",")
      ph =  ", ".join(vr)
      self.publishNav('The JSONP communication with <b>%s</b>.' %  ph )
      self.publish( "%s/%s" % (self.server().fileScriptURL(),"hello/hellojsonp.js"),role=pmRoles.script())
      self.publish({'hosts' : hosts.split(","),'query': query,'params': params })

def leftMenu():
    """ Return html for inclusion in left menu """
    #Temporary to preserve the backward compatibility 
    txt = "<a href='%s/hellojsonp'>Hello JSONP cross domain connections</a>" % self.server().branchUrl()
    return txt
