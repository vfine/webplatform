# $Id: listtasks.py 9690 2011-11-16 22:28:01Z fine $
# ATLAS Dataset Nomenclature: https://cdsweb.cern.ch/record-restricted/1070318/? 
# https://cds.cern.ch/record/1525527?
# https://twiki.cern.ch/twiki/bin/viewauth/Atlas/DatasetNomenclature
# Display DB status and stats
from pmUtils.pmState import pmstate
from pmCore.pmModule import pmRoles
from  pmTaskBuffer.pmTaskBuffer import pmgrisliaskbuffer as gmt
from  pmTaskBuffer.pmTaskBuffer import pmgrisliwbuffer   as gwr
import pmUtils.pmUtils as utils
import pmUtils.Stopwatch as Stopwatch
import monitor.taskDef_conf as taskDef_conf
#  from monitor.prototype import queryValidFormats, queryValidProjects

from  pmCore.pmModule import pmModule
import re
import sys
import time
import checkTask

 
################################
def specCharReplace(param) :
   sc = ['%21', '%40', '%23', '%24', '%25', '%5E', '%26', '*',  '%28', '%29',\
         '%3A', '%3B', '+',   '_',   '-',   '%7B', '%2B', '%5B','%5D', '%5C',\
         '%5D', '%5C', '%7C', '%2C', '%3C', '%3E']
   alp= ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')',\
         ':', ';', ' ', '_', '-', '=', '+', '{', '}', '[',\
         ']', '\\', '|',',','<','>']
   qp = param
   try :
       int(param)
   except :
     for n in range(len(sc)) :
      qp = qp.replace(sc[n],alp[n])
     qp = qp.strip()
   return qp
#_____________________________________________________
def containsAny(str) :

#  set = '!@#$%^&*()-+={}[]\|?<>,:;'
#  PN , 10.02.07
  set = '!@#$%^&*()={}[]\|?<>,:;'
  return 1 in [c in str for c in set]


#_____________________________________________________
def OutputDataset(dsi) :

   error = 0
   errtxt= ''
   dso   = ''
   nnn   = 0
   phref = ''
   type  = 'unknown'
   junk = dsi.split('.')
   if len(junk) > 3 :
      # check for invalid characters
      dsi = specCharReplace(dsi)
      ret = containsAny(dsi)
      if ret == 1 :
         error = 1
         errtxt = "Dataset : %s. Have invalid characters"%dsi
      else :
         outs = findInputDataset(dsi)
         # print "ssssssss", outs,len(outs)
      if len(outs) >= 0 :
         project = junk[0].strip()
         nnn     = junk[1].strip()
         iphref = 2;  itype = 3
         if len(junk) == 4 : iphref = 3; itype = 2
         phref   = junk[iphref].strip()
         type    = junk[itype].strip()
#       dso = "%s.%s.%s"%(project,nnn,phref)
      else :
        error = 1
        errtxt = "%s. Not Found in catalog"%dsi
   else :
     error  = 1
     errtxt = "%s  Cannot build Output DatasetName."%dsi

   return (nnn, phref, type, error, errtxt)
#_____________________________________________________
def checkProject(project):
    return (0,'') # This should be Ok for cloning VF
    error = 1
    errtxt="%s. Not found"%project
    for p in (getProjectNameList()):#taskDef_conf.projects['name']) :
         if p == project :
              error = 0
              errtxt = ''
              break
    return (error,errtxt)

#_____________________________________________________
def checkUserID(nick):
#
# May 2, 2006 ak
# check nick and returns e-m
#
   r = gmt.getTaskUsers(nick) 
   if len(r['rows']) >0:
      mail = r['rows'][0][0]
      if mail : return (0,'',mail)
   return (0,'',nick)

   error = 1
   errtxt= "UserID : %s. Not known" % (nick)
   mail  = nick

   return (error,errtxt,mail)

#_____________________________________________________
def getProjectNameList():
    list_ = []
    list_ += taskDef_conf.projects['name']
    list_ += queryValidProjects()
    list_ = list(set(list_))
    list_.sort()
    return list_

#_____________________________________________________
def findInputDataset(ds) :
#
   outs  = []
   dds   = ds.split('.')
   dsp   = dds[0]
   if len(dds)==4 and dds[3]=='py' :
      outs.append(ds.strip())
   elif '.te.mc.csc.ctb.rome.dc2'.find(dsp[:2])>0 :
      outs.append(ds.strip())
   else :   # out of system data
      return outs
   return outs

