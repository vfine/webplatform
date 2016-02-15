#!/usr/bin/python
"""
pandamon Oracle routines
$Id: pmOracle.py 16351 2013-07-25 20:58:23Z fine $
"""
import cx_Oracle,threading
import pmUtils
import pmConfig.pmConfig as config
import datetime 

#______________________________________________________________________________________      
class pmDbPool(object):
   _pool = None
   _poolHadnlerLock = threading.RLock()
   @classmethod
   def pool(cls): 
      cls._poolHadnlerLock.acquire()
      if cls._pool == None:  cls._pool = pmDbPool() 
      cls._poolHadnlerLock.release()
      return cls._pool

   #______________________________________________________________________________________      
   @classmethod
   def connect(cls,dbUser,dbName,dbPasswd,counter=9):
      pool =  cls.pool().dbPool(dbUser,dbName,dbPasswd)
      conn =  pool.acquire()
      try:
         # conn.clientinfo = 'python 2.6.4 - win32'
         conn.module = 'pandamon cx_Oracle pmDbPool SessionPool'
         conn.action = 'ping'
         conn.ping()
      except cx_Oracle.DatabaseError, exception:
         error, = exception
         # check if session was killed (ORA-00028)
         session_killed = 28
         if error.code == session_killed:
              #
              # drop session from the pool in case
              # your session has been killed!
              # Otherwise pool.busy and pool.opened
              # will report wrong counters.
              #
            pool.drop(connection)
            print "Session droped %s from the pool... error.code=%s"  % (counter,error.code)
         if counter>0: 
            try: 
               pool.release(conn)
            except:
               print "pmOracle:48 Session released %s from the pool... error.code=%s. Reconnecting . . . "  % (counter,error.code)
               pass 
            return cls.connect(dbUser,dbName,dbPasswd,counter=counter-1)
         else:
            raise
      return conn

   #______________________________________________________________________________________      
   @classmethod
   def poolKey(cls,dbUser,dbName,dbPasswd):
      return "%s.%s.%s" %(dbUser,dbName,dbPasswd)

   #______________________________________________________________________________________      
   @classmethod
   def release(cls,connection):
      if connection!= None:
         cls.pool().releaseConnection(connection)

   #______________________________________________________________________________________      
   def __init__(self):
      object.__init__(self)
      self._pandaPoolServers = {}
      self._poolDictLock = threading.RLock()

   #______________________________________________________________________________________      
   def releaseConnection(self,connection):
      self._poolDictLock.acquire()
      key = self.poolKey(connection.username,connection.dsn,connection.password)
      pool = self._pandaPoolServers.get(key)
      if pool != None:
          pool.release(connection)
      self._poolDictLock.release()
      return pool 

   #______________________________________________________________________________________      
   def dbPool(self,dbUser,dbName,dbPasswd,threaded=True):
      self._poolDictLock.acquire()
      key = self.poolKey(dbUser,dbName,dbPasswd)
      pool = self._pandaPoolServers.get(key)
      if pool==None: 
         pool = cx_Oracle.SessionPool(dbUser,dbPasswd,dbName,5,50,5,
                connectiontype=cx_Oracle.Connection,
                threaded=threaded,getmode=cx_Oracle.SPOOL_ATTRVAL_NOWAIT, 
                homogeneous=True)
         pool.timeout = 10
         self._pandaPoolServers[key] =  pool
      self._poolDictLock.release()
      return pool

