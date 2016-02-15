#!/usr/bin/python
# $Id: pyrootfile.py 12759 2012-08-31 19:29:44Z fine $
# Serialize  ROOT objects
import sys,os
from subprocess import call

from datetime import timedelta
from datetime import datetime

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
print ' from file load os.environ["LD_LIBRARY_PATH"] = ', os.environ["LD_LIBRARY_PATH"]
if '-b' not in sys.argv: sys.argv.append( '-b' )
try:
  from ROOT import gROOT,TF1,gSystem,gStyle,TFile,TH1F,TH1,TAttFill,TAttLine,TAttMarker,TAxis,TAttAxis,TDirectory,TIter
except:
  pass

class root2json(object):
   def __init__(self):
        object.__init__(self)
   def color(self, color,opacity=0):
      tcolor = gROOT.GetColor(color)
      a =  tcolor.GetAlpha()
      sfx  = ''
      alpha = ''
      opacity = int(opacity)
      if opacity <=0 or opacity >100: opacity=15
      if opacity >0 and opacity <=100: 
         ofactor = (100-opacity)/100.
         a = a*ofactor
         sfx = 'a'
         alpha = ',%.1f' % a
      else: 
         a  = ''
      hxcolor = tcolor.AsHexString()[1:]
      return "rgb%s(%s,%s,%s%s)" % (sfx,int(hxcolor[0:2],16),int(hxcolor[2:4],16),int(hxcolor[4:6],16),alpha)
   def serialize(self,obj,strict=True):
      msg =  "No Method %s" % obj.ClassName()
      if strict: 
        raise ValueError(msg)
      else:
         print " %s --- %s " % (utils.lineUtils(), msg)
      return None

class attfill( root2json ):
   def __init__(self):
        root2json.__init__(self)
   def serialize(self,obj):
      if isinstance(obj,TAttFill):
         fillstyle =  obj.GetFillStyle() - 4000
         color =  self.color(obj.GetFillColor(),fillstyle)
         return  {    'background-color' : color
                    , 'background-style' : obj.GetFillStyle()
                 }
      else: 
         return root2json.serialize(self,obj)          
         
class attline( root2json ):
   def __init__(self):
        root2json.__init__(self)
   def serialize(self,obj):
      if isinstance(obj,TAttLine):
         lcolor = obj.GetLineColor()
         lineAttr = {  'width'  : obj.GetLineWidth()
                     , 'pattern': obj.GetLineStyle()
                 }
         lcolor = obj.GetLineColor()
         if  lcolor != 0:  lineAttr['color'] =  self.color(lcolor)
         return  lineAttr
      else: 
         return root2json.serialize(self,obj)          

class attmarker( root2json ):
   def __init__(self):
        root2json.__init__(self)
   def serialize(self,obj):
      if isinstance(obj,TAttMarker):
         return  {   'marker-color'  : self.color(obj.GetMarkerColor())
                   , 'marker-size'   : obj.GetMarkerSize()
                   , 'marker-pattern': obj.GetMarkerStyle()
                 }
      else: 
         return root2json.serialize(self,obj)          

class attaxis( root2json ):
   def __init__(self):
        root2json.__init__(self)
   def serialize(self,obj):
      if not isinstance(obj,TAttAxis): return root2json.serialize(self,obj)   
      return {
                'color' : self.color(obj.GetAxisColor())
               ,'label-color' :self.color(obj.GetLabelColor())
               ,'label-font'  :obj.GetLabelFont()
               ,'label-offset':obj.GetLabelOffset()
               ,'label-size'  :obj.GetLabelSize()
               ,'title-color' :self.color(obj.GetTitleColor())
               ,'title-font'  :obj.GetTitleFont()
               ,'title-offset':obj.GetTitleOffset()
               ,'title-size'  :obj.GetTitleSize()
               ,'division'    :obj.GetNdivisions()
             }

class axis( root2json ):
   def __init__(self):
        root2json.__init__(self)
   def serialize(self,obj):
      if not isinstance(obj,TAxis): root2json.serialize(self,obj)   
      title = obj.GetTitle()
      name = obj.GetName()
      if title == '':
         title = "<msub><mi>%s</mi><mi>%s</mi></msub>" % (name[0].upper(), name[1:])
      me =  {
                'color': self.color(obj.GetAxisColor())
               ,'style': attaxis().serialize(obj)
               ,'min'  : obj.GetXmin()
               ,'max'  : obj.GetXmax()
               ,'title': title
               ,'name' : name
             }
      if obj.IsVariableBinSize():    
         me['bins'] = obj.GetXbins()
      else:   
         me['width'] = obj.GetBinWidth(1)
      if  obj.GetTimeFormat():
         me['time']   = obj.SetTimeFormat()      
         me['offset'] = obj.SetTimeOffset()    
      labels = TIter(obj.GetLabels()) 
      alabels = []
      label = labels.Next()
      while label != None: 
         alabels.append(label.GetName())
         label = labels.Next()
      if len(alabels)>0:
         me['labels'] = alabels
      return me