#_____________________________________________________
def OutputDatasetIH(dsi) :
# Dec 10, 2005 I.H. file : DC3.NNN.PhRef.py
  error = 0
  errtxt=''
  dso   =''
  nnn   = 0
  phref =''
  junk = dsi.split('.')
  if len(junk) > 3 :
  # check for invalid characters
   dsi = specCharReplace(dsi)
   ret = containsAny(dsi)
   if ret == 1 :
    error = 1
    errtxt = "%s Have invalid characters"%dsi
   else :
    nnn     = junk[1].strip()
    phref   = junk[2].strip()

  return(nnn,phref,error,errtxt)

def getTag (trf,vp,lp,trfv,email):
# PPPPPPPPPPPP
  return 0
  mdeb = 1
  (pdb,dbcur,OracleDatasetDB) = connectGRISLI('R')
  table   =  "%s.%s"%(OracleDatasetDB,'t_trf_config')
  t_users =  "%s.%s"%(OracleDatasetDB,'t_users')
  vpa = myReplace(lp,vp)
  #------------------
  q1="select tag,cid from %s where trf='%s' and lparams='%s' and vparams='%s' and trfv='%s'" %\
      (table,trf,lp,vpa,trfv)
  x=dbcur.execute(q1)
  t=dbcur.fetchall()
  if mdeb: print 'in gettag1:',vpa,t

  if len(t)>0 :
       DButilsOracle.closeDB(pdb, dbcur)
       tag=t[0][0]
       cid=t[0][1]
       tcid="%s%s" % (tag,cid)
       return tcid

  q2="select role from %s where activity='Task request' and status='approved' and email='%s'"%\
      (t_users,email)
  y=dbcur.execute(q2)
  v=dbcur.fetchall()
  DButilsOracle.closeDB(pdb, dbcur)
  if mdeb: print 'in gettag2 role:',v
  if not v:
     return 'unknown'


  try :
    role=v[0][0]
    if role=='admin':
       (pdb,dbcur,OracleDatasetDB) = connectGRISLI('W')
    else :
       (pdb,dbcur,OracleDatasetDB) = connectGRISLI('R')
    t_trf_list   = "%s.%s"%(OracleDatasetDB,'t_trf_list')
    t_trf_config = "%s.%s"%(OracleDatasetDB,'t_trf_config')
    yt   = dbcur.execute("select tag from %s where trf='%s'" % (t_trf_list,trf))
    tag  = dbcur.fetchall()[0][0]
    if mdeb: print ' in gettag2 tag:',tag
    yc   = dbcur.execute("select max(cid) from %s where tag='%s'" % (t_trf_config,tag))
    uuu  = dbcur.fetchall()[0][0]
    if mdeb: print ' in gettag2 uuu:',uuu
    n    = 10
    if uuu: n    = int(uuu)+1
    if mdeb: print ' in gettag2  n :',n
    ami  =-1
    tnow = 0
    if role=='admin':
     dbcur.execute("insert into %s (tag,cid,trf,lparams,vparams,trfv,ami_flag) \
           values ('%s','%s','%s','%s','%s','%s',%s)" %  (t_trf_config,tag,n,trf,lp,vpa,trfv,ami))
     pdb.commit()
    pdb.close()
    tcid="%s%s" % (tag,n)
    return tcid
  except:
    DButilsOracle.closeDB(pdb, dbcur)
    return 'unknown'


#_____________________________________________________
def taskVersion(trfv) :
#
# trfv     - transformation version
# tversion - task version
   junk = trfv.split('.')
   version = 'v'
   for j in (junk) :
     try:
      if int(j) < 10 :
       version += "0%s"%j
      else :
       version += "%s"%j
     except:
       version += "%s"%j
   return version
   
#_____________________________________________________
def addTaskChecks(qparams) :
     debugmode = 0
     email     = ''
     tname     = ''
     trf       = ''
     trfv      = ''
     project   = ''
     status    = ''
     intype    = ''
     line      = 'addTaskChecks'
     error     = 0
     ERROR     = 0

