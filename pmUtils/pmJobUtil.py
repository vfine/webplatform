#!/usr/bin/python
from datetime import datetime,timedelta
import pmUtils as utils
from  pmTaskBuffer.pmTaskBuffer import pmtaskbuffer as pmt
from monitor.PandaHistogram import PandaHistogram, PandaTimeHistogram
import monitor.mond_conf as mond_conf

import itertools,re

class pmJobUtil(object):
  #______________________________________________________________________________________      
   def __init__(self,header=None,errorcodes=None):
      object.__init__(self)
      self._jobsetid = None
      self._tmpjslist = []
      self._creationtDict = None
      self._maxDuration = timedelta(0)
      self._maxTransfer = timedelta(0)
      self._histograms = None
      self.fgMultiSiteSetLabel = 'Multi-site'
      self._header = header
      self._cleanHeader =  None
      self._errorCodes =  errorcodes
      self._errorDict =  None
      self._headerindx = None
      self._newRetried = re.compile('(\s+new PandaID=)([0-9]+)(\s*)')
  #______________________________________________________________________________________ 
   @classmethod  
   def cleanUserID(cls, dnid):
        """ Extract name from DN """
        if not utils.isFilled(dnid): return ""
        up = re.compile('/(DC|O|OU|C|L)=[^\/]+')
        username = up.sub('', dnid)
        up2 = re.compile('/CN=[0-9]+')
        username = up2.sub('', username)
        up3 = re.compile(' [0-9]+')
        username = up3.sub('', username)
        up4 = re.compile('_[0-9]+')
        username = up4.sub('', username)
        username = username.replace('/CN=proxy','')
        username = username.replace('/CN=limited proxy','')
        username = username.replace('limited proxy','')
        pat = re.compile('.*/CN=([^\/]+)/CN=([^\/]+)')
        mat = pat.match(username)
        if mat:
            username = mat.group(2)
            if 'Robot:' in username: username = mat.group(1)
        else:
            username = username.replace('/CN=','')
        if username.lower().find('/email') > 0: username = username[:username.lower().find('/email')]
        pat = re.compile('.*(limited.*proxy).*')
        mat = pat.match(username)
        if mat: username = mat.group(1)
        username = username.replace('(','')
        username = username.replace(')','')
        username = username.replace("'","")
        return username   
   #______________________________________________________________________________________________________
   @classmethod  
   def getSpaceToken(destToken, ddm, setoken):
       # print 'destToken', destToken
       spaceToken = '?'
       if utils.isFilled(destToken):
           tokenName = destToken
           ddmList = ddm.split(',')
           if utils.isFilled(setoken):
               setokenList = setoken.split(',')
           else:
               setokenList = []
           # print 'ddmList', ddmList
           # print 'setokenList', setokenList
           i=0
           for d in setokenList:
               if d == tokenName:
                   spaceToken = ddmList[i]
                   break
               i += 1
       else:
           spaceToken = ddm.split(',')[0]
       # print 'spaceToken', spaceToken
       return spaceToken

   #______________________________________________________________________________________      
   def header(self,hdr=None):
      if hdr != None: 
         if self._header == None: self._header = []
         self._header += hdr
         self.cleanHeader(self._header)
      return self._header  
   #______________________________________________________________________________________      
   def hindex(self):
      if self._headerindx == None :           
         self._headerindx = utils.name2Index(self.header())
      return self._headerindx
   #______________________________________________________________________________________      
   def cleanHeader(self,header=None):
      if self._cleanHeader == None or header != None: 
         self._cleanHeader = [x for x in itertools.ifilterfalse(lambda a: a.lower() in ['pandaid','jobsetid','destinationdblock','proddblock','taskid'], self.header() if header == None else header) ]
         self.jobsets()['header'] = self._cleanHeader    
      return  self._cleanHeader        
   #______________________________________________________________________________________      
   def maxTransfer(self,newmax=None):
      if newmax != None: self._maxTransfer = newmax
      return self._maxTransfer
  #______________________________________________________________________________________      
   def maxDuration(self,newmax=None):
      if newmax != None: self._maxDuration = newmax
      return self._maxDuration
  #______________________________________________________________________________________      
   def histograms(self):
      if self._histograms == None:  self._histograms = {}
      return self._histograms
  #______________________________________________________________________________________      
   def creationtDict(self):
      if self._creationtDict== None:  self._creationtDict = {}
      return self._creationtDict
  #______________________________________________________________________________________      
   def jobsets(self):
      if self._jobsetid == None:  self._jobsetid = {}
      return self._jobsetid
  #______________________________________________________________________________________
   @classmethod  
   def factory(cls,header,jobs,errorCodes,sites,nicks):
      jsets = pmJobUtil(None,errorCodes)
      jsets.header(header)
      jsets.header(['tostart','duration','endt','transfert','username'])
      jsets.header(['ddm','ddmsite','ddmse'])
      jarr = []
      for job in jobs:
         zpj = utils.zipa(header,job)
