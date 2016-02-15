#!/usr/bin/python
#  Copyright (c) 2012. Brookhaven National Laboratory. Valeri Fine (fine@bnl.gov)
#  $Id: pmObject.py 13760 2012-12-11 20:41:05Z fine $
#try:
#  from pandalogger.PandaLogger import PandaLogger
#except:
import logging as PandaLogger
  
from threading import local

class pmObject(object):
   _topObject = local() 

   #________________________________________________________________________________________
   @classmethod
   def setTopObject(cls,top):
      if isinstance(top,pmObject):
        cls._topObject._top = top 
      else:
         raise  ValueError, "The top object <%s> must be <%s>" % (top, top.__class__.__name__)
   #________________________________________________________________________________________
   @classmethod
   def topObject(cls):
      try:
        top = cls._topObject._top
      except:
         cls._topObject._top  = None
         top = cls._topObject._top
      return  top
   #________________________________________________________________________________________
   def __init__(self,name=None,parent=None,obj=None,regular=True):
      """  object anything but pmObject   
            parent is pmObject only
      """ 
      object.__init__(self)
      if name == None: 
         self._name = self.__class__.__name__
      else:
         self._name     = name
#      try:   
      #self._logger = PandaLogger().getLogger(self._name)
      self._logger = PandaLogger.getLogger(self._name)
      # except:
         # self._logger = PandaLogger.getLogger(self._name)
      self._alias    = ''
      self._children = None
      self._parent   = None
      self._cargo    = obj 
      self._level    = 0
      self._currentItem = self
      if parent == None and regular: 
         if self.topObject()== None:
            self.setTopObject(pmObject(name="__top__",regular=False))
         self.setParent(self.topObject())
      elif parent != None:
         self.setParent(parent)
   #______________________________________________________________________________________      
   def info(self,log=None):
      self._logger.info("%s",log)
   #______________________________________________________________________________________      
   def debug(self,log=None):
      self._logger.debug("%s",log)
   #______________________________________________________________________________________      
   def error(self,log=None):
      self._logger.error("%s",log)
   #______________________________________________________________________________________      
   def fatal(self,log=None):
      self._logger.fatal("%s",log)
   #________________________________________________________________________________________
   def setCargo(self,obj):
      oldCargo = self._cargo
      self._cargo = obj
      return oldCargo
   #________________________________________________________________________________________
   def addChild(self,child,mychild=False):
      if child!= None:
         if mychild:
            child.setParent(self)
         else:  
            myChildren = self.children(True)
            myChildren.append(child)
      return self
   #________________________________________________________________________________________
   def cd(self,name):
      self._currentItem = self[name]
      return self.pwd()
   #________________________________________________________________________________________
   def pwd(self):
      return  self._currentItem
   #________________________________________________________________________________________
   def children(self, init=False):
      if self._children == None and init:
         self._children = [] 
      return self._children
   #________________________________________________________________________________________
   def findChild(self,childName=None,all=True):
      """ Returns the child of this object and that is called childNname, 
          or None if there is no such object. 
          Omitting the childName argument causes all object names to be matched. 
          The search is performed recursively.
          If there is more than one child matching the search, the most direct ancestor is returned.
          If there are several direct ancestors, it is undefined which one will be returned. 
          In that case, findChildren() should be used.
      """
      child = None
      if self.children() !=None:
         for c in self.children():
            if childName==None or c.objectName() == childName: 
               child = c
               break
            child = c.findChild(childName)
            if child !=None and child.objectName() == childName: 
               break
      return child   
   #________________________________________________________________________________________
   def isMyChild(self,child):
      return child.parent() == self
   #________________________________________________________________________________________
   def root(self):
      top = self.parent()
      if top == None: top = self
      else: top = self.parent().root()
      return top
   #________________________________________________________________________________________
   def findIds(self,idi=None):
      """ Returns the array of ids of the object childrens.
      """
      ids   = []
      if (idi == None or id(self) == idi ):
        ids.append(self)
      children = self.children()
      if children:
         for child in children:
           ids.extend(child.findIds(idi))
      return ids
   #________________________________________________________________________________________
   def findChildren(self,childName=None,all=True):
      """ Returns the new pmObject with all children of this object with the given childName 
          or None if there are no such objects. 
          Omitting the name argument causes all object names to be matched. 
          The search is performed recursively
      """
      children  = pmObject()
      myChildren = self.children()
      if myChildren != None and ( childName or childName == None):
         for ch in myChildren:
            if childName == None or childName == ch.objectName(): 
               if all  or self.isMyChild(ch):
                  children.addChild(ch)
            nxt = ch.findChildren(childName)
            if nxt and len(nxt) > 0:
               children.children(True).append(nxt.children());
      if children == None or len(children) == 0: children = None
      return children
   #________________________________________________________________________________________
   def parent(self):
      """Returns the parent object  """
      return self._parent
   #________________________________________________________________________________________
   def setParent(self,parent):
      """ Makes the object a child of parent.
          if parent == None: make the object orphan
      """
      if parent == None:
         if self.parent():
            self.parent().children().remove(self)
            self._parent = parent
            self._level = 0
      else:
         if not isinstance(parent,pmObject) :
            # raise ValueError, "Only pmObject can be parent of %s. '%s' is not a pmObject" % (self, parent.__class__.__name__ )
            pass
         if self._parent != None:
            raise ValueError("Only parent is allowed. This '%s' already had the parent '%s'. Another one '%s' is provided " %(self, self._parent, parent) )
            pass
         if parent!=None: parent.addChild(self)
         self._parent = parent
         if self._parent:
            self._level = parent.level() + 1
         else:
            self._level = 0
      return self
   #________________________________________________________________________________________
   def objectName(self):
      return self._name   
   #________________________________________________________________________________________
   def rename(self,name):
      self._name = name
      return self
 #________________________________________________________________________________________
   def level(self):
      return self._level
   #________________________________________________________________________________________
   def mkdir(self,dir):
      nx = None
      nxName = dir.split("/",1)
      top = self.pwd()
      if len(nxName) == 2 and nxName[0]=='':
         top = self.root()
         if nxName[1] != '':
            nx = top._mkdir(nxName[1]);
      else:
            nx =  top._mkdir(dir)
      return nx
   #________________________________________________________________________________________
   def _mkdir(self,dir):
      nx = None
      nxName = dir.split("/",1)
      if len(nxName) > 0:
         if  self.children() == None:
            nx = pmObject(nxName[0],self)
         else:
            for n in self.children():
               if n.objectName() == nxName[0]:
                  nx = n;
                  break
            else:      
               nx = pmObject(nxName[0],self)
         if len(nxName)==2 and nxName[1] != '':
            nx = nx._mkdir(nxName[1])
      return nx
   #________________________________________________________________________________________
   def hasCargo(self):
      return self.cargo() != None
   #________________________________________________________________________________________
   def cargo(self):
      return self._cargo
   #________________________________________________________________________________________
   def shunt(self,newParent=None):
      self.setParent(None)
      self.setParent(newParent)
      return self
   #________________________________________________________________________________________
   def __len__(self):
      ln = 0
      if self._children != None: 
         ln =len(self._children)
      return ln
   #________________________________________________________________________________________
   def prune(self):
      """ prune """
      return len(self._children)
   #________________________________________________________________________________________
   def remove(self,childName):
      return len(self._children)
   #________________________________________________________________________________________
   def __iter__(self,name=None):
      return self.iterator(name)
   #________________________________________________________________________________________
   def __str__(self):
      out = ''
      out += self.objectName()
      if self.cargo() != None: out += ":%s" % self.cargo()
      l = len(self)
      bracketo = ''
      bracketc = ''
      sep  = ''
      if l >= 1: 
         out += "/" 
         if l > 1: 
            bracketo += "["
            bracketc += "]"
            sep  = ','
            out += bracketo
      myChildren = self.children()
      if myChildren != None:
         for i,child in enumerate(self.children()):
            if i == l-1: sep = bracketc
            out += "%s%s" % (child,sep)
      if l > 1: 
         out += bracketc
      return out
   #________________________________________________________________________________________
   def getItemByKey(self,key):
      name = key
      nxName = name.split("/",1)
      search = self.pwd()
      found = None
      name = nxName[0]
      lnxt =  len(nxName)
      if name == '': 
         search = self.root()
         if lnxt == 2:  
            nxName = nxName[1].split("/",1)
            name = nxName[0]
            lnxt =  len(nxName)
         else:  name = None
      if name == None:   
         found = search
      else:
         for me in search.children(): 
            # print ' 197 ', me.objectName() , name, lnxt
            if me.objectName() == name:
               if lnxt ==  2: found = me[nxName[1]]
               else: found = me
               break
      return found
   #________________________________________________________________________________________
   def getItemByIndex(self,key):
      it = self.iterator(key)
      return it.next()
   #________________________________________________________________________________________
   def ls(self,dir=None,level=None):
      if level >=0 or level == None:
         search = self.pwd()
         if dir != None: seach = self[dir]
         self._ls(level,0)
         
   #________________________________________________________________________________________
   def _ls(self,level,shift):
      if level >=0 or level == None:
         space = ''
         for i in range(0,shift): space += '-'
         arr  = ''
         if  len(self) > 0:
            arr =  '[%s]' % len(self)
         print "- %s> %s %s" % ( space, self.objectName(),arr)
         if self.children()  != None:
            for ch in self.children():
               if level != None: level -= 1
               ch._ls(level,shift+1)
               
   #______________________________________________________________________________________      
   def stealFrom(self,oldparent):
      """ take ownership of all children of oldparent """
      try:    
         for c in oldparent:
            c.setParent(self)
      except:
         pass      
      return self
   #________________________________________________________________________________________
   def __contains__(self,obj):
      c = False
      try:
         typeString = isinstance (obj,str)
         for s in self.children():
            if typeString:
               if s.objectName() == obj: 
                  c = True
                  break
            else:   
               if s.objectName() == obj.ObjectName(): 
                  c = True
                  break
         else:
            c = False
      except:
         c = False
      return c
   #________________________________________________________________________________________
   def get(self,key, default=None):
      r = default
      if self.__contains__(key): 
         r = self[key]
      return r
   #________________________________________________________________________________________
   def __getitem__(self, key):
      try: 
         if key != None:
            if isinstance(key,int):
               return self.getItemByIndex(key)
            elif isinstance(key,str):
               return self.getItemByKey(key)
      except:
         pass
      return None

   #________________________________________________________________________________________
   def iterator(self,path = None):
      # print " 226 ITERATOR ", self.objectName(), path
      search = self
      if path != None:  search  = self[path]
      if search != None:
         myChildren = search.children()
         # print " 231 ITERATOR search ", search.objectName()
         yield self 
         if myChildren != None and  len(myChildren) > 0:
            for ch in myChildren: 
               for nxch in ch:
                    # print " 235 ", nxch.objectName()
                    yield nxch
      else:
         print " 240 ITERATOR END "
      

