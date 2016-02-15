# $Id$
# Author: Valeri Fine (fine@bnl.gov) Sept 22, 2011
from pmCore.pmModule import pmModule 
import pmUtils.pmUtils as utils
from pmCore.pmModule import pmRoles



#______________________________________________________________________________________      
class menu(pmModule):
   """ Create the left pane menu """

   #______________________________________________________________________________________      
   def __init__(self,name=None,parent=None,obj=None):
      pmModule.__init__(self,name,parent,obj)

#______________________________________________________________________________________      
   def leftMenu(self):
      return self.leftMenuOpen() + self.leftMenuOld() + self.leftMenuNew() +self.leftMenuClose() +self.leftMenuScript()
#______________________________________________________________________________________      
   def leftMenuOpen(self):
      """ Build left menu bar of monitor """
      return utils.openAccordion("pandaLeftMenuId")
#______________________________________________________________________________________      
   def leftMenuJedi(self):
      version = self.server().version().get('version')
      if version == None: version = ''
      else: version = "/~%s" % version

      try:
         classicUrl=self.config().config.classic['url']
      except:
         classicUrl = "http://panda.cern.ch"
      indent = "<div style='padding-top:5px;'></div>"
      htmlstr = ''   
      # htmlstr += "<table class='ui-corner-top ui-widget ui-widget-header' width='100%'><thead><tr><th align=left>" +"Classic PanDA"+ "</th></tr></thead></table>";
      divStyle = "<div style='font-size:8pt;'>"
      gap = "<tr><td width='5px'></td>"
      jeditaskheader = "Jedi Tasks"
      jeditaskhtml  = "<p><b>&nbsp;Summary:</b>"
      jeditaskhtml  += "<table style='padding:0px;margin:0px;'>" 
      jeditaskhtml +=gap
      jeditaskhtml += "<td style='font-size:8pt;'><a href='%(version)s/jedi/taskinfo?tasktype=*&limit=2000&days=20'>All Tasks</a></td>" % { 'version': version  }
      jeditaskhtml += "<td style='font-size:8pt;'><a href='%(url)s%(version)s/jedi/taskinfo?tasktype=analysis&username=auto&hours=24'>My Tasks</a></td>" % { 'version': version.replace("http:","https:") ,"url" : self.server().host().replace('http:','https:')}      
      jeditaskhtml += "</tr>"
      jeditaskhtml += "</tr></table>"
      jeditaskhtml += "<b>&nbsp;States:</b><table style='padding:0px;margin:0px;'>" 
      for i,s in enumerate(utils.jediTaskStates):
         if i%2==0: jeditaskhtml += gap
         jeditaskhtml += "<td style='font-size:8pt;'><a href='%(version)s/jedi/taskinfo?status=%(state)s&days=20'>%(state)s</a></td>" % { 'version': version, 'url': classicUrl,'state': s }
         if i%2 ==1: jeditaskhtml += "</tr>\n"
         
      jeditaskhtml += "</table>"

      htmlstr += utils.addAccordion(jeditaskheader, jeditaskhtml)
      return htmlstr
#______________________________________________________________________________________      
   def leftMenuFax(self):
      version = self.server().version().get('version')
      if version == None: version = ''
      else: version = "/~%s" % version

      indent = "<div style='padding-top:5px;'></div>"
      htmlstr = ''   
      # htmlstr += "<table class='ui-corner-top ui-widget ui-widget-header' width='100%'><thead><tr><th align=left>" +"Classic PanDA"+ "</th></tr></thead></table>";
      divStyle = "<div style='font-size:8pt;'>"
      gap = "<tr><td width='5px'></td>"
      faxheader = "FAX"
      faxhtml  = "<p><b>&nbsp;Summary:</b>"
      faxhtml  += "<table style='padding:0px;margin:0px;'>" 
      faxhtml +=gap
      faxhtml += "<td style='font-size:8pt;'><a href='%(version)s/fax/failover?hours=20'>Fail over</a></td>" % { 'version': version  }
      faxhtml += "</tr>"
      faxhtml +=gap
      faxhtml += "<td style='font-size:8pt;'><a href='%(version)s/fax/map'>Configuration</a></td>" % { 'version': version  }
      faxhtml += "</tr>"
      faxhtml += "</table>"
      htmlstr += utils.addAccordion(faxheader, faxhtml)
      return htmlstr


#______________________________________________________________________________________      
   def leftMenuJobTypes(self):
      version = self.server().version().get('version')
      if version == None: version = ''
      else: version = "/~%s" % version
      types = "analysis production prod_test install test retried jedi merging all".split()
      htmlstr = ''   
      divStyle = "<div style='font-size:8pt;'>"
      gap = "<tr><td width='5px'></td>"
      jobheader = "Job Types"
      jobhtml  = "<p><b>&nbsp;Types:</b>"
      jobhtml += "<table>"
      for i,t in enumerate(types):
         if i%2==0: jobhtml += gap
         jobhtml += "<td style='font-size:8pt;'>"
         if t == 'retried':
            jobhtml += "<a href='%(version)s/jobinfo?jobtype=&jobStatus=%(state)s&plot=no'>%(state)s</a></td>" % { 'version': version,'state': t }
         elif t == 'merging':
            jobhtml += "<a href='%(version)s/jobinfo?jobtype=&processingType=usermerge&hours=3&plot=no'>%(state)s</a></td>" % { 'version': version, 'state': t }
         elif t == 'all':
            jobhtml += "<a href='%(version)s/jobinfo?jobtype=&hours=3&plot=no'>%(state)s</a>&nbsp;&nbsp;</td>" %  { 'version': version, 'state' : t }
         else:
            jobhtml += "<a href='%(version)s/jobinfo?jobtype=%(state)s&hours=3&plot=no'>%(state)s</a>&nbsp;&nbsp;</td>" %  { 'version': version, 'state' : t }
         if i%2 ==1: jobhtml += "</tr>\n"
      jobhtml += "</table>"
      htmlstr += utils.addAccordion(jobheader, jobhtml)
      return htmlstr
#______________________________________________________________________________________      
   def leftMenuJobMetrics (self):
      version = self.server().version().get('version')
      if version == None: version = ''
      else: version = "/~%s" % version
      types = "analysis production prod_test jedi all".split()
      indent = "<div style='padding-top:5px;'></div>"
      htmlstr = ''   
      divStyle = "<div style='font-size:8pt;'>"
      gap = "<tr><td width='5px'></td>"
      jobheader = "Jobs' Metrics"
      jobhtml  = "<p><b>&nbsp;"
      jobhtml  += '<a title="Q:What are the jobMetrics?" href="https://twiki.cern.ch/twiki/bin/viewauth/AtlasComputing/PandaPilot#QaJobMetrics">'
      jobhtml  += "VM Metrics:</a></b>"
      jobhtml +='<table>'
      for i,t in enumerate(types):
         if i%2==0: jobhtml += gap
         jobhtml += "<td style='font-size:8pt;'>"
         if t == 'retried':
            jobhtml += "<a href='%(version)s/jobs/jobram?jobtype=&jobStatus=%(state)s'>%(state)s</a></td>" % { 'version': version, 'state': t }
         elif t == 'merging':
            jobhtml += "<a href='%(version)s/jobs/jobram?jobtype=&processingType=usermerge&hours=3'>%(state)s</a></td>" % { 'version': version,'state': t }
         elif t == 'all':
            jobhtml += "<a href='%(version)s/jobs/jobram?jobtype=&hours=3'>%(state)s</a>&nbsp;&nbsp;</td>" %  { 'version': version, 'state' : t }
         else:
            jobhtml += "<a href='%(version)s/jobs/jobram?jobtype=%(state)s&hours=3'>%(state)s</a>&nbsp;&nbsp;</td>" %  { 'version': version, 'state' : t }
         if i%2 ==1: jobhtml += "</tr>\n"
      jobhtml += "</table>"
      htmlstr += utils.addAccordion(jobheader, jobhtml)
      return htmlstr

#______________________________________________________________________________________      
   def leftMenuJobTiming (self):
      version = self.server().version().get('version')
      if version == None: version = ''
      else: version = "/~%s" % version
      types = "analysis production prod_test test jedi all".split()
      indent = "<div style='padding-top:5px;'></div>"
      htmlstr = ''   
      divStyle = "<div style='font-size:8pt;'>"
      gap = "<tr><td width='5px'></td>"
      jobheader = "Jobs' Timing"
      jobhtml  = "<p>&nbsp;"
      jobhtml  += '<a title="Q:Which are the timings in pilotTiming?" href="https://twiki.cern.ch/twiki/bin/viewauth/AtlasComputing/PandaPilot#QaPilotTiming">'
      jobhtml  += '<b>Timing:<b></a>'
      jobhtml +='<table>'
      for i,t in enumerate(types):
         if i%2==0: jobhtml += gap
         jobhtml += "<td style='font-size:8pt;'>"
         if t == 'retried':
            jobhtml += "<a href='%(version)s/jobs/jobtiming?jobtype=&jobStatus=%(state)s'>%(state)s</a></td>" % { 'version': version, 'state': t }
         elif t == 'merging':
            jobhtml += "<a href='%(version)s/jobs/jobtiming?jobtype=&processingType=usermerge&hours=3'>%(state)s</a></td>" % { 'version': version,'state': t }
         elif t == 'all':
            jobhtml += "<a href='%(version)s/jobs/jobtiming?jobtype=&hours=3'>%(state)s</a>&nbsp;&nbsp;</td>" %  { 'version': version, 'state' : t }
         else:
            jobhtml += "<a href='%(version)s/jobs/jobtiming?jobtype=%(state)s&hours=3'>%(state)s</a>&nbsp;&nbsp;</td>" %  { 'version': version, 'state' : t }
         if i%2 ==1: jobhtml += "</tr>\n"
      jobhtml += "</table>"
      htmlstr += utils.addAccordion(jobheader, jobhtml)
      return htmlstr
#______________________________________________________________________________________      
   def leftMenuOld(self):
      version = self.server().version().get('version')
      if version == None: version = ''
      else: version = "/~%s" % version

      try:
         classicUrl=self.config().config.classic['url']
      except:
         classicUrl = "http://panda.cern.ch"
      indent = "<div style='padding-top:5px;'></div>"
      htmlstr = ''   
      # htmlstr += "<table class='ui-corner-top ui-widget ui-widget-header' width='100%'><thead><tr><th align=left>" +"Classic PanDA"+ "</th></tr></thead></table>";
      divStyle = "<div style='font-size:8pt;'>"
      gap = "<tr><td width='5px'></td>"
      jobheader = "Jobs"
      jobhtml  = "<p><b>&nbsp;Summary:</b>"
      jobhtml  += "<table style='padding:0px;margin:0px;'>" 
      jobhtml +=gap
      jobhtml += "<td style='font-size:8pt;'><a href='%(version)s/jobinfo?jobtype=*&limit=150'>All Jobs</a></td>" % { 'version': version  }
      jobhtml += "<td style='font-size:8pt;'><a href='%(version)s/jobinfo?jobtype=analysis&VO=cms&limit=150'>CMS Jobs</a></td>" % { 'version': version  }
      jobhtml += "</tr>"
      jobhtml +=gap
      jobhtml += "<td style='font-size:8pt;'><a href='%(url)s%(version)s/jobinfo?jobtype=analysis&prodUserName=auto&hours=24'>My Jobs</a></td>" % { 'version': version.replace("http:","https:") ,"url" : self.server().host().replace('http:','https:')}      
      jobhtml += "<td style='font-size:8pt;'><a href='%(version)s/jobinfo?jobtype=*&VO=atlas&limit=150'>ATLAS Jobs</a></td>" % { 'version': version  }
      jobhtml += "</tr>"
#      jobhtml +=gap
#      jobhtml += "<td style='font-size:8pt;'><a href='%(url)s%(version)s/jobinfo?jobtype=analysis&JediTaskID=nonull&hours=24'>Jedi Jobs</a></td>" % { 'version': version.replace("http:","https:") ,"url" : self.server().host().replace('http:','https:')}      
#      jobhtml += "</tr>"
      jobhtml +=gap
      jobhtml += "<td style='font-size:8pt;' colspan='2'><b>Clouds' Summary:</b></td>" % { 'version': version , "t":'jedi' }
      jobhtml +=gap
      jobhtml += "<td style='font-size:8pt;'><a href='%(version)s/cloudsummary?jobtype=%(t)s'>%(t)s</a></td>" % { 'version': version , "t":'analysis' }
      jobhtml += "<td style='font-size:8pt;'><a href='%(version)s/cloudsummary?jobtype=%(t)s'>%(t)s</a></td>" % { 'version': version , "t":'production,test'}
      jobhtml += "</tr>"
      jobhtml +=gap
      jobhtml += "<td style='font-size:8pt;'><a href='%(version)s/cloudsummary?jobtype=%(t)s&hours=72'>%(t)s</a></td>" % { 'version': version , "t":'jedi' }
      jobhtml += "<td style='font-size:8pt;'><a href='%(version)s/cloudsummary?jobtype=&hours=72'>%(t)s</a></td>" % { 'version': version , "t":'all' }
      jobhtml += "</tr>"
      jobhtml +=gap
      jobhtml += "<td style='font-size:8pt;' colspan='2'><b>Regions' Summary:</b></td>"
      jobhtml +=gap
      jobhtml += "<td style='font-size:8pt;'><a href='%(version)s/cloudsummary?jobtype=%(t)s&region=yes'>%(t)s</a></td>" % { 'version': version , "t":'analysis' }
      jobhtml += "<td style='font-size:8pt;'><a href='%(version)s/cloudsummary?jobtype=%(t)s&region=yes'>%(t)s</a></td>" % { 'version': version , "t":'production,test'}
      jobhtml += "</tr>"
      jobhtml +=gap
      jobhtml += "<td style='font-size:8pt;'><a href='%(version)s/cloudsummary?jobtype=%(t)s&hours=72&region=yes'>%(t)s</a></td>" % { 'version': version , "t":'jedi' }
      jobhtml += "<td style='font-size:8pt;'><a href='%(version)s/cloudsummary?jobtype=&hours=72&region=yes'>%(t)s</a></td>" % { 'version': version , "t":'all' }
      jobhtml += "</tr>"
      jobhtml +="</table>"
      jobhtml += "<b>&nbsp;States:</b><table style='padding:0px;margin:0px;'>" 
      for i,s in enumerate(utils.jobStates + ('unassigned',)):
         if i%2==0: jobhtml += gap
         if s == 'unassigned':
            pars = 'cancelled&computingSite=NULL&limit=150'
            jobhtml += "<td style='font-size:8pt;'><a href='%(version)s/jobinfo?jobStatus=%(pars)s&plot=no'>%(state)s</a></td>" % { 'version': version, 'url': classicUrl,'state': s ,'pars':pars}
         else:
            jobhtml += "<td style='font-size:8pt;'><a href='%(version)s/jobinfo?jobStatus=%(state)s&plot=no'>%(state)s</a></td>" % { 'version': version, 'url': classicUrl,'state': s }
         if i%2 ==1: jobhtml += "</tr>\n"
         
      jobhtml += "</table>"

      button={ "href" : '%s?mode=jobquery' % classicUrl
             , "html" : "&bull;&nbsp;Search"
             , "title" : "Attention: &quot;Long query&quot;! Show &quot;Search job&quot; dialog" }

      htmlstr += utils.addAccordion(jobheader, jobhtml,button=button)
      # ---------------------- JOB types -------------------------------
      htmlstr += self.leftMenuJobTypes()
      # ---------------------- JOB timing -------------------------------
      htmlstr += self.leftMenuJobTiming()
     # ---------------------- JOB metrics -------------------------------
      htmlstr += self.leftMenuJobMetrics()
      # ---------------------- JEDI -------------------------------
      htmlstr += self.leftMenuJedi()
      # ---------------------- FAX  -------------------------------
      htmlstr += self.leftMenuFax()

      # ---------------------- Quick search  -------------------------------
      qsearchheader = "Quick Search"
      qsearchhtml = indent
      qsearchhtml += "<form method=GET style='margin-top:0; margin:0; border:0; font-size:8pt;  font-weight:normal;' \
      action='%(version)s/%(module)s'>&nbsp;Panda jobID <input  title='Please fill out this field' style='margin-top:0; margin:0; \
      border:1; font-size:8pt;' type=text border=0 name=job size=5 maxlength=100></form>" %  { 'version': version , 'module' : 'jobinfo' }
      
      qsearchhtml += "<hr>"
      
      qsearchhtml += "<form method=GET style='margin-top:0; margin:0; border:0; font-size:8pt; font-weight:normal;' \
      action='%(version)s/%(module)s'>&nbsp;Batch ID <input  title='Please fill out this field' style='margin-top:0; margin:0; border:1; font-size:8pt;' \
      type=text border=0 name='batchID' size=8 maxlength=200></form>" %  { 'version': version , 'module' : 'jobinfo'}

      qsearchhtml += "<form id='formdsid' method=GET style='margin-top:0; margin:0; border:0; font-size:8pt;' \
      action='%s'>&nbsp;Dataset <input title='Please fill out this field' id=informdsid style='margin-top:0; margin:0; border:1; font-size:8pt;' \
      type=text border=0 name=name size=9 maxlength=200><input type=hidden name=mode \
      value=dset></form>" % classicUrl

      qsearchhtml += "<form method=GET style='margin-top:0; margin:0; border:0; font-size:8pt;' \
      action='%s'>&nbsp;Task&nbsp;request&nbsp;<input title='Please fill out this field' style='margin-top:0; margin:0; border:1; \
      font-size:8pt;' type=text border=0 name=qTID size=5 maxlength=100><input type=hidden \
      name=mode value=taskquery><input type=hidden name=qsubmit value=QuerySubmit></form>" % classicUrl

      qsearchhtml += "<form method=GET style='margin-top:0; margin:0; border:0; font-size:8pt;' \
      action='%s'>&nbsp;Task&nbsp;status&nbsp;<input  title='Please fill out this field' style='margin-top:0; margin:0; border:1; \
      font-size:8pt;' type=text border=0 name=taskname size=6 maxlength=100><input type=hidden \
      name=overview value=taskinfo></form>" % classicUrl

      qsearchhtml += "<form method=GET style='margin-top:0; margin:0; border:0; font-size:8pt;' \
      action='%s'>&nbsp;File <input  title='Please fill out this field' style='margin-top:0; margin:0; border:1; font-size:8pt;' \
      type=text border=0 name=lfn size=13 maxlength=200><input type=hidden name=overview \
      value=findfile><input type=hidden name=archive value=yes></form>" % classicUrl
      
      #qsearchhtml += "<hr>"
      #qsearchhtml += "&nbsp;&bull;&nbsp;<a title='List of the Corrupted Files' href='%(version)s/taskBuffer?method=corruptFiles'>Corrupted Files</a>" % { 'version': version }
      #qsearchhtml += "<hr>"

      ## Added to support jobDefID quick search for logged in users ##
      if False and logged == 'yes':
         qsearchhtml += "<form method=GET style='margin-top:0; margin:0; border:0; font-size:8pt;' \
          action='%s'>&nbsp;Job set<input  title='Please fill out this field' style='margin-top:0; margin:0; border:0; font-size:8pt;' \
         type=text border=0 name=jobDefinitionID size=6 maxlength=200><input type=hidden \
         name=job value=*><input type=hidden name=user value=%s><input type=hidden name=days \
         value=3></form>" % (classicUrl, utils.userName)
      htmlstr += utils.addAccordion(qsearchheader, qsearchhtml)
      # ---------------------- Errors -------------------------------
      errorsheader  = "Errors"
      button= {  "href"  : 'jobs/joberror'
              , "html"  : " &nbsp;&bull;&nbsp;Task Errors"
              , "title" : "Show &quot;Panda Job Error Distribution;&quot;" }
      errorshtml = divStyle
      errorshtml += indent
      errorshtml += "<br>&nbsp;&bull;&nbsp;<a title='Error Distribution for the failed production Tasks'  href='%(version)s/jobs/joberror?jobtype=production&item=taskID'>Production Tasks</a>" % { 'version': version }
      errorshtml += "<br>&nbsp;&bull;&nbsp;<a title='Site Error Distribution for the failed production Tasks'  href='%(version)s/jobs/joberror?jobtype=production&item=computingSite&hours=48'>Production Sites</a>" % { 'version': version }
      errorshtml += "<br>&nbsp;&bull;&nbsp;<a title='User Error Distribution for the failed production Tasks'  href='%(version)s/jobs/joberror?jobtype=production&item=prodUserName&hours=48'>Production Users</a>" % { 'version': version }
      errorshtml += "<br>&nbsp;&bull;&nbsp;<a title='Site Error Distribution for the failed Analysis Jobs'  href='%(version)s/jobs/joberror?jobtype=analysis&item=computingSite&hours=48'>Analysis Site</a>" % { 'version': version }
      errorshtml += "<br>&nbsp;&bull;&nbsp;<a title='User Error Distribution for the failed Analysis Jobs'  href='%(version)s/jobs/joberror?jobtype=analysis&item=prodUserName&hours=48'>Analysis Users</a>" % { 'version': version }
      errorshtml += "<br>&nbsp;&bull;&nbsp;<a title='Cloud Error Distribution for the failed production Tasks'  href='%(version)s/jobs/joberror?jobtype=production&item=cloud&hours=48'>Production Cloud</a>" % { 'version': version }
      errorshtml += "<br>&nbsp;&bull;&nbsp;<a title='Cloud Error Distribution for the failed Analysis Jobs'  href='%(version)s/jobs/joberror?jobtype=analysis&item=cloud&hours=48'>Analysis Cloud</a>" % { 'version': version }
      errorshtml += "<br>&nbsp;&bull;&nbsp;<a title='Error Distribution for the failed Jedi Tasks'  href='%(version)s/jobs/joberror?jobtype=&item=JediTaskID'>JEDI Tasks</a>" % { 'version': version }
      errorshtml += "<br>&nbsp;&bull;&nbsp;<a title='Site Error Distribution for the failed CMS Jobs'  href='%(version)s/jobs/joberror?jobtype=analysis&item=computingSite&VO=cms&hours=72'>CMS jobs</a>" % { 'version': version }
      errorshtml += "<br>&nbsp;&bull;&nbsp;<a title='Job Type Error Distribution for the Failed Jobs'  href='%(version)s/jobs/joberror?jobtype=all&item=prodSourceLabel&hours=48&opt=sum+item+time'>Job Types</a>" % { 'version': version }
      errorshtml += "<br>&nbsp;&bull;&nbsp;<a title='My Failed Jobs Error Distribution'  href='%(url)s%(version)s/jobs/joberror?jobtype=analysis&item=jobsetID&prodUserName=auto&hours=72'>My Jobs</a>" % { "url" : self.server().host().replace('http:','https:'),'version': version }
      errorshtml += "<br>&nbsp; "
      errorshtml += "</div>"
      htmlstr += utils.addAccordion(errorsheader,errorshtml,button=button)

      # ---------------------- Operations -------------------------------
      operationheader  = "Operations"
      button= {  "href"  : 'wnlist'
              , "html"  : " &nbsp;&bull;&nbsp;Worker Nodes"
              , "title" : "Show &quot;Panda Operations Dashboards;&quot;" }
      operatiohtml = divStyle
      operatiohtml += indent
      operatiohtml += "<p>&nbsp;&bull;&nbsp;<a title='Panda Production Operations Dashboard. Summary of Panda WN jobs status (per site/host)'  href='%(version)s/wnlist?jobtype=&jobStatus=wn'>Worker Nodes</a>" % { 'version': version }
      operatiohtml += "<br>&nbsp;&bull;&nbsp;<a title='Panda Production Operations Dashboard. Summary of Panda WN jobs status (per site/host)'  href='%(version)s/wnlist?jobtype=production&jobStatus=wn'>Worker Nodes (prod)</a>" % { 'version': version }
      operatiohtml += "<br>&nbsp;&bull;&nbsp;<a title='Panda Production Operations Dashboard. Summary of Panda WN jobs status (per site/host)'  href='%(version)s/wnlist?jobtype=analysis&jobStatus=wn'>Worker Nodes (analy)</a>" % { 'version': version }
      operatiohtml += "<p>&nbsp;&bull;&nbsp;<a title='Panda Production Operations Dashboard. Summary of Panda Factory jobs status (per site/host)'  href='%(version)s/wnlist?jobtype=&jobStatus=factory'>Factories</a>" % { 'version': version }
      operatiohtml += "<br>&nbsp;&bull;&nbsp;<a title='Panda Production Operations Dashboard. Summary of Panda Factory jobs status (per site/host)'  href='%(version)s/wnlist?jobtype=production&jobStatus=factory'>Factories (prod) </a>" % { 'version': version }
      operatiohtml += "<br>&nbsp;&bull;&nbsp;<a title='Panda Production Operations Dashboard. Summary of Panda Factory jobs status (per site/host)'  href='%(version)s/wnlist?jobtype=analysis&jobStatus=factory'>Factories (analy)</a>" % { 'version': version }
      operatiohtml += "<hr>"
      operatiohtml += "&nbsp;&bull;&nbsp;<a target='_classic' title='Panda Production Operations Dashboard. Summary of Panda production status (per Region)' href='%s?dash=prod'>Production (region)</a>" % classicUrl
      operatiohtml += "<br>&nbsp;&bull;&nbsp;<a target='_classic'title='Panda Production Operations Dashboard. Summary of Panda production status (per Cloud)' href='%s?dash=prod&view=cloud'>Production (cloud)</a>" % classicUrl
      operatiohtml += "<br>&nbsp;&bull;&nbsp;<a target='_classic' title='Information on Panda-based analysis using pathena'  href='%s?dash=analysis'>Analysis</a>" % classicUrl
      operatiohtml += "<hr>"
      operatiohtml += "<br>&nbsp;&bull;&nbsp;<a title='Summary of the Panda-based CMS analysis jobs'  href='%(version)s/cloudsummary?jobtype=analysis&VO=cms'>Analysis (CMS)</a>" % { 'version': version }
      operatiohtml += "<br>&nbsp;&bull;&nbsp;<a title='Summary of the Panda-based ATLAS analysis jobs'  href='%(version)s/cloudsummary?jobtype=analysis&VO=atlas'>Analysis (ATLAS only)</a>" % { 'version': version }
      operatiohtml += "<hr>"
      operatiohtml += "&nbsp;&bull;&nbsp;<a target='_classic' title='Organization and task assignment of clouds (Tier 1 + Tier 2/3s) processing Panda jobs' href='%s?dash=clouds'>Clouds</a>" % classicUrl
      operatiohtml += "<br>&nbsp;&bull;&nbsp;<a title='PanDA Clouds&#39; Specifications' href='%(version)s/taskBuffer?method=getCloudList'>Clouds&#39; Spec</a>" % { 'version': version }
      operatiohtml += "<br>&nbsp;&bull;&nbsp;<a title='PanDA Clouds&#39; Configuration' href='%(version)s/taskBuffer?method=getCloudConfig'>Clouds&#39; Config</a>" % { 'version': version }
      operatiohtml += "<br>&nbsp;&bull;&nbsp;<a target='_classic' title='Configuration Details of Sites' href='%s?dash=site'>Sites</a>" % classicUrl
      operatiohtml += "<br>&nbsp;&bull;&nbsp;<a title='PanDA Site Specifications' href='%(version)s/taskBuffer?method=getSiteInfo'>Sites' Spec</a>" % { 'version': version }
      operatiohtml += "<br>&nbsp;&bull;&nbsp;<a title='PanDA Site Current Activities' href='%(version)s/wnlist'>Sites' Activities</a>" % { 'version': version }
      operatiohtml += "<hr>"
      operatiohtml += "&nbsp;&bull;&nbsp;<a title='Release Availability at Sites' href='%(version)s/releaseinfo'>Releases</a>" % { 'version': version }
      operatiohtml += "<br>&nbsp;&bull;&nbsp;<a target='_classic' title='AutoPilot Pilot/Scheduler System. Pilot Submission System Serving All of OSG and LCG' href='%s?tp=main'>AutoPilot</a>" % classicUrl
      operatiohtml += "<br>&nbsp;&bull;&nbsp;<a target='_classic' title='Summary of DDM systems information and tools' href='%s?dash=ddm'>DDM</a>" % classicUrl
      operatiohtml += "<br>&nbsp;&bull;&nbsp;<a target='_classic'title='Centralized excluded sites in DDM production' href='%s/blacklisted_production.html'>Blacklisted Sites</a>" % "http://bourricot.cern.ch"
      operatiohtml += "<br>&nbsp;&bull;&nbsp;<a target='_classic' title='Panda DQ2 dataset mover status. Monitors Panda jobs that replicate datasets using dq2-cr' href='%s?ddm=dash'>DQ2 DS Mover</a>" % classicUrl
      operatiohtml += "<hr>"
      operatiohtml += "&nbsp;&bull;&nbsp;<a title='Recent Panda Analysis Users' href='%(version)s/listusers'>Users</a>" % { 'version': version }
      operatiohtml += "<br>&nbsp;&bull;&nbsp;<a title='Recent Most Active Panda Analysis Users' href='%(version)s/listusers?topsize=20'>20 Most Active Users</a>" % { 'version': version }
      operatiohtml += "<br>&nbsp;&bull;&nbsp;<a target='_classic' title='Panda statistics on site usage, performance and analysis activity' href='%s?mode=sitestats'>Panda statistics</a>" % classicUrl
      operatiohtml += "<br>&nbsp; "
      operatiohtml += "</div>"
      htmlstr += utils.addAccordion(operationheader,operatiohtml,button=button)

            
      # ---------------------- Summaries -------------------------------
      sumform = "<form method=GET style='margin:1px; border:0; font-size:8pt;' action='%s'>"  % classicUrl
      sumheader = "Summaries"
      sumhtml  = sumform
      sumhtml += "<br>&nbsp;Blocks:&nbsp;<input  title='Please fill out this field' style='margin-top:0; margin:0; border:0; \
      font-size:8pt;' type=text border=0 name=days size=3 maxlength=3><input type=hidden \
      name=overview value=prodlist>&nbsp;days</form>"

      sumhtml +=  sumform
      sumhtml += "&nbsp;Errors:&nbsp;<input  title='Please fill out this field' style='margin-top:0; margin:0; border:0; font-size:8pt;' type=text \
      border=0 name=days size=3 maxlength=3><input type=hidden name=overview value=errorlist>\
      &nbsp;days</form>"

      sumhtml +=  sumform
      sumhtml += "&nbsp;Nodes:&nbsp;<input  title='Please fill out this field' style='margin-top:0; margin:0; border:0; font-size:8pt;' type=text \
      border=0 name=days size=3 maxlength=3><input type=hidden name=overview value=wnlist>\
      &nbsp;days</form>"

      sumhtml += "&nbsp;Usage <a href='%(url)s?overview=usage'>1</a>, <a href='%(url)s?overview=daysusage&days=3'>\
      3</a> days" % { 'url' : classicUrl }
      sumhtml += "<br>&nbsp; "
      htmlstr += utils.addAccordion(sumheader, sumhtml)
     
      taskheader = "Tasks"
      taskhtml  = divStyle
      taskhtml  += "<p>&nbsp;<a href='%s?mode=reqtask1'>Generic Task Req</a>" % classicUrl
      taskhtml += "<br>&nbsp;<a href='%s?mode=reqtask2&type=evgen'>EvGen Task Req</a>" % classicUrl
      #taskhtml += "<br>&nbsp;<a href='%s?mode=reqtask2&type=ctbsim'>CTBsim Task Req</a>" % classicUrl
      taskhtml += "<br>&nbsp;<a href='%s?mode=reqtask3'>HLT Task Req</a>" % classicUrl
      taskhtml += "<br>&nbsp;<a title='List the Active Task Requests for the Last 96 Hours. Exclude the Aborted and Failed Tasks' href='%(version)s/tasks/listtasks1'>Task List</a>" % { 'version': version }
      taskhtml += "<br>&nbsp;<a title='List All Task Requests for the Last 96 Hours Including the Aborted and Failed Ones' href='%(version)s/tasks/listtasks1?failed=yes'>All Tasks List</a>" % { 'version': version }
      taskhtml += "<br>&nbsp;<a href='%s?mode=defNewTag'>New Tag</a>" % classicUrl
      taskhtml += "<br>&nbsp;<a href='%s?mode=listBugReport'>Bug Report</a>" % classicUrl
      taskhtml += "<br>&nbsp;<a href='%s?mode=tinfoSearch'>Task overview query</a>" % classicUrl
      taskhtml += "<form method=GET style='margin-top:0; margin:0; border:0; font-size:8pt;' \
      action='%s'>&nbsp;Clone Task&nbsp;<input  title='Please,provide the TaskID to clone' style='margin-top:0; margin:0; border:1; \
      font-size:8pt;' type=text border=0 name=tid size=6 maxlength=7></form>" % "https://pandamon.cern.ch/tasks/clonetask"
      taskhtml += "<br>&nbsp; "
      taskhtml += "</div>"
      button={ "href" : '%s?mode=taskquery' % classicUrl
            , "html" : " &nbsp;&bull;&nbsp;Search"
            , "title" : "Show &quot;Task and Tag Query Form&quot;" }
      htmlstr += utils.addAccordion(taskheader, taskhtml, button=button )

      datasetheader = "Datasets"
      datasethtml = divStyle
      datasethtml += "<p>&nbsp;<a href='https://bourricot.cern.ch/dq2/share/results/'>DQ2 Share Search</a>"
      datasethtml += "<br>&nbsp;<a href='http://popularity.cern.ch'>DQ2 Popularity</a>"
     
     
      # <form method="POST" action="/dq2/share/results/" name="searchform">
      # <input type="search" name="datasetSearched" id="datasetSearched" autofocus required placeholder="Dataset Name..." style="width: 400px;" />
      # <input type="submit" value="Get dataset and files" onClick="return forbidContainers();"/>
      # </form>

     
      datasethtml += "<br>&nbsp;<a href='%s?mode=listAbortedDatasetsState'>Aborted datasets</a>" % classicUrl
      dataset_browser_temp_path = 'http://panda.cern.ch/ddmbrowser/browser'
      # taskhtml += "<br><a href='%s'>Datasets Browser</a>" % dataset_browser_temp_path
      datasethtml += "</div>"
      button={ "href" : '%s?mode=dbquery' % classicUrl
             , "html" : " &nbsp;&bull;&nbsp;Search"
             , "title" : "Show &quot;Database Query Form&quot;" }
      htmlstr += utils.addAccordion(datasetheader, datasethtml,button=button)
     
      datriheader = "Datasets &nbsp;Distribution"
      datrihtml  = divStyle
      datrihtml += "<p><b>DaTRI:</b>"
      datrihtml += "<br>&nbsp;&bull;&nbsp;<a href='%s?mode=ddm_req'>Data_Transfer_Request</a>&nbsp;" % classicUrl
      datrihtml += "<br>&nbsp;&bull;&nbsp;<a href='%s?mode=ddm_req&action=List'>List_User_Requests</a>" % classicUrl
      datrihtml += "<br>&nbsp;&bull;&nbsp;<a href='%s?mode=ddm_pathenareq&action=List'>List_Pathena_Requests</a>" % classicUrl
      datrihtml += "<br>&nbsp;&bull;&nbsp;<a href='%s?mode=ddm_gangareq&action=List'>List_Ganga_Requests</a>" % classicUrl
      datrihtml += "<br>&nbsp;&bull;&nbsp;<a href='%s?mode=ddm_groupreq&action=List'>Group_Production</a>" % classicUrl
      datrihtml += "<p>&nbsp;<a href='%s?mode=pd2p'>PD2P</a>" % classicUrl
      datrihtml += "<br>&nbsp;<a href='%s?mode=listAODReplications'>AODs</a>" % classicUrl
      datrihtml += "<br>&nbsp;<a href='%s?mode=listEVNTReplications'>EVNTs</a>" % classicUrl
      datrihtml += "<br>&nbsp;<a href='%s?mode=listConditionsDB'>Conditions DS</a>" % classicUrl
      datrihtml += "<br>&nbsp;<a href='%s?mode=listDBRelease'>DB Releases</a>" % classicUrl
      datrihtml += "<br>&nbsp;<a href='%s?mode=listPacballs'>SIT pacballs</a>" % classicUrl
      datrihtml += "<br>&nbsp;<a href='%s?mode=listValidationReplications'>Validation Samples</a>" % classicUrl
      datrihtml += "<br>&nbsp;<a href='%s?mode=listFunctionalTests'>Functional Tests</a>" % classicUrl
      datrihtml += "<br>&nbsp;<a href='%s?mode=listCR'>ATLAS Data</a>" % classicUrl
      datrihtml += "<br>&nbsp;<a href='%s?mode=listReproDSReplications'>Reprocessed_Datasets</a>" % classicUrl
      datrihtml += "</div>"
      htmlstr += utils.addAccordion(datriheader, datrihtml)
      # ---------------------- User -------------------------------
      userheader  = "User"
      button= {  "href"  : '%s' % ("%(version)s/listusers" % {'version': version }) 
              , "html"  : " &nbsp;&bull;&nbsp;Summary"
              , "title" : "Show &quot;Recent Panda Analysis Users&quot;" }
      userhtml  = divStyle
      userhtml += "&nbsp;&bull;&nbsp;<a title='Recent Most Active Panda Analysis Users' href='%(version)s/listusers?topsize=20'>20 Most Active Users</a>" % { 'version': version }

      # datrihtml += "<br>&nbsp;<a href='%s?mode=listFunctionalTests'>Functional Tests</a>" % classicUrl
      userhtml += "</div>"
      htmlstr += utils.addAccordion(userheader,userhtml,button=button)

      # ---------------------- Stats -------------------------------
      statheader  = "Stats"
      button= {  "href"  : '%s?%s' % (classicUrl ,"mode=sitestats" ) 
              , "html"  : " &bull;&nbsp;Stats"
              , "title" : "Show &quot;Panda Statistics on Site Usage, Performance and Analysis Activity&quot;" }
      htmlstr += utils.addAccordion(statheader,"",button=button)
      # ---------------------- Stats -------------------------------
      dashheader  = "Dashboards"
      dashhtml = divStyle
      dashhtml += "<br>&nbsp;&bull;&nbsp;<a title='Panda Physics Data Dashboard' href='http://panda.cern.ch/server/pandamon/query?dash=physics'>Physics data</a>" 
      dashhtml += "<br>&nbsp;&bull;&nbsp;<a title='Production Operator UI' href='http://dashb-atlas-task-prod.cern.ch/templates/task-prod'>Task Production</a>" 
      dashhtml += "<br>&nbsp;&bull;&nbsp;<a title='Atlas DDM Dashboard' href='http://dashb-atlas-data.cern.ch/dashboard/ddm2/'>DDM Dashboard</a>" 
      dashhtml += "<br>&nbsp;&bull;&nbsp;<a href='http://dashb-atlas-ssb.cern.ch/dashboard/request.py/siteview'>SSB</a>" 
      dashhtml += "<br>&nbsp;&bull;&nbsp;<a title='ATLAS Computing and Muon Calibration Center' href='http://www.aglt2.org/csum.php'>AGLT2</a>" 
      dashhtml += "</div>"
      htmlstr += utils.addAccordion(dashheader,dashhtml)

      #htmlstr += "<p><b>Applications</b>"
      #htmlstr += "<br><a href='%s?vomon=charmm'>CHARMM</a>" % classicUrl

      # ---------------------- Logging  -------------------------------
      monitorheader  = "Logging monitor"
      button= {  "href"  : 'logsummary'
              , "html"  : " &bull;&nbsp;Summary"
              , "title" : "Show &quot; Summary of the Logged Incidents Over Last 36 Hours &quot;" }
      monitorhtml = divStyle
      monitorhtml += "<br>&nbsp;&bull;&nbsp;<a href='%s?overview=incidents&typekey=queuecontrol'>Queue Control</a>&nbsp;" % classicUrl
      monitorhtml += "<br>&nbsp;&bull;&nbsp;<a href='%s?overview=incidents&typekey=monconfig'>Configuration</a>&nbsp;" % classicUrl
      monitorhtml += "</div>"
      htmlstr += utils.addAccordion(monitorheader,monitorhtml,button=button)
      
      # ---------------------- Analytics -------------------------------
      analyticsheader = 'Analytics'
      analytichtml = divStyle
      analytichtml +="<br>&nbsp;&bull;&nbsp;<a title='Project and Data Type Popularity for ATLAS Analysis Jobs' href='//pandamon.atlascloud.org/ppop'>Popularity</a>"
      analytichtml +="<br>&nbsp;&bull;&nbsp;<a title='Timing distribution for ATLAS analysis job' href='//pandamon.atlascloud.org/ptimes'>Analysis Timing</a>"
      analytichtml += "</div>"
      htmlstr += utils.addAccordion(analyticsheader,analytichtml)
      
      return htmlstr

   #______________________________________________________________________________________      
   def leftNewMenuCont(self):
       """ Return html for inclusion in left menu """
       homemenu = [ ["system/home", "Introduction"]
                  , ["jobinfo" , "Job Information"]
                  , ["jobs/joberror?item=cloud" , "Job Errors"]
                   ,["alist"  , "List Monitor Modules"]
                   ,["logsummary"  , "Incidents"]
                   ,["listusers", "Users"]
                   #, ["dbstats" , "DB  Status"]
                   ,["cloudsummary" , "Production"]
                   ,["cloudsummary?jobtype=analysis" , "Analysis"]
                   ,["releaseinfo" , "Releases"]
                   ,['taskBuffer?method=countReleases' , "Jobs/Releases"]
                   ,['taskBuffer?method=getSiteInfo', "Sites"]
                   ,['taskBuffer?method=getCloudList', "Clouds"]
                   ,['taskBuffer?method=getCloudConfig', "Clouds' Config"]
                   ,['taskBuffer?method=getMCShares', "MC Shares "]
                   ,['taskBuffer?method=getJediTaskAtt&db=jmt', "JEDI Tasks"]
                   ,['schedcfg', "Sites' MaxTime"]
                   ,['mcore', "Multi Core Tasks"]
                   ,['wnlist', "Worker Nodes"]
                   ,['joblfn', "List Jobs' IDs and DataSets"]
                   ,['taskBuffer?method=getJobIds(status="failed",site=None,username="Jiri*",jobtype="analysis")', "Plain List of the Selected Jobs' IDs"]
                   ,['taskBuffer?method=getScriptOfflineRunning(1673414844)', "Get Prod Job Script"]
                   ,['reqtask1', "Task Request"]
                   ,['tasks/listtasks1', "Task List"]
                   ,['errorcodes', "List Panda Error Codes"]
                   ,['fax/map', "FAX viewer"]
                   ,['old', "Classic PanDA Pages"]
                  ]
       pandamonmenu = [
                        ['ptimes' , 'Analysis Timing']
                       ,['ppop'   , 'Popularity']
                      ] 
       pandaprotected = [
                          ['describe' , 'Describe the Db Tables']
                         ,['taskBuffer?method=pandacols' , 'Describe the Db Table Columns']
                        ]
       
       txt = ''
       script = self.server().script()
       version = self.server().version().get('version')
       if version == None: version = ''
       else: version = "/~%s" % version
       txt += "<a href='%(url)s%(version)s/%(item)s'>%(label)s</a><hr><p>" % {"url" : self.server().host().replace('http:','https:'), "version" : version, "item" : 'jobinfo?prodUserName=auto&hours=24', "label" : "My Jobs" }
       for h in   homemenu:
          txt += "<a href='%(url)s/%(item)s'>%(label)s</a><p>" % {"url" : version, "item" : h[0], "label" : h[1] }
       for h in   pandamonmenu:
          txt += "<a href='%(url)s/%(item)s'>%(label)s</a><p>" % {"url" :"//pandamon.atlascloud.org", "item" : h[0], "label" : h[1] }
       user = self.server().user()   
       if user != None:
         txt += '<hr>User %s%s Protected Items:<hr>' % ( user[0].upper(),user[1:] )
         for h in  pandaprotected:
            txt += "<a href='%(url)s/%(item)s'>%(label)s</a><p>" % {"url" :script, "item" : h[0], "label" : h[1] }
       
       return txt
       
#______________________________________________________________________________________      
   def leftMenuNew(self):
      htmlstr = ''
      style = " style='padding:0;' title='New Experimental Entries'"
      # htmlstr += "<table class='ui-corner-top ui-widget ui-widget-header' width='100%'><thead><tr><th align=left>" +"New Platform"+ "</th></tr></thead></table>";
      htmlstr += utils.addAccordion("New Panda", "<div style='padding:4px;' id='menu'>%s</div>" % self.leftNewMenuCont(), style)
      return htmlstr
      
#______________________________________________________________________________________      
   def leftMenuClose(self):
      return utils.closeAccordion()
#______________________________________________________________________________________      
   def leftMenuScript(self):
      """ script to activate the accordion ui and its cookie """
      htmlstr = """
        <script>
        $(document).ready(function() {
            var active = $.cookie('#pandaLeftMenuId');
            if  ( active == undefined ) { active = 0; }
            function bindCookiEvent(event, ui) { 
               $.cookie('#pandaLeftMenuId',ui.options.active,{ expires: 7, path: '/' });
            }
            var opt = { header: 'h3' 
               ,"active" : parseInt(active, 10)
               , change: bindCookiEvent
               , autoHeight: false
               ,  clearStyle: true
               };
            $("#pandaLeftMenuId").accordion(opt);
        });
        </script>
      """
      return htmlstr

