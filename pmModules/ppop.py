""" Project and Data Type Popularity for ATLAS Analysis Jobs  </td><td>$Rev: 14508 $"""
# $Id: helloora.py 9690 2011-11-16 22:28:01Z fine $
# Display DB status and stats
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

class ppop(pmModule):
   """ Project and Data Type Popularity for ATLAS Analysis Jobs  </td><td>$Rev: 14508 $"""

    #______________________________________________________________________________________
   def __init__(self,name=None,parent=None,obj=None):
      pmModule.__init__(self,name,parent,obj)      
      self.publishUI(self.doJson)
      self._plots= 'data_mc,user'
         
   #______________________________________________________________________________________      
   def doMain(self,plots='mc_data,user',year='last', month='last',dir='/data4/work/analysis_15/ALL/ALL', layout=None, width=440, height=240,log=False,options='H',block='pyrootfile'):
      connectionTime = Stopwatch.Stopwatch()
      rootout =  os.tmpnam()
      # print ' RedirectOutput=' , gSystem.RedirectOutput(rootout,'a')
      if dir==None   or dir=='':   dir = '/home/fine/panda/pandamon/static/root'
      if plots==None or plots=='': plots = self._plots
      if layout == None: 
         layout = { 
                  'columns': len(plots.split(','))
                , 'rows'   : 1 
                  }
      else: 
         lt = layout.split('x',1)
         layout = { 'columns': int(lt[0].strip()), 'rows' : int(lt[1].strip()) }
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
      dirlist=sorted(os.listdir(dir))
      filtered = []
      filteredAll = []
      pattern = 'analysis_15_ALL_ALL_(%(year)s)(%(month)s)(.root)$' % {'year' : '\\d{4}' if lastYear else '%04d' % year , 'month' : '\\d{2}' if lastMonth else '%02d' % month} 
      patternAll = 'analysis_15_ALL_ALL_(%(year)s)(%(month)s)(.root)$' % {'year' : '\\d{4}', 'month' : '\\d{2}' } 
      lut = re.compile(pattern)
      lutAll = re.compile(patternAll)
      years = {}
      for f in dirlist:
         if lut.match(f): filtered.append(f)
         yearmm =  lutAll.match(f)
         if yearmm: 
            filteredAll.append(f)
            yymm = yearmm.groups()
            if not years.has_key(yymm[0]): years[yymm[0]] = []
            years[yymm[0]].append(yymm[1])
      if lastMonth or lastYear: 
         file = filtered[-1]
         note = file.replace('analysis_15_ALL_ALL_','').replace('.root','')
         self.publishTitle('Project and Data Type Popularity for ATLAS Analysis Jobs in the %s.%s Month' % (note[:4], note[4:] ) )
         self.publishNav('The Projects for %s %s.%s' % ( plots,note[:4], note[4:] ) ) 
      else:
         file='analysis_15_ALL_ALL_%(year)04d%(month)02d' % {'year' : year,'month':month }
         self.publishTitle('Project and Data Type Popularity for ATLAS Analysis Jobs in the %04d.%02d Month' % (year,month ) )
         self.publishNav('The Projects for "%s" in %04d.%02d' % ( plots,year,month ) )
      name = plots
      timer = Stopwatch.Stopwatch()
      #
      # Open ROOT file
      #
      if options == None: options=''
      if file[-5:] != ".root" : file += '.root'
      main = {}
      main['header'] =  ["Params","values"]
      processor = os.path.join(os.path.dirname(utils.lineInfo(False,'%(filename)s')),'processor')
      info =  pmt.getPopularity(name,file,dir,options,block,path=processor)
      for i in info:
         if  not 'Histogram' in i[0]: continue
         try:
          hists = i[1]
          for h in hists:
            property = h['data']['property']   
            property['xbound'] = 20
            title = h['attr']['title']
            if 'type' in title: h['attr']['xaxis']['title'] = 'Project and Type'
            else:  h['attr']['xaxis']['title'] = 'Project'
            h['attr']['yaxis']['title'] = 'Jobs'
         except: pass
      main['info']   = info
      main['files']  = filteredAll
      main['months'] = years
      main['width']  = width
      main['height'] = height
      main['layout'] = layout
      if log == True or isinstance(log,str) and  (log.lower()=="true" or log.lower()=="yes"): 
         main['log'] = True
      main['time'] = {}
      self.publish(main)

   #______________________________________________________________________________________      
   def doJson(self,plots='mc_data,user',year='last', month='last',dir=None, layout=None, width=440, height=240,log=True,options='H',block='pyrootfile'):
      """ 
          Project and Data Type Popularity for ATLAS Analysis Jobs
          <br><ul>
          <li>plots - the comma separated list of the plots:'mc_data,user'
          <li>year - the 4 digits year to publish the plots for 
          <li>month - the 2 digits month number 1-12
          <li>dir - the local directory name to pick the input ROOT files from
          <li>layout - [columns x rows ] layout to display the multiply plots<br>
          'by default'<br>
          <code>columns</code> = number of the 'plots'<br>
          <code>rows</code> = 1
          <li>width - the width of the plots in px
          <li>height - the height of the plots in px
          <li>log   - use logarithmic scale for Y-axis
          <li>options - some ROOT <a href='http://root.cern.ch/root/html534/THistPainter.html#HP01b'>Paint options</a>
          </ul>
      """ 
      if dir == None:
         try:
            dir = self.server().config().analytics['popularity']
         except:
            dir = '/data4/work/analysis_15/ALL/ALL'
      timer = Stopwatch.Stopwatch()
      self.doMain(plots,year, month, dir, layout, width, height,log,options,block)
      self.publish( "%s/%s" % ( self.server().fileScriptURL(),"hello/%s.js" % "ppop" ),role="script")

#______________________________________________________________________________________      
def leftMenu():
    """ Return html for inclusion in left menu """
    #Temporary to preserve the backward compatibility 
    txt = "<a href='%s/ppop'>Popularity</a>" % "//pandamon.atlascloud.org" # self.server().branchUrl()
    return txt
