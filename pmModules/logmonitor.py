""" Display Panda Logger Content """
# $Id$
# Display Panda logger content
#
import pmUtils.pmUtils as utils
from pmUtils.pmOracle import sqlSelect
from  pmCore.pmModule import pmModule
from  pmTaskBuffer.pmTaskBuffer import pmtaskbuffer as pmt
    
class logmonitor(pmModule):
   #______________________________________________________________________________________      
   def __init__(self,name=None,parent=None,obj=None):
      pmModule.__init__(self,name,parent,obj)
      self.publishUI(self.doQuery)

   #______________________________________________________________________________________      
   def doQuery(self,site="panda.mon.bamboo", tstart=None,tend=None,hours=6,days=None, level='', type='',module=None,limit=1000,count=None,message=None):
      """ Show the the Selected Panda logger messages 
      <ul>
      <li> site - the patter to select the messaged from <a href='https://twiki.cern.ch/twiki/bin/view/PanDA/PandaPlatform#CommaParam'>sites</a>
      <li> tstart - the start time of the period the messages belongs to      
      <li> tend   - the start time of the period the messages belongs to      
      <li> hours  - select the messages for the last '24*days+hours' hours 
      <li> days   - select the messages for the last 'days+hours/24' days 
      <li> level  - select messages of the certain level only ('INFO', 'WARNING', 'DEBUG', 'ERROR') 
      <li> type   - the message 'type' (for example: 'taskbrokerage' )
      <li> limit  - the max number of records to be fetched from the Db table
      <li> message- the <a href='https://twiki.cern.ch/twiki/bin/view/PanDA/PandaPlatform#CommaParam'>comma separted list</a> of the patterns to select the messages
      </ul>
      """
   
      sitename  = "category=<b>%s</b>" % site if site !='' else ''
      typename  = "type=<b>%s</b>" % type if type !='' else ''
      levelname = "level=<b>%s</b>" % level   if level !='' else ''
      levelmap = { 'INFO':20, 'WARNING':30 , 'DEBUG':10, 'ERROR':40 }
      levelname = ''
      levelcode= ''
      if level != None and level != '':
         levelcode = levelmap[level.upper()];
         levelname  = "level=<b>%s</b>" % level
      if tstart != None and tend!=None: hours=None   
      duration = sqlSelect().prepareTime(hours,tstart,tend,'f',days).times('duration')
      hrs =duration.days*24+duration.seconds/3600 
      q = pmt.getLogInfo(site,type,levelcode,hours=hours,limit=limit,message=message,module=module,days=days,tstart=tstart,tend=tend)
      header = q['header']
      rows   = q['rows']
      if len(rows) <=0: header = []
      main = {}
      main['header'] = header
      main['levelmap'] = levelmap
      main['info'] =  rows
      main['limit'] = limit
      try:
         count = int(count)
         main['count'] = count
      except:
         pass
      main['limit'] = limit
      main['time'] = {}
      main['params'] = {'hours':hrs}
      self.publish(main)
      self.publishNav(' %s'  % '&nbsp; '.join((sitename, typename,levelname)) )
      self.publish( "%s/%s" % ( self.server().fileScriptURL(),"monitor/%s.js" % "logmonitor" ),role="script")
      self.publishTitle("Panda logging monitor (logged incidents) over last %s hours ( %.2f days ) " % (hrs,hrs/24.0 ) )
    

