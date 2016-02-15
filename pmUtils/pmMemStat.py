# $Id: pmMemStat.py 18995 2014-05-18 21:39:04Z jschovan $

import ctypes,os
from  math import fabs,sqrt

"""
    Mixing languages in python files is not the smartest idea.
    Commenting that out.
"""

#fgUsed=0
#fgList= None
#
##define LOWEST_VAL 0.0000001                                           /*! \def
#LOWEST_VAL = */
#
#class pmMemStat:
##______________________________________________________________________________
#   def __init__(self,name):
#     self._tally =0
#     &self._last =0
#     self_min =  1.e+33
#     self._max = -1.e+33
#     if (fgList==None) fgList=[]
#     fgList.append(self)
#
##______________________________________________________________________________
#  def ~pmMemStat():
#     fgList.remove(self)
#     if len(fgList) == 0:  fgList=None
#
#
##______________________________________________________________________________
#   def start(self):
#      self._last = self.used()
#
#
##______________________________________________________________________________
#   def stop(self):
#     self._tally++
#     dif = self.used() - self._last
#
#     #printf("DEBUG >> time distance between two stops Used=%f Last=%f\n",Used(),fLast)
#     if  fabs(dif) < LOWEST_VAL: dif  = 0.0
#     if  dif < self._min:        self._min = dif
#     if  dif > self._max:        self._max = dif
#
#     self._aver += dif
#     self._rms  += (dif*dif)
#
#
##______________________________________________________________________________
#   def __str__(self):
#     if !self._tally: return
#     aver = self._aver/self._tally
#     rms  = sqrt(fabs(self._rms/self._tally - aver*aver))
#
#     #printf("DEBUG :: %.10f %d %.10f %.10f\n",self._aver,fTally,self._rms,aver)
#     if fabs(aver) < LOWEST_VAL: aver = 0.0
#     if rms        < LOWEST_VAL: rms  = 0.0
#
#     return "%40.40s(%d)%12.6f%12.6f%12.6f%12.6f" %
#            (GetName(),fTally,self._min,aver,self._max,rms)
#
##______________________________________________________________________________
#   def summary(self):
#   #define NUMTICKS (40+4*12+5)
#
#     dmin=1.e+33
#     daver=0
#     dmax=-1.e+33
#     drms=0
#     dtally=0
#
#     if not fgList == None:
#        fgList.sort()
#        printf("%40.40s%12s%12s%12s%12s\n",
#               "pmMemStat::Summary(calls)","Min ","Aver ","Max ","RMS ")
#
#        for( i=0   i < NUMTICKS   i++) printf("=")
#        printf("\n")
#
#        TListIter next(fgList)
#        pmMemStat  *m
#        for m in fgList:
#             if( m._tally == None or m._tally ==0 )  continue
#             m.Print()
#             dtally++
#             if m.self._min < dmi: dmin=m.self._min
#             if m.self._max > dmax: dmax=m.self._max
#             dmp = m._aver/m._tally
#             daver += dmp
#             drms  += fabs(m._rms/m._tally-dmp*dmp)
#
#        if dtally:
#           for( i=0   i < NUMTICKS   i++) printf("-")
#           printf("\n")
#
#           #VP daver /= dtally
#           drms   = sqrt(fabs(drms))
#           printf("%40.40s(%d)%12.6f%12.6f%12.6f%12.6f\n",
#                   "Total",(int)dtally,dmin,daver,dmax,drms)
#
#           for( i=0   i < NUMTICKS   i++) printf("=")
#           printf("\n")
#
#   #______________________________________________________________________________
#   def used(self):
#     struct mallinfo info
#     info = mallinfo()
#     return double(info.uordblks + info.usmblks)/1000000
#
#   #______________________________________________________________________________
#   def free(self):
#     struct mallinfo info
#     info = mallinfo()
#     return double(info.fordblks + info.fsmblks)/1000000
#
#   #______________________________________________________________________________
#   def progSize(self):
#      res=0
#      pid = os.getpid()
#      line = "/proc/%d/status" % pid
#      try:
#         proc = open(line,"r")
#         for line in proc:
#            if (strncmp("VmSize:",line,7)==0) :
#               proc.close()
#               char *aft=0
#               res = (strtod(line+7,&aft))
#               while ((++aft)[0]==' '){}
#               int b = 0
#               if (strncmp("kB",aft,2)==0) b = 1024
#               if (strncmp("mB",aft,2)==0) b = 1024*1024
#               if (strncmp("gB",aft,2)==0) b = 1024*1024*1024
#               res = (res*b)/(1024*1024)
#               break
#         proc.close()
#      except:
#         #    status file not found. Use ugly way via "ps"
#         static char *ps = 0
#         if (!ps) :
#             ps = (char*)malloc(25)
#             sprintf(ps,"/bin/ps -l -p %d",pid)
#         }
#         FILE *pipe = ::popen(ps,"r")
#         if (!pipe) return 0.
#
#         char   psBuf[130]
#         psBuf[0] = ' '
#         while( !feof( pipe ) ) :
#             psBuf[1]=0
#             if(!fgets( psBuf+1, 128, pipe)) continue
#         #    printf("%s\n",psBuf)
#             int ifild=0 char *c
#
#             for (c=psBuf  c[0]  c++) :
#               if (c[0]==' ' && c[1]!=' ') ifild++
#               if (ifild == 10) break
#             }
#             res = int(c+1)
#             if res: break
#           }
#         ::pclose(pipe)
#         res *=::getpagesize()/(1024.*1024.)
#      finally:
#        return res
#
#   #______________________________________________________________________________
#   def printMem(self, title=None):
#      used = self.used()
#      free = self.free()
#      exec = self.progSize()
#
#      if title !=None: printf("\nStMemStat::%s",tit)
#      printf("\t total =%10.6f heap =%10.6f and %10.6f(%+10.6f)\n",exec,used,free,used-fgUsed)
#      self.fgUsed = used
#
#   #______________________________________________________________________________
#   def PM(self):
#        used = self.used()
#        printf("\nStMemStat: ")
#        printf("pmMemStat::heap =%10.6f(%+10.6f)\n",used,used-fgUsed)
#        self.fgUsed = used

