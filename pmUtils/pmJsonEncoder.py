# $Id$
try:
   import json
except:
   import simplejson as json
# json.encoder.FLOAT_REPR = lambda o: format(o, '.2f')
from monitor.PandaHistogram import *
from pmData.pmHist2Json import  *
from datetime import *
class pmJsonEncoder(json.JSONEncoder):
   def default(self, obj):
      if isinstance(obj, PandaHistogram):
         return sh1f().serialize(pmHFASh1f(obj))
      # Let the base class default method raise the TypeError
      elif isinstance(obj,datetime)  or isinstance(obj,timedelta):
         return '%s' % obj
      try:
         iterable = iter(obj)
      except TypeError:
         pass
      else:
         return list(iterable)
      return json.JSONEncoder.default(self, obj)
   # def encode(self,obj):
      # if isinstance(obj, float ):  
         # if obj < 1.0:
            # txt += "%4.2f" % obj
         # else:
            # txt += "%s" %  obj
         # return txt   
      # else:
#         return json.JSONEncoder.encode(self,obj)
   