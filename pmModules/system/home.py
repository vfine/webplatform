from pmUtils.pmState import pmstate
from pmCore.pmModule import pmModule
from pmCore.pmModule import pmRoles
import pmUtils.pmUtils as utils

class home(pmModule):

   #______________________________________________________________________________________      
   def __init__(self,name=None,parent=None,obj=None):
      pmModule.__init__(self,name,parent,obj)
      self.publishUI(self.doQuery,role='html')
      # self.publishUI(self.doScript,role=pmRoles.script())
   #______________________________________________________________________________________      
   def pageSection(self,text) :
    """ JQuery UI '.ui-widget-header' page section separator """
    txt = "<p><table class='ui-corner-all ui-widget ui-widget-header' width='100%'><thead><tr><th align=left>" +text+ "</th></tr></thead></table><p>"
    return txt;

   #______________________________________________________________________________________      
   def frontPageClassic(self):
      """ Classic Panda monitor main page """
      try:
         classicUrl=self.config().config.classic['url']
      except:
         classicUrl = "http://panda.xxxx.xx"
      title = "Quick Guide to the Panda Monitor</a>"
      maintxt = "<div class='ui-corner-all ui-widget ui-widget-header' >"  +title+ "</div>"
      maintxt += "<p>For Panda documentation and information on support and problem reporting see \
            the <a href='%s?overview=info'>Panda info and user support</a> page." % classicUrl
      maintxt += self.pageSection("Monitor Instances")
