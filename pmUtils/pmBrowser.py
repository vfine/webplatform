"""
pandamon routines for interacting with and presenting to the browser
"""
import os, pwd, socket
from datetime import datetime

from pmState import pmstate
import pmConfig.pmConfig as config
import pmUtils as utils
from  pmCore.pmModule import pmModule as pmModule


_dummyMain="<center> . . . Downloading . . . </center>"
_dummyTitle='PanDA monitor ( new )'
#________________________________________________________________________
class pmBrowser(pmModule):

   def __init__(self,name='browser',parent=None,obj=None,server=None,config=None):
      pmModule.__init__(self,name,parent,obj,server,config)
      self._menu = None
      try:
         menu = self.config().config.frontpage['menu']
         self._menu = self.factory(menu,parent=self)
      except:
        raise
        pass

   def head(self,toptxt='Panda monitor and browser'):
       """ Build page header """
       tmpdatestring = datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")
       if pmstate().windowTitle != '': toptxt = pmstate().windowTitle
       ## If the active module has custom header material, include it
       try:
           mh = pmstate().moduleHandle[pmstate().module]
           modheader = mh.header()
       except:
           modheader = ''

       htmlstr ="""<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML//EN">
   <html><head id='head'><title>%s</title>
   <meta http-equiv="content-type" content="text/html; charset=utf-8" />
   <meta http-equiv="X-UA-Compatible" content="IE=edge" >
   <meta name="robots" content="noindex,nofollow" />
   <meta name="description" content="Panda monitor" />
   <meta name="date" content="%s">
   <meta http-equiv="Content-Script-Type" content="text/javascript">
   <link rel=start href="%s" title="Panda monitor home page">
   <style type="text/css">
   td {font-family: sans-serif; font-size: 12px;}
   #tophome #topleft{text-align: center; vertical-align: middle;}
   #topheader #topbar{text-align: left; vertical-align: middle;}
   #browsertitle{visibility: hidden;}
   #homeup{text-align: center; vertical-align: middle; font-family: sans-serif; font-size: 18px; font-weight: bold;}
   #hometop{text-align: center; vertical-align: middle; }
   #homedown #menuinfo{text-align: center; vertical-align: middle;}
   #titleheader{text-align: left; vertical-align: middle; font-family: sans-serif; font-size: 20px; font-weight: bold;}
   #nav #navright{vertical-align: middle; font-family: sans-serif;}
   #menu{vertical-align: top; font-family: sans-serif;}
   #foot{font-size: 12px; font-family: sans-serif;}
   .top {  font-family: sans-serif; font-size: 12px; }
   .headerbar {background: #e3e3e3; font-family: sans-serif;}
   .topheader  {background: #376797; font-family: sans-serif; font-size: 12px;}
   .menubartop  {background: #4A7FB4; font-family: sans-serif; font-size: 12px; opacity:0.99; }
   .menubar  {background: #e3e3e3; font-family: sans-serif; font-size: 12px;}
   .overlap {background: #d3d3d3; font-family: sans-serif; font-size: 12px; opacity:0.99; }
   .mainpage {text-align: left; vertical-align: top; background: white; font-family: sans-serif; font-size: 12px;}
   body.wait *, body.wait {cursor:progress !important; }
.bigpandamonbanner {
    border: 5px red solid;
    text-align: center;
    text-valign: middle;
    font-weight:bold;
}
.jedititle{
  font-size: large;
  color: red;
  color: red;
}


   </style>
   <style media="all" type="text/css"> 
   .alignRight { text-align: right; } 
   .nomargin {margin: 0px; }
   </style> 

   <!-- Module-specific header insertion -->
   %s
   %s
   </head>
   <noscript>
   JavaScript must be enabled in order for you to use this browser.
   </noscript>
   """ % ( toptxt, tmpdatestring, self.server().branchUrl(), modheader,self.scripts() )
   #    htmlstr += scripts()
       return htmlstr

   def foot(self,description='',stopwatch = None):
       """HTML page footer"""
       if description == '':
           version = "Code $Rev: 19982 $"
           version = version.replace('$','')
           description = version
       htmlstr = "<div id='foot' style='font-size: 11px'>"
       htmlstr += "<br> &nbsp; &nbsp; Module: %s/%s" % ( pmstate().context, pmstate().module )
       htmlstr += "<br> &nbsp; &nbsp; %s" % pmstate().timer

       if not stopwatch== None: htmlstr += "<br> &nbsp; Build time: %s" % stopwatch
       htmlstr += "<br> &nbsp; &nbsp; Page created %s" % datetime.utcnow().strftime("%m-%d %H:%M:%S")
       if description != '': htmlstr += "<br> &nbsp; &nbsp; %s" % description
       pandaUsername = pwd.getpwuid(os.getuid())[0]
       hostname = socket.gethostbyaddr(socket.gethostname())
       if pandaUsername != 'root': htmlstr += "<br> &nbsp; &nbsp; Run by %s @ %s" % \
                ( pandaUsername, os.environ.get("HOSTNAME") )
       if not stopwatch== None:  
         htmlstr += ". To produce this page our server spent: %s  at %s. " % (stopwatch, datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC") )

   #    if os.environ.has_key('HOSTNAME'): htmlstr += "<br> &nbsp; &nbsp; Host: %s" % os.environ.get("HOSTNAME")
       htmlstr += """
   <br> &nbsp; &nbsp; <a href='https://savannah.cern.ch/bugs/?func=additem&group=panda'>Report a problem</a>
        &nbsp; &nbsp; <a href='mailto:hn-atlas-dist-analysis-help@cern.ch'>Email list for help</a>
   <br> &nbsp; &nbsp; <a href='mailto:atlas-adc-pandamon-support@cern.ch'>Webmaster</a></div>
   """

       analytics = """
   <!-- Google analytics  take it out. It slows down the JQuery !!! [[ and you consider that an analytics problem rather than jQuery problem?? - TW ]]
   <script type="text/javascript">
   var gaJsHost = (("https:" == document.location.protocol) ? "https://ssl." : "http://www.");
   document.write(unescape("%3Cscript src='" + gaJsHost + "google-analytics.com/ga.js' type='text/javascript'%3E%3C/script%3E"));
   </script>
   <script type="text/javascript">
   var pageTracker = _gat._getTracker("UA-4802332-1");
   pageTracker._initData();
   pageTracker._trackPageview();
   </script>
    -->
   """
       # htmlstr += analytics
       htmlstr += "</body></html>"
       return htmlstr

   def buildMenu(self,logged='no'):
       """ Build left menu bar of monitor """
       txt = ''
       style = " style='padding:0;' "
       if self._menu!=None:
            txt += self._menu.leftMenu()
       else: txt+=  "<div id='menu' class='ui-widget ui-widget-content ui-cornel-all' style='margin:0px;padding:0px'></div>"
       # txt += self.buildClassicMenu()
       txt += """
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
             //,  clearStyle: true
               };
            $("#pandaLeftMenuId").accordion(opt);
        });
        </script>
       """
       return txt      

       for m in config.modules:
           try:
               mh = pmstate().moduleHandle[m]
               txt += "<p>%s" % mh.leftMenu()
           except:
               pass
       return txt

   def buildDashboards(self):
       """ Return the list of dashboard links along the top of the monitor """
       txt = ''
       for m in config.modules:
           try:
               mh = pmstate().moduleHandle[m]
               txt += "%s &nbsp; " % mh.topMenu
           except:
               pass
       return txt
               
   def buildMain(self,title, menuinfo, navtxt, maintxt,mode="html"):
       """ Build main page """
       print " 203 ---- ", mode
       leftbox = None
       topbar = None
       menu = None
       if mode == "html":
           sc = pmstate().script
           if sc != '': sc =  "<br><small>(%s's version)</small>" % sc[2:] 
           leftbox = " PanDA Monitor %s<br><div style='font-size: 12px; font-weight: normal'>Times are in UTC</div>" % sc
           topbar = self.buildDashboards()
           menu = self.buildMenu()
           return self.buildMainFull(title, menuinfo, navtxt, menu, maintxt,
                                leftbox=leftbox, topbar=topbar)
       else:
           return self.buildMainFullJson(title, menuinfo, navtxt, menu, maintxt,
                                    leftbox=leftbox, topbar=topbar)

   def buildMainFullJson(self,title='PanDA Monitor', menuinfo=None, nav=None, menu=None,
                 main=None, topleft=None,leftbox=None,upleft=None,
                 upright=None,titleleft='',navright=None,topbar=None):
      """ Build main page """
      def dflt(k,v,comma=',') :
         out = ''
         if v!=None: 
            out = ' { "id" : "%(id)s" , "html" : " %(json)s" } ' % {'id' : k , 'json' : v.replace('"','\\"').replace('\n','\\n') } 
            out += comma
         return out
      out = ''
      out += dflt('title',title)
      out += dflt('homedown',menuinfo)
      out += dflt('nav',nav)
      out += dflt('topmenu',menu)
      out += dflt('main',main)
      out += dflt('topleft',topleft)
      out += dflt('leftbox',leftbox)
      out += dflt('upleft',upleft)
      out += dflt('upright',upright)
      out += dflt('titleleft',titleleft)
      out += dflt('navright',navright)
      out += dflt('topbar',topbar)
      out  = out[:-1]
      # layout = arg
      # out  = ''
      # for id in layout:
         # json =  layout[id] 
         # if json != None:
            # if len(out) > 0: out += ','
            # out += ' { "id" : "%(id)s" , "html" : "%(json)s" } ' % {'id' : id , 'json' : json }
      out = '[%s]' % out 
      return out
       
   def buildMainFull(self,title='PanDA Monitor', menuinfo=None, nav=None, menu=None,
                 main=None, topleft=None,leftbox=None,upleft=None,
                 upright=None,titleleft='',navright=None,topbar=None):
       """ Build main page """
       """  
                        Main page layout 
       -------------------------------------------------------------------------
       |   3px   |  tophome.topleft    |           topheader. topbar           |
       -------------------------------------------------------------------------
       |   12px  |  hometop.titleleft  | topright.upleft  | topright.upright   |
       -------------------------------------------------------------------------
       |   40px  |  homeup             |           titleheader.title           |
       -------------------------------------------------------------------------
       |   20px  | homedown (menuifo)  |  nav  |  nav.navright |  nav.navhelp  |
       -------------------------------------------------------------------------
       |         |    topmenu          |                main                   |
       |         |  classic menu       |                main                   |
       |         |       menu          |                main                   |
       -------------------------------------------------------------------------
       |                                 foot                                  |
       -------------------------------------------------------------------------
       """
   # def buildMainFull(title='PanDA Monitor', menuinfo=None, nav=None, menu=None,
                 # main=None, topleft=None,leftbox=None,upleft=None,
                 # upright=None,titleleft='',navright=None,topbar=None):
       def dflt(a) :
            if a==None: a = "&nbsp;"
            return a
       title    = dflt(title)
       menuinfo = dflt(menuinfo)
       nav      = dflt(nav)
       menu     = dflt(menu)
       main     = dflt(main)
       topleft  = dflt(topleft)
       leftbox  = dflt(leftbox)
       upleft   = dflt(upleft)
       upright  = dflt(upright)
       titleleft= dflt(titleleft)
       navright = dflt(navright)
       topbar   = dflt(topbar)

       htmlstr = ''
       upleft += ""  # "&nbsp;"
       if pmstate().navmain != '': pmstate().navmain = "<br>" + pmstate().navmain
       if pmstate().navmain != '': nav += '<br>%s' % pmstate().navmain
       if pmstate().navright != '':
           navright = pmstate().navright
           pmstate().navright = '&nbsp;'
       if pmstate().titleleft != '':
           titleleft = pmstate().titleleft
           pmstate().titleleft = ''
       htmlstr += """
     <body marginwidth=0 marginheight=0>
     <table border=0 width="100%%" cellspacing=0 cellpadding=5>
         <tr height="10px"  style="font-family: sans-serif; font-size: 8px;">
            <td width="3px" class="topheader"></td>
            <td id="tophome" class="menubartop nomargin" nowrap> 
               <b> &nbsp; &nbsp; &nbsp;<span id='topleft'>%(topleft)s</span>&nbsp;&nbsp; &nbsp; </b>
            </td>
            <td id="topheader_row" class="topheader nomargin" width="100%%" colspan=2 nowrap>
               <table class="nomargin" border="0" >
                  <tr class="nomargin">
                     <td class="nomargin" >
                        <span  title="The URL of this page" id="urlIconId" style="cursor:pointer;" class="ui-icon   ui-widget-header ui-icon-link nomargin"></span>
                        <span id="urlID" style="display:none; cursor:pointer;" class="ui-state-highlight ui-corner-all;">
                           <span id="url_qr_id"></span><span id="url_text_id"></span>
                        </span>
                     </td> 
                     <td id="topheader"></td>
                     <td width="90%%"><span id='topbar'>%(topbar)s</span></td>    
                     <td>
                        <span id='navright'>%(navright)s</span>
                        <div align="left" style="float:right; width:550px;" class="ui-widget">
                           <div id="navhelp" style="display:none" class="ui-state-highlight ui-corner-all">
                                   Help
                           </div>
                        </div>
                     </td>
                     <td><span id="savejsonID" style="cursor:pointer; display:inline-block; " title="Save the data in json format" class="ui-icon ui-widget-header ui-icon-disk"> </span></td>
                     <td><span id="navhelpbuttonId" style="cursor:help;  display:inline-block;"  title="Click to see the help" class="ui-icon ui-widget-header ui-icon-help"> </span></td>    
                  </tr>
                  </table>
            </td>
         </tr>
     <tr>
        <td height="6px" class="headerbar"></td>
        <td id="hometop" class="overlap" nowrap><span id='titleleft'>%(titleleft)s</span></td>
        <td id="topright" class="headerbar" align="left" width="75%%">
            <span id='upleft'>%(upleft)s</span></td>
        <td id="topright" class="headerbar" align="right" style="vertical-align:top">
            <span id='upright'>%(upright)s</span></td>
     </tr>
     <tr>
        <td height="40px" class="headerbar"></td>
        <td id="homeup" class="overlap" nowrap>%(leftbox)s</td>
        <td id="titleheader" class="headerbar"  colspan=2><span id ='title'>%(title)s</span></td>
     </tr>
     <tr>
        <td height="10px" class="headerbar" rowspan="2"></td>
        <td id="homedown" class="overlap" nowrap rowspan="2"> %(menuinfo)s</td>
        <td id="nav" class="headerbar" align="left"> %(nav)s</td>
        <td id="nav" class="headerbar" align="right"  style="vertical-align:bottom">
              <div style="display:inline-box;" id='navright'>%(navright)s</div>
         </td>
     </tr>  
     <tr>
    <td colspan="2" class="bigpandamonbanner">
        <br/><br/><br/><br/>
        <div class="jedititle"><span class="jedititle">JEDI is the default analysis backend since August 12 2014!</span></div>
        <br/><br/>
        JEDI tasks/jobs can be monitored on 
        <a href="http://bigpanda.cern.ch/" target="_blank">http://bigpanda.cern.ch/</a>. <br/>
        Submission to JEDI is the default setup using Panda/Ganga tools from CVMFS since August 12, 2014!<br/>
        <br/>
        JEDI instruction are available on TWiki
        <a href="https://twiki.cern.ch/twiki/bin/view/PanDA/PandaJediAnalysis"
    target="_blank">PandaJediAnalysis</a>.
        <br/><br/><br/><br/>
    </td>
     </tr>  
     <tr>
     <td></td>
     <td id="topmenu" class="ui-widget menubar" style="vertical-align:text-top;padding:1px;">
       %(menu)s
     </td>
     <td id="main" class="mainpage" colspan=2> %(main)s</td>
     </tr></table>
   """ %{'topleft': topleft, 'topbar': topbar, 'titleleft': titleleft, 'upleft': upleft, 'upright':upright,'leftbox': leftbox,'title':title,'menuinfo': menuinfo,'nav': nav,'navright': navright,'menu':menu,'main': main}
       return htmlstr    

   def buildPage(self,titletxt=_dummyTitle, menuinfo='', navtxt='', maintxt=_dummyMain, mode='html'):
      cached = {'s-maxage':999999,'max-age':600} 
      if not mode in ('html','json'):
         return maintxt, mode,cached
      else:
         page = ''
         if mode == 'html':  page = self.head(titletxt)
         page += self.buildMain(titletxt, menuinfo, navtxt, maintxt,mode)
         if mode == 'html':  page += self.foot()
         return page, mode, cached

   def scripts(self):
       """ Javascript used in monitor page """
       google =''
       if config.google:
          google = """
                       var _gaq = _gaq || [];
                       _gaq.push(['_setAccount', 'UA-%(account)s']);
                       _gaq.push(['_setDomainName', '%(domain)s']);
                       _gaq.push(['_trackPageview']);

                       (function() {
                         var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
                         ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
                         var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
                       })();
                  """ % { 'account' : config.google['property'], 'domain' : config.google['domain'] }

       htmlstr = """
            <!--Load the JQUERY/FLOT -->
                   <link type="text/css" href='%(css)s/%(ui_css)s' rel='stylesheet' />	
                   <link type="text/css" href='%(css)s/%(dt_css)s' rel='stylesheet' />	
                   <link  id="favicon" type='image/x-icon' href='%(images)s/favicon.ico' rel='shortcut icon' />
                   <!--[if IE]><script language="javascript"  src="%(script)s/%(excanvas)s"></script><![endif]-->                
                   <script   src='%(script)s/%(dateformat)s'></script>
                   <script   src='%(cdn)s/%(jquery)s'></script>
                   <script   src='%(script)s/%(jquery-url)s'></script>
                   <script   src='%(script)s/%(cookie)s'></script>
                   <script   src='%(cdn)s/%(datapicker)s'></script>
                   <script   src='%(script)s/%(flot)s'></script>
                   <script   src='%(script)s/%(crosshair)s'></script>
                   <script   src='%(script)s/%(stack)s'></script>
                   <script   src='%(script)s/%(timers)s'></script>
                   <script   src='%(msn)s/%(datatable)s'></script>
                   <script   src='%(script)s/%(qrcode)s'></script>
                   <script   src='%(script)s/%(uid)s'></script>
                   <!-- <script   src='%(script)s/%(encoder)s'></script> -->
                   <!--Load the PANDA API-->
                   <script  src='%(script)s/%(pmMonitor)s'> </script>
                   <script  src='%(script)s/%(utils)s'> </script>
                   <script  src='%(script)s/%(views)s'> </script>
                   <script  src='%(script)s/%(plot)s'> </script>
                   <script  src='%(script)s/%(sm)s'> </script>
                   <script  src='%(script)s/%(ajaxrender)s'> </script>
   <style>
   .ui-widget {
     font-size: 9pt;
   }
   </style>
             <script> 
            // JQuery init
                jQuery.fn.log = function (msg) {
                  console.log("%%s: %%o", msg, this);
                  return this;
                };
               document.pandaURL = '%(url)s';
               // JQuery init
               $(document).ready(function() {
                   $(this).log('Activate JQuery');
                   utils();
                   var pm = new Pm('%(wscript)s');
                   pm._topElement.ChangeStatus('modified');
               }); 
             <!--Load the Google / Analytics-->
                  %(google)s
            </script>
                   """ % {  'url'      : self.server().fileURL()
                           ,'script'   : self.server().fileScriptURL()
                           ,'images'   : self.server().fileImageURL()
                           ,'cdn'      : 'https://ajax.googleapis.com/ajax/libs'
                           ,'msn'      : 'http://ajax.aspnetcdn.com/ajax'
                           ,'jqcdn'    : 'http://code.jquery.com'
                           ,'utils'    : 'PandaMonitorUtils.js'
                           ,'views'    : 'PandaMonitorViews.js'
                           ,'plot'     : 'pmPlot.js'
                           ,'pmMonitor': 'pmMonitor.js'
                           ,'jquery'   : 'jquery/1.7.2/jquery.min.js'
                           ,'jquery-url' : 'jquery/jquery.ba-bbq.min.js'
                           ,'flot'     : 'flot/jquery.flot.js'
                           ,'crosshair': 'flot/jquery.flot.crosshair.js'
                           ,'stack'    : 'flot/jquery.flot.stack.js'
                           ,'excanvas' : 'jquery/excanvas.min.js'
                           ,'timers'   : 'jquery/jquery.timers.js'
                           ,'datapicker': 'jqueryui/1.8.18/jquery-ui.min.js'
                           ,'datatable': 'jquery.dataTables/1.9.1/jquery.dataTables.min.js'
                           ,'css'      :  self.server().fileScriptCSS()
                           ,'ui_css'   : 'ui-lightness/jquery-ui.css'
                           ,'dt_css'   : 'demo_table_jui.css'
                           ,'dateformat': 'date.format.js'
                           ,'encoder'  : 'jquery/jquery.encoder.js'
                           ,'qrcode'   : 'jquery/jquery.qrcode.min.js'
                           ,'uid'      : 'jquery/jquery.unique-element-id.js'
                           ,'wscript'   : pmstate().script
                           ,'google'   :  google
                           ,'cookie'    : 'jquery/jquery.cookie.js'                        
                           ,'sm'       : '3dparty/state-machine/state-machine.js'
                           ,'ajaxrender': 'core/ajaxrender.js'
                         }
       ## If the active module has any custom scripts, add that too.
       try:
           mh = pmstate().moduleHandle[pmstate().module]
           htmlstr += mh.scripts()
       except:
           pass
       return htmlstr