class sqlSelect(object):
   """ Utility to prepare the SQL query """
   #______________________________________________________________________________________      
   def __init__(self,varswhere=None,counter=-1):
      object.__init__(self)
      self._varCounter = int(counter) if counter != None else -1
      if varswhere != None:
         self._vars  = varswhere[0]
         self._where = varswhere[1]
         try: 
            self._times = varswhere[3]
         except:
            self._times = {}
            pass
      else:   
         self._vars  = {}
         self._times = {}
         self._where = []
  #______________________________________________________________________________________________________________
   def counter(self):
      """ Return the variable name counter
      """
      return self._varCounter
  #______________________________________________________________________________________________________________
   def where(self):
      return self._where
  #______________________________________________________________________________________________________________
   def vars(self):
      return self._vars
  #______________________________________________________________________________________________________________
   def times(self,key=None):
      if key == None:
         return self._times
      else:
         return  self._times.get(key) 
  #______________________________________________________________________________________________________________
   def isOld(self,hours=72,key=None):
      """ return:  1  if the time  starts more then 'hours' from now
                  +2  if the time  ends  more then 'hours' from now
                   0  otherwise
      """
      t = self.times();
      old = 1 
      if len(t) >0 : 
         now = datetime.datetime.utcnow()
         deadline = datetime.timedelta(hours=int(hours))
         old = 0
         p = None
         if key != None:
           p = t.get(key)
         else:
           p = t
         if p != None:
           old  = 1 if p.get('start') != None and now - p['start'] >= deadline else 0
           old += 1 if p.get('end')   != None and now - p['end']   >= deadline else 0
      return old
  #______________________________________________________________________________________________________________
   @classmethod
   def varConv(cls,var):
      return var.upper().replace(".","_")
  #______________________________________________________________________________________________________________
   def varName(self,var):
      self._varCounter += 1
      return ":%s_%d" % (self.varConv(var),self._varCounter)
   #______________________________________________________________________________________________________________
   def add(self,variable,value=None, ops='='):
      """ this - the SQL template with %(var)s and %(val)s formats
          For example, to create the clause:
          "stdout LIKE :stdout" 
          the  input parameters should look like this
          " sqlSelect.add('stdout', value=v, ops='LIKE') 
      """
      if ops == None: ops = '='
      vars  = self._vars
      where = self._where
      varname = self.varName(variable)
      if ( isinstance(value,str) and value.lower() == 'null') or value == None: 
         value = 'NULL'
         if ops == '=': ops = ' IS NOT '
         if ops == '!=': ops = ' IS  '
         where.append('%(var)s %(ops)s %(val)s'% {'var' : variable, 'ops': ops, 'val':value} )
      else:
         vars[varname] = value
         where.append('%(var)s %(ops)s %(val)s'% {'var' : variable, 'ops': ops, 'val':varname} )
      return self
   #___________________________________________________________________________________________________
   def addDict(self,dict,ops='=' ):
      """ add 'dict' to sqlSelect """
      if dict != None and len(dict) > 0:
         for k in dict:
            self.add(k,dict[k],ops)
      return self
   
  #______________________________________________________________________________________________________________
   @classmethod
   def is_all(cls,item):
      return  item == None or item=='None' or item == '' or (isinstance(item,str) and item.lower() in ('all','*') )

   #______________________________________________________________________________________________________________
   def prepareTime(self,hours=None, tstart=None, tend=None, field='modificationTime', days=None,format=None):
      """ 
         hours  - the  duration period
         tstart - the  start time of the period
         tend   - the  end time of the period
         field  - the Db table field to create the SQL statement for
                  Note: It is ambiguous to define all 3 'time' parameters simultaneously 
         format  - format to convert the char columns into the Oracle DATE datatype if needed
                   see :http://docs.oracle.com/cd/B19306_01/server.102/b14200/functions183.htm
                        http://docs.oracle.com/cd/B19306_01/server.102/b14200/sql_elements004.htm#i34924
                   
                  Example: ' Month dd, YYYY, HH:MI A.M.',   
                           For  "2011-12-13 13:51:22" -> "YYYY-MM-DD HH:MI:SS"
      """
      vars  = self._vars
      where = self._where
      times = self._times
      starttime = None
      endtime = None
      hrs = None
      try:
         hrs = float(days)*24
      except: 
         hrs = 0
         pass
      try:
         hrs += float(hours)
      except: pass   
      if hrs == 0: hrs = None
      if hrs != None and tstart !=None and tend!=None: 
         raise ValueError("Only 2 parameteres are allowed. All 3 have been provided: hours=%(hours)s, tstart=%(tstart)s, tend=%(tend)s" %{  'hours' : hrs,'tstart': tstart, 'tend':tend } )
      if tstart != None:
         starttime = pmUtils.timeValue(tstart)
         if hrs != None:
            endtime = starttime + datetime.timedelta(hours=int(hrs))
      if tend != None:
         endtime = pmUtils.timeValue(tend)
         # print utils.lineInfo(), " : " , tend, endtime
         if hrs != None:
            starttime = endtime - datetime.timedelta(hours=int(hrs))
      if starttime == None and endtime == None and hrs != None:
         endtime =  datetime.datetime.utcnow()
         starttime = endtime - datetime.timedelta(hours=int(hrs))
      if starttime != None:
          var = ':%s_START' % self.varConv(field)
          vars[var] = starttime
          if not times.has_key(self.varConv(field)):  times[self.varConv(field)] = {}
          times[self.varConv(field)]['start'] = starttime
          times['start'] = starttime
          if format == None:
             where.append(' %(field)s > %(var)s' % {'field': field, 'var': var })
          else:
             where.append(" TO_DATE(%(field)s,'%(format)s') > %(var)s " % {'field': field, 'var': var, 'format' :format })
      if endtime != None:
          var = ':%s_END' % self.varConv(field)
          vars[var] = endtime
          if not times.has_key(self.varConv(field)):  times[self.varConv(field)] = {}
          times[self.varConv(field)]['end']=endtime
          times['end']=endtime
          if format == None:
              where.append(' %(field)s <= %(var)s ' % {'field': field, 'var': var })
          else:
              where.append(" TO_DATE(%(field)s,'%(format)s') <= %(var)s" % {'field': field, 'var': var, 'format' :format })
      duration = None
      if starttime != None and endtime != None:
         duration = endtime-starttime
      elif  starttime != None:
         duration = datetime.datetime.utcnow()-starttime
      if not times.has_key(self.varConv(field)):  times[self.varConv(field)] = {}   
      times[self.varConv(field)]['duration'] = duration
      times['duration'] = duration

      return self 
   #______________________________________________________________________________________________________________
   def prepareJobType(self,jobtype,testsite=False):
      if jobtype==None or jobtype.lower() in ('all',''): return self
      vars  = self._vars
      where = self._where
      jbType = pmUtils.parseArray(jobtype)
      labels = {} 
      hasProduction = 'production' in jbType
      hasJedi       = 'jedi' in jbType
      for nxtType in jbType:
         nxtType = nxtType.lower()
         if nxtType=='install':
            prodtype = labels.get('prodSourceLabel',[])
            prodtype += ['install']
            labels['prodSourceLabel'] = prodtype
         elif nxtType=='production':
            prodtype = labels.get('prodSourceLabel',[])
            prodtype += ['managed']
            labels['prodSourceLabel'] = prodtype
         elif nxtType =='test':
            prodtype = labels.get('prodSourceLabel',[])
            if (hasProduction):
               prodtype += ['prod_test']
            else:   
               prodtype += ['*test']
               self.add('prodSourceLabel','prod_test','!=')
            labels['prodSourceLabel'] = prodtype
         elif nxtType =='analysis':
            prodtype = labels.get('prodSourceLabel',[])
            prodtype += ['user','panda']
            labels['prodSourceLabel'] = prodtype
         elif nxtType =='osg':
            prodtype = labels.get('VO',[])
            prodtype +=['osg']
            labels['VO'] = prodtype
         elif nxtType =='cms':
            prodtype = labels.get('VO',[])
            prodtype +=['cms']
            labels['VO'] = prodtype
         elif nxtType =='jedi':
            self.add('JediTaskID')
         else:
            prodtype = labels.get('prodSourceLabel',[])
            prodtype += [nxtType]
            labels['prodSourceLabel'] = prodtype
         if testsite==True:
            prodtype = labels.get('prodSourceLabel',[])
            if (hasProduction):
               prodtype += ['prod_test']
            else:   
               prodtype += ['*test']
               self.add('prodSourceLabel','prod_test','!=')
            labels['prodSourceLabel'] = prodtype
         if hasProduction:
            self.add('taskID')

      return self.prepareCommaList(labels)
   #______________________________________________________________________________________________________________
   def prepareLimit(self,limit=15000):
      if limit != None: self.add('rownum',limit,'<=')
      return self

   #______________________________________________________________________________________________________________
   def prepareRegexp(self,key,value=None,opt ='i'):
      """ prepare the regexp 'value' pattern to look up the 'key' Db column 
         ','   -> ')|('
         '%'   -> '*'
         '*'   -> '.*'
         '.'   -> '\.'
         '$$)' -> '$)'
      """
      if value != None: 
         if not isinstance(value,str):
            raise ValueError(" Non string  pattern %s to look up the %s column is not acceptable" %(value,key))
         if pmUtils.isFilled(value) and not self.is_all(value):
            vars  = self._vars
            where = self._where
            endclause =  ''
            if not ',' in value:
               endclause =  '$'
            v = '(%s%s)' % (value.replace(',',')|(').replace('.','\\.').replace('%','*').replace('*','.*'),endclause)
            # clean up
            v = v.replace('$$)','$)').replace('|()','').replace('()|','')
            qvar = self.varName(key)
            vars[qvar] = v
            where.append("REGEXP_LIKE (%(key)s,%(value)s,'%(opt)s') " % {'key': key ,'value': qvar,'opt':opt } )
      return self

   #______________________________________________________________________________________________________________
   def prepareCommaList(self,key,value=None,forceregexp=False):
      """ prepare the parameter as comma separated, simple, or list  """ 
      if ( value==None or value =='None' )and isinstance(key,dict):
         for cmd,val in key.iteritems():
              self.prepareCommaList(cmd,val,forceregexp)
      else:
         vars  = self._vars
         where = self._where
         if not self.is_all(value): 
            if isinstance(value,tuple) : value = list(value)
            if not isinstance(value,list) and isinstance(value,str):
               if forceregexp or '*' in value:
                  return self.prepareRegexp(key,value)
               elif ',' in value:
                  v = value.split(",")
                  if len(v) > 1 : value =v
            if isinstance(value,list):
               ## check regexp
               reg = forceregexp
               if not reg:
                  for x in value:
                     try:
                        if '*' in x: 
                           reg = True
                           break
                     except:
                        pass
               if reg:
                  self.prepareRegexp(key,','.join(value)) 
               else:
                  sqlin = []
                  for i,v in enumerate(value):
                     qvar = self.varName(key)
                     vars[qvar] = v
                     sqlin.append(qvar)
                  if len(sqlin) > 0:
                     where.append("%s in (%s)" % (key, ' ,'.join(sqlin) ) )
            elif not (isinstance(value,str) and ("%" in value or "*" in value)):
               vstar = '%s' % value
               if vstar.lower() == 'null':
                 self.add(key,value, ' IS ')
               else:               
                 self.add(key,value)
      return self
   #______________________________________________________________________________________________________________
   def makeWhere(self,operation='AND', prefix=' WHERE '):
      op = ' %s ' % operation
      ot = op.join(self.where())
      if len(ot) > 0: ot = '%s%s' % (prefix,ot)
      return ot
      
