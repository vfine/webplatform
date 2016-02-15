# $Id$
class pmHistFacad(object):
   def __init__(self,pandaHist):
      object.__init__(self)
      if isinstance(pandaHist,pmHistFacad):
         self._pmHist = pandaHist.hist()
      else:   
         self._pmHist = pandaHist
   def hist(self):
      return self._pmHist
   def GetTitle(self):
      return self.hist().getTitle()
   def GetName(self):
      return self.hist().getName()
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

class pmHFAttfill( pmHistFacad ):
   def __init__(self,pandaHist):
        pmHistFacad.__init__(self,pandaHist)
   def GetFillStyle(self):
      return 0
   def GetFillColor(self):
      return 0
         
class pmHFAttline( pmHistFacad ):
   def __init__(self,pandaHist):
        pmHistFacad.__init__(self,pandaHist)
   def GetLineColor(self):
      return 1
   def GetLineWidth(self):
      return 1
   def GetLineStyle(self):
      return 1

class pmHFAttmarker( pmHistFacad ):
   def __init__(self,pandaHist):
        pmHistFacad.__init__(self,pandaHist)
   def GetMarkerColor(self):
      return 1
   def GetMarkerSize(self):
      return 1
   def GetMarkerStyle(self):
      return 1

class pmHFAttaxis( pmHistFacad ):
   def __init__(self,pandaHist):
        pmHistFacad.__init__(self,pandaHist)
   def GetLabelColor(self):
      return ''
   def GetAxisColor(self):
      return ''
   def GetLabelFont(self):
      return ''
   def GetLabelSize(self):
      return 1
   def GetLabelOffset(self):
      return ''
   def GetTitleColor(self):
      return ''
   def GetTitleFont(self):
      return ''
   def GetTitleOffset(self):
      return ''
   def GetTitleSize(self):
      return ''
   def GetNdivisions(self):
      return ''
      

class pmHFAxis( pmHistFacad ):
   def __init__(self,pandaHist):
        pmHistFacad.__init__(self,pandaHist)
   def GetAxisColor(self):
       return ''
   def GetXmin(self):
      return self.hist().minb()
   def GetXmax(self):
      return self.hist().maxb()
   def GetXbins(self):
      return self.hist().getBinCenters()
   def SetTimeFormat(self):
      return 'time'
   def GetBinWidth(self,ibin):
      return self.hist().width()
   def SetTimeOffset(self):
      return 0
   def GetTimeFormat(self):
      tmode = self.hist().mode()
      if tmode == 'time': return tmode      
      else: return None
   def GetLabels(self):
      if self.hist().mode() == 'name':
         return self.hist().getBinCenters()
      else:   
         return None   
   def IsVariableBinSize(self):
      return False
   def GetTitle(self):
      return self.hist().getTitle()
   def GetName(self):
      return self.hist().getName()
      
class pmHFXAxis( pmHFAxis ):
   def __init__(self,pandaHist):
        pmHFAxis.__init__(self,pandaHist)
   def GetAxisColor(self):
       return ''
   def GetXmin(self):
      return self.hist().minb()
   def GetXmax(self):
      maxb = self.hist().maxb()
      if self.hist().mode() == 'name': maxb += 1
      return maxb
   def GetXbins(self):
      return self.hist().getBinCenters()
   def SetTimeFormat(self):
      return 'time'
   def GetBinWidth(self,ibin):
      return self.hist().width()
   def SetTimeOffset(self):
      return 0
   def GetTimeFormat(self):
      tmode = self.hist().mode()
      if tmode == 'time': return tmode      
      else: return None
   def GetLabels(self):
      if self.hist().mode() == 'name':
         return self.hist().getBinCenters()
      else:
         return None   
   def IsVariableBinSize(self):
      return False
   def GetTitle(self):
      if self.GetTimeFormat() == 'time':
         return 'time'
      else:
         return 'errors'
   def GetName(self):
      return 'x-axis'

class pmHFYAxis( pmHFAxis ):
   def __init__(self,pandaHist):
        pmHFAxis.__init__(self,pandaHist)
   def GetAxisColor(self):
       return ''
   def GetXmin(self):
      return 0
   def GetXmax(self):
      return None
   def GetXbins(self):
      return None
   def SetTimeFormat(self):
      return None
   def GetBinWidth(self,ibin):
      return None
   def SetTimeOffset(self):
      return None
   def GetTimeFormat(self):
      return None
   def GetLabels(self):
      return None   
   def IsVariableBinSize(self):
      return False
   def GetTitle(self):
      return  "<msub><mi>%s</mi><mi>%s</mi></msub>" % ('Jobs', 'failed')
   def GetName(self):
      return 'y-axis'
      
class pmHFSoptstat( pmHistFacad ):
   def __init__(self,pandaHist):
      pmHistFacad.__init__(self,pandaHist)
   def GetOptStat(self):
      return None
   def GetKurtosis(self):
      return None
   def GetSkewness(self): 
      return None
   def Integral(self): 
      return self.hist().integral()
   def GetMean(self): 
      return None
   def GetRMS(self): 
      return None
   def GetEntries(self):
      return self.hist().entries()
         
class pmHFASh1f( pmHistFacad ):
   def __init__(self,pandaHist):
        pmHistFacad.__init__(self,pandaHist)
   def GetDimension(self):
      return 1
   def GetXaxis(self): 
       return pmHFXAxis(self.hist())
   def GetYaxis(self):
       return pmHFYAxis(self.hist())
   def GetOption(self):
       return  'SB'
   def GetNbinsX(self):
      return self.hist().nBin()
   def GetUnderflow(self):
      return self.hist().getUnderflow()
   def GetOverflow(self):
      return self.hist().getOverflow()
   def GetBinContent(self,ibin):
      return self.hist()[ibin]
       
   
