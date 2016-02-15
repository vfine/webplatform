# $Id: helloora.py 13701 2012-12-03 20:46:09Z fine $
# Display DB status and stats
from datetime import timedelta
from datetime import datetime

from pmUtils.pmState import pmstate
from pmCore.pmModule import pmRoles
import pmUtils.pmOracle as pdb
import pmUtils.pmUtils as utils
import pmUtils.Stopwatch as Stopwatch

from  pmCore.pmModule import pmModule

class helloora(pmModule):

    #______________________________________________________________________________________
   def __init__(self,name=None,parent=None,obj=None):
      pmModule.__init__(self,name,parent,obj)
      self.publishUI(self.doJson)
   #______________________________________________________________________________________      
   def doMain(self,query):
      connectionTime = Stopwatch.Stopwatch()
      sql = pdb.pmDb()
      if query==None or query=='': query =  "select distinct jobstatus from JOBSARCHIVED4"
      timer = Stopwatch.Stopwatch()
      s =  sql.fetchallh(query)
      header = s['header']
      rows = s['rows']
      stime = "%s" % timer
      sql.close()
      main = {}
      main['header'] = header if len(rows) >0 else []
      main['info'] = rows
      main['time'] = {}
      main['time'] ["fetch"] = stime
      self.publish(main)

   #______________________________________________________________________________________      
   def doJson(self,query='select distinct jobstatus from ATLAS_PANDA.JOBSARCHIVED4',start='2012-03-01',end='',job=None, fields="NINPUTDATAFILES,INPUTFILEBYTES,NOUTPUTDATAFILES,OUTPUTFILEBYTES",limit=10000,describe=None):
      """ 
          Place any query with the CERN Oracle Db <br><ul>
          <li><code>query = "select distinct jobstatus from ATLAS_PANDA.JOBSARCHIVED4"</code><br>
          <li><code>query = "us" - is to select the US users who were using the panda within start/end time range</code><br>
          <li><code>query = "releaseinfo" - is to select the release info for all Panda sites</code><br>
          <li><code>job&nbsp;&nbsp;   = "*" is to show the 'fields' for the 10k jobs </code><br>
          <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; = 'PandaIDs' is to the comma  separated list of PAnda Ids to show its 'fields' </code><br>
          <li><code>fields= the comma separated list of the Db columns to show for the jobs selected with the 'job' parameter 'job' </code><br>
          <li><code>start = the start date   for "us" query (default 2012-02-01) </code><br>
          <li><code>end&nbsp;&nbsp; = the end for the "us" query (the default is start date + 30 days) <code>
          </ul>
      """ 
      releaseinfo=False
      if describe !=None: 
        query = "select distinct column_name,data_type  from all_tab_columns where table_name='%s'" % describe.upper()
      if query=="us":
         if start=='': 
            tstart = datetime.now() - timedelta(days=3*30) + 1;
         else:
            tstart = datetime.strptime(start,'%Y-%m-%d')
         starttime=" and MODIFICATIONTIME >= to_date('%s','YYYY-MM-DD') " % tstart.strftime('%Y-%m-%d')
         if end=='': 
            tend = tstart+timedelta(days=30)
         else: 
            tend = datetime.strptime(end,'%Y-%m-%d')
         table =  'ATLAS_PANDAARCH.JOBSARCHIVED' if tstart <  datetime.now() - timedelta(days=3*30) else 'ATLAS_PANDA.JOBSARCHIVED4'
         endtime=" and MODIFICATIONTIME < to_date('%s','YYYY-MM-DD') " % tend.strftime('%Y-%m-%d')
         query="select distinct PRODUSERNAME,PRODUSERID from %(table)s where regexp_like(PRODUSERID,'(/C=US/)|(/DC=doegrids/)') and JOBSTATUS='finished' %(start)s %(end)s" %{ "table" : table, "start" : starttime,"end":endtime} 
      elif  query=="releaseinfo":
         query="select * from ATLAS_PANDAMETA.installedsw  order by release desc, siteid, cache"
      elif   job !=None:
         if fields=='' or fields == None: fields = "*"
         if isinstance(job,str) and job.strip() =="*": where = ' where ROWNUM <= %d ' % limit
         else: where = " where pandaid in (%s) " % job
         query="select pandaid, %s from ATLAS_PANDA.JOBSARCHIVED4 %s " % ( fields, where)
      self.publishTitle('Hello Oracle Db from pid: %s !!!' % self.server().getpid() )
      timer = Stopwatch.Stopwatch()
      self.doMain(query)
      self.publishNav('The Oracle Db table from CERN: "%s".  "%s"' % ( query , timer ) ) # I know the cyber security will be mad ;-) VF.
      self.publish( "%s/%s" % ( self.server().fileScriptURL(),"hello/%s.js" % "helloora" ),role="script")

#______________________________________________________________________________________      
def leftMenu():
    """ Return html for inclusion in left menu """
    #Temporary to preserve the backward compatibility 
    txt = "<a href='%s/helloora'>Hello Oracle DB status</a>" % self.server().branchUrl()
    return txt
