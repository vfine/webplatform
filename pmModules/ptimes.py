""" Timing distribution for ATLAS analysis jobs """
# $Id: helloora.py 9690 2011-11-16 22:28:01Z fine $
import sys,os
import re

from datetime import timedelta
from datetime import datetime

from pmUtils.pmState import pmstate
from pmCore.pmModule import pmRoles
import pmUtils.pmUtils as utils
import pmUtils.Stopwatch as Stopwatch

from  pmCore.pmModule import pmModule
from  pmTaskBuffer.pmTaskBuffer import pmtaskbuffer as pmt
from ctypes import *

if os.environ.get('ROOTSYS') == None: 
    os.environ['ROOTSYS'] = '/home/fine/public/root/root'
rootsys = os.environ["ROOTSYS"]
path = "%s/%s" % (rootsys, 'lib')
if path not in sys.path:
   sys.path.append(path)
if  not os.environ.has_key("LD_LIBRARY_PATH"):  os.environ["LD_LIBRARY_PATH"] = path
elif not path in os.environ["LD_LIBRARY_PATH"]: os.environ["LD_LIBRARY_PATH"] = ":".join((os.environ["LD_LIBRARY_PATH"],path))
# print sys.path

class ptimes(pmModule):
   """ Timing distribution for ATLAS analysis jobs """
    #______________________________________________________________________________________
   def __init__(self,name=None,parent=None,obj=None):
      pmModule.__init__(self,name,parent,obj)      
      self.publishUI(self.doJson)
      self._plots= 'twall,tcpu,twait,trun'
      self._app= 'prun,pathena,ganga'
      self._dimension='h1'
         
   #______________________________________________________________________________________      
   def doMain(self,app='prun,pathena,ganga',plots='twall,tcpu,twait,trun',year='last', month='last',dir=None, layout=None, width=600, height=400,log=False,options='H',block='pyrootfile'):
      connectionTime = Stopwatch.Stopwatch()
      rootout =  os.tmpnam()
      # print ' RedirectOutput=' , gSystem.RedirectOutput(rootout,'a')
      if dir==None   or dir=='':   dir = '/home/fine/panda/pandamon/static/root'
      if app==None   or app=='':   app = self._app
      if plots==None or plots=='': plots = self._plots
      if layout == None: 
         layout = { 
                  'columns': len(app.split(','))
                , 'rows'   : len(plots.split(',')) 
                  }
      else: 
         lt = layout.split('x',1)
         layout = { 'columns': lt[0].strip(), 'rows' : lt[1].strip() }
      lastMonth = False
      lastYear  = False
      try:
         if month.lower()=='last': lastMonth = True
      except:
         pass
      try:
         if year.lower()=='last': lastYear = True
      except:
         pass
      if lastMonth or lastYear: 
         dirlist=sorted(os.listdir(dir))
         filtered = []
         pattern = 'analysis_14_ALL_ALL_(%(year)s)(%(month)s)' % {'year' : '\\d{4}' if lastYear else '%04d' % year , 'month' : '\\d{2}' if lastMonth else '%02d' % month} 
         lut = re.compile(pattern)
         for f in dirlist:
            if lut.match(f): filtered.append(f)
         file = filtered[-1]
         note = file.replace('analysis_14_ALL_ALL_','').replace('.root','')
         self.publishTitle('Timing distribution for ATLAS analysis jobs in the %s.%s month' % (note[:4], note[4:] ) )
         self.publishNav('The histogram for %s %s %s.%s' % ( app,plots,note[:4], note[4:] ) ) 
      else:
         file='analysis_14_ALL_ALL_%(year)04d%(month)02d' % {'year' : year,'month':month }
         self.publishTitle('Timing distribution for ATLAS analysis jobs in the %(year}04d.%(month)02d onth' % {'year' : year,'month':month } )
         self.publishNav('The histogram for %s %s %04d.%02d' % ( app,plots,year,month ) )
      if file==None or file=='': file =  'fillrandom.root'
      name = ''
      for p in plots.split(','): 
         for a in app.split(','):
             name += "%(dim)s_%(plot)s_%(app)s," % {'dim': self._dimension,'plot' : p ,'app' : a }
      timer = Stopwatch.Stopwatch()
      #
      # Open ROOT file
      #
      if options == None: options=''
      if file[-5:] != ".root" : file += '.root'
      main = {}
      main['header'] =  ["Params","values"]
      processor = os.path.join(os.path.dirname(utils.lineInfo(False,'%(filename)s')),'processor')
      main['info'] = pmt.getPopularity(name,file,dir,options,block,path=processor) # eval(txt)
      main['width'] = width
      main['height'] = height
      main['layout'] = layout
      if log == True or isinstance(log,str) and  (log.lower()=="true" or log.lower()=="yes"): 
         main['log'] = True
      main['time'] = {}
      self.publish(main)

   #______________________________________________________________________________________      
   def doJson(self,app='prun,pathena,ganga',plots='trun,tcpu,twall,twait',year='last', month='last',dir=None, layout=None, width=320, height=160,log=True,options='H',block='pyrootfile'):
      """ 
          Timing distribution for ATLAS analysis jobs
          <br><ul>
          <li>app - comma separated list of the applications: prun,pathena,ganga
          <li>plots - the comma separated list of the plots:'twall,tcpu,twait,trun'
          <li>year - the 4 digits year to publish the plots for 
          <li>month - the 2 digits month number 1-12
          <li>dir - the local directory name to pick the input ROOT files from
          <li>layout - [columns x rows ] layout to display the multiply plots<br>
          'by default'<br>
          <code>columns</code> = number of the 'app' applications<br>
          <code>rows</code> = number of the 'plots'
          <li>width - the width of the plots in px
          <li>height - the height of the plots in px
          <li>log   - use logarithmic scale for Y-axis
          <li>options - some ROOT <a href='http://root.cern.ch/root/html534/THistPainter.html#HP01b'>Paint options</a>
          </ul>
      """ 
      timer = Stopwatch.Stopwatch()
      if dir == None:
         try:
            dir = self.server().config().analytics['times']
         except:   
            dir = '/data4/work/analysis_14/ALL/ALL'
      
      self.doMain(app,plots,year, month, dir, layout, width, height,log,options,block)
      self.publish( "%s/%s" % ( self.server().fileScriptURL(),"hello/%s.js" % "ptimes" ),role="script")

#______________________________________________________________________________________      
def leftMenu():
    """ Return html for inclusion in left menu """
    #Temporary to preserve the backward compatibility 
    txt = "<a href='%s/ptimes'>Analysis Jobs Distribution</a>" %"//pandamon.atlascloud.org"#  self.server().branchUrl()
    return txt