# check input dataset
     inputDataset  = specCharReplace(qparams['qDSInput'])
     dds = inputDataset.split('.')
     if len(dds)==4 and dds[3] == 'py' :
     # special case I.H. files
       (nnn,phref,error,errtxt) = OutputDatasetIH(inputDataset)
     else :
       (nnn, phref, intype, error, errtxt) = OutputDataset(inputDataset)
     if error != 0 :
        ERROR += error
        # line += TextField("Input Dataset",errtxt,"tomato")
        line += 'Input Dataset'
# check project
     project = qparams['qProject']
     (error,errtxt) = checkProject(project)
     if error != 0 :
       ERROR += error
       # VF line += TextField("Project",errtxt,"tomato")
       line += " Project "
       print ' error line=',line,errtxt,project
# check TRF/input dataset consistency
     else :
        trf = qparams['qTaskTRF']
        trfv= qparams['qTaskTRFVersion']
        (error, errtxt) = checkTRFvsInputDatset(trf,inputDataset)
        if error != 0 :
         ERROR += error
         line += "Input Dataset/TRF"
         if debugmode : print ' error line=',line

# check e-mail
# 29.05.05 ak
        mail  =''
        email = specCharReplace(qparams['qMail'])
        (error,errtxt,mail) = checkUserID(email)
        if error != 0 :
         ERROR += error
         line = "Requested by (check nick name)  %s ",errtxt
         if debugmode : print ' error line=',line
        else :
         email = mail
        # print " 266 ",mail,email,qparams['qMail']
     return (nnn,phref,intype,email, ERROR, errtxt + " from " + line)
     
#_____________________________________________________
def checkUserGroup(email):#
  return ''
  # (pdb,dbcur,OracleDatasetDB) = connectGRISLI('R')
  # table       = "%s.%s"%(mond_conf.daemon['oracle_metadb'],'t_users')
  # sql   = "SELECT groupname FROM %s WHERE email='%s' " % (table,email)
  # sql  += " and activity like 'Task%' and status='approved' "
  # all = DButilsOracle.QueryAll(pdb,sql)
  # DButilsOracle.closeDB(pdb,dbcur)

  # if not all: return 'unknown'
  # group = all[0][0]
  # group = "GP_%s" % group.split('_')[-1]
  # return group
#_____________________________________________________
def  checkTRFvsInputDatset(trf,inputDataset) :
 error  = 0
 errtxt = ''

 # dataset = {'rome.004024.evgen.Photon_Pt_60','rome.004022.evgen.Electron_Pt_25'}
 #             mc11.004003.Electrons_e100.digit.v1100000
 # 4/5/6 fields
 # 4 : project.nnn.step.phys
 # 5 : project.nnn.phys.step.version
 # 6 : project.nnn.phys.step.format.version

 junk = inputDataset.split('.')
 l = len(inputDataset.split('.'))
 if l == 4 :
      if junk[3]=='py' : ds_input = 'py'
      else             : ds_input = junk[2]
 elif l > 4 :
      ds_input = junk[3]
      if junk[4]=='RAW' : ds_input='bstream'
      if junk[4]=='TXT' : ds_input='txtgen'
 else :
      error = 1
      errtxt = "cannot parse input dataset : %s "%inputDataset
 i = 0
 if error == 0 :
  for t in taskDef_conf.trfs['name'] :
   if t == trf :
    intype=taskDef_conf.trfs['input'][i]
    # pn: 1.1.09: Reco_trf takes it all!
    if intype!='none' and intype.find(ds_input)<-10:
      print 'TMP err=', i, intype, ds_input
      error = 1
      errtxt = "%s mismatch with %s %s" %(trf,inputDataset,ds_input)
    break
   i += 1

 return (error,errtxt)

#_____________________________________________________
def  OutputProdStep(itrf,itrfv,tag) :
  prodstep = ''
  intype   = ''
  cpu      = 0
  ram      = 0
  i        = 0
  prio     = 0
  nevo     = 0
  error    = 0
  errtxt   = ''
  k=itrf.find('unknown')
  if k>=0:
     step=itrf[k:].replace('_','.').split('.')[1]
     return (step,0,0,0,0,0,0,'')

  if tag and tag[:1]!='v':
     cache,trf,trfv,ll,vv,intype,prodstep,formats,cpu,ram,prio,nevo=getAllFromTag(tag)
     if trf==itrf:  return prodstep,intype,cpu,ram,prio,nevo,error,errtxt

  try:
     i=taskDef_conf.trfs['name'].index(itrf)
     prodstep = taskDef_conf.trfs['step'][i]
     intype   = taskDef_conf.trfs['input'][i]
     cpu      = taskDef_conf.trfs['cpu'][i]
     ram      = taskDef_conf.trfs['ram'][i]
     prio     = taskDef_conf.trfs['priority'][i]
     nevo     = taskDef_conf.trfs['nevout'][i]
  except: a=0

  if prodstep == '' :
     error = 1
     errtxt = "%s. Unknown Transformation or Version"%itrf

  return (prodstep,intype,cpu,ram,prio,nevo,error,errtxt)