#         jarr += [jsets.jobsetTime(zpj)]
         jarr += [jsets.jobDq2Site(jsets.jobsetTime(zpj),sites,nicks)]
# future         jarr += [jsets.jobRetry(zpj)]
# future         zpj = jsets.jobsetTime(utils.zipa(header,job))
# future         jarr += [jsets.jobRetry(zpj)]
      for job in jarr:
         jsets.fillJobsetId(job)
      jsets.jobsets()['histograms']=jsets.histograms()
      return jsets 
   #______________________________________________________________________________________      
   def setid(self, job):
      analysis = utils.isJob(job)      
      jtype = "A" if analysis else "P"
      id =  job.get('jobsetID') 
      if id != None:  jtype = "A"
      else:
         id = job.get('taskID')
         if id != None:  jtype = "P"
         else:
            id = job.get('JediTaskID')
            if id != None:  jtype = "J"
      return "%s:%s" % (jtype, id )
   #______________________________________________________________________________________      
   def cleanjob(self,job):
      return utils.unzip(self.cleanHeader(),job)
   #______________________________________________________________________________________ 
   def getSelfErrors(self,job):
     self._errorDict=  self.getErrors(job,self._errorDict, self._errorCodes)
     return self._errorDict
   #______________________________________________________________________________________      
   @classmethod  
   def getErrors(cls,job,errdict,errorcodes):
      """ collect the unique errors to publish """
      for errcode in errorcodes.keys():
         errval = 0
         errval = job[errcode]
         if errdict!=None:
            ec = errdict.get(errcode)
            if ec!=None: 
               ev = ec.get(errval)
               if ev != None: continue
         try:  
            if errval != 0 and errval != '0' and utils.isValid(errval):
               errval = int(errval)
   
               ## set prompt to True if error code is 1178 ##
               if errval == 1178: prompt = bool(1)

               errdiag = errcode.replace('ErrorCode','ErrorDiag')
               if errcode.find('ErrorCode') > 0:
                  diagtxt = job[errdiag]
               else:
                  diagtxt = ''
               if utils.isValid(diagtxt) and len(diagtxt) > 0:
                  desc = diagtxt
               elif errorcodes[errcode].has_key(errval):
                   desc = errorcodes[errcode][errval]
               else:
                  desc = "Unknown %s error code %s" % ( errcode, errval )
               errname = errcode.replace('ErrorCode','')
               errname = errname.replace('ExitCode','')
               if errdict ==None: 
                  errdict = {errcode: { errval : ( errname, desc ) }}
               else:
                  errcd = errdict.get(errcode);
                  if errcd == None: errdict[errcode] =  { errval : ( errname, desc ) }
                  else:             errcd[errval]=( errname, desc )
         except:
            incident  = "Wrong  data: %s " % utils.reportError("Unexpected value '%s' of the '%s' error code" %(errval,errcode))
            # utils.recordIncident(incident,'monalarm')
            pass
      return errdict
      
  #______________________________________________________________________________________      
   @classmethod  
   def isRetried(cls,job):
      errcode = job.get('taskBufferErrorCode')
      return errcode in ( 107, 106 )
  #______________________________________________________________________________________      
   def fillJobsetId(self,job,merge=None):
      analysis = utils.isJob(job)
      username = job['username']
      # jid = "jobsetID=<a href='%s?job=*&jobsetID=%s&user=%s'>%s</a>" % ( utils.monURL, job['jobsetID'],username, job['jobsetID'] )
      jobsetid = self.setid(job)
      jsetid = '%s:%s' % ( username, jobsetid )
      ## added to fix sorting bug ## 
      # if have_tmpuser == bool(0):
         # if not str(utils.cleanUserID(job['prodUserID'])) == "":
             # tmpuser = '%s' % username
             # have_tmpuser = bool(1)
      # if have_tmpuser == bool(1):
         # if not tmpuser == username:
             # oneuser = bool(0)
      # if not int(job['jobsetID']) in tmpjslist:
         # tmpjslist.append(int(job['jobsetID']))
      ##############################
      jsets = self.jobsets()
      if  not  jsets.has_key('jobsets') : jsets['jobsets'] = {}
      jobsets =  jsets['jobsets']
      creationtDict = self.creationtDict()
      jobid = job['PandaID']
      attempt  = job.get('attemptNr',0)
      if  attempt>0 and job['parentID']==None and job['jobsetID']!=None:  attempt = 0  # workaround issue #https://savannah.cern.ch/bugs/index.php?91176#comment6
      status   = job.get('jobStatus')
      if jsetid != None and not jobsets.has_key(jsetid):
         jobsets[jsetid] = {} 
         jobsets[jsetid]['analysis'] = analysis
         jobsets[jsetid]['workingGroup'] = job['workingGroup']
         jobsets[jsetid]['user'] = username
         jobsets[jsetid]['created'] = creationtDict[jobsetid]
         jobsets[jsetid]['latest']  = job.get('modificationTime',creationtDict[jobsetid])

         jobsets[jsetid]['site'] = job['computingSite']
         jobsets[jsetid]['inDS'] = job['prodDBlock']
         jobsets[jsetid]['outDS'] = job['destinationDBlock']
         jobsets[jsetid]['mergingJobs'] = { } 
         jobsets[jsetid]['attempt'] = attempt
         jobsets[jsetid]['jobs'] = {jobid: self.cleanjob(job) }
         jobsets[jsetid]['retried'] = 1 if self.isRetried(job) else 0
      else:
         jbTime = job.get('modificationTime')
         if jbTime != None and jobsets[jsetid]['latest'] < jbTime:
            jobsets[jsetid]['latest'] = jbTime

         jobsets[jsetid]['jobs'][jobid] = self.cleanjob(job)
         if self.isRetried(job): jobsets[jsetid]['retried'] += 1
         if jobsets[jsetid]['site'] != job['computingSite']:
              jobsets[jsetid]['site'] = self.fgMultiSiteSetLabel;
         jobsets[jsetid]['attempt'] += attempt+1
      try:
         if job['transformation'].find('buildJob') > 0:
            jobsets[jsetid]['libDS'] = job['destinationDBlock']
            jobsets[jsetid]['build'] = jobid 
         elif job['transformation'].find('runJob') > 0 or job['transformation'].find('runAthena') > 0:
            # set color
            pass
      except:
         pass
      if job['prodSourceLabel'] == 'user' and job['processingType'] == 'usermerge':
         mj = jobsets[jsetid]['mergingJobs'] 
         mj['all']  = mj.get('all',0) + 1
         mj[status] = mj.get(status,0) + 1
      elif utils.isValid(merge):
         try:
            # check  whether there is merging status for the job 
            tbuffer = pmt.checkMergeStatus( job['prodUserID'] ,job['jobDefinitionID'])
            if tbuffer != None:
               mj = jobsets[jsetid]['mergingJobs'] 
               status = tbuffer['status']
               if status in ( 'generated' ):
                  mj = jobsets[jsetid]['mergingJobs'] 
                  mj['all']=mj.get('all',0) + 1
                  mj[status] = mj.get(status,0) + 1
               elif status in ('NA'):   
                  pass 
               else:
                   mj[status] = len(tbuffer.get('mergeIDs',[]))
         except:
            pass
  #______________________________________________________________________________________      
   def jobRetry(self,job):
      if self.isRetried(job):
         diag = job.get('taskBufferErrorDiag')
         if utils.isValid(diag):
            pandaid=self._newRetried.search(diag)
            if pandaid:
               c = pandaid.group(2)
               job['retryID'] = c
      return job
  #______________________________________________________________________________________      
   def jobDq2Site(self,job,sites,nicks):
      siterow = job.get('computingSite')
      if job['jobStatus'] in ('finished','failed', 'canceled'):
         siterow = 'destinationSE'
      dqsite =  job.get(siterow);
      siteInfo = sites.get(dqsite)
      ddm = None
      tokens = None
      if siteInfo != None: 
         ddm = siteInfo.get('ddm')
         tokens = siteInfo.get('setokens')
         job['ddm'] = ddm
         job['setokens'] = tokens
         linksite = ddm
      if not utils.isFilled(ddm):
         linksite = job.get('computingSite');
         destSite =  job.get('destinationSE')
         if utils.isFilled(destSite): linksite = destSite
         if sites.has_key(linksite) and sites[linksite].has_key('dq2Site'):
            linksite = sites[linksite]['dq2Site']
      job['ddm']    = ddm   
      job['ddmsite']= linksite
      self.getSiteDDM(job,sites,nicks)
      return job
      
  #______________________________________________________________________________________      
   def getSiteDDM(self, job,sites,nicks):
      """ Get DDM for  site from schedconfig for logfiles """
      def getDDM(site):
         siteDDM=None
         if site != None:
            siteDDM = sites.get(site)
            if siteDDM != None:
               siteDDM =siteDDM['ddm']
            if siteDDM == None:
               siteDDM = nicks.get(site)
               if siteDDM != None: siteDDM =siteDDM['ddm']   
            if siteDDM == None:
               for nick in nicks:
                  if nick.startswith(site): 
                     siteDDM = nicks[nick].get('ddm')
                     break                
         return siteDDM
          
      ddmse  =  job.get('ddm')
      if not utils.isFilled(ddmse):
         computingElement =  job.get('computingElement')
         computingSite    =  job.get('computingSite')
         pilotID          =  job.get('pilotID')
         if computingSite != None and utils.isValid(pilotID) and pilotID.startswith('tp_') \
                 and computingElement != None and computingElement.find('.') < 0:
              ddmse = getDDM(computingElement)
         else:
              ddmse = getDDM(computingSite)
         if sites.has_key(ddmse) and sites[ddmse].has_key('dq2Site'): \
              ddmse = sites[ddmse]['dq2Site']
      job['ddmse'] =  ddmse
      return job
  #______________________________________________________________________________________      
   def jobsetTime(self,job):
      # if not utils.isJob(job): return None
      job['username'] = self.cleanUserID(job['prodUserID'])  
      # if job['creationTime'] == None or job['startTime'] == None or job['jobStatus'] == None or job['endTime'] ==None: return job
      creationtDict = self.creationtDict()
      maxDuration = self.maxDuration()
      maxTransfer = self.maxTransfer()
      jobsetid = self.setid(job)
      crtime = job.get('creationTime')
      job['tostart']  = timedelta(0)
      job['duration'] = timedelta(0)
      job['endt']     = None
      job['transfert']= timedelta(0)
      if crtime != None:   
         if not creationtDict.has_key(jobsetid):
            creationtDict[jobsetid] = job['creationTime']
         elif creationtDict[jobsetid] > job['creationTime']:
                   creationtDict[jobsetid] = job['creationTime']
         (duration,endt,tostart,transfert) = self.jobTimes(job)
         try:
            if duration >  maxDuration  and  job['jobStatus'] !='cancelled': self.maxDuration(duration) 
         except:
            raise ValueError(" %s %s JOB: %s " % (duration,maxDuration, job) )
         if utils.isValid(transfert) and transfert> maxTransfer : self.maxTransfer(transfert)
         job['tostart']  = tostart
         job['duration'] = duration
         job['endt']     = endt
         job['transfert']= transfert
      return job

   #______________________________________________________________________________________      
   def fillErrorHists(self,job,tstarth=None,tendh=None,tsteph=None,hours=None):