if __name__ == '__main__':
   print "Starting ...... "
   a = pmObject("A",regular=False)
   b = pmObject("B",regular=False)
   c = pmObject("C",regular=False)
   c1 = pmObject("C1",regular=False)
   print "4 object have been created",a,b,c,c1
   b.addChild(c,True)
   b.addChild(c1,True)
   a.addChild(b,True)
   a.ls()
   
   # print "--- Panda Object Test---- ", len(a), a,  "\n" , dir(a),  "\n",  a["B"], "\n --- ", a["B/C"]
   print "--- Panda Object Test---- ", len(a), a 
   print ' a["B"]=', a["B"]
   #, "\n --- ", a["B/C"]
   a.cd("B")
   print "--- Panda Object Test---- ", a["B"], " pwd=", a.pwd()
   d = a.mkdir("o1/t2/t3/f4/f5/s6")
   print d,d.objectName() , " ----------- "
   a.ls()
   a.mkdir("o1/t21/t32")
   a.ls()
   d = a.mkdir("/t3/t33/f45")
   print d,d.objectName() , " ----------- "
   a.ls()
   print "291 the entire structure: ", a.root()
   a.root().ls()
   a.ls("/")
   allIDs= a.findIds()
   print "411: all object as one array", len(allIDs),allIDs
   for i in allIDs:
       print "\n--", i
       print i.objectName()
   print "Excluding C;"
   a.ls()   
   c.setParent(None);
   print "Excluded C;"
   a.ls()   
   a['o1'].setParent(None)
   print "Excluded o1;"
   a.ls()
   
   
