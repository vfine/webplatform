# $Id: helloora.py 9690 2011-11-16 22:28:01Z fine $
# Display DB status and stats
import sys,os
from subprocess import call

from datetime import timedelta
from datetime import datetime

from pmUtils.pmState import pmstate
from pmCore.pmModule import pmRoles
import pmUtils.pmOracle as pdb
import pmUtils.pmUtils as utils
import pmUtils.Stopwatch as Stopwatch

from  pmCore.pmModule import pmModule
from ctypes import *

if os.environ.get('ROOTSYS') == None: 
    os.environ['ROOTSYS'] = '/home/fine/public/root/root'
rootsys = os.environ["ROOTSYS"]
path = "%s/%s" % (rootsys, 'lib')
if path not in sys.path:
   sys.path.append(path)
if  not os.environ.has_key("LD_LIBRARY_PATH"):  os.environ["LD_LIBRARY_PATH"] = path
elif not path in os.environ["LD_LIBRARY_PATH"]: os.environ["LD_LIBRARY_PATH"] = ":".join((os.environ["LD_LIBRARY_PATH"],path))
print sys.path

class pyroot(pmModule):
   """ ROOT Histogram  Object as Data Source Example """

   #______________________________________________________________________________________
   def __init__(self,name=None,parent=None,obj=None):
      pmModule.__init__(self,name,parent,obj)      
      self.publishUI(self.doJson)
   
         
   #______________________________________________________________________________________      
   def doMain(self,name='h1f',file='fillrandom', dir='/home/fine/panda/pandamon/static/root', width=600, height=400,log=False,options='H',block='pyrootfile'):
      connectionTime = Stopwatch.Stopwatch()
      rootout =  os.tmpnam()
      print "-------------- rootout=", rootout
      # print ' RedirectOutput=' , gSystem.RedirectOutput(rootout,'a')
      if dir==None or dir=='': dir = '/home/fine/panda/pandamon/static/root'
      if file==None or file=='': file =  'fillrandom.root'
      timer = Stopwatch.Stopwatch()
      #
      # Open ROOT file
      #
      if options == None: options=''
      print utils.lineInfo(), block
      if block=='pyrootfile':
         if file[-5:] != ".root" : file += '.root'
         call(['/home/fine/panda/pandamon/pmModules/processor/%s.py' % block, rootout, name,file,dir,options])
      elif block=='pandsusers':
         dir = '/home/fine/panda/pandamon/static/data'
         if file == 'fillrandom': file='useact180days'
         call(['/home/fine/panda/pandamon/pmModules/processor/%s.py' % block, rootout, file,dir,options])
      r4panda  = open(rootout)
      txt = r4panda.readlines()[0][:-1]
      r4panda.close()
      os.remove(rootout)
      main = {}
      main['header'] =  ["Params","values"]
      main['info'] = eval(txt)
      main['width'] = width
      main['height'] = height
      if log == True or isinstance(log,str) and  (log.lower()=="true" or log.lower()=="yes"): 
         main['log'] = True
      main['time'] = {}
      self.publish(main)

   #______________________________________________________________________________________      
   def doJson(self,name='h1f',file='fillrandom', dir='/home/fine/panda/pandamon/static/root',width=600, height=400, log=False,options='H',block='pyrootfile'):
      """ 
          Histogram  Object Rendering Example
          <br><ul>
          <li>name - name of the ROOT histogram
          <li>file - name of the ROOT file the  histogram ' name' should be read from
          <li>dir - the directory on the file server 
          <li>width - the width of the plots in px
          <li>height - the height of the plots in px
          <li>log   - use logarithmic scale for Y-axis
          <li>options - some ROOT <a href='http://root.cern.ch/root/html534/THistPainter.html#HP01b'>Paint options</a>
          </ul>
      """ 
      self.publishTitle('Histogram object example' )
      timer = Stopwatch.Stopwatch()
      self.doMain(name, file, dir, width, height,log,options,block)
      if file == 'fillrandom': file='useact180days.json'
      self.publishNav('The histogram from "%s/%s".  "%s"' % ( dir,file , timer ) ) # I know the cyber security will be mad ;-) VF.
      self.publish( "%s/%s" % ( self.server().fileScriptURL(),"hello/%s.js" % "pyroot" ),role="script")

#______________________________________________________________________________________      
def leftMenu():
    """ Return html for inclusion in left menu """
    #Temporary to preserve the backward compatibility 
    txt = "<a href='%s/pyroot'>Hello Histogram Objects</a>" % self.server().branchUrl()
    return txt
