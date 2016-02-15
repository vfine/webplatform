""" Show  he list of Panda Jobs with LFN or versa verse LFNs by Panda IDs </td><td>$Rev$"""
# $Id: joblfn.py 19632 2014-07-06 07:30:10Z jschovan $
from pmUtils.pmState import pmstate
from pmCore.pmModule import pmRoles
from  pmTaskBuffer.pmTaskBuffer import pmtaskbuffer as pmt
import pmUtils.pmUtils as utils

from  pmCore.pmModule import pmModule

class joblfn(pmModule):
   """  Show  the list of Panda id with LFN or versa verse LFNs by Panda IDs """

    #______________________________________________________________________________________
   def __init__(self,name=None,parent=None,obj=None):
      pmModule.__init__(self,name,parent,obj)
      self.publishUI(self.doJson)

   #______________________________________________________________________________________      
   def doJson(self,lfn=None, jobs=None,type='input',ds=None,table='new',limit=1000,jobstatus=None,site=None,jobtype='production',days=1,user=None,select=None):
      """ 
         Show  the list of Panda id with LFN or versa verse LFNs by Panda IDs
         <ul>
         <li><code>lfn</code>   - the list of the comma separated files 
         <li><code>ds</code>    - the list of the comma separated datasets 
         <li><code>jobs</code>  - the list of the comma separated Panda's job IDs
         <li><code>table</code>  = "new" (default) look up the records for last 3 days
                        <br> ="old" - look up the records those more than 3 days old (slow)
                        <br> ="deep" - look up the "old" and "new" tables (slow)
         <li><code>type</code>  - the type selector. <br>
                               =  'input - the default value<br>
                               =  '*' | 'all' - list all types available.
          <li><code>jobstatus</code> = the comma separated list of the job status to filter
          <br>For example: 'defined, waiting,assigned,activated,sent,starting,running'
          <li><code>site</code> = the comma separated list of the sizte to list the jobs from         
          <br> For example 'UTA_SWT2'
          <li><code>jobtype</code> = the comma separated list of the job type to filter
          <br> For example, "analysis, production"
          <li><code>days</code> = the number of the days to look up the list of the jobs if either 'jobstatus' or 'site'  parameter is defined
          <li><code>user</code> = the comma separated list of the usernames . 
          <br>NB. The names may contain the the wildcard symbol '*'. Be aware the wildcard slows the search down
         </ul>
      """ 
      title = 'The list of files for the  '
      if jobstatus and jobstatus.strip()   =='': jobstatus = None
      if site and site.strip()   =='':        site = None
      if lfn and lfn.strip()   =='': lfn = None
      if jobs and isinstance(jobs,str) and jobs.strip() =='': jobs = None
      if ds and ds.strip()     =='': ds=None
      if type and type.strip() =='': type='all'
      if  lfn==None and jobs==None and ds==None and jobstatus==None and site==None:
           self.publishTitle("Ambigios query: lfn=%(lfn)s; pandaid=%(pandaid)s either lfn or padaid can be defined. One can not define lfn and pandaid at once" % { 'lfn': lfn, 'pandaid' : jobs} )
           self.publish('<h2>Check the input parameters. Click the "?" to see the API documentaion<h2>', role=pmRoles.html())
      else:
         nav = ''
         if limit:
             nav += "Limit %s rows." % limit
         if type=='*' or type==None: type = 'all'
         if lfn != None:
            self.publishTitle("The list of the PANDA jobs with the LFN of the '%s' type provided" % type)
            if not '*' in lfn:  # disregard the jobtype parameter
               if utils.isFilled(jobtype): 
                  nav += " Disregarding the jobtype='%s' default parameter" % jobtype 
                  jobtype = None
         if ds != None:   
            self.publishTitle("The list of the PANDA jobs with the DATASETs of the '%s' type provided" % type)
         if jobs!=None:
            self.publishTitle("The list of the '%s' LFN with the PANDA Job IDs provided" % type)
         if utils.isFilled(nav):
            self.publishNav(nav)
         main = {}
         main["buffer"] = {}
         main["buffer"]["method"] = "joblfn"
         main["buffer"]["params"] = (lfn if lfn!=None else '',jobs if jobs!= None else '' ) 
         if jobs != None: main["buffer"]["jobs"] = jobs
         main["buffer"]["type"] = False
         if (utils.isFilled(jobstatus) or utils.isFilled(site) or utils.isFilled(user)) and  not utils.isFilled(jobs):
             tables = ['atlas_panda.jobsArchived4','atlas_panda.jobsActive4','atlas_panda.jobsWaiting4','atlas_panda.jobsDefined4']
             r = pmt.getJobIds(site, jobtype,jobstatus,table=tables,days=days,username=user)
             jobs = [i[0] for i in r['rows']]
         if not utils.isFilled(select):
            select = []    
            if jobs == None or ( not isinstance(jobs,int) and len(jobs) > 1): select.append('pandaid');
            select += ['type', 'lfn', 'fsize', 'dataset', 'guid', 'scope', 'destinationse']
         else:
            select = utils.parseArray(select);         
         main["buffer"]["data"] = pmt.getJobLFN(select=','.join(select),table=table,lfn=lfn,pandaid=jobs,type=type,ds=ds,limit=limit)
         self.publish(main)
         self.publish( "%s/%s" % (self.server().fileScriptURL(),"taskBuffer/%s.js" % "getJobLFN"),role=pmRoles.script())
