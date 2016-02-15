#!/usr/bin/python
# $Id: pandsusers.py 11885 2012-05-18 20:10:18Z fine $
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
  from ROOT import gROOT,TF1,gSystem, gDirectory, TFile,TH1F,TH1,TAttFill,TAttLine,TAttMarker,TAxis,TAttAxis,TDirectory,TIter,gStyle,TDatime
except:
  pass
#_____________________________________________________________________  
def total_seconds (td, offset=0):
   return td.seconds + (td.days+offset) * 24 * 3600
  
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
         print " %s --- %s " % ('55', msg)
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
         return  {   'color'  : self.color(obj.GetLineColor())
                   , 'width'  : obj.GetLineWidth()
                   , 'pattern': obj.GetLineStyle()
                 }
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
      if  obj.GetTimeDisplay():
         me['time']   = obj.GetTimeDisplay() 
         me['offset'] = gStyle.GetTimeOffset()
      labels = TIter(obj.GetLabels()) 
      alabels = []
      label = labels.Next()
      while label != None: 
         alabels.append(label.GetName())
         label = labels.Next()
      if len(alabels)>0:
         me['labels'] = alabels
      return me

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
      data = {
                'dimension' : obj.GetDimension()
               ,'bins'      : bins
               ,'name'      : obj.GetName()
               ,'title'     : obj.GetTitle()
               ,'style'     : style
               ,'xaxis'     : axis().serialize(obj.GetXaxis())  
               ,'yaxis'     : axis().serialize(obj.GetYaxis())
               ,'options'   : obj.GetOption()
             }
      if obj.GetXaxis().GetLabels():
         nx = range(1,obj.GetNbinsX()+1)
         data['underflow'] = obj.GetBinContent(0)
      else:
         nx = range(1,obj.GetNbinsX())
         data['underflow'] = obj.GetBinContent(0)
         data['overflow'] = obj.GetBinContent(obj.GetNbinsX()+1)
      for i in nx:
         bins.append(obj.GetBinContent(i))
      me =  { 'class' : 'h1f'
             ,'data'  : data
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
class pandusers(object):

    #______________________________________________________________________________________
   def __init__(self,outfile=None):
      object.__init__(self)
      self._file = open(outfile,"w");
      
   #______________________________________________________________________________________      
   def doMain(self,file='useact', dir='/home/fine/panda/pandamon/static/data',options='',dateformat='%y%m%d'):
      if dir==None or dir=='': dir = '/home/fine/panda/pandamon/static/root'
      if file==None or file=='': file =  'fillrandom.root'
      false = False
      null = None
      try:
         f = open("%s/%s.json" % (dir,file))
         print f
      except: 
         raise
      info = []   
      info = [["JSON File","%s" % file ]]
      try:
         jdata = eval(f.read())
      except: 
         raise
      data = jdata['pm'][0]['json']['buffer']['data']
      header = data[0]
      rows =  data[1]
      timeOffset = 0
      minTime = None
      maxTime = None
      for i,r in  enumerate(rows):
         if i == 0: 
            minTime =  datetime.strptime("%s" % r[0],dateformat)
            maxTime = minTime
         timeStamp = datetime.strptime("%s" % r[0],dateformat)
         if timeStamp < minTime: minTime = timeStamp
         if timeStamp > maxTime: maxTime = timeStamp
      maxTime += timedelta(days=1)
      timeOffset =  minTime
      duration = total_seconds(maxTime-minTime)
      nbins = (maxTime-minTime).days 
      h = TH1F( file, 'The PANDA users activity for the last %s days ' % (duration/(3600*24)-1), nbins,0,duration)
      for r in  rows:
        time =  total_seconds(datetime.strptime("%s" % r[0],dateformat) - timeOffset + timedelta(hours=12))
        h.Fill(time);

      h.GetYaxis().SetTitle("Users")
      xaxis = h.GetXaxis()
      xaxis.SetTimeDisplay(1)
      da = TDatime(timeOffset.year,timeOffset.month,timeOffset.day,0,0,0).Convert();
      xaxis.SetTimeOffset(da)
      gStyle.SetTimeOffset(da)
      xaxis.SetTitle("%s" % maxTime.year)  
      
      rootfile = gDirectory
      info.append(['File',directory().serialize(rootfile)]) 
      lineColor = None
      rhists = []
      if True:        
         h1f = h
         hColor = h1f.GetLineColor();
         if hColor == lineColor:
            fillColor = h1f.GetFillColor()
            h1f.SetLineColor(fillColor)
         lineColor = hColor  
         h2sell = sh1f().serialize(h1f)
         h2sell['data']['options'] += options
         rhists.append(h2sell)         
      info.append(['Histogram', rhists])
      info.append(['Name',"<b>%s</b>" % h1f.GetName()])
      info.append(['Title',"<b>%s</b>" % h1f.GetTitle()])
      nx = range(1,h1f.GetNbinsX())
      info.append(['integral',h1f.Integral()])
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
        p = pandusers(sys.argv[1])
        p.doMain(sys.argv[2],sys.argv[3],sys.argv[4])
