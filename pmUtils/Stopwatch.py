#!/usr/bin/python
# $Id: Stopwatch.py 11376 2012-04-12 00:38:32Z fine $
#
class Stopwatch(object):
   """ Stopwatch class. This class returns the real and cpu time between 
      the start and stop events. The class mimic the ROOT C++ TStopwatch class
      (see : http://root.cern.ch/root/html528/TStopwatch.html )      
   """      
#________________________________________________________________________________________      
   def getRealTime(cls):  
      " Return  the walltime CPU time  "
      import time
      return time.time()

#________________________________________________________________________________________      
   def getCPUTime(cls):
      " Return (on Unix) the CPU time  "
      import resource      
      return resource.getrusage(resource.RUSAGE_SELF)[0] # time in user mode (float)
      
   getRealTime = classmethod(getRealTime)      
   getCPUTime  = classmethod(getCPUTime)      
#________________________________________________________________________________________      
   def checkState(self):
      """ Check the object status 
      """
      if self.state == None: raise ValueError("Stopwatch not started")
#________________________________________________________________________________________      
   def __init__(self,start=True):
      """ Create a Stopwatch and start it if start == True. 
      """
      object.__init__(self)
      # if gTicks <= 0.0:  gTicks = os.sysconf("SC_CLK_TCK")
      self.counter = 0
      self.startCpuTime = 0.0 
      self.startRealTime = 0.0
      self.state =None           # Stopwatch state 'u', 's', 'r' 'u' - undefined, 's' - stopped, 'r' - running
      self.stopCpuTime=0.0       # cpu stop time 
      self.stopRealTime=0.0      # wall clock stop time 
      self.totalCpuTime=0.0      # total cpu time 
      self.totalRealTime=0.0     # total real time 
      self.kRunning ='r'
      self.kStopped ='s'
      
      if start: self.start()
      else:     self.reset()
#________________________________________________________________________________________      
   def copy(self):
      import copy
      return copy.copy(self)
#________________________________________________________________________________________      
   def keep(self):
      """ Resume a stopped Stopwatch. The Stopwatch continues counting from the last
          start() onwards (this is like the laptimer function).
      """

      self.checkState()
      if self.state == self.kStopped:
         self.totalCpuTime  -= self.stopCpuTime  - self.startCpuTime
         self.totalRealTime -= self.stopRealTime - self.startRealTime

      self.state = self.kRunning
      
#________________________________________________________________________________________      
   def cpuTime(self): 
      """ Return the cputime passed between the start and stop events. If the
          Stopwatch was still running stop it first.
          See keep() method to resume the Stopwatch
      """   
      self.checkState()
      if self.state == self.kRunning:   self.stop();
      return self.totalCpuTime;
#________________________________________________________________________________________      
   def cpu(self): 
      """ Return the cputime passed between the start and stop events. If the
          Stopwatch was still running stop it first.
          See keep() method to resume the Stopwatch
      """ 
      return self.cpuTime()      
      
#________________________________________________________________________________________      
   def wall(self): 
      """ Return the realtime passed between the start and stop events. If the
          Stopwatch was still running stop it first.
          See keep() method to resume the Stopwatch
      """ 
      return self.realTime()

   #________________________________________________________________________________________      
   def realTime(self): 
      """ Return the realtime passed between the start and stop events. If the
          Stopwatch was still running stop it first.
          See keep() method to resume the Stopwatch
      """ 
      self.checkState()
      if self.state == self.kRunning:  self.stop();
      return self.totalRealTime;
#________________________________________________________________________________________      
   def reset(self): 
      self.resetCpuTime()
      self.resetRealTime();
#________________________________________________________________________________________      
   def resetCpuTime(self,time = 0.0) :
      self.stop();  
      self.totalCpuTime = float(time)
#________________________________________________________________________________________      
   def resetRealTime(self,time = 0.0):
      self.stop();  
      self.totalRealTime = float(time)