#            if jobstat in ('failed', 'cancelled'):
      if tendh == None: tendh = datetime.now()
      if hours == None: hours = 8
      if tstarth == None: tstarth = tendh - timedelta(hours=hours)
      if tsteph  == None: tsteph  = timedelta(minutes=30) # Ale request
      endt = job['endt']
      for f in self.getSelfErrors(job):
         nmcode = '%sErrorCode' % f
         nmdiag = '%sErrorDiag' % f
         error = job[f]
         if error != 0: 
            taskId  = job['taskID']
            site    = job['computingSite']
            #___________________________________________________________   
            def  currentHistograms(site,time,maxlenth=4):
               h = self.histograms()
               if site == 'all':
                  sitekey =  'TaskID %s - errors/hour distribution' % taskId
               else: 
                  sitekey = 'TaskID  %s - errors/hour/site distribution' % taskId 
               if h.has_key(sitekey):
                  esitehist = h[sitekey]
               else:
                  h[sitekey] = {}
                  esitehist = h[sitekey]

               if site == 'all':
                  ekey = '%s|%s' % (f.replace("ErrorCode",""),error)
               else:
                  ekey = site                        
               if esitehist.has_key(ekey):
                  hist = esitehist[ekey]
               else:
                  hist = esitehist[ekey] = PandaTimeHistogram(ekey,max=tendh,min=tstarth,step=tsteph)
                  if site =='all':
                     # sitepar = '&site=%s&cloud=%s' % ( site, job['cloud'] )
                     # errcode = "Unknown error code"
                     # errcode = errorCodes.get(nmcode,{}).get(error,errcode)
                     # errplotlink = utils.linkJobList(mode=mode, params='&%s=%s%s&sort=jobStatus&reverse=yes' % \
                        # (f, error, sitepar), showtxt=ekey, hours=total_hours,title=errcode)
                     errplotlink = error
                     hist.setLegend(errplotlink)   
               hist.fill(time)
            #___________________________________________________________  
            if tendh-tstarth >tsteph:
               currentHistograms(site, endt)
               currentHistograms("all",endt)
   #_______________________________________________________________________________________________________ 
   def fillJobDuration(self,job,total_hours,selectID=None,transfer=None):
      duration = job['duration']
      jobstat  = job['jobStatus']
      tostart  = job['tostart']
      transferPlot = transfer if jobstat in ('canceled', 'finished', 'failed') else False
      tkey = 'transfer'
      skey = 'stage out'
      
      if selectID == None:
         if utils.hasParam("taskID"):
            selectID = 'taskID'
         else:
            selectID = 'jobsetID'
      id = job[selectID]
      if id == None or id==-1: 
         selectID = 'The'
         id = ' '
      h    = self.histograms()
      sitekey   = "%s %s  job duration for all sites " %  (selectID.title(),id )
      waitsitekey = "%s %s  job wait time for all sites " %  (selectID.title(),id )
      if transferPlot:
         transfert = job['transfert']
         transfersitekey = "%s %s  job transfer time for all sites " %  (selectID.title(),id )
         if not h.has_key(transfersitekey):
            hh  = {  tkey:PandaHistogram(tkey,max=0.7*total_hours,min=0.001,step=0.05) 
                   , skey:PandaHistogram(tkey,max=0.7*total_hours,min=0.001,step=0.05) 
                  }
            for hi in hh:
               hh[hi].integralOpt(True)            
            h[transfersitekey] = hh                           
         tsitehist = h[transfersitekey]
         time = transfert.days*24.0+float(transfert.seconds)/3600.0
         tsitehist[tkey].fill(time)
         try:
            time = PilotTiming(job['pilotTiming'])['stageout']
            v = time.value
            u = time.unitvalue*60.
            tsitehist[skey].fill(float(v)/u)
         except:
            pass         
      elif not transfer:   
         if not h.has_key(sitekey):
            h[sitekey] = {}
         if not h.has_key(waitsitekey):
            h[waitsitekey] = {}

         esitehist = h[sitekey]
         wsitehist = h[waitsitekey]
         ekey = '%s' % jobstat
         
         if not esitehist.has_key(ekey):
            esitehist[ekey] = PandaHistogram(ekey,max=total_hours,min=0,step=0.1)
            esitehist[ekey].integralOpt(True)
            
         if not wsitehist.has_key(ekey):
            wsitehist[ekey] = PandaHistogram(ekey,max=total_hours,min=0,step=0.1)
            wsitehist[ekey].integralOpt(True)

         dhist = esitehist[ekey]
         time = duration.days*24.0+float(duration.seconds)/3600.0
         dhist.fill(time)
         
         whist = wsitehist[ekey]
         wait= tostart.days*24.0+float(tostart.seconds)/3600.0
         whist.fill(wait)
   #_______________________________________________________________________________________________________ 
   @classmethod  
   def region4Sites(self,pmt):
      sites = pmt.getSiteInfo()
      region4sites = {}
      site4regions = {}
      for site,s in sites.iteritems():
         k = s['sitename']
         v = s['cloud']
         region4sites[k] = v
         site4regions[v] = site4regions.get(v,[]) + [k]
      return region4sites,site4regions  
   #_______________________________________________________________________________________________________ 
   def fillJobProgess(self,job,selectID=None):
      endt    = job['endt']
      jobstat = job['jobStatus']
      if selectID == None:
         if utils.hasParam("taskID"):
            selectID = 'taskID'
         else:
            selectID = 'jobsetID'
      id = job[selectID]
      if id == None: 
         selectID = 'The'
         id = ' '
      h       = self.histograms()
      time    = endt
      for site in ('all', job['computingSite']):
         if site == 'all':
            sitekey = '%s %s  jobs/hour for all sites progress' %  (selectID.title(),id )
         else: 
            sitekey = '%s %s jobs/hour/site progress' %  (selectID.title(),id )
         if h.has_key(sitekey):
            esitehist = h[sitekey]
         else:
            h[sitekey] = {}
            esitehist = h[sitekey]
         if site == 'all':
            ekey = '%s' % jobstat
         else:
            ekey = site                        
         if esitehist.has_key(ekey):
            hist = esitehist[ekey]
         else:
            hist = esitehist[ekey] = PandaTimeHistogram(ekey,max=self.tendh,min=self.tstarth,step=self.tsteph)
         hist.fill(time)
   #______________________________________________________________________________________________________
   def total_hours(self):
      return self.maxDuration().days*24+self.maxDuration().seconds/3600 
   #______________________________________________________________________________________________________
   def total_hours_transfer(self):
       return self.maxTransfer().days*24+self.maxTransfer().seconds/3600 
   #______________________________________________________________________________________________________
   def doPlots(self,job,hours=12,tsteph=None,tstarth=None,tendh=None):
      if tendh   == None: tendh   = datetime.now()
      if tstarth == None: tstarth = tendh - timedelta(hours=hours)
      if tsteph  == None: tsteph  = timedelta(minutes=30) # Ale request
      total_hours = self.maxDuration().days*24+self.maxDuration().seconds/3600 
      total_hours_transfer = self.maxTransfer().days*24+self.maxTransfer().seconds/3600 
      # errorPlot    = utils.hasParam('jobStatus') and ( utils.queryParams['jobStatus'] == 'failed' or utils.queryParams['jobStatus'] == 'cancelled' ) and jobstat in ('failed', 'cancelled')
      # walltimePlot = utils.hasParam('walltime') or (utils.hasParam('processingType') and  utils.queryParams['processingType']=='reprocessing') if not errorPlot else False
      # progressPlot = tendh-tstarth > tsteph if not ( walltimePlot or errorPlot)  else False
      # transferPlot = utils.hasParam('walltime') and 't' in utils.queryParams['walltime']
      mode = 'oldarchive'
      if total_hours <= 72:
         mode = 'archive'
      for job in rows:
         endt = job['endt']
         jobstat = job['jobStatus']
         # and taskID
         if errorPlot or True:
            self.fillErrorHists(job,self.errorFields,tstarth,tendh,tsteph)
         elif walltimePlot: #  and "sort=duration":
            # Vanjashin issue TBD yet
            self.fillJobDuration(job,total_hours_transfer if transferPlot else total_hours, transfer=transferPlot)
         elif progressPlot:
            self.fillJobProgess(job)
      if  walltimePlot: 
         self.histograms()['xaxis']='hours';

