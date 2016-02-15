""" Display Panda Logger Content """
# $Id$
# Display information on jobs that failed over to FAX  
#
import pmUtils.pmUtils as utils
from pmCore.pmModule import pmModule
from pmCore.pmModule import pmRoles
from pmTaskBuffer.pmTaskBuffer import pmtaskbuffer as pmt
from pmUtils.Stopwatch import Stopwatch

class failoverfast(pmModule):
   #______________________________________________________________________________________      
   def __init__(self,name=None,parent=None,obj=None):
      pmModule.__init__(self,name,parent,obj)
      self._faxVariables = 'WithFAX WithoutFAX bytesWithFAX bytesWithoutFAX timeToCopy'.split()
      self._sites,self._cloud4sites, sname, nicks = pmt.getSiteInfo('region')
      self._description,params = utils.normalizeDbSchema(pmt,'jobsarchived4')
      self.publishUI(self.doQuery,params=params)
   #______________________________________________________________________________________      
   def cloud(self, site):
      cloud = 'unknown'
      try:
         cloud = self._cloud4sites[site]
      except:
         pass
      finally:
         return "%s:%s" %(cloud,site)
   #______________________________________________________________________________________      
   @classmethod
   def toObj(cls,message):
      """ Convert the comma separated assignment into the Python dict
          This is the deprecated method to be deleted soon
      """
      pairs = message.split(",")
      out = []
      for pair in pairs:
         elem = pair.split("=",1)
         if len(elem) == 2:
            out.append('"%s":%s' %(elem[0],elem[1]))
         elif len(elem[0]) > 0:
            out.append(pair)
      return eval("{%s}" % ",".join(out))
   #______________________________________________________________________________________      
   def doQuery(self,tstart=None,tend=None,hours=6,days=None, type='FAXrecovery',limit=None,count=None,message=None):
      """ Shows Panda logger messages coming from FAX failovers. Messages are summarized per site.  
      <ul>
      <li> tstart - the start time of the period the messages belongs to      
      <li> tend   - the start time of the period the messages belongs to      
      <li> hours  - select the messages for the last '24*days+hours' hours 
      <li> days   - select the messages for the last 'days+hours/24' days 
      <li> limit  - the max number of records to be fetched from the Db table
      <li> <b><a title='Click to see the full list of the jobinfo parameters available' href='http://pandamon.cern.ch/describe?table=^JOBSARCHIVED4&doc=*'>PARAM</a>=value</b> - comma-separated list of the value <a href ='https://twiki.cern.ch/twiki/bin/view/PanDA/PandaPlatform#API_parameter_value_format'> patterns</a> to filter the job records.
      </ul>
      """
      site="panda.mon.fax"
      vals = self.extraValuesFilled()
      if vals == None:  vals = {}
      if not vals.has_key("jobStatus"):
          vals["jobStatus"] = 'finished,cancelled,failed'
      levelcode= ''
      hrs = 0
      try:
         hrs = int(hours)
      except:
         pass
      try:
         hrs += int(days)*24 
         days = None
      except:
         pass
      logwatch = Stopwatch()
      jobparam="computingSite,jobStatus,prodUserName"
      conditions=None
      q = pmt.getFaxInfo(site,type,levelcode, message=message, limit=limit, hours=hrs,select=["PID as PandaID ",'MESSAGE','Time'],selectjobs=jobparam,conditions=conditions,days=days,tstart=tstart,tend=tend,table='ATLAS_PANDA.PANDALOG_FAX tab')
      logwatch.stop()
      header = utils.normalizeSchema(q['header'])
      rows   = q['rows']
      main = {}
      main['header'] = []
      main['info'] =  rows
      try:
         count = int(count)
         main['count'] = count
      except:
         pass
      jobwatch = None   
      if len(rows) > 0:
         jobwatch = Stopwatch()   
         main['header'] = header
         # extract the "pandaid"
         iPandaId = utils.name2Index(header,'pandaid')
         if iPandaId ==None:  iPandaId = utils.name2Index(header,'pid')
         iProdUserName =  utils.name2Index(header,'prodUserName')
         iComputingSite =  utils.name2Index(header,'computingSite')
         rows = sorted(rows, key=lambda fax: fax[iPandaId])
         selRows = []
         for r in rows:
            if r[iProdUserName] == 'gangarbt': continue
            r[iComputingSite] = self.cloud(r[iComputingSite])
            selRows += [r]
         rows = selRows
         main['info'] = rows
         # split the message by variables
         header += self._faxVariables
         iMessage = utils.name2Index(header,'message')
         vIndx = utils.name2Index(header)
         for r in rows:
            r += [0]*len(self._faxVariables)
            try:
               faxcolumns = self.toObj(r[iMessage])
            except:
               print " FAX message {%s} from the job record [%s] is corrupted" % (r[iMessage], r)
               continue
            for f in faxcolumns:
               try:
                  r[vIndx[f]] = faxcolumns[f]
               except:
                  raise ValueError(" len=%s r=%s f=%s vIndx=%s %s" % (len(r),r,f,vIndx,faxcolumns))
            r.pop(iMessage) # removing message column
         header.pop(iMessage) # removing message from header
         jobwatch.stop()
      main['time'] = {'logquery': '%s' % logwatch,'jobquery': '%s' % jobwatch}
      main['params'] = {'hours':hrs}
      self.publish(main)
      self.publish( "%s/%s" % ( self.server().fileScriptURL(),"fax/%s.js" % "failoverfast" ),role=pmRoles.script() )
      self.publishTitle("Panda report on jobs failovers to FAX over last %s hours  " % hrs )
    