#________________________________________________________________________________________      
   def start(self,reset = True):
      """ Start the Stopwatch. 
          If reset is True  reset the Stopwatch before starting it (including the Stopwatch counter). 
          Use False to continue timing after a Stop() without  resetting the Stopwatch. 
      """     
      if reset:
         self.state         = None
         self.totalCpuTime  = 0.0
         self.totalRealTime = 0.0
         self.counter       = 0

      if self.state == None or self.state != self.kRunning:
         self.startRealTime = Stopwatch.getRealTime()
         self.startCpuTime  = Stopwatch.getCPUTime()

      self.state = self.kRunning
      self.counter += 1
      
#________________________________________________________________________________________      
   def stop(self): 
      """ 
         Stop the Stopwatch. 
         See keep() method to resume the Stopwatch
     """
      self.stopRealTime = Stopwatch.getRealTime();
      self.stopCpuTime  = Stopwatch.getCPUTime();
      if self.state == self.kRunning:
         self.totalCpuTime  += self.stopCpuTime  - self.startCpuTime
         self.totalRealTime += self.stopRealTime - self.startRealTime

      self.state = self.kStopped
#_________________________________________________________________________________________
   def printme(self,opt=None):
      """  Print the real and cpu time passed between the start and stop events.
           and the number of times (slices) this TStopwatch was called
           (if this number > 1). If opt="m" print out realtime in milli second
           precision. If opt="u" print out realtime in micro second precision.
      """     
      saveState = self.state
      if saveState != self.kStopped: self.stop()
      realt = self.realTime();
      cput  = self.cpuTime();

      savet = realt
      hours  = int(realt / 3600)
      realt -= hours * 3600
      min    = int(realt / 60.);
      realt -= min * 60;
      sec    = int(realt);

      if realt < 0: realt = 0
      if cput  < 0: cput  = 0
      nicetxt = ''
      if opt and opt == 'm': 
         if self.counter > 1:
            nicetxt = "Elapsed %02d:%06.3f CPU %.2fs Slices %d" % ( min, realt, cput, self.counter )
         else:
            nicetxt =  "Elapsed %02d:%06.3f CPU %.2fs" %  (min, realt, cput)
      elif opt and opt == 'u': 
         if self.counter > 1:
            nicetxt= "Elapsed %02d:%09.6f CPU %.2fs Slices %d" %( min, realt, cput, self.counter)
         else:
            nicetxt = "Elapsed %02d:%09.6f CPU %.2fs" % ( min, realt, cput);
      else:
         if self.counter > 1:
            nicetxt= "Elapsed %.2fs CPU %.2fs Slices %d" % (savet, cput, self.counter)
         else:
            nicetxt = "Elapsed %.2fs CPU %.2fs" % ( savet, cput)
      if saveState != self.kStopped: self.keep()
      return nicetxt
      
#________________________________________________________________________________________      
   def __str__(self):
      return self.printme()
      
def clockit(func):
    """Function decorator that times the evaluation of *func* 
       Returns the tuple with function value and its execution time.
    """
    def new(*args, **kw):
        t = Stopwatch()
        retval = func(*args, **kw)
        t.stop()
        return retval,t
    return new
    
# ---------------------------  Simple demo and tests  -------------------------
if __name__ == '__main__':
   import time
   t = Stopwatch();
   for i in range(100000): 
      j=i*i/2.0
   time.sleep(10)

   print "\n - 10000 cycles and 10 secs sleeping=", t.wall()
   t.keep()
   t2 = Stopwatch();
   for i in range(1000000): 
      j=i*i/2.0
   time.sleep(15)

   print "\n - additional 1000000 cycles and additional 15 secs sleeping=", t.wall(), "CPU=", t.cpu()
   print "\n - 1000000 cycles and 15 secs sleeping alone=", t2
   @clockit   
   def timed_multiply(a, b):
      for i in range(1000000):
         c = a * b *i/2.0
      return "1000000 operations have been completed"   
   print  "%s %s" % timed_multiply(3,b=4)
   print " Check copy"
   ct2 = t2.copy()
   print "Copy=", ct2, "; original=", t2
      
   
