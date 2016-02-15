# cassandrajob.py
# Display Panda job lists and job details as extracted from Cassadnra
#
import re, time, calendar, os
from datetime import datetime
from itertools import izip, count


import pmConfig.pmConfig as config
import pmUtils.pmUtils as utils
from  pmCore.pmModule import pmModule

def cleanJob(job):
    """ Tidy up the job record """
    if not 'JOBSETID' in job and 'JOBDEFINITIONID' in job: job['JOBSETID'] = job['JOBDEFINITIONID']
    if not 'PRODUSERNAME' in job and 'PRODUSERID' in job: job['PRODUSERNAME'] = job['PRODUSERID']
    if not 'PRODDBLOCK' in job: job['PRODDBLOCK'] = ''
    ## Convert times to real times
    for p in ( 'MODIFICATIONTIME', 'CREATIONTIME', 'STARTTIME', 'ENDTIME' ):
        itime = int(job[p])
        t = time.gmtime(itime)
        newtime = datetime(t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec)
        job[p] = newtime
    return job


def description():
    """ Description and intro page for job search using Cassandra back-end"""
    txt = """
<pre><font size=0>
    The cassandrajob module supports archival job queries against the BNL Cassandra cluster, returning information on one or many jobs.
    The Cassandra cluster serves as the backend of 'Mnemosyne' Web service, which returns results of queries as JSON.
    With Mnemosyne, supported query parameters are as follows:
    
    Time range: date=YYYYMMDD-YYYYMMDD. A single date would be just that: date=YYYYMMDD

    Parameter value: param=value  (multiple params are ANDed)
    
    Throughout, we assume that all parameter names are lowercase. Allowed parameters which directly correspond to DB column names:
    pandaid, taskid, produsername, prodsourcelabel, jobdefinitionid, jobsetid, computingsite, countrygroup

    While the way parameters are specified does not indicate correlation in their use, in the current version,
    only the following combinations are recognized (because they map onto composite indexes):

    pandaid
    taskid
    date and produsername
    date and prodsourcelabel
    date and computingsite and prodsourcelabel
    date and produsername and prodsourcelabel
    date and prodsourcelabel and countrygroup
    prodsourcelabel and jobsetid
    produsername and jobdefinitionid and prodsourcelabel

    This limitation related to combination of specific parameters will be removed going forward.

    Parameters governing the behavior of the query
    * limit - if omitted, will default to 10. It limits the number of entried extracted from Cassandra, for one single date listed in the query.
      It's a basic safeguard against user/developer errors resulting in DOS.

    * attrs - comma separated list of columns that need to be extracted. Limits the amount of data transmitted at three levels:
      Cassandra cluster internals, Apache-Cassandra link, Browser-Apache link
      If omitted, will extract all columns available.

    Sample queries:
    http://osgdev.racf.bnl.gov:20005/mnemosyne/jobs?prodsourcelabel=managed&date=20110110&limit=300
    http://osgdev.racf.bnl.gov:20005/mnemosyne/jobs?produsername=borut.kersevan@ijs.si&date=20110105&limit=1000
    http://osgdev.racf.bnl.gov:20005/mnemosyne/jobs?pandaid=1174713286
    http://osgdev.racf.bnl.gov:20005/mnemosyne/jobs?produsername=Angelantonio%20Castelli&jobdefinitionid=264&prodsourcelabel=user
    http://osgdev.racf.bnl.gov:20005/mnemosyne/jobs?computingsite=ANALY_CERN&prodsourcelabel=user&date=20110108-20110110&limit=100
      
"""
    txt += "</font></pre>"
    return txt

def doTitle():
   return 'Job data'

class cassandrajob(pmModule):
   #______________________________________________________________________________________      
   def __init__(self,name=None,parent=None,obj=None):
      pmModule.__init__(self,name,parent,obj)
      self.publishUI(self.doQuery)
   
   #______________________________________________________________________________________      
   def doQuery(self,pandaid=None,taskid=None,date=None,produsername=None,prodsourcelabel=None,jobsetid=None,computingsite=None):
       params = {}
       if pandaid:		params['pandaid']         = pandaid
       if taskid:		params['taskid']          = taskid
       if date:			params['date']            = date
       if produsername:		params['produsername']    = produsername
       if prodsourcelabel:	params['prodsourcelabel'] = prodsourcelabel
       if jobsetid!=None:	params['jobsetid']        = jobsetid
       if computingsite:	params['computingsite']   = computingsite
       
       self.publishTitle( doTitle(),"html")
       self.publish(params)
       self.publish("%s/%s" % (self.server().fileScriptURL() ,"cassandraJobRender.js"),role="script")

