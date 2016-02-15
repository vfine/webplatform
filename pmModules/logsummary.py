""" Summary of the Panda Log </td><td>$Rev: 16465 $ """
# $Id$
# Display Panda logger content
#
import re, os
from datetime import datetime, timedelta

import pmConfig.pmConfig as config
import pmUtils.pmUtils as utils
from pmUtils.pmOracle import sqlSelect
from pmUtils.pmState import pmstate
from  pmCore.pmModule import pmModule
from  pmTaskBuffer.pmTaskBuffer import pmtaskbuffer as pmt

logColumns = ( 'TIME', 'NAME', 'LEVELNAME', 'TYPE', 'MESSAGE' )
    
class logsummary(pmModule):
   """ Summary of the Panda Log </td><td>$Rev: 16465 $ """
   #______________________________________________________________________________________      
   def __init__(self,name=None,parent=None,obj=None):
      pmModule.__init__(self,name,parent,obj)
      self.publishUI(self.doQuery)

   #______________________________________________________________________________________      
   def doQuery(self,tstart=None,tend=None,hours=6,days=None):
      if tstart != None and tend != None: hours = None
      duration = sqlSelect().prepareTime(hours,tstart,tend,'f',days).times('duration')
      hrs =duration.days*24+duration.seconds/3600 
      q = pmt.logSummary(hours,tstart,tend,days)
      header =  q['header']
      rows    = q['rows'] 
      main = {}
      main['header'] = header if len(rows) >0 else []
      main['info'] =  rows
      main['time'] = {}
      main['params'] = {'hours':hrs}
      self.publish(main)
      # elf.publishNav('Incindent log summary: "%s".  "%s"' % ( query , timer ) ) # I know the cyber security will be mad ;-) VF.
      self.publish( "%s/%s" % ( self.server().fileScriptURL(),"monitor/%s.js" % "logsummary" ),role="script")
      self.publishTitle("Summary of Panda logged incidents, last %s hours" % hrs )
    

