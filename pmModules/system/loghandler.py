""" The accept the Panda Logger message to fill the logger db table  $Id$"""
import re, time, calendar, os, copy
from datetime import datetime
from itertools import izip, count
from  pmTaskBuffer.pmTaskBuffer import pmtaskbuffer as pmt
from  pmTaskBuffer.pmTaskBuffer import pmwtaskbuffer as pmw
import pmConfig.pmConfig as config
import pmUtils.pmUtils as utils
from pmCore.pmModule import pmModule
from pmCore.pmModule import pmRoles

class loghandler(pmModule):
   #______________________________________________________________________________________      
   def __init__(self,name=None,parent=None,obj=None):
      pmModule.__init__(self,name,parent,obj)
      self._description =  pmt.describe('^PANDALOG$')
      # add the optional parameters:
      params = {}
      ci = utils.name2Index(self._description['header'],'column_name')
      collist = 'name message asctime Type PandaID loglevel levelname filename lineno module'.split()
      exclude = "pid line type name levelname BINTIME LOGUSER".upper().split()
      nmap = {}
      for c in collist:
         nmap[c.upper()] = c
      for c in self._description['rows']:
         p = not c[ci] in exclude
         nm = nmap.get(c[ci],c[ci])
         c[ci]  = nm
         if p: params[nm] = ' '
      self._allparams = ','.join(params.keys())
      self._levelmap = { 'INFO':20, 'WARNING':30 , 'DEBUG':10, 'ERROR':40 }
      ## 'publishUI' must be the last init statement  !
      self.publishUI(self.doJson,params=params)
      self.publishUI(self.doScript,role=pmRoles.script())
    
   #______________________________________________________________________________________      
   def doJson(self,pid,line,type='filesWithFAX',name='panda.mon.fax',levelname='INFO'):
      """ Accept the logger information
          <p>Supported query parameters are as follows:
          <table>
          <tr><td><a href='http://pandamon.cern.ch/describe?table=^PANDALOG&doc=*'>PARAM</a>=</td><td>[The value to be recorded]</td></tr>
          </table>
      """
      user = self.server().user() 
      #if self.server().user() == None:
      #   raise ValueError("No user name was present or none secure connection was used" )
      if name != 'panda.mon.fax':    
         raise ValueError("this module is not ready for %s category yet" % name)
      record = self.extraValues()
      record['pid'] = pid
      record['type'] = type
      record['line'] = line
      record['name'] = name
      record['levelname'] = levelname
#      if name == 'panda.mon.fax':      
#         record['message'] = '%s%s=%s'  % (record['message'] ,type,line)
      record['LOGUSER'] = user
      record['loglevel'] = self._levelmap[levelname]
      record['BINTIME'] = datetime.utcnow()
      record['TIME'] = record['BINTIME'].strftime('%Y-%m-%d %H:%M:%S')

      rupp = {}
      for r in record:
         rupp[r.upper()] = record[r]
      # pmw.addPandaLogRecord(rupp,self._description['rows']) 
      pmw.addFaxRecord(rupp,self._description['rows']) 
      self.publishTitle("Panda Logger")
      self.publish(record)
      self.publish({'s-maxage':0,'max-age': 0 }, role=pmRoles.cache())
   #______________________________________________________________________________________      
   def doScript(self,pid,line,type='filesWithFAX',name='panda.mon.fax',levelname='INFO'):
      """ 
         doScript(self,script=None) publishes the Javascript function to render the content onto the client Web browser
         The content is to be published by doJson 
         NB.The signatures (list of parameters) of the doJson and doScript should be the same
      """   
      javascript = """
         function _anyname_(tag,content) {
             /* Render the "content" */
             $(tag).empty();
             $(tag).html("<pre>"+ JSON.stringify(content,undefined,2)+"\n</pre>");
         }
      """
      self.publish(javascript,role=pmRoles.script())