#______________________________________________________________________________________      
class pmDb(object):
   """
   This class is  not thread safe intentionally (for the time being)
   One is supposed to get one dedicated instance of pmDb per each thread 
   """

   #______________________________________________________________________________________      
   def __init__(self,dbuser=None,pwd=None,dbname=None,db='archive',mode='r'):
         " task dd = 'meta' "
         self._theadId= threading.currentThread();
         object.__init__(self)
         self._dbuser = dbuser if dbuser!=None else config.dbconfig['oracle_%sdbuser-%s' % (db,mode) ]
         self._pwd = pwd if pwd !=None else config.dbconfig['oracle_%sdbpass-%s' % (db,mode)]
         self._dbname = dbname if dbname !=None else config.dbconfig['oracle_%sdbhost' % db ]
         self._connect = None
         self.__enter__()
         
   #______________________________________________________________________________________      
   def __enter__(self):
      if self._connect==None:
         self._connect = pmDbPool.connect(self._dbuser,self._dbname,self._pwd)
         self._cursor = self._connect.cursor()
         self._cursor.execute("ALTER SESSION SET TIME_ZONE='UTC'")
      return self

   #______________________________________________________________________________________      
   def __exit__(self, type, value, tb):
      self.close()

   #______________________________________________________________________________________      
   @classmethod
   def open(cls,dbuser=None,pwd=None,dbname=None,db='archive',mode='r'):
      return pmDb(dbuser,pwd,dbname,db,mode)
   
   #______________________________________________________________________________________      
   def connection(self):
      return  self._connect
      
   #______________________________________________________________________________________      
   def cursor(self):
      return  self._cursor

   #______________________________________________________________________________________      
   def checkThread(self, msg=pmUtils.lineInfo()):
      if self._theadId != threading.currentThread(): raise ValueError("wrong thread from: %s" % msg)

   #______________________________________________________________________________________      
   def close(self):
      self.commit()
      self._cursor.close()
      pmDbPool.release(self.connection())
      self._connect = None
      self._cursor  = None
      
   #______________________________________________________________________________________      
   def execute(self,query, vars=None, arraysize=100, comment=''):
       self.checkThread(pmUtils.lineInfo())
       if comment == None or comment == '': comment = 'pmOracle.pmDb.execute:333' 
       query += " /* %s */ " % comment
       print 'Oracle execute: ', query
       self.cursor().arraysize = arraysize
       if vars==None:
          res = self.cursor().execute(query)
       else:
          print vars
          res = self.cursor().execute(query,vars)
       return res

   #______________________________________________________________________________________      
   def fetchone(self,query=None, vars=None,arraysize=100, comment=''):
      if query !=None: self.execute(query,vars,arraysize,comment)
      header = []
      fullRows = []
      desc = self.cursor().description
      r = self.cursor().fetchone()
      for h in desc: header.append(h[0])
      row = []
      if r != None and len(r)>0:
         for  i,col in enumerate(r):
            nm = header[i]
            if isinstance(col, cx_Oracle.LOB):
                row.append(col.read())
            else:
                row.append(col)
         fullRows = [row]
      return  { 'header' : header,'rows' : fullRows }
   
   #______________________________________________________________________________________      
   def commit(self):
      try:
         c = self.connection()
         if c!=None: c.commit()
         return True
      except: raise
   #______________________________________________________________________________________      
   def fetchall(self,query=None, vars=None,arraysize=1000, comment=''):
       self.checkThread(pmUtils.lineInfo())
       if query !=None: self.execute(query,vars,arraysize,comment)
       desc = self.cursor().description
       rdlist = []
       for r in self.cursor():
           rdict = {}
           i = 0
           for col in r:
               nm = desc[i][0]
               if isinstance(col, cx_Oracle.LOB):
                   rdict[nm] = col.read()
               else:
                   rdict[nm] = col
               i += 1
           rdlist.append(rdict)
       return rdlist
       
   #______________________________________________________________________________________      
   def fetchallh(self,query=None, vars=None, arraysize=1000, comment='',one=False):
       if one: return self.fetchone(query,vars,arraysize, comment);
       self.checkThread(pmUtils.lineInfo())
       if query !=None: self.execute(query,vars,arraysize,comment)
       header = []
       desc = self.cursor().description
       rows = self.cursor().fetchall()
       for h in desc: header.append(h[0])
       fullRows = []
       for r in rows: 
           row = []
           for  i,col in enumerate(r):
               if isinstance(col, cx_Oracle.LOB):
                   row.append(col.read())
               else:
                   row.append(col)
           fullRows.append(row)
       return { 'header' : header,'rows' : fullRows }
#______________________________________________________________________________________      
if __name__ == '__main__':
   def getJobRecords(where, selection):
       query = "select %s from ATLAS_PANDA.JOBSARCHIVED4 where %s" % ( selection, where ) 
       return query 
   sql = pmDb()
   rows = sql.fetchallh(getJobRecords("1=1","distinct jobstatus"))
   sql.close()
   print rows
          