""" Show the non-zero MAXTIME values from schedconfig for each site """
# $Id: schedcfg.py 9690 2011-11-16 22:28:01Z fine $
from pmUtils.pmState import pmstate
from pmCore.pmModule import pmRoles
from  pmTaskBuffer.pmTaskBuffer import pmtaskbuffer as pmt     
import pmUtils.pmUtils as utils
import pmUtils.Stopwatch as Stopwatch

from  pmCore.pmModule import pmModule

class schedcfg(pmModule):
   """ Show the non-zero MAXTIME values from schedconfig for each site """

   #______________________________________________________________________________________
   def __init__(self,name=None,parent=None,obj=None):
      pmModule.__init__(self,name,parent,obj)
      self.publishUI(self.doJson)
   #______________________________________________________________________________________      
   def doMain(self):
      main = {}
      timer = Stopwatch.Stopwatch()
      tasks= pmt.schedCfg()
      main["buffer"] = {}
      main["buffer"]["method"] = 'schedcfg'
      main["buffer"]["params"] = ''
      main["buffer"]["type"] = isinstance(tasks,str)
      main["buffer"]["data"] = tasks
      
      main['time'] = {'fetch' : "%s" % timer}

      self.publish(main)

   #______________________________________________________________________________________      
   def doJson(self):
      """ 
      Show the non-zero MAXTIME values from schedconfig for each site
      ( see <a href='http://atlas-agis-api.cern.ch/request/pandaqueue/query/list/?json&preset=schedconf.all'>AGIS schedconf</a> also )
      """ 
      self.publishTitle('The schedconfig MAXTIME <font size=-2> ( see <a href="http://atlas-agis-api.cern.ch/request/pandaqueue/query/list/?json&preset=schedconf.all">AGIS schedconf</a> also)</font>')
      timer = Stopwatch.Stopwatch()
      self.doMain()
      self.publishNav('The maxtime from schedconfig:  "%s"' % (timer ) )
      self.publish( "%s/%s" % (self.server().fileScriptURL(),"taskBuffer/%s.js" % 'tbTable' ),role="script")
      self.publish( {'s-maxage':600,'max-age': 600}, role=pmRoles.cache())

def leftMenu():
    """ Return html for inclusion in left menu """
    #Temporary to preserve the backward compatibility 
    txt = "<a href='%s/schedcfg'>Maxtime</a>" % self.server().branchUrl()
    return txt