#______________________________________________________________________________________________________
   @classmethod 
   def jobTimes(self,job):
      creationt = job.get('creationTime')
      startt    = job.get('startTime')
      jobstat   = job.get('jobStatus')
      endt      = job.get('endTime')
      transfert = timedelta(0)
      duration  = timedelta(0)
      try:
         if utils.isValid(endt) and utils.isValid(startt)  and endt > startt:
             duration = endt - startt
         elif utils.isValid(endt) and utils.isValid(creationt):
             duration = endt - creationt
         elif utils.isValid(startt) and not jobstat in ('failed', 'finished', 'cancelled'):
             duration = datetime.utcnow() - startt
         else:
             duration = timedelta(0)
      except:
         duration = timedelta(0)
      if jobstat in ('finished', 'failed','cancelled'):
         try:
            transfert = job.get('modificationTime') - endt
         except:
            transfert = timedelta(0)
            pass
      else:
         endt = job.get('modificationTime')
      if utils.isValid(creationt) and utils.isValid(startt):
            tostart = startt - creationt
      elif utils.isValid(creationt) and utils.isValid(endt):
            tostart = endt - creationt
      elif utils.isValid(creationt) and not jobstat in ('failed', 'finished', 'cancelled'):
            tostart = datetime.utcnow() - creationt
      else:
         tostart = timedelta(0)
      return (duration,endt,tostart,transfert)
 
jobutil = pmJobUtil()
if __name__ == '__main__':
   u = jobutil
   print  __file__