#      for i in mond_conf.instances:
#            maintxt += "<br><a href='%s'>%s</a>: %s" % ( i['url'], i['name'], i['desc'] )
      maintxt += "<a href='%s'>%s</a>: %s" % ( classicUrl, "CERN", "Primary production monitor at CERN" )
      maintxt += "<br><a href='%s'>%s</a>: %s" % ( "http://pandamon.xxxx.xx", "NEW", "New production monitor at CERN" )
      maintxt += "<br><a href='%s'>%s</a>: %s" % ( "http://pandamon-eu.aaaacloud.org", "CLOUD", "Experimental monitor at <a href='http://aws.amazon.com/ec2'>EC2 cloud</a>" )
      maintxt += "<p>"
      # activateAccordion
      maintxt += self.pageSection("Left Bar")
      opJobs  =  0
      opQuick =  6
      opErr   = opQuick+1
      opIndx  = opErr  +1
      opSum   = opIndx +1
      opTask  = opSum  +1
      opDs    = opTask +1 
      opDist  = opDs   +1
      opUsr   = opDist +1
      opStat  = opUsr  +1
      opDash  = opStat  +1
      opLog   = opDash +1 
      maintxt += """
      <div title='The items from the the "Classic" PanDA top menu bar' class='ui-widget ui-widget-content ui-corner-all' style='padding:4px;'>
      <table class='ui-corner-top ui-widget ui-widget-header' width='100%%'><thead><tr><th align=left>The Items From the Former 'Classic' PanDA Monitor Top Menu Bar</th></tr></thead></table>
      %(Production)s Panda Production Operations Dashboard. Summary of Panda production status
      <br>%(Clouds)s Organization and task assignment of clouds (Tier 1 + Tier 2/3s) processing Panda jobs
      <br>%(DDM)s Summary of DDM systems information and tools
      <br>%(PandaMover)s Panda DQ2 dataset mover status. Monitors Panda jobs that replicate datasets using dq2-cr.
      <br>%(AutoPilot)s Pilot submission system serving all of OSG and LCG
      <br>%(Sites)s Collection of grid-wide and site-level monitoring links
      <br>%(Analysis)s Information on Panda-based analysis using pathena
      <br>%(Physics)s aaaa data discovery and access info and tools for physicists
      <!--- <br><b>Usage:</b> CPU usage by user -->
      <br>%(ProdDash)s Link to the ARDA aaaa production dashboard
      <br>%(DDMDash)s Link to the ARDA aaaa DDM dashboard
      <br>%(users)s Lists Panda users and gives an access to 'your' Panda page
      </div>
        """ %{'Production' :utils.activateAccordion('Production',opIndx,tooltip='"Operations"')
         , 'Clouds': utils.activateAccordion('Clouds',opIndx,tooltip='"Operations"')
         , 'DDM':utils.activateAccordion('DDM',opIndx,tooltip='"Operations"')
         , 'PandaMover':utils.activateAccordion('DQ2 DS Mover',opIndx,tooltip='"Operations"')
         , 'AutoPilot':utils.activateAccordion('AutoPilot',opIndx,tooltip='"Operations"')
         , 'Sites':utils.activateAccordion('Sites',opIndx,tooltip='"Operations"')
         , 'Analysis':utils.activateAccordion('Analysis',opIndx,tooltip='"Operations"')
         , 'Physics':utils.activateAccordion('Physics data',opDash,tooltip='"Dashboards"')
         , 'ProdDash':utils.activateAccordion('ProdDash',opDash,tooltip='"Dashboards"')
         , 'DDMDash':utils.activateAccordion('DDMDash',opDash,tooltip='"Dashboards"')
         , 'users' : utils.activateAccordion('List users',opUsr,tooltip='"Users"')
         }
      maintxt += "<hr>"
      maintxt += """
        <div  title='The items from the "Classic" PanDA top menu bar' class='ui-widget ui-widget-content ui-corner-all' style='padding:4px;'>
        %(jobs)s Job links at left list the <code>running</code>
          , <code>activated</code> (ready for pickup by a pilot)
          , <code>waiting</code> (waiting for input data availability)
          , <code>assigned</code> (brokered and waiting for completion of input data transfer to processing site)
          , <code>defined</code> (awaiting brokerage)
          , <code>finished</code>
          , <code>failed</code> 
          and <code>cancelled</code> jobs. 
          <br><it>"Analysis"</it> jobs (as opposed to <it>"Managed Production"</it> jobs) can be listed separately. 
          <br>The 'old archive' contains all finished/failed/cancelled jobs older than 3 days. 
        <p>%(Quick)s Enter a Panda job name or ID, dataset name or ID, or task name or ID into the appropriate field and hit return in order to do a quick lookup.
        <p>%(Summaries)s Enter a day count in the desired summary field and hit return to bring up a summary covering the last N days.
        <br>&nbsp;&bull;&nbsp;The 'blocks' summary shows the production datablocks (datasets) currently being processed in the production system, with details on where they are being processed, job states etc.
        <br>&nbsp;&bull;&nbsp;The 'errors' summary shows overall production status at all Panda sites with details of the error conditions encountered.
        <br>&nbsp;&bull;&nbsp;The 'nodes' summary shows worker nodes active at all production sites with statistics on processed jobs and states.
        <p>%(Tasks)s Task request forms are provided for entering generic, event generation and CTB tasks. The full task list gives statistics on tasks by grid and a listing of all tasks.
        The task browser allows selection of tasks based on their metadata (physics type, production series, release, output type, etc.) with navigation to datasets associated with the task, where data availability and access information is provided.
        <p>%(Datasets)s Dataset searches can be done with the search form (with wildcards) or quick search (by name, no wildcards). Listings are available for input datasets (a short list; the datasets which are inputs to the tasks processed by Panda), output datasets (very long -- the datasets produced by Panda production -- but the task browser is more convenient for navigating to produced data), dispatch blocks (Panda internal), and all datasets. Long lists are truncated and useful only to get the overall count and a sample list.
        <p>%(distribution)s Dataset replication requests, operational displays from aaaa DDM Ops for distribution of AODs, RDOs, conditions data, real DAQ data, etc.
        <!-- 
           <p><b>Subscriptions:</b> Shows DQ2 subscriptions managed by Panda, which handle Panda's data movement. 'Dispatch blocks' are used to dispatch data to processing sites in advance of processing; destination blocks are used to route outputs to archival storage.
           <p><b>Sites:</b> Configuration details of sites. Site pages provide access to monitors, jobs running at the site, DQ2 configuration, etc.
        -->
        <p>%(Logging)s Summary of the incident logging sent by Panda components to record
        Panda activity. Shows job requests (analysis and production) from pilots, by site.
        <!--
           <p><b>Panda system configuration and status:</b> Configuration link, top left, gives system configuration
           parameters and server status.
           The system statistics page at left gives overall production summary and stats.
        -->
        </div>
        """ % {'jobs' : utils.activateAccordion('Jobs running in Panda',opJobs,tooltip='"Jobs"')
              ,'Quick' :utils.activateAccordion('Quick searches',opQuick)
              ,'Summaries':utils.activateAccordion('Summaries',opSum)
              ,'Tasks':utils.activateAccordion('Tasks',opTask)
              ,'Datasets':utils.activateAccordion('Datasets',opDs)
              ,'distribution':utils.activateAccordion('Datasets distribution',opDist)
              ,'Logging':utils.activateAccordion('Logging monitor',opLog)
        }
      return maintxt

    #______________________________________________________________________________________      
   def frontPageNew(self):
      """ New  Panda monitor main page """
      maintxt = """
   <div style="width:600px; float:left; padding:5px;">
   <div class='ui-widget ui-widget-content ui-corner-all' style="padding:7px;" >
   This is a <a href="https://indico.xxxx.xx/getFile.py/access?contribId=4&resId=0&materialId=slides&confId=202874">new Panda Web Platform</a> based Monitor that is more maintainable,
   supports the <a href="http://www.json.org/">json<a/>/<a href="http://jquery.com">jQuery</a> architecture 
   of ADC monitoring, is easily extensible, and integrates
   well with other ADC monitoring tools and components.
   <p> <b><a href="http://panda.xxxx.xx">Go to the "Classic Panda" </a></b>
   </div>
   <p>
   <div class='ui-widget-header ui-corner-top' style="padding:7px;">
   Notes on this prototype:
   </div>
   <div class='ui-widget ui-widget-content ui-corner-bottom' style="padding:7px;">
   <ul>
   <li> Supported job archive databases are SimpleDB (Amazon) and Oracle.
   <li> Functional modules are included automatically and dynamically. There is no hard coding of
     functional components or user interface elements.
     pmModules/modname.py is used to interpret URLs of the form
     http://baseurl/modname/?param1=1&param2=2
   <li> Modules declare their own contributions (menu items) to be included in the interface.
   <li> Standard module routines publish the data to be sent to the client
     The module can specify  the various roles of the data it publishes via "publish" method
   <li> Modules can be static html, they are referenced by URL the same way. Thus a module may change
     from a python implementation to a fully client/jQuery based implementation (static html)
     transparently to the user.
   <li> The data the module publishes is interpreted, compressed and sent to the client / browser according the the data role 
     defined as parameter of the publish method and the client type / capability.
     so monitor modules can serve as either web page builders, or json data providers or the rendering 
     function providers or all above
   <li> The platform  is backward compatible with the classic Panda  Monitor. It does support the legacy "classic" Panda Monitor Interface.
   <br> For example, the  3 different URLs, the classic one : <a href="http://panda.xxxx.xx?dash=prod">http://panda.xxxx.xx?dash=prod</a> and the new 
    <a href="http://pandamon.xxxx.xx?dash=prod">http://pandamon.xxxx.xx?dash=prod</a> and <a href="http://pandamon-eu.aaaacloud.org?dash=prod">http://pandamon-eu.aaaacloud.org?dash=prod</a>   
    generate the same  "classic" Web page
   </div>
   </div>
       """
      return  maintxt
      
   #______________________________________________________________________________________      
   def doTab(self):
      maintxt = """
   <div id="tabs">
   <ul>
      <li><a href="#tabs-2">Quick guide to the<a href='https://twiki.xxxx.xx/twiki/bin/view/PanDA/PandaPlatform'>PanDA Monitor</a></a></li>
      <li><a href="#tabs-1"><a href='https://twiki.xxxx.xx/twiki/bin/view/PanDA/PandaPlatform'>PanDA monitor ( to be decommissioned )</a></a></li>
   </ul>
   <div id="tabs-1">
      %(new)s
   </div>
   <div id="tabs-2">
      %(old)s
   </div>
</div>
<script>
      $(document).ready(function() {
             $( "#tabs" ).tabs();
      });
</script>
      """ % {'old' : self.frontPageClassic(), 'new':self.frontPageNew() } 
      return maintxt
      
   #______________________________________________________________________________________      
   def doQuery(self,config=None):
       """ Process the query request 
       <ul>
        <li>Click <a href="http://pandamon.xxxx.xx/alist">here to see the <b>"List of all available Monitor Modules"</b></a>
       </ul>
       """
       title = 'PanDA monitor ( new )'
       m = self.frontPageNew() + self.frontPageClassic()
       m= self.doTab()
       self.publishPage(title=title,main=m )
       # self.publish(self.leftMenu(),"menu",role=pmRoles.html())
       self.publish({'s-maxage': 999999,'max-age':1800},role=pmRoles.cache())
       # self.ls()

   #______________________________________________________________________________________      
   def leftMenu(self):
       """ Return html for inclusion in left menu """
       raise RuntimeError("An astray invocation of the leftMenu method")  

   #______________________________________________________________________________________      
   def scripts(self):
       """ Custom scripts needed by this module """
       txt = ''
       return txt

   #______________________________________________________________________________________      
   def header(self):
       """ Custom css style block and/or other material for inclusion in the page header """
       txt = """
       """
       return txt
   #______________________________________________________________________________________      
   def doScript(self,config=None):
      script = """
        function db(tag,maindata) { 
            var th = views().jqTag(tag);
            var dashboard  = $("<div>hello gues</div>");
            tag.append(dashboard);
            function appendJobSummary(tag,main) {
               var _jobsummary = main.jobsummary;
               var dhead = main.header;  
               if (main.info.length > 0 && dhead != undefined ) {
                  var dinfo    = {  
                                "data"   : main.info
                               ,"rows"   : main.info
                               ,"header" : dhead 
                               ,"jobsummary" : _jobsummary
                              };
                  var tg = dhead[0] + "_"+tag;
                  var nxdiv = views().renderJobSummary(dashboard,dinfo);
                  nxdiv.show();
               }
            }
            function fetchJobSummary() {
                  var lpars = {};
                  lpars['summary']=true;
                  aj = new AjaxRender();
                  lpars['jobparam'] = 'jobStatus';
                  aj.download('jobsummaryid',appendJobSummary, "jobinfo",lpars);
            }
           /* fetchJobSummary(); */
         }         
      """
      print utils.linInfo(), script
      self.publishNav(script,pmRoles.script())
   
  
