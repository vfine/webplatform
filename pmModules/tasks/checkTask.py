# $Id;$
from  pmCore.pmModule import pmModule
from  pmTaskBuffer.pmTaskBuffer import pmgrisliaskbuffer as gmt
import monitor.taskDef_conf as taskDef_conf
import pmUtils.pmUtils as utils


class checkTask(pmModule):
   #______________________________________________________________________________________
   def __init__(self,name=None,parent=None,obj=None):
       pmModule.__init__(self,name,parent,obj)

   #______________________________________________________________________________________
   def trfTypes(self,trf,tag):
      Input=Step=Format = ''
      if tag :
       tg=tag[:1]
       id=tag[1:]
       if tg !='v':
         try:
           print utils.lineInfo(), tg
           r = gmt.getTrfTypes(tg,id)
           Input,Step,Format=r['rows'][0]
         except:
            a=0
         if Format: return Input,Step,Format
   # old:
      try: 
        i=taskDef_conf.trfs['name'].index(trf)
        Input   = taskDef_conf.trfs['input'][i]
        Step    = taskDef_conf.trfs['step'][i]
        Format  = taskDef_conf.trfs['format'][i]
      except: a=0
      return Input,Step,Format
###########################################################################
   #______________________________________________________________________________________
   def getStandard (self,input) :
   ### decode input name into base and extention ###
     if input=='none': return (0,('',''),utils.lineInfo())
       
     inps = input.split('.')
     leni = len(inps)
     if leni<4 :   return (-2,'CheckTask: input DS name too short',utils.lineInfo())      
     if leni>6 :   return (-3,'CheckTask: input DS name too long',utils.lineInfo())      
     (inp,dsn,psh,ext) = inps[0:4]
     fori = ''
     veri = ''
     if (leni==4)&(ext!='py') :
      if ('.dc2.rome.bphys'.find(inp)>0)&('.evgen.simul.digit.recon.pileup'.find(psh)>0) :
        # legacy format
        psh = inps[3]
        ext = inps[2]
      else :
       err  = 'CheckTask: Input dataset too short: %s' % input    
       return (-3,err,utils.lineInfo())       
     if leni==5 :
       veri = inps[4]
     if leni==6 :
       fori = inps[4]
       veri = inps[5]
       if fori =='RAW' : ext='bstream'
     ########### check components ##########
     check_string = ''
     for p in taskDef_conf.projects['name'] :
     #  check_string += '.%s.%s' % (p,p.upper())
     #if check_string.find(inp)<0 :
       if inp.find(p) == 0 : check_string='ok'
     if not check_string and '.DC3.CSC.M4.M5.ddmf5.ccrc08.MC8.MC9.MC10.MC11.MC12.data08.data09.data10..data11.data12.data13'.find(inp.split('_')[0])<=0 :
       err = 'CheckTask: unknown input project : %s' % inp
       return (-3,err, utils.lineInfo())

     if ext=='PhysCont' :  return (0, (dsn+'.'+psh,ext),'')
     
     fori0 = fori.split('_')[0]
     ie = '.py.evgen.simul.digit.recon.recon.pileup.txtgen.bstream.bstream.merge.daq.'.find(ext)
     if ie<0 :    return (-4,'CheckTask: unknown input type: '+ext,utils.lineInfo())
     ii = '....EVNT..HITS..RDO...AOD...ESD...RDO....TXT....RAW.....BS......HITS..RAW.'.find(fori0)
     if  ii<0 and 'HIST.NTUP.TAG.DAOD.LIST.DRAW'.find(fori0)<0:
         return (-5,'CheckTask: unknown input format %s %s'%(ext,fori),utils.lineInfo())
     if ext=='evgen' and fori0=='TXT' : ie=ii
     if ext=='merge' and fori0=='HITS': ii=ie
     if ext=='simul' and fori0=='EVNT': ii=ie  
     if (fori!='')&(ii!=ie) :
          if   ext=='recon' and fori0=='ESD'  : pass
          elif '.HIST.NTUP.TAG.LIST'.find(fori0)>0: pass
          elif ext=='merge' and fori=='AOD'   : pass
          elif ext=='merge'                   : pass
          else: return (-6,"CheckTask: input format and type mismatch : %s %s " % (ext,fori),utils.lineInfo())

     if len(veri)>1000 :                 #    PN, 13feb08: take this check out 
       if veri[0:1]!='v'                 :    return (-7,'CheckTask: wrong version format on input dataset ',utils.lineInfo())
       if len(veri)!= 9 and fori!='RAW'  :    return (-8,'CheckTask: wrong version length on input dataset',utils.lineInfo())
     return (0, (dsn+'.'+psh,ext),'')
   #______________________________________________________________________________________
   def getStep(self,transf,ext,tag) :
   ### check trans and input types ###
     trani = transf.replace('_','.').split('.')
     if len(trani)<3 :  return (-8,'CheckTask: missing fields in transformation ',utils.lineInfo())
     ptr=trani[0]
     trf=trani[1]
     # if len(trani)>3 : trf=trani[2] 
     etr=trani[-1]
     if ptr=='unknown' : return (0,trf,utils.lineInfo())
     
     #if '.csc.fdr.ctb'.find(ptr)<0 :  return (-8,"CheckTask: unknown transformation project %s" % ptr)
     if '.trf.py.'.find(etr)<0     :  return (-8,'CheckTask: wrong transformation extention',utils.lineInfo())
     (inp,st,outs) = self.trfTypes(transf,tag)
     err = ''
     if ext=='evgen' and inp[:3].lower()=='txt' : return (0,st,'')
     if inp=='none'                             : return (0,st,'')
     if ext=='recon' and inp=='ESD'             : return (0,st,'')
     if ext=='recon' and inp=='AOD'             : return (0,st,'')
     if ext=='recon' and inp=='bstream'         : return (0,st,'')
     if inp=='HIST'                             : return (0,st,'')
     if inp=='HITS'                             : return (0,st,'')
     if ext=='merge' and inp=='simul'           : return (0,st,'')
     if ext=='merge' and inp=='recon'           : return (0,st,'')
     if ext=='merge' and inp=='bstream'         : return (0,st,'')
     if ext=='merge'                            : return (0,st,'')
     if ext=='PhysCont'                         : return (0,st,'')
     if ext=='recon' and inp=='ROOT'            : return (0,st,'')
     if inp.find(ext)<0:  err = "CheckTask: transformation input %s mismatch %s" % (ext,inp)
     print utils.lineInfo(),'WWWWWWWWWWW inp=<',inp,'>WWWWWWWWWWWWWWW'
     if inp==''        :  err = "CheckTask: unknown transformation %s"           % transf
     if err!= ''       :  return (-8,err,utils.lineInfo())

   #  it = '.evgen.mcatnlo.pythia.simul.digit.recon.'.find(trf)
   #  if it<0 :                return (-8,'CheckTask: unknown transformormation type')
   #  ti = ".py....evgen...py.....evgen.simul.digit..."[it:it+5].replace('.','')
   #  if ti!=ext :             return (-8,'CheckTask: transformation input mismatch')
   #  st = ".evgen.evgen...evgen..simul.digit.recon..."[it:it+5].replace('.','')
     # exception ?
     if transf=='csc.simul.trf' : st='digit'
     return (0,st,'')
   #______________________________________________________________________________________
   def getVersion (self,swvers):
   ### convert SW version into text ###
     try:
       rr = swvers.split('.')
       vv = 'v'
       for r in rr:
         v = ('00%s' % r)[-2:]
         vv+=v
     except:
       return (-8,'CheckTask: non-numeric transformation version',utils.lineInfo())
     if len(vv)<9: return(-9,'CheckTask: transformation version is not 4-digit %s' %vv,utils.lineInfo())
    #
     return (0,vv,utils.lineInfo())
   #______________________________________________________________________________________
   def  getStat (self,inreqs):
   # check ifirst,niftot,netot,neof
   # input: reqid,first_file,total_files,nev_tot,nev_out,grid...
     try:
       k   = len(inreqs)
       if k<=0 : return (0,(0,0,0),utils.lineInfo())
       nn1 = inreqs[0]
       nt  = 0
       for i in range (0,k):  nt+=inreqs[i][3]
       neif = nn1[3]/nn1[2]
       neof = nn1[4]
       ratim= neof/neif
       # 17.05.09 in merging nt may be small...
       if (nt%neif) | ((nt%neof) and ratim<=1) :
         txt="bad evt counters nt,neif=%d %d or %d are bad" % (nt,neif,neof)
         return (-11,'CheckTask: '+txt,utils.lineInfo())
       #print " normal return ", nt,neif,neof
       return (k,(nt,neif,neof),utils.lineInfo())
     except:
       #print  'CheckTask: error decoding event counters'
       return (-11,'CheckTask: error decoding event counters',utils.lineInfo())
     print 'HERE we never are'
   #______________________________________________________________________________________
   def checkStat (self,input,task,requp) :
    sdeb = 0
    dot  = '.'
    if sdeb: print '=> in check stat: input, task,requp=',input,task,requp
    inpus=input
    ii=input.split('.')
    if len(ii)==6 : inpus=dot.join(ii[:4])+dot+ii[5]
    inpud=inpus
    # proj=ii[0]
    # the list of mc project has to contain mc1X,csc1X or valid... or more later
    # if proj.find('mc')>=0 or proj.find('csc')>=0 or proj.find('valid')>=0 :
      # if '.mc11.mc12.csc11.'.find(ii[0])>0:
    inpud=inpus.replace('simul','digit')
    
    if sdeb : print 'MY TMP input,inpus,task=',input,inpus,inpud,task
    err=''
    try :
   #if 2>1:
      #       0         1                2                  3            4          5       6           7       8       9  
      list='reqid,first_inputfile_n,total_input_files,total_events,events_per_file,grid,inputdataset,inputdataset,taskname,lparams,timestamp'
      r = gmt.checkTaskRequests(inpus,inpud) 
      inreqs = r['rows']
      utask  = task
      if requp>0 :
         utask = gmt.listTaskRequests(tid=requp,select='taskname',hours=None)
         utask =utask['rows'][0][0]
      stasks = gmt.listTaskRequests(taskname=utask,select=list,hours=None)
      stasks = stasks['rows']
      if sdeb: print "------------------------------"
      if sdeb: print 'qri=','inreqs',inreqs
      if sdeb: print 'qry=','stasks',stasks
 
      # 12.05.09: verify that the input chain is complete:
      if sdeb: print "CHECKSTAT inp:"
      idone=1; nperf=0; err=''; faulty=''
      hdr = [h.lower() for h in r['header']];
      for inrr in inreqs:
        inr = dict(zip(hdr,inrr))
        if sdeb :           print "            ",inr
        if sdeb :           print "++++++++++++++++++++++++++++++"
        if sdeb :           print utils.lineInfo(), inr," <<<<<<<<<<<<<<<" 
        if inr['taskname']!=inpus and inr['taskname']!=inpud:
           if sdeb: print utils.lineInfo(), inr," <<<<<<<<<<<<<<<" 
           return (-8,'does not match existing '+inr['taskname'],utils.lineInfo())
        try:
          ii1=int(inr['first_inputfile_n'])
          nn1=int(inr['total_input_files'])
          npf=int(inr['events_per_file'])
          if ii1!=idone:           err="input non-consequitive: 1st input file %s != %s " %(ii1,idone)
          if nperf and nperf!=npf: err="illegal input file length events_per_file(%s)!=0 " % ( npf)
          nperf =npf       
          idone+=nn1
        except:
          err='input fault'
        if err:
          if sdeb :           print utils.lineInfo(),"++++++++++++++++++++++++++++++"
          if sdeb :           print utils.lineInfo(),inr
          faulty="%s" % [inr]
          if sdeb :           print utils.lineInfo(),">>>>>>>>>>>>>>>>>>"
          return(-8,err+':'+faulty[2:-2],utils.lineInfo())
        
      # 12.05.09: verify that the output chain is legal:
      if sdeb: print "CHECKSTAT out:"
      idone=1; nperf=0; err=''; faulty=''
      vlist = list.split(',')
      for tsks in stasks:
        tsk = dict(zip(vlist,tsks))
        if sdeb:  print "            ",tsk
        if tsk['taskname']!=utask :  return (-8,'does not match existing '+tsk['taskname'],utils.lineInfo())
        try: 
          ii1=int(tsk['first_inputfile_n'])
          nn1=int(tsk['total_input_files'])
          npf=int(tsk['events_per_file'])
          if ii1!=idone:           err="input non-consequitive: 1st input file %s != %s " %(ii1,idone)
          if nperf and nperf!=npf: err="illegal input file length events_per_file(%s)!=0 " % ( npf)
          
          nperf =npf       
          idone+=nn1
        except:
          err='output fault'
        if err:
          faulty="%s" % [tsk]
          return(-8,err+':'+faulty[2:120],utils.lineInfo())

    except:
      return (-9,'CheckTask: can not verify existing requests, try later'+err,utils.lineInfo())
    # only last request of the same task can be updated
    ks = len(stasks)
    if requp>0 :
      if sdeb: print 'MY TMP1: ', ks,stasks
      if ks>0: 
        if stasks[-1]['reqid']==requp :
          stasks=stasks[0:-1]
          # print "output list shorted"
        else :
          err = 'Other requests have been later made for the same task. '
          err+= 'Only the last request of the same task can be updated. '
          return (-9,'CheckTask: ' + err,utils.lineInfo()) 
         
   # return stati/o = Ntot events, Nev per input file, Nev per output file
    (code,stati,el) = self.getStat(inreqs)
    if code<0: return (code,stati,el)
    # fake file splitting
    (n1,n2,npf) = stati
    step=task.split(dot)[3]
    if npf>=1000000 and step.find('gen')<=0 : stati=(n1,n2,5000)
    if code>0 and sdeb:
      print 'Input task',inreqs,' was requested ',code,' times, stati=',stati
    npfi=npf
    (code,stato,el) = self.getStat(stasks)
    if code<0: return (code,stato,el)
    # fake file splitting
    inpu   = ''
    inpold = inpus
    (n1,n2,npf) = stato
    if sdeb: print utils.lineInfo(),'WWW',ks,stasks,len(stasks),stato,"WWWWWWWWW"
    if ks>0 and stasks:
      stsk = dict(zip(vlist,stasks[0]))
      inpold=stsk['inputdataset']
      inpu=inpold[-3:]
      parold=stsk['inputdataset']

    if sdeb: print utils.lineInfo(),"-----------------"
    if sdeb: print utils.lineInfo(),n2,inpu,step,stato
    if sdeb: print utils.lineInfo(),npfi
    if n2>=1000000 and inpu!='.py' and step.find('gen')<=0 : stato=(n1,5000,npf)
    if npfi>=1000000 and stato==(0,0,0) and step.find('gen')>0: stato=(0,0,npfi) 

    if sdeb: print 'stato=',stato
    if code>0 and sdeb:
      print 'Same task was already requested ',code,' times, stat=',stato
    inpolt=inpold.replace('s___imul','digit')
    inpp=inpolt.split(dot)
    if len(inpp)==6: inpolt=dot.join(inpp[:4])+dot+inpp[5]
    if sdeb:  print ' inputs found ',inpold,inpolt

    if inpolt!=inpus:
      if sdeb:  print 'INCONSISTENT INPUTS',inpolt,input,inpus
      return (-77,"used with "+inpold,utils.lineInfo())
    allstat = [stati,stato,inreqs,stasks]
    if sdeb: print "CHECK STAT OK"
    return (0,allstat,'')
    
   #______________________________________________________________________________________
   def newTask(self,key,qpars,allpars='') :
   # first decoding only
    mdeb = 0
    dot  = '.'
    key1 = key[0:1]
    l0   = len(qpars)
    if mdeb != 0 :
     print 'INSIDE CheckTaskPave NewTask',key1,l0
     print 'QPARS=',qpars
    types = {'py':'', 'evgen':'EVNT', 'simul':'HITS', 'digit':'RDO', 'recon':'AOD'}
    if (key1=='a')|(key1=='u') :     ##### add or update task request #####
      pass
   #### new task request #####
    project = qpars['project']
    input   = qpars['inputdataset']
    task    = qpars['taskname']
    transf  = qpars['trf']
    swvers  = qpars['trfv']
    swrel   = qpars['swrelease']
    mail    = qpars['email']
    cpu     = qpars['cpuperevent']
    mem     = qpars['memory']
    forms   = qpars['formats']
    ifirst  = int(qpars['first_inputfile_n'])
    niftot  = int(qpars['total_input_files'])
    netots  = ("%s" % qpars.get('total_events','')).split(' ')
    netot   = int(netots[0])
    neflt   = int(qpars.get('total_f_events',0))
    neof    = int(qpars.get('events_per_file',0))
    grid    = qpars['grid']
    prio    = qpars['priority']
    cache   = qpars['trf_cache']
    comment = qpars['comment_']
    inbase  = ''
    jobconfig = ''
    plist   = qpars['vparams']
   # for one in plist.split(','):
       # if one.lower()=='input file base': inbase = qpars[iii]
   # if l0>20:
    # VF to be tested yet. inbase  = qpars[20]   # first trf parameter infact
     # plist   = allpars.get('pList',''); iii = 20
     # for one in plist.split(','):
       # if one.lower()=='input file base': inbase = qpars[iii]
       # iii+= 1
    pnames  = qpars['lparams']
    plist   = qpars['vparams']
    status  = qpars['status']
    update  = qpars['updtime']
    modiby  = qpars['updemail']
    projmode= qpars['projectmode']
    reqid   = qpars.get('reqid','')
    ########### decode input dataset ##########
    ttt=task.split(dot)
    tag=ttt[-1].split('_')[-1]
    if mdeb : print 'CTPAVE tag=',tag
    
    ### check input, trans and version syntax ###
    inproj = input.split(dot)[0]
    (code,stand,el) = self.getStandard(input)
    if mdeb : print "gotStandard=",code,stand
    if code : return (code,stand,el)
    (base,ext)   = stand
    (code,step,el)  = self.getStep(transf,ext,tag)
    if mdeb : print "gotStep=",code,step,el
    if code : return (code,step,el)
    for swvers1 in swvers.split(','): (code,vers,el)  = self.getVersion(swvers1)
    if mdeb : print "gotVersion=",code,vers
    if code : return (code,vers,el)

    ctag=''
    if task:
       ctag=task.split('.')[4]
       if ctag[:1]=='v' : ctag=''
    if mdeb: print ' task,ctag=', task,ctag   

   # check special case of external input files:
    nn=''
    if step=='evgen' and pnames+inbase and input[-3:]=='.py':
      if mdeb: print '????? pn=',pnames,'inb=',inbase
      dsn=input.split(dot)[1]
      try:
        if pnames:
          pna=pnames.split(',');
          for i in range(len(pna)):
            if mdeb: print 'pna=',i,pna[i]
            if pna[i].lower().find('input file')>=0 : inbase=plist.split(',')[i]
            if pna[i].lower().find('jobconfig')>=0  : jobconfig=plist.split(',')[i]
        if inbase:     nn=inbase.split(dot)[1]
        if jobconfig:  nn=jobconfig.split(dot)[1]
      except: nn=''
      
    if transf.find('modgen')>0 and nn:
      if inbase:    base=dot.join(inbase.split(dot)[1:3])
      if jobconfig: base=dot.join(jobconfig.split(dot)[1:3])
      # print "NEW BASE",base
             
    if ctag:
      mytask  = '.'.join((project,base,step,ctag))
      myshort = '.'.join((base,step,ctag))
    else:
      mytask  = '.'.join((project,base,step,vers))
      myshort = '.'.join((base,step,vers))      

    mytaska = '.'.join((inproj,base,step,vers))
    if inproj.find(project):  mytaskb = '.'.join((project+'_'+inproj,base,step,vers))
    else:                     mytaskb = '.'.join((inproj,base,step,vers))

    otask = task
    if task==''     :
         new        = (transf[-3:]=='.py')
         full_proj  = project
         #full_phref = phref
         if new and transf.find('evgen')<0 and transf.find('modgen')<0 : ttask=mytaskb
         else : ttask=mytask
    else            :
         #ttask=task.replace('_filtered','')
         ttask=task
    if transf.find('modgen')>0     : ttask=mytaska; otask=mytaska
    # if transf.find('Reco_trf')>=0: ttask=mytaska; otask=mytaska
    # if transf.find('atlfast')>0  : ttask=mytaska; otask=mytaska
    if mdeb: print utils.lineInfo(),'task=',task,'mytask=',mytask,'a=',mytaska,'b=',mytaskb,'t=',ttask
    ttshort='.'.join(ttask.split('.')[1:])
    #if ttask!=mytask and ttask!=mytaska and ttask!=mytaskb :
    if ttshort!=myshort and transf.find('Reco_trf')<0:
         err = "Checktask: WRONG task naming %s %s" % (task,mytask)
         return (-8, err,utils.lineInfo())

    requp = 0
    if key1=='u'   : requp=reqid
    if mdeb:  print utils.lineInfo(),'checkStat for requp=',requp
    (code,allstat,el) = self.checkStat (input,ttask,requp)
    if code !=0    : return (code,allstat,el)
    if requp>0 and status=='aborted' :
      otask = gmt.listTaskRequests(tid=requp,select='taskname',hours=None)
      return (0,'ok',otask['rows'][0][0])
    
    # event number check

    try:
      (netotin,neifin,neofin) = allstat[0]     # inputs statistics
      (netot1, neif1, neof1)  = allstat[1]     # outputs statistics
      inreqs                  = allstat[2]     # inputs: reqid,first_file,tot_file,nev_tot,nev_out,grid
      if netot1==0: 
        neif1 = netot/niftot
        neof1 = neof
      netot2=netot1+netot                      # new outputs
   #   if ((netot%neif1) | (netot%neof1)) and transf.find('HIST')<0:
      if ((netot%neif1) | (netot%neof1)) and neof1<=neif1:
        err = "Bad Total Number of Events %d. Inconsistent with events per input %d and output %d" \
            % (netot,neif1,neof1)
        return (-9,'CheckTask: ' + err,utils.lineInfo())
    except:
      err="requested event counters are illegal %d %d %d %d " % (ifirst,niftot,netot,neof)
      return (-9,'CheckTask: ' + err,utils.lineInfo())

    intype=input.split('.')[-1]
    rawtype=(input.find('RAW')>0) 
    if mdeb: print 'YYY outputs: netot1,neif1,neof1=',netot1,neif1,neof1
    if intype!='py' and not rawtype and \
       input[-12:]!='evgen.TXT.e4' and input[-13:]!='evgen.EVNT.e4' \
       and input[-7:]!='.o3_f47' and input[-7:]!='.o3_f48' \
       and input.find('.ESD.f')<0 and input.find('merge.AOD.f')<0 and input.find('LIST')<0 :
      if netot2>netotin:
        if netotin==0 :
          err = 'Input does not exist. Please check input components for %s '%input
        else:
          err = "Not enouph input events. Requested total is %d, existing input is %d" % (netot2,netotin)
        return (-9,'CheckTask: ' + err,utils.lineInfo())
      if neofin!=neif1 :
        if neofin> neif1 and len(netots)>1 and netots[1]=='only' :
          print "inputs statistics  netotin,neifin,neofin=", allstat[0]     
          print "outputs statistics netot1, neif1, neof1 =", allstat[1]    
          print "inputs: reqid,first_file,tot_file,nev_tot,nev_out,grid=", allstat[2]   
          print "neofin,neif1=",neofin,neif1
   #       return (-9,'test','')      
        elif input.find('merge')<0:
          err  = "This Total_Input_Files and Total_Number_of_Events requires"
          err += " events_per_input_file (%d) inconsistent with input task value (%d), inp=%s" % (neif1,neofin,input)
          return (-9,'CheckTask: ' + err,utils.lineInfo())

    nif1 = netot1/neif1+1
    nif2 = netot2/neif1
    nof1 = netot1/neof1+1
    nof2 = netot2/neof1
    nif  = nif2-nif1+1

    if step=='evgen' and pnames+inbase :
      if nn and nif2!=nof2:
        err = "evgen jobs with external input requre 1:1 inputs instead of %s:%s " % (nif2,nof2)
        return (-9,'CheckTask: ' + err,utils.lineInfo())

   #  check dsn in inputs and jobopts
      if nn and nn!=dsn  and transf.find('modgen')<0 and key1!='u'  and nif1<=1:
        err = "dataset number in input files (%s) should match the number in joboptions %s"%(nn,input)
        return (-9,'CheckTask: ' + err,utils.lineInfo())

    if (ifirst>0)&(ifirst!=nif1) :
      err = "This Task already exists. To enlarge it, First_Input_File should be requested as %d instead of %d"%(nif1,ifirst)
      return (-9,'CheckTask: ' + err,utils.lineInfo())
    if niftot!=nif:
      err = "For Total_Number_of_Events=%d corresponding Total_Input_Files should be requested as %d"%(netot,nif)
      return (-9,'CheckTask: ' + err,utils.lineInfo())
    if mdeb: print 'CHECK PAVE XXXXXX',transf,nof2,nif2,otask
    if transf.find('merge')>0 and  2*nof2>nif2 :
      err = " Merging job has to read more then one input file per job, actially it is %s:%s " % (nif2,nof2)     
      return (-9,'CheckTask: ' + err,utils.lineInfo())
    if mdeb: print 'ALL OKAY' ,' nni=',nif1,nif2,' nno=',nof1,nof2
    tt = 0
    gg = ''
    if mdeb: print 'netot1,netot2=',netot1,netot2
    for inreq in inreqs:
      if mdeb: print 'inreq=',inreq
      (iq,f1,nf,te,oe,gr,in1,vpar,tna,lpar) = inreq
      if mdeb: print tt,tt+te,gr
      t1=tt; tt+=te
      if tt<=netot1 : continue
      if t1>=netot2 : continue
   #  if gr.replace('-dq','')!=grid.replace('-dq','')   : gg+=gr+','
      if gr[:3] != grid[:3]  : gg+=gr+','
    if gg and grid!='panda' and key1!='u' and step!='simul' :
      err = " Task defined for %s requires cross-grid data movement from %s " % (grid,gg[:-1])
      return (-9,err,utils.lineInfo())

    return (0,'ok',otask)