class soptstat( root2json ):
   def __init__(self):
      root2json.__init__(self)
   def serialize(self,obj, opt):
      """Serialize the ROOT Opt Stat parametere for TH object accorind toaiff
         http://root.cern.ch/root/html/src/TStyle.cxx.html#HRoVzE
            The parameter mode can be = ksiourmen  (default = 000001111)
            
         k = 1;  kurtosis printed
         k = 2;  kurtosis and kurtosis error printed
         s = 1;  skewness printed
         s = 2;  skewness and skewness error printed
         i = 1;  integral of bins printed
         o = 1;  number of overflows printed
         u = 1;  number of underflows printed
         r = 1;  rms printed
         r = 2;  rms and rms error printed
         m = 1;  mean value printed
         m = 2;  mean and mean error values printed
         e = 1;  number of entries printed
      """
      optstat = gStyle.GetOptStat()
      optDisplay = {}
      for s in reversed('ksiourmen'):
         ops = optstat%10
         optstat = optstat/10
         check = False
         try:
            check = s in opt
         except:
            check = ops and ops > 0 
         if check:
            if   s == 'k': optDisplay['Kurtosis']= obj.GetKurtosis() 
            elif s == 's': optDisplay['Skewness']= obj.GetSkewness() 
            elif s == 'i': optDisplay['Total']   = obj.Integral() 
            elif s == 'm': optDisplay['Mean']    = obj.GetMean() 
            elif s == 'r': optDisplay['Rms']     = obj.GetRMS() 
            elif s == 'e': optDisplay['Entries'] = int(obj.GetEntries())
      return optDisplay
         
class sh1f( root2json ):
   def __init__(self):
        root2json.__init__(self)
   def serialize(self,obj):
      if not isinstance(obj,TH1): return root2json.serialize(self,obj)    
      style=  {}
      style.update(attmarker().serialize(obj))
      style.update(attline().serialize(obj))
      style.update(attfill().serialize(obj))
      bins = []
      data = {'bins' : bins }
      property ={}
      attr = {
                'dimension' : obj.GetDimension()
               ,'name'      : obj.GetName()
               ,'title'     : obj.GetTitle()
               ,'style'     : style
               ,'xaxis'     : axis().serialize(obj.GetXaxis())  
               ,'yaxis'     : axis().serialize(obj.GetYaxis())
               ,'options'   : obj.GetOption()
             }
      if obj.GetXaxis().GetLabels():
         nx = range(1,obj.GetNbinsX()+1)
         property['underflow'] = obj.GetBinContent(0)
      else:
         nx = range(1,obj.GetNbinsX())
         property['underflow'] = obj.GetBinContent(0)
         property['overflow']  = obj.GetBinContent(obj.GetNbinsX()+1)
      property.update(soptstat().serialize(obj,'i'))
      for i in nx:
         bins.append(obj.GetBinContent(i))
      if len(property) > 0: data['property'] = property  
      me =  { 'class' : 'h1f'
             ,'data'  : data
             ,'attr'  : attr
            }
      return me
class directory( root2json ):
   def __init__(self):
        root2json.__init__(self)
   def serialize(self,obj):
      if not isinstance(obj,TDirectory): return root2json.serialize(self,obj,False)
      keys = TIter(obj.GetListOfKeys())
      nxtkey = keys.Next()
      me  = { 'class' : 'directory', 'data' : [] }
      data = me['data']
      while nxtkey != None:
         if 'TH1' in nxtkey.GetClassName():
            data.append({nxtkey.GetClassName(): nxtkey.GetName()})
         nxtkey = keys.Next()
         
      return me      
class pyrootfile(object):

    #______________________________________________________________________________________
   def __init__(self,outfile=None):
      object.__init__(self)
      self._file = open(outfile,"w");
   #______________________________________________________________________________________      
   def doMain(self,name='h1f',file='fillrandom.root', dir='/home/fine/panda/pandamon/static/root',options=''):
      if dir==None or dir=='': dir = '/home/fine/panda/pandamon/static/root'
      if file==None or file=='': file =  'fillrandom.root'
      #
      # Open ROOT file
      #
      info = [["Root File","%s" % file ]]
      rootfile = TFile.Open( "%s/%s" % (dir,file) )
      info.append(['File',directory().serialize(rootfile)]) 
      hnames = name.split(",")
      rhists = []
      lineColor = None
      try:
         for h in hnames:
              
               if h==None or h.strip() == '': continue
               h1f = rootfile.Get(h)
               try:
                  hColor = h1f.GetLineColor();
                  if hColor == lineColor:
                     fillColor = h1f.GetFillColor()
                     h1f.SetLineColor(fillColor)
                  lineColor = hColor  
                  h2sell = sh1f().serialize(h1f)
                  h2sell['attr']['options'] += options
                  rhists.append(h2sell)
               except:
                  pass
         info.append(['Histogram', rhists])
      except:
         print "Can't serialize %s from %s" % (h, hnames)
         pass
      rootfile.Close()   
      rootfile = None
      print >>self._file, info
      self._file.close()
      return info

if __name__ == '__main__':
   if len(sys.argv) < 1: 
       sys.stderr.write('Usage: sys.argv[0]  %s ' % sys.argv ) 
       sys.exit(1)
   me = sys.argv[0]
   if sys.argv[1] == '-e': 
      pars = []
      for p in sys.argv:
         if p != '-e': pars.append(p)
      call(pars)
   else: 
        p = pyrootfile(sys.argv[1])
        p.doMain(sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5])
