""" List of the Existing  Monitor Active Modules </td><td>$Rev: 18129 $"""
# $Id: helloora.py 9690 2011-11-16 22:28:01Z fine $
# List of the Panda Monitor active modules
import sys,os
import re

from pmCore.pmModule import pmRoles
import pmUtils.pmUtils as utils

from  pmCore.pmModule import pmModule


class alist(pmModule):
   """ List the existing  modules """

    #______________________________________________________________________________________
   def __init__(self,name=None,parent=None,obj=None):
      pmModule.__init__(self,name,parent,obj)      
      self.publishUI(self.doJson)
      pattern = '.*\\.py$'
      self._lut = re.compile(pattern)

   #______________________________________________________________________________________      
   def listFiles(self,contextDir,hello,pat):
      alist = []      
      if os.path.isdir(contextDir):
         dirlist=sorted(os.listdir(contextDir))
         for f in dirlist:
            if f=='processor' or f =='system' : continue # exclude the system dirs from the list
            if hello== None and 'hello' in f: continue 
            if self._lut.match(f):
                modName = f.replace('.py','')
                if pat == None or pat.match(modName):
                  alist.append(f.replace('.py',''))
            else: alist += [ os.path.join(f,h) for h in self.listFiles(os.path.join(contextDir,f),hello,pat)]
      return alist
      
   #______________________________________________________________________________________      
   def doJson(self, hello=None,pattern=None):
      """ 
          List the Panda Monutor Modules:
          <ul>
          <li><code>hello</code> = "yes" to list the hello appplication
          <li><code>pattern</code> = regexp  pattern to list the  matched  modules only
          </ul>
      """ 
      modulesDir = os.path.dirname(utils.lineInfo(False,'%(filename)s'))
      pat = None
      if pattern != None: pat = re.compile(pattern)
      filtered = self.listFiles(modulesDir,hello,pat)
      # htmlList='<IMG SRC="http://www.mikesfreegifs.com/main4/underconstruction/coolconstr.gif" ALIGN=LEFT BORDER=0 HSPACE=10>'
      htmlList = "<table><thead><tr><th>#</th><th>Module Name</th><th>Module Description</th><th>SVN rev</th></tr></thead><tbody>"
      usr = self.server().user()
      version = self.server().version().get('version')
      if version == None: version = ''
      else: version = "/~%s" % version
      script = version
      i = 0
      for f in sorted(filtered):
         if f == 'taskBufferList' and usr == None: 
            continue
         else:
            try:
               object = pmModule.factory(f.replace(".py",""),fileonly=True); 
               doc  = object.__doc__
               if doc == None: doc = "The module is under development. It has not been documented yet"
               i = i+1
               htmlList += "<tr><td>%d</td><td>" % i
               htmlList +="<a title='Click to start the %(module)s application and see its API doc' href='%(version)s/%(module)s'>%(module)s</a>\n" % {'version':version, 'module':f}
               htmlList +="</td><td>%s</td></tr>" % doc
            except:
               # raise
               # htmlList += "<tr><td>-</td><td>"
               # htmlList +="<a title='Click to start the %(module)s application and see its API doc' href='%{script}s/%(module)s'>%(module)s</a>\n" % {'script':script, 'module':f}
               # htmlList +="</td><td>%s</td></tr>" %  f.replace(".py","").replace('/','.')
               pass
      htmlList += "</tbody></table>"
      self.publishTitle("The list of the <a href='https://twiki.cern.ch/twiki/bin/view/PanDA/PandaPlatform#API'>Panda Monitor Modules</a>")
      self.publishMain(htmlList)
      self.publish( {'s-maxage':9000,'max-age': 9000}, role=pmRoles.cache())