#______________________________________________________________________________________      
def getUsersMails():  
   r = gmt.getTaskUsers(None,'distinct nickname,email',False)
   return dict(zip(r['header'],r['rows']))
#______________________________________________________________________________________      
def getTaskRequest(tid):  
   r = gmt.listTaskRequests(tid=tid,hours=None,select='*')
   return dict(zip(r['header'],r['rows'][0]))

#______________________________________________________________________________________      
#
#         clonetask
#______________________________________________________________________________________      
class clonetask(pmModule):

   #______________________________________________________________________________________
   def __init__(self,name=None,parent=None,obj=None):
      pmModule.__init__(self,name,parent,obj)
      self._tpattern = re.compile('([^\.]+)\.([^\.]+)\.([^\.]+)\.([^\.]+)\.(.*)')
      self._tagpattern = re.compile('(.*)_([^_]+)$')
      #                              SQL                    Web          Edit                             URL           linit    opt
      #                              [0]                    [1]            [2]                            [3]             [4]    [5]
      self._input = (
                          ('project',                    'Project',    'Project'                      ,'qProject'        ,  60, 'src')
                        , ('inputdataset',               'Input',      'Input dataset'                ,'qDSInput'        , 150, 'src')
                        , ('trf' ,                         None,       'Transformation'               ,'qTaskTRF'        ,  80, 'src')
                        , ('trfv',                         None,       'Transformation Version'       ,'qTaskTRFVersion' ,  40, 'src')
                        , ('trf_cache',                    None,       'Transformation Cache'         ,'qTRFCache'       ,  30, 'src')
                        , ('lparams',                      None,       'Transformation Parameters'    ,'qTRFParamsL'     ,1024, 'src')
                        , ('vparams',                      None,       'Values'                       ,'qTRFParamsV'     ,4000, 'src')
                        , ('total_events',               'Evnts' ,     'Total Number Of Output Events','qTaskNEvents'    ,None)
                        , ('first_inputfile_n',      'First_File',     'First File Number in Input Dataset','qDSFFile'   ,None)
                        , ('total_input_files',      'N_Files',        'Total Input Files'            ,'qDSNFiles'       ,None)
                        , ('events_per_file',        'Evt_File',       'Number Of Events for Output File' ,'qTaskFEvents',None)
                        , ('cpuperevent',            'CPU_Event',      'CPU per Event'                ,'qCPUJob'         ,None, 'src')
                        , ('memory',                  None,            'Memory Usage'                 ,'qRAMJob'         ,None)
                        , ('grid',                    'Grid',          'Grid Flavour'                 ,'qTaskGrid'       ,20 ) #
                        , ('email',                 'E_mail',          'E-mail'                       ,'qMail'           ,60  )
                     )
      self._output = (
                         ('taskname',                   'Task_Name',  'Output Task Name'             ,'qTaskName'       ,130 ) # ,'src')
                       , ('formats',                       None,     'Output Formats'                ,'qFormats'        ,256 ) # 'qDSNNN'
                       , ('priority',                   'Pri',        'Priority'                     ,'qPriority'       ,None)
                       , ('swrelease',             'Release',        'SW Release'                    ,'qSWRelease'      ,20 , 'src' )
                       , ('status',                     'State',      'State'                        ,'qStatus'         ,12  ) #  hide 
                       , ('comment_',              'Comments',       'Comments'                      ,'qDSPhLong'       ,250 )
                       
                       , ('projectmode',           'pMode',          'Project Mode'                  ,'qProjectMode'    ,250 )
                       , ('updtime',               'Mod_Time',     'Modification Time'               ,'qUpdTime'        ,None) #
                       , ('updemail',              'Modified',     'Modified by'                     ,'qUpdMail'        ,60  ) #
                       , ('total_req_jobs',       'Req_Jobs',       'Total_req_jobs'                 ,'qTotal_req_jobs' ,None, 'src')
                       , ('total_avail_jobs',       None,          'Total_avail_jobs'                 ,'qTotal_avail_jobs',None,'src') #
                       , ('phys_group',             None,          'Physics group'                   ,'qXXX'             ,20  )
                       , ('queue',                 'Queue',        'Queue'                           ,'qQueue'           ,12, 'src'  ) #
                       , ('ctag',                  "Ctag",         "Ctag"                            ,'qCtag'            ,8   )
                     #  , ('bug_report',           'Bug_report',    'Bug report'                     ,'qBug'               ) #
                     )
      #                              SQL                    Web          Edit                              URL 
                     #   ('reqid',                      'Id',         'Request Id'                   ,'qReqid'            ) # 'qTaskReqID'
                     # , ('total_done_jobs',            'Done_Jobs',  'Total_done_jobs'              ,'qTotal_done_jobs'  ) #
                     #    ('postproduction',             'post' ,      'Post Production'              , None              ) #
                     #   , ('timestamp',                  'timestamp' , 'Request Time'                 , None             ) #
                     #  , ('dsn' ,                       'dsn',        'Dataset Name'                 , None              )
                     #  , ('phys_ref',                   'phys_ref',   'phys_ref'                     , None              )
                     #  , ('prodstep',                   'step',       'step'                         , None              )
                     #  , ('prodtag',                    'tag' ,       'tag'                          , None              )
                     # , ('phys_ref',               None,          'Physics  refs'                  ,'qDSPHREF'           )
      grp = gmt.getTaskProdGroups()['rows']
      self._groups = []
      if False:
         # fetch the groups from 'ATLAS_GRISLI.t_users'
         for g in grp:
             if g[0] == None or g[0] =='': continue
             self._groups.append('GP_%s' % g[0].split('_',1)[-1])
      else:
         # ''phys_group.ATLAS_GRISLI.t_task_request'
         for g in grp:
             if g[0] == None or g[0] =='': continue
             self._groups.append(g)
      self._groups.sort()
      # Create the inverse map
      self._column = {} 
      # prepare extra params
      expars = {}
      for p in self._input:
         if p[3]!= None: 
            expars[p[3]]=None
            self._column[p[3]]= p[0]
      for p in  self._output:
         if p[3]!= None: 
            expars[p[3]]=None
            self._column[p[3]]= p[0]
      self._users = getUsersMails()
      self._config = gmt.getTaskConfig()
      proj = gmt.getProjectsAMI()
      self._projects=[p[0] for p in proj['rows']]
      self._steps=gmt.getTaskConfig()
      self._checkTask = checkTask.checkTask('checkTask',self)

      self.publishUI(self.doJson)
      self.publishUI(self.addTaskRequestStep22,alias='addTaskRequest',params=expars)

   #______________________________________________________________________________________      
   def mail(self,user):
      return self._users.get(user)
   #______________________________________________________________________________________      
   def groups(self):
      return self._groups
   #______________________________________________________________________________________      
   def parseTaskName(self, taskName):
      """ Parse taskname  """
      tn = self._tpattern.match(taskName)
      if tn:
         tags = {'all': tn.group(5) }
         ts = {    'project' : tn.group(1)
                  , 'dsn'    : tn.group(2)
                  , 'physics': tn.group(3)
                  , 'stage'  : tn.group(4)
                  , 'tags'   : tags
               }
         tagsds = self._tagpattern.match(tn.group(5))
         tags['tag'] = tagsds.group(2) if tagsds else tags['all']
         return   ts       
      else: 
         return None
   #______________________________________________________________________________________      
   def map_name(self,dbname):
      """ Map the Db name to the Web name"""
      wrong = True
      for s in  self._output: 
         p = s[0] if s[1]==None else s[1]
         if p.lower() == dbname: 
            wrong = False
            break
      if wrong: raise ValueError(" Unsupported optional column name: '%s'" % dbname)
      return s[0],p,s[2:]
         
   #______________________________________________________________________________________      
   def taskAttr(self,dbname):
      """ find the URL attribute name"""
      a = None
      for s in  self._input:
         if dbname == s[0]: 
            a = s[3]
            break
      if a == None:      
         for s in self._output:
            if dbname == s[0]: 
               a = s[3]
               break
      return a
   #______________________________________________________________________________________      
   def fixed(self,tid,task,clone=True):
      head = task['header']
      row =  task['rows'][0]
      indx = utils.name2Index(head)

      row[indx['MOD_TIME']] =  time.time()
      if clone:      
         # row[indx['STATUS']] = 'pending'
         row[indx['REQ_JOBS']] = 0
         # row[indx['TIMESTAMP']] = TIMESTAMP
         # row[indx['GRID']] = 'None'
         # u = self.server().user();
         # if u != None:
            # row[indx['COMMENTS']] += '. It is cloned from %s by %s ' % (tid,u)
      return  task  

   #______________________________________________________________________________________      
   def doJson(self,tid=1023121):
      """ 
        Clone Task
        <ui>
        <li> tid  - TaskId to be cloned
        </ul>
        See the <a href='http://pandamon.atlascloud.org/static/doc/tasks/clonetask.html'>ATLAS Dataset Nomenclature</a> for details 

      """
      ss = []
      ed = []
      for e in self._input:
            m = (e[0],e[0]) if e[1] == None else e[0:2] 
            ss.append(" %s as %s" % m)
            ed.append(e)
      for e in self._output:
            m = (e[0],e[0]) if e[1] == None else e[0:2] 
            ss.append(" %s as %s" % m)
            ed.append(e)
      select = ", ".join(ss)
      timer = Stopwatch.Stopwatch()
      q = gmt.listTaskRequests(tid=tid,hours=None,select=select)
      if len(q['rows']) == 0: raise ValueError("No TASK with TaskID=%s was found to clone" % tid) 
      upmail = self.server().email()
      if upmail==None: upmail=self.server().user()
      if upmail==None: upmail=self.server().username()
      if upmail!=None:
         modified  = utils.name2Index(q['header'],'MODIFIED');
         q['rows'][0][modified] = upmail
      main = {}
      main["method"] = 'clonetask'
      main['time'] = {'fetch' : "%s" % timer}
      main["tasks"] = self.fixed(tid,q)
      main["taskDef"] = { 'name'   : sorted(self._projects)
                         ,'jobs'   : self._config['trf'] # taskDef_conf.trfs['jobs']
                         ,'version': self._config['trfv'] #  taskDef_conf.swversion['version'] 
                         ,'groups' : self.groups()
                         ,'cache'  : self._config['cache']
                         ,'formats': self._config['formats']
                         ,'input'  : len(self._input)
                         ,'steps'  : self._steps
                         ,'priority': taskDef_conf.trfs['priority']
                       }
      main["edit"] = ed
      main['taskid']=tid

      taskhtml = """<form style='display:inline-block;' method=GET style='margin-top:0; margin:1; border:1;' 
      action='%s'><input  title='Edit this field to select another TaskId to clone'  
       type=text border=2 name=tid size=7 value=%s maxlength=7></form>""" % ( "https://pandamon.cern.ch/tasks/clonetask", tid)
      
      self.publishTitle('Clone the %(tid)s Task Request Parameters' % {'tid': taskhtml})
      self.publish(main)
      self.publish( "%s/%s" % (self.server().fileScriptURL(),"taskdef/%s.js" % 'clonetask' ),role=pmRoles.script())
      self.publish( {'s-maxage':6000,'max-age': 6000}, role=pmRoles.cache())
      self.publishNav("Cloning the <a href='http://panda.cern.ch/server/pandamon/query?overview=taskinfo&taskname=%(tid)s'>%(tid)s</a>  Task Request." % {'tid': tid })
   #______________________________________________________________________________________      
   def addTaskRequestStep22(self,edit,validated=None):
      """  edit = taskid to edit, otherwise clone 
          <br>pending the <a href='http://pandamon.atlascloud.org/static/doc/TaskValidateAPI.html'>validation API</a> implementation 
      """
      validate = not validated == "yes"
      timenow       = int(time.time())
      main = {   "tid" : edit }
      c = None
      try: 
        tid = int(edit)
        if tid < 0: 
            tid = -tid 
            edit=None
        main["tid"]=tid   
        qparams = self.extraValues()
        # qparams = self.extraValuesFilled()
        # convert qparam to takDef.py Db notation
        qpars = {}
        for q,v in qparams.iteritems(): qpars[self._column[q]] = v
        if validate:
           c = self._checkTask.newTask('add22',qpars)
        debugmode = 0
        titletxt  = ''
        email     = ''
        group     = ''
        tname     = ''
        trf       = ''
        trfv      = ''
        intype    = ''
        page      = ''
        line      = ''
        error     = 0
        ERROR     = 0
        ier       = 0
        code      = 'ok'


      # PN: let default swrel always be derived from swvers
        swvers  = qparams['qTaskTRFVersion']
        swrelo  = qparams['qSWRelease']
        swreln  = '.'.join(swvers.split('.')[0:3])
        if swrelo!=swreln:  print 'SW release set to ',swreln
        qparams['qSWRelease'] = swreln
        em = self.server().email()
        if em != None: 
           qparams['qMail']  = em
        if validate and c[0] == 0:
            (nnn,phref,intype,email,ERROR, errtxt) = addTaskChecks(qparams)
            if c[0] == 0:
              c = (ERROR,errtxt,utils.lineInfo() )
        # print utils.lineInfo(), (nnn,phref,intype,email,ERROR, errtxt)
            inputDataset  = qparams['qDSInput']
            inproj        = inputDataset.split('.')[0]
            project       = qparams['qProject']
            trf           = qparams['qTaskTRF']
            trfv          = qparams['qTaskTRFVersion']
            prodstep,intype,cpu,ram,prio,nevo,error,errtxt = OutputProdStep(trf,trfv,'')
            tversion      = taskVersion(trfv)
            email_body    = ''
            paramsL       = specCharReplace(qparams['qTRFParamsL'])
            paramsV       = qparams['qTRFParamsV']
            phlong        = specCharReplace(qparams['qDSPhLong'])
            tag = getTag(trf,paramsV,paramsL,trfv,email)
            if debugmode: print ' tag,ERROR =', tag,ERROR
           # ERROR = 0
            if tag=='unknown' :
               ERROR = 1
               errtxt  = "<font size=5> you must use an existing transformation configuration"
               errtxt += " for %s %s %s <font>" % (trf,paramsV,paramsL)
               c = (ERROR,errtxt,utils.lineInfo() )

            if ERROR != 0 :
               titletxt = "Check TASK PARAMETERS to add %s *" % code
               c = (ERROR,errtxt,utils.lineInfo() )

         #  tname = "%s.%s.%s.%s.%s"%(project,nnn,phref,prodstep,tversion)
         # new        = (trf[-3:]=='.py')

         # full_proj  = project
         # full_phref = phref
         # if new and trf.find('gen')<0 :
           # if inproj.find(project) : full_proj=project+'_'+inproj
           # else                    : full_proj=inproj
         # if intype==prodstep       : full_phref=phref+'_filtered'
         # tname = "%s.%s.%s.%s.%s"%(full_proj,nnn,full_phref,prodstep,tversion)
         # if otask : tname=otask
         # if debugmode: print 'tname=',tname

        nto = int(qparams['qTaskNEvents'])
        nvo = int(qparams['qTaskFEvents'])
        estimated   = (nto-1)/nvo+1
         # since tid>99999:
        tidtype     = '_00'
        if estimated>12000 : tidtype='_%2.2d' % ((estimated-1)/10000)
        cloned = {}
        for s in  self._input:
            cloned[s[0]] = None
        for s in self._output:
            cloned[s[0]] = None
        for s in "status,timestamp,updemail,updtime,phys_group,queue,ctag,tidtype,ppstate,pptimestamp".split(','):
           cloned[s] = None
        for s in "total_req_jobs,total_done_jobs,total_avail_jobs".split(','):
           cloned[s] = 0
        upmail = self.server().email()
        if upmail==None: upmail=self.server().user()
        if upmail==None: upmail=self.server().username()
        for nxt in cloned:
            q = self.taskAttr(nxt)
            val = None
            if q == None:
               if nxt == 'ppstate': 
                  group = qparams.get('qXXX','').upper() # checkUserGroup(email)
                  if group.find('GP_') >= 0 :
                     val = 'group'
                  elif group.find('LOCAL') >= 0 :
                     val = 'local'
                  else :
                     val = 'atlas'
               elif nxt.lower() == 'pptimestamp':             val = timenow
               elif nxt.lower() == 'status' and  edit==None:  val = 'pending'
               elif nxt.lower() == 'tidtype'   :              val = tidtype
               elif nxt.lower() == 'timestamp' :              val = timenow
               elif nxt.lower() == 'total_done_jobs':         val = 0
            else: 
               val = qparams.get(q)
               if val != None:
                  if email == '' and q == 'qMail' : val = specCharReplace(val)
                  elif q=='qFormats'              : val=val.replace(',','.')
                  elif q=='qUpdMail'              : val = '' if edit == None else upmail
                  elif q=='qStatus' and edit == None: val = 'pending'
            if val == None:
               errtxt = "Undefined %s for %s " % (q,nxt)
               c = (-11,errtxt,utils.lineInfo() )
            cloned[nxt] = val
        main["saninty"] =  c 
        if validated != None:
            main['validated'] = validated
      except:
         import traceback
         import sys
         (type, value, tback) =  sys.exc_info()
         # print utils.lineInfo(),c
         if c != None and c[0] == 0:
#            (type, value, tback) =  sys.exc_info()
            errorReport = ["error:\n -- %s < %s  > \n" % (type, value)]
            c =  ( -101,errorReport,utils.lineInfo())
         main["saninty"]  = c
         tblines = traceback.extract_tb(tback)
         report = ''
         for l in tblines:
               fname = l[0][l[0].rfind('/')+1:]
               report += "\n      %s: %s: %s: %s" % ( fname, l[1], l[2], l[3] )
         # print utils.lineInfo(),c,sys.exc_info(),report
         # validated == None
      if edit == None:
         if validated != None:
            src = getTaskRequest(tid);
            del src['REQID']
            cupper = {}
            for k,v in cloned.iteritems():
               if k != 'requid':  cupper[k.upper()]=v
            cupper['STATUS']='pending' # the cloned task is always "pending" 
            cupper['total_req_jobs'.upper()] = 0            
            src.update(cupper) 
            src['UPDTIME'] =  time.time()
            src['TIMESTAMP'] =  time.time()
            # src['GRID'] = 'none'
            u = self.server().user();
            if u != None: u = 'by %s' % u
            else: u = ''
            src['COMMENT_'] = "%s; cloned from %s %s" % (src['COMMENT_'],tid, u)
            clonedone= gwr.addTaskRequests(src)
            iReqid = utils.name2Index(clonedone['header'],'reqid')
            tid = int(clonedone['rows'][0][iReqid])
            main["tid"] = tid

         taskhtml = """<form style='display:inline-block;' method=GET style='margin-top:0; margin:1; border:1;' 
         action='%s'><input  title='Edit this field to select another TaskId to clone'  
         type=text border=2 name=tid size=7 value=%s maxlength=7></form>""" % ( "https://pandamon.cern.ch/tasks/clonetask", tid)
   
         self.publishTitle(" The new task %(tid)s has been cloned" %{'tid':taskhtml})
         self.publishNav(" The new task <a href='http://panda.cern.ch/server/pandamon/query?overview=taskinfo&taskname=%(tid)d'>%(tid)d</a> has been cloned" %{'tid': tid})
         main["action" ] = "Clone"
         if validated == 'ignored': c = 'skipped'
         main["note"]    = "Sanity check: %(c)s %(tid)s " %{'tid': tid, 'c' : c}
      else: 
         if validated != None:
            cloned['UPDTIME'] = time.time()
            clonedone= gwr.updateTaskRequests(cloned,edit)
            iReqid = utils.name2Index(clonedone['header'],'reqid')
            tid = int(clonedone['rows'][0][iReqid])
            main["tid"] = tid
            
         taskhtml = """<form style='display:inline-block;' method=GET style='margin-top:0; margin:1; border:1;' 
         action='%s'><input  title='Edit this field to select another TaskId to clone'  
         type=text border=2 name=tid size=7 value=%s maxlength=7></form>""" % ( "https://pandamon.cern.ch/tasks/clonetask", tid)
   
         self.publishTitle(" The task %(tid)s has been updated" %{'tid': taskhtml} )
         self.publishNav(" The task <a href='http://panda.cern.ch/server/pandamon/query?overview=taskinfo&taskname=%(tid)d'>%(tid)d</a> has been updated" %{'tid': tid})
         main["action"] = "Update"
         if validated == 'ignored': c = 'skipped'
         main["note"]   = "Sanity check: %(c)s %(tid)d" %{'tid': tid, 'c' : c}
      self.publish(main)
