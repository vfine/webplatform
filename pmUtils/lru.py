#!/usr/bin/python
# -*- coding:utf-8 -*-
"""
    Author:cleverdeng
    E-mail:clverdeng@gmail.com
    $Id: lru.py 15385 2013-05-06 23:29:29Z fine $
"""
# from __future__ import with_statement

import threading
import time, copy
from functools import wraps
from functools import update_wrapper
from decorator import decorator

class LruCache(object):
    def __init__(self, item_max=1000, factor=600, grace=10):
        if item_max <=0:
             raise ValueError('item_max must be > 0')
        self.lock = threading.Lock()
        self.item_max = item_max
        self._time = time.time()
        self._factor = factor
        self._grace = grace
        self.clear()

    def clear(self):
        self.hits = 0
        self.miss = 0
        self.cache = {}
        self.keys = []
        self.used = 0
        self.remove = 0

    def _warp(self, f,*args, **kwargs):
       mytime = int( (time.time() -  self._time) ) 
       key = "%s:%s" % (f.func_name, repr((args,  frozenset(kwargs.iteritems())))[70:])
       result = self[key]
       if result == None or result[1] < mytime:
          # print " 39", result, mytime
          factor = kwargs.get('_factor')
          if factor == None: factor= self._factor
          else: del kwargs['_factor']             
          expiration = mytime +  factor          
          grace = kwargs.get('_grace')
          if grace == None: grace= self._grace
          else: del kwargs['_grace']             
          res = f(*args, **kwargs)
          result = (res,expiration,grace)
          r =  copy.deepcopy(res)
          self[key] = result
          result = (r,expiration,grace) 
       return result[0]

    def fn_cache(self, fn):
        return decorator(self._warp, fn)

    def prefetch(self,key, fn, *args, **kwargs):
#       with stachfnlock:
#           next = stack.pop();
       result = fn(*args, **kwargs)
       self[key] = result
    
    def __getitem__(self, key):
        return self.get(key)


    def __setitem__(self, key, value):
        self.put(key, value)


    def get(self, key, default=None):
        with self.lock:
            if key in self.cache:
                self.hits += 1
                self.__lru_key(key)
                return copy.deepcopy(self.cache[key])
            else:
                self.miss += 1
                d = copy.deepcopy(default) if default != None else default
                return d


    def put(self, key, val):
        with self.lock:
            oldKey = self.cache.has_key(key)
            self.cache[key] = val
            if oldKey==None: 
               if self.used == self.item_max:
                  # remove the oldest key from 'keys' and from 'cache'
                  try:
                     r_key = self.keys.pop()
                     self.cache.pop(r_key)
                  except:
                     raise ValueError("Cache error:  key size=%s cache size=%s used=%s max=%s" % ( len(self.keys), len(self.cache), self.used, self.item_max) )
                  self.remove += 1
               else:
                  self.used += 1
            self.__lru_key(key)


    def __lru_key(self, key=None):
      if key:   
         if key in self.keys:
            self.keys.remove(key)
         self.keys.insert(0, key)


    def status(self):
        used_status = """
Single process cache used status:
    max:%s
    used:%s
    key:%s
    miss:%s
    hits:%s
    remove:%s
""" % (self.item_max, self.used, ','.join(self.keys), self.miss, self.hits, self.remove)
        print used_status
        
if __name__ == '__main__':
   """
       Author:cleverdeng
       E-mail:clverdeng@gmail.com
   """
   lru = LruCache(item_max=5,factor=10)

   @lru.fn_cache
   def test_fn(x,y):
       return x,y

   print test_fn(1,2,_factor=7)
   time.sleep(5)
   print test_fn(1,2)
   print test_fn(1,2)
   time.sleep(12)
   print test_fn(1,2)
   lru.status()
   print test_fn(3,4)
   print 'get key:test1 value:%s' % lru.get("test1") 
   lru.put('test1', 1)
   lru.put("test2", 2)
   lru.put("test3", 3)
   lru.put("test4", 4)
   lru.put("test5", 5)
   print 'get key:test1 value:%s' % lru.get("test1") 
   lru.put("test6", 6)
   lru.put("test7", 7) 
   print 'get key:test6 value:%s' % lru.get("test6") 
   print 'get key:test3 value:%s' % lru.get("test3") 
   lru.status()           
