""" Calculate the PanDA Users Activity """
# $Id: useract.py 9690 2011-11-16 22:28:01Z fine $
# Display DB status and stats
from pmUtils.pmState import pmstate
from pmCore.pmModule import pmRoles
from  pmTaskBuffer.pmTaskBuffer import pmtaskbuffer as pmt
import pmUtils.pmUtils as utils
import pmUtils.Stopwatch as Stopwatch
from pmUtils.pmOracle import sqlSelect
from  pmCore.pmModule import pmModule
from datetime import timedelta
from datetime import datetime
import time
import os
#______________________________________________________________________________________      
def convert(dt):
   return time.mktime(dt.timetuple())
#_____________________________________________________________________  
def total_seconds (td, offset=0):
   return td.seconds + (td.days+offset) * 24 * 3600

class useract(pmModule):

    #______________________________________________________________________________________
   def __init__(self,name=None,parent=None,obj=None):
      pmModule.__init__(self,name,parent,obj)
      self.publishUI(self.doJson)
   #______________________________________________________________________________________      
   def doPlot(self, bins, width,xmin, xmax, xoffset, time=True, color = "rgba(0,0,153,0.8)", fillcolor="rgba(255,255,255,0.8)", title="The PANDA users activity for the last 180 days ", xtitle='2012', ytitle='Users'):
      h =   {  "attr": { 
                   "style": { "width": 1
                            , "color": color
                            , "background-color": fillcolor
                           }
                  , "options": "H"
                  , "name": "useact180days"
                  , "xaxis": {  "width": width # sec for time 86400.0
                              , "title": xtitle
                              , "max": xmax # 15638400.0 msec
                              , "min": xmin
                              , "time": True
                              , "offset": xoffset  # 1321660800.0 msec 
                             }
                  , "title": title
                  , "yaxis": {   "min": min(bins)
                               , "max": max(bins)
                               , "title": ytitle
                               , "width": 1.0
                             }
                 }
               , "data" : bins 
               , "class": "h1f"
             }
      return h
   
      
   #______________________________________________________________________________________      
   def makePlotPoints(self,rows,dateformat='%y%m%d'):
      maxTime = datetime.strptime("%s" % rows[0][0],dateformat) 
      try:
         nxtTime = datetime.strptime("%s" % rows[1][0],dateformat) 
         width = total_seconds(maxTime-nxtTime)
      except:
         width = 0      
      minTime =datetime.strptime("%s" % rows[-1][0],dateformat) 
      # maxTime += timedelta(days=1)
      timeOffset =  minTime
      nbins = (maxTime-minTime).days
      xmin = 0
      xmax = total_seconds(maxTime-minTime)
      bins =[ r[1]  for  r in reversed(rows) ]
      xoffset = convert(minTime);
      title="The PANDA users activity for the last  %s days " % nbins
      return self.doPlot(bins,width, xmin, xmax, xoffset, color = "rgba(0,0,153,0.8)", fillcolor="rgba(255,255,255,0.8)", title=title, xtitle=maxTime.year, ytitle='Users')
      
   #______________________________________________________________________________________      
   def publishPlot(self,plot,name,title,width=800,height=600,options='',log=False): 
      info = []   
      info.append(['File',""]) 
      rhists = []
      h2sell = plot
      if options != None and options != '':
         h2sell['attr']['options'] = options
      rhists.append(h2sell)
      info.append(['Histogram', rhists])
      info.append(['Name',"<b>%s</b>" % name])
      info.append(['Title',"<b>%s</b>" % title])
      main = {}
      main['info']   = info
      main['width']  = width
      main['height'] = height
      if log == True or isinstance(log,str) and  (log.lower()=="true" or log.lower()=="yes"): 
          main['log'] = True
      main['time'] = {}
      self.publish(main)

   #______________________________________________________________________________________      
   def doFile(self,file):
      """
         Read the the users' activities from the file
      """
      if file and file.strip() != '':
         pandadir =  os.environ.get('PANDA_HOME',os.path.expanduser("~"))
         item = pmt.getJson(file,os.path.join(pandadir,"panda/pandamon/static/data"))
         try:
            # new format
            rows = item['buffer']['data']['rows']
            header = item['buffer']['data']['header']
         except:
            # old one
            rows = item['buffer']['data'][1]
      return {"header": header, "rows" : rows }   
   #______________________________________________________________________________________      
   def doTaskBuffer(self, jobtype, select, timefield, tstart, tend, days):
      tables=('atlas_panda.jobsArchived4','ATLAS_PANDAARCH.JOBSARCHIVED')
      q =    pmt.getUserActivity(jobtype, select, timefield, tables, tstart, tend, days,True)
      return q
   #______________________________________________________________________________________      
   def doMergePush(self, file, jobtype, select, timefield, tstart=None, tend=None, days=None,pop=True,dateformat='%y%m%d'):
      """Merge the db and file data:
          - Push the fresh data from the db table
          - Pop the old data from the file data
      """
      fileData = self.doFile(file)
      fRows   = fileData['rows']
      sel =  sqlSelect()
      sel.prepareTime(None,tstart,tend,field='',days=days)
      times = sel.times()
      if times.get('start') != None or times.get('end') != None:
         if times.get('start') == None:
            tstart =  datetime.strptime("%s" % fRows[0],dateformat) -  timedelta(days=1)
         else:
            tstart = times.get('start')
         if times.get('end') == None:  
            tend = datetime.utcnow() + timedelta(days=1)
         else: 
            tend =  times.get('end') 
         days= None   
         fRows   = dict(fRows)
         dbTableData = self.doTaskBuffer(jobtype, select, timefield, tstart, tend, days)
         fDbRows = dict(dbTableData['rows'])
         # exclude duplicates
         fRows.update(fDbRows)
         f = []
         for d in sorted(fRows.keys(),reverse=True):
            f.append( [d,fRows[d]] )
         if pop==True:
            f.pop()         
         fRows=f  
      return { 'header' : fileData['header'], 'rows' : fRows }
   #______________________________________________________________________________________      
   def doMain(self, jobtype, select, timefield, tstart, tend, days,width,height,options,plot,log,file):
      main = {}
      params = "getUserActivity"     
      header = ['time','Users']
      rows = []
      timer = Stopwatch.Stopwatch()
      dateformat = '%y%m' if 'M' in options else '%y%m%d'
      if file and file.strip() != '':
         pop = True
         q = self.doMergePush(file,jobtype, select, timefield, tstart, tend, days,pop,dateformat)
      else:
         if tstart == None and tend==None and days == None: days = 3
         q = self.doTaskBuffer(jobtype, select, timefield, tstart, tend, days)
      if plot:
         title = "The PANDA users activity for the last %s days " % days
         self.publishPlot(self.makePlotPoints(q['rows'],dateformat),"h1d",title,width,height,options,log)
      else:
         main["buffer"] = {}
         main["buffer"]["method"] = params
         main["buffer"]["params"] = (jobtype, select, timefield, tstart, tend, days)
         main["buffer"]["type"] = False
         main["buffer"]["data"] = q
         main['time'] = {'fetch' : "%s" % timer}

         self.publish(main)

   #______________________________________________________________________________________      
   def doJson(self, jobtype='analysis', timefield='MODIFICATIONTIME', tstart=None, tend=None, days=None,width=600,height=400,options='',plot=False,log=False,file='useract365daysTotal'):
      """ 
          User activity plots <ul>
          <li>jobtype - name of the ROOT histogram
          <li>file - name the file to get the data from rather from Db
          <li>width - the width of the plots in px
          <li>height - the height of the plots in px
          <li>plot - = 'True' to create the plot; 'False' to use the table view render the data
          <li>log   - use logarithmic scale for Y-axis
          <li>options - some ROOT <a href='http://root.cern.ch/root/html534/THistPainter.html#HP01b'>Paint options</a> or <br>
          'M' = to get the "per month" rather "per day" data
          </ul>
      """ 
      self.publishTitle('Panda User activities for %(jobtype)s jobs'  % {'jobtype': jobtype}  )
      timer = Stopwatch.Stopwatch()
      select = "to_char(MODIFICATIONTIME ,'YYMMDD') as time,PRODUSERID" 
      if 'M' in options:
         select = "to_char(MODIFICATIONTIME ,'YYMM') as time,PRODUSERID"          
      self.doMain(jobtype, select, timefield, tstart, tend, days,width,height,options,plot,log,file)
      self.publishNav('The User Activities for %s  from CERN ( %s)' % ( jobtype, timer ) ) 
      render  = "taskBuffer/%s.js" % ("tbTable") if not plot else  "hello/%s.js" % "pyroot" 
      self.publish( "%s/%s" % (self.server().fileScriptURL(),render),role=pmRoles.script())
      self.publish( {'s-maxage':86400,'max-age': 86400}, role=pmRoles.cache())
