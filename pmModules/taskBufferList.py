""" Document the PanDA Server TaskBuffer API """
# $Id: taskBufferList.py 9690 2011-11-16 22:28:01Z fine $
# Display DB status and stats
from pmUtils.pmState import pmstate
from pmCore.pmModule import pmRoles
from  pmTaskBuffer.pmTaskBuffer import pmtaskbuffer as pmt
from  pmTaskBuffer.pmTaskBuffer import pmgrisliaskbuffer as gmt
import pmUtils.pmUtils as utils
import pmUtils.Stopwatch as Stopwatch
from datetime import datetime
import inspect

from  pmCore.pmModule import pmModule

class taskBufferList(pmModule):

   #______________________________________________________________________________________
   def __init__(self,name=None,parent=None,obj=None):
      pmModule.__init__(self,name,parent,obj)
      self.publishUI(self.doJson,role=pmRoles.object())
      self.publishUI(self.doScript,role=pmRoles.script() )
      
      self._doc = None
   #______________________________________________________________________________________
   def makeMethodDoc(self, name, obj,label=None):
      """ Create the documentation for the UI """
      if label != None:   name = name +"."+label       
      doc = obj.__doc__
      pars = ''
      try:
         (args, varargs, keywords, defaults) = inspect.getargspec(obj)
         ndef = len(defaults) if defaults else 0
         largs = len(args) if args else 0
         iDfl = largs - ndef
         sep = ''
         for i,arg in enumerate(args):
            if arg == 'self': continue
            pars +=  "%s%s" % (sep, arg)
            if sep == "": sep = '&#44'
            if i >= iDfl: pars += "=%s" % defaults[i-iDfl]
      except:
         pass      
      return (name, pars, doc)

   #______________________________________________________________________________________      
   def doMain(self,undoc=False,method=None):
      main = {'undoc' : undoc }
      main["taskBuffer"] = [ self.makeMethodDoc( name,obj) for name, obj in  inspect.getmembers(pmt)]
      self.publish(main)
      return 
   #______________________________________________________________________________________      
   def doScript(self,undoc=False,method=None):
      version = self.server().version().get('version')
      if version == None: version = ''
      else: version = "/~%s" % version

      func = """
         function(tag,data) {
            $(tag).empty();
            var taskBuffer = data.taskBuffer;
            var undoc = data.undoc;
            var html = "<ol>";
            var nUndocumented = 0;
            for  (var method in taskBuffer ) {
               var mn =  taskBuffer[method];
               var mname =  mn[0];
               var pars  =  mn[1];
               var doc   =  mn[2];
               if ( mname.indexOf('getProxyKey') < 0 ) { 
                   if (doc == undefined || doc == null) {  nUndocumented++;  if (! undoc) continue; doc = 'Under construction. To be documented yet!';} 
                   else {doc = "<b>" +doc+ "</b>"; }
                   html += "<li><a href='%(version)s/taskBuffer?method=" + mname+ "'>" + mname+"(" + pars + "): </a><br> " + doc;
               }
            }
            html += "</ol>";
            if (nUndocumented >0) { html += "<hr>" + nUndocumented +" undocumented  methods were found but not listed" ; } 
            $(tag).html(html);
         }
      """ % { 'version' : version }
      self.publish(func,role=pmRoles.script())
   #______________________________________________________________________________________      
   def doJson(self,method=None,undoc=False):
      """ 
          List of All <a href="https://svnweb.cern.ch/trac/panda/browser/panda-server/current/pandaserver/taskbuffer/TaskBuffer.py"> TaskBuffer Class </a>Methods
      """ 
      self._doc = None
      usr = self.server().user()
      if usr  == None:
          self.publishTitle('Only the known user can list  All TaskBuffer methods. Please, use https protocol')
          self.publish({'s-maxage':0,'max-age': 0 }, role=pmRoles.cache())
          self.publish( {} )
      else: 
         if not "fine"  in usr.lower() and not  "wenaus" in usr.lower() and undoc: 
            self.publishTitle('List of All TaskBuffer Methods for  the User &lt;%s&gt; You can not see the undocumented methods though' % usr)
            undoc=False
         else:   
            self.publishTitle('List of All TaskBuffer Methods for  the User &lt;%s&gt; ' % usr)
         self.doMain(undoc,method)
         self.publish({'s-maxage':90000,'max-age': 90000 }, role=pmRoles.cache())