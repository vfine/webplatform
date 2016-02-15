"""
pandamon utility routines
"""
import sys, os, re, urllib, commands, time, traceback, calendar
from datetime import datetime
# from xml.dom import minidom

from pmState import pmstate
import pmConfig.pmConfig as config
from  monitor.nameMappings import nmap

# https://twiki.cern.ch/twiki/bin/viewauth/AtlasComputing/PandaShiftGuide#Job_state_definitions_in_Panda
# select distinct jobstatus from jobsdefined4;
# select distinct jobstatus from jobswaiting4;
# select distinct jobstatus from jobsactive4;
# select distinct jobstatus from jobsarchived4;

jobStates = ( 'defined', 'pending', 'waiting', 'assigned', 'activated', 'sent', 'starting', 'running', 'holding'
                 ,'transferring', 'finished', 'failed', 'cancelled')
jobTables = [ ['defined'], ['waiting'], ['waiting'], ['defined'], ['active'], ['active'], ['active'], ['active'], ['active']
                 ,['active'], ['archived'], ['active','archived'],['archived']]
                 
jediTaskStates= (  'registered', 'waiting','defined', 'pending', 'assigning', 'ready'
                  , 'scouting',  'running', 'holding', 'merging','prepared'
                  , 'finished',  'aborting','aborted', 'finishing', 'broken', 'failed'
                 )
for ts in  jobTables:
   for i,t in enumerate(ts):
     ts[i] = 'ATLAS_PANDA.jobs%s4' % t
      
jobStateTables =  dict(zip(jobStates,jobTables))
jobTablesOld = 'ATLAS_PANDAARCH.JOBSARCHIVED'
#________________________________________________________________________________________
def isJob(job,type='analysis'):
   """ Check the job type [ production | 'analysis" | None ] """
   isJb = False
   try:
      label = job['prodSourceLabel'].lower()
      tp = type.lower().strip()
      lb = label=='user' or label=='panda'
      if tp=='analysis':
         isJb =  lb
      elif tp =='production':
         isJb =  not lb
   except:
      pass
   return isJb

   
#________________________________________________________________________________________
def toSDBTime(tval):
    """ turn time object into integer time since epoch, as string, for SimpleDB """
    if type(tval) == type('string'): tval = timeValue(tval)
    strtime = "%s" % tval.strftime("%Y-%m-%d %H:%M:%S")
    timestruct = time.strptime(strtime,"%Y-%m-%d %H:%M:%S")
    itime = calendar.timegm(timestruct)
    return str(itime)

#________________________________________________________________________________________
def fromSDBTime(sdbtime):
    """ turn SimpleDB time, integer time since epoch, into datetime object """
    t = time.gmtime(int(sdbtime))
    return datetime(t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec)
    
#________________________________________________________________________________________
def replaceDoc(proxy):
   """ return the description of the source code line this function was called from """
   import inspect
   frame = inspect.currentframe()
   caller = frame
   try:
      frames = inspect.getouterframes(frame)
      try:
         caller =  frames[1]
      finally:
         filename, lineno, function, code_context, index = inspect.getframeinfo(caller[0])
   finally:
      del frame
   if function.__doc__ == '': function.__doc__  =  proxy.__doc__   
   return format % { 'filename' : filename, 'function' : function,'lineno' : lineno }

#________________________________________________________________________________________
def lineInfo(basename=True,format="%(filename)s.%(function)s:%(lineno)s%(comment)s",comment=''):
   """ return the description of the source code line this function was called from """
   import inspect
   frame = inspect.currentframe()
   caller = frame
   try:
      frames = inspect.getouterframes(frame)
      try:
         caller =  frames[1]
      finally:
         filename, lineno, function, code_context, index = inspect.getframeinfo(caller[0])
         if basename: filename = os.path.basename(filename)
   finally:
      del frame
   return format % { 'filename' : filename, 'function' : function,'lineno' : lineno,'comment':comment }

#________________________________________________________________________________________
def name2Index(array,name=None):
   indx = None
   if array != None:
      if name == None:
         indx = {}
         for  i,nm in enumerate(array):
            indx[ nm ] = i
      else:
         for  i,nm in enumerate(array):
            if nm.lower() == name.lower():  
               indx =i;
               break
   return indx;
#________________________________________________________________________________________
def createIdSet(pandaid):
   """ Create the list of the PandaIds """
   idlist = set([])
   try:
      id = int(pandaid)
      idlist.add(id)
   except:
      try:
         for k in pandaid:
            idlist.add(int(k))
      except:
         raise ValueError("wrong PandaID %s ", pandaid)
   return list(idlist)

#________________________________________________________________________________________
def zipa(header,array):
   zipped = dict(zip(header,array))
   return zipped
#________________________________________________________________________________________
def unzip(header,zipped):
   indx= name2Index(header)
   arr = [None]*len(indx)
   for z,r in zipped.iteritems():
      i = indx.get(z)
      if i == None: continue
      arr[i]=r
   return  arr  
#________________________________________________________________________________________
def epochTime(val):
    """ turn time object into integer time since epoch, as string """
    itime = None
    if isinstance(val,int): itime = val
    elif val !=None:
      try:
          strtime = "%s" % val.strftime("%Y-%m-%d %H:%M:%S")
          timestruct = time.strptime(strtime,"%Y-%m-%d %H:%M:%S")
          itime = calendar.timegm(timestruct)
          newtime = time.gmtime(itime)
      except:
         pass
    return itime

#________________________________________________________________________________________
def total_hours(duration):
      return duration.days*24+duration.seconds/3600 
   
#________________________________________________________________________________________
def timeValue(tstr):
    """ Parse time string into time value """
    res = None
    if isinstance(tstr,datetime):
      res = tstr
    else:
       if tstr == 'now': 
          res = datetime.utcnow()
       else:
          if len(tstr) == 10:
              res = datetime.strptime(tstr,'%Y-%m-%d')
          elif len(tstr) == 13:
              res = datetime.strptime(tstr,'%Y-%m-%d %H')
          elif len(tstr) == 16:
              res = datetime.strptime(tstr,'%Y-%m-%d %H:%M')
          elif len(tstr) >= 19:
              res = datetime.strptime(tstr[:18],'%Y-%m-%d %H:%M:%S')
          else:
              raise ValueError( ' time length %s not parseable: %s' % ( len(tstr), tstr ) )
    return res

#________________________________________________________________________________________
def reportError(errstr):
    """ Report an error with traceback """
    excInfo =  sys.exc_info()
    (etype, value, tback) = excInfo
    uname = os.uname() # (sysname, nodename, release, version, machine) 
    (sysname, nodename, release, version, machine)  = uname
    try:
       _logger.error(" %s %s %s " %  (errstr, etype, value)  )
       terr =  datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')  
       report = "ERROR: %s" % errstr
       etype, value, tback = sys.exc_info()
       if etype:
           report += "\nnode: %s: at $s  %s: %s" % ( nodename, terr,  etype, value )
           tblines = traceback.extract_tb(tback)
           for l in tblines:
               fname = l[0][l[0].rfind('/')+1:]
               report += "\n      %s: %s: %s: %s" % ( fname, l[1], l[2], l[3] )
       pmstate().errorReport = report
       print report
       #_logger.error(report)
    except:
      raise sys.exc_info()   
    raise ValueError(report)
    return report

#___________________________________________________________________________________________________
def reportWarning(errstr):
    """ Report a warning """
    report = "WARNING: %s" % errstr
    pmstate().errorReport = report
    print report
    #_logger.warning(report)
    return report
#_____________________________________________________________________________________
def openAccordion(id):
    return '<div id="%s" style="padding:0px;margin:0px;" class="ui-accordion ui-widget" title= "Select the item you need and click to expand">' % id
#_____________________________________________________________________________________
def closeAccordion():
    return '</div>'
    
#________________________________________________________________________________________
def activateAccordion(name,index,id=None, tooltip=None):
   tip = " title=' Click to activate and use the left pane %s item'" % (tooltip if tooltip != None else '"'+name+'"' )
   html ="""
      <div %(tip)s onclick='utils().activateAccordion(%(index)s)' class='ui-widget ui-widget-content ui-state-highlight ui-cornel-all' style='display:inline;cursor:pointer;'><b>%(showtxt)s</b></div><b>: </b>
   """ % {'showtxt' :name, 'index' : index, 'tip' : tip }
   return html    
#_____________________________________________________________________________________
def addAccordion(header,body,extra='',tag="h3",button=''):
   """ Create JQuery UI accordion entry 
       button should be the dict {"href": url, "html", body, "title" : title } 
   """
   if extra==None: extra = ''
   if button != None and button != '':
      title = button.get('title',"Click me")
      button = """
         <span>&nbsp;&nbsp;&nbsp;
         <span style="text-decoration:underline; color:blue; cursor:pointer" title="%(title)s" onclick="location.href='%(href)s'">%(html)s</span></span>
         """ % {"href" : button['href'], "html": button['html'], "title" : title}
   else: 
      button = ''      
   html = """<%(tag)s class='ui-accordion-header' style="padding:0;margin:0;"><a style="padding:0px 2px 0 16px;margin:0;" href=#>&nbsp;%(header)s%(button)s</a></%(tag)s>
             <div style="padding:0;margin:0; font-weight:normal;" class="ui-accordion-content ui-widget-content" %(extra)s >%(body)s</div>
             """ % {"header":header, "tag" : tag, "body" : body, "extra" : extra , "button": button }
   return html

   
#___________________________________________________________________________________________________
def isValid(val):
    """ Is the value valid? """
    if val == None: return False
    if isinstance(val, datetime):
        if val.year > 1900 and val.year < 2030:
            return True
        else:
            return False
    if isinstance(val, str):
        if val.lower() == 'null': return False
        if val.lower() == 'none': return False
        if val.lower() == 'undefined': return False
    return True

#___________________________________________________________________________________________________
def isFilled(val):
    """ Is the value filled? """
    if not isValid(val): return False
    if isinstance(val, str):
        if val != '' and val != ' ': return True
    if isinstance(val, int):
        if val != 0: return True
    if isinstance(val, datetime): return True
    return False

#______________________________________________________________________________________________________________
def parseArray(value,unique=False):
   """ 
      Convert the 'value' into the list parsing it as comma separated strings, tuple, or list 
      unique=True - removes the duplicates from the final array. 
      and it may alter the order of the values from 'value'
   """
   out = value
   if isinstance(out,tuple): out = list(out)
   if not isinstance(out,list) and isinstance(out,str):
      if ',' in out:
         v = [x.strip() for x in out.split(",")]
         if len(v) > 0 : out = v
   if not isinstance(out,list):
      out = [out]
   if unique:
      tmp = set(out)
      out = list(tmp)
   return out
#___________________________________________________________________________________________________
def hostName(url):
      """ Extract the host name from the URL with the [N@]hostname format  """
      host = 'unknown'
      try:
         ih = url.find('@')
         if ih >= 0: host=url[ih+1:]
         else: host = url
      except:   
         pass
      return host
#___________________________________________________________________________________________________
def parseQueryString(query):
    """Return a dictionary of key value pairs given in the query string"""
    qdict = {}

    params = query.split('?')

    """Return if nothing or nothing after the '?'"""
    if len(params) == 0 or len(params) == 1 :
        return qdict
    if len(params[1]) == 0 :
        return qdict

    if len(params) != 1:
        params = params[1].split('&')
        for p in params:
            pair = p.split('=')
            if len(pair) > 1:
                pair[1] = urllib.unquote_plus(pair[1])
                #qdict[pair[0]] = pair[1]
                if pair[0].find(";")>0:
                    qdict[pair[0].split(";")[1]] = pair[1]
                else:
                    qdict[pair[0]] = pair[1] 
            else:
                #qdict[pair[0]] = ''
                if pair[0].find(";")>0:
                    qdict[pair[0].split(";")[1]] = ''
                else:
                    qdict[pair[0]] = ''

    ## string checking for key, value pair ##
    proceed = bool(1)
    for key in qdict:
        keyok = checkString(key)
        if not keyok in [0, 1]:
            newkey = keyok 
            qdict[newkey] = qdict[key]
            del qdict[key]
            keyok = bool(1)
        if keyok: 
            valok = checkString(qdict[key])
            if not valok in [0, 1]:
                qdict[key] = valok
                valok = bool(1)
            if not valok:
                qdicttxt =self.cleanParamsUp(qdict[key])
                increport = "Invalid parameter value: [%s] for key: [%s]" % (qdicttxt, self.cleanParamsUp(key))
                if key != 'errinfo': 
                    recordIncident(increport, 'monsecurity')
                pmstate().navmain += "\n%s" % increport
                proceed = bool(0)
        else:
            if not str(qdict[key]) == '':
                pmstate().navmain += "\nWarning: Invalid parameter key: %s" % (self.cleanParamsUp(key))
                proceed = bool(0)
    if proceed:
        return qdict
    else:
        return {}

def cleanParamsUp(html):
    """ Remove the rogue code from HTML  """
    html =  urllib.unquote(str(html))
    html = "&#39".join(html.split("'"))  
    html = "&#34".join(html.split("\""))  
    html = "&#60".join(html.split("<"))  
    html = "&#62".join(html.split(">"))  
    return html

def checkString(mystring):
    """ Alphanumeric checking to weed out hacker chaff """
    isAlphaNumeric = bool(1)
    watchList = "HREF IMG XSS SCRIPT BODY URL JAVASCRIPT SCRIPTLET OBJECT EMBED HTML XML META HEAD CONTENT-TYPE STYLE FRAME IFRAME LINK LAYER ALERT ONLOAD BACKGROUND SRC".split()
    ## checks for uneven quotes ##
    tstring = mystring
    ismodified = bool(0)
    quotationCheckList = ['"', "'", '`']
    for xq in quotationCheckList:
        if tstring and (not tstring.count(xq)%2 == 0):
            tstring = tstring.replace(xq,'')
            ismodified = bool(1)
    mystring = tstring
    if ismodified == bool(1):
        return mystring
    ## new HTML default checks ##
    # Can be passed ints, so cast into str()
    tmpstring = urllib.unquote_plus(str(mystring))
    for item in watchList:
        itemStr1 = r'<+\s*[\/]*\s*'
        for xchar in item:
            itemStr1 += r'%s\s*' % xchar
        itemStr1 += r'=?'
        patHtmlWatch1 = re.compile(itemStr1 , re.I)
        try:
            matchHtml1 = patHtmlWatch1.search(tmpstring)
            if not matchHtml1 == None:
                isAlphaNumeric = bool(0)
                return isAlphaNumeric
        except:
            pass

    for item in watchList:
        itemStr1 = r'<+\s*[\/]*\s*'
        for xchar in item:
            itemStr1 += r'%s\s*' % xchar
        itemStr1 += r'=?'
        patHtmlWatch1 = re.compile(itemStr1 , re.I)
        try:
            matchHtml1 = patHtmlWatch1.search(mystring)
            if not matchHtml1 == None:
                isAlphaNumeric = bool(0)
                return isAlphaNumeric
        except:
            pass
    pat = re.compile('[\w\s\.-]')
    patOthers = re.compile('[~|#|$|^|(|)|{|}|;|?]+')
    if pmstate().bypass == False:
        ## check for alphanumeric ##
        try:
            match = pat.match(mystring)
            ## matches pat (is string) ##
            if match != None:
                ## level 2 matching: check for other special characters ##
                matchOthers = patOthers.search(mystring)
                ## matches patOthers (not string) ##
                if matchOthers != None:
                    isAlphaNumeric = bool(0)
                    return isAlphaNumeric
            ## not pat (not string) ##
            else:
                ## this section handles url escape chars ##
                try:
                    tmpstring   = urllib.unquote_plus(mystring)
                    matchOthers = patOthers.search(tmpstring)
                    ## matches patOthers (not string) ##
                    if not matchOthers == None:
                        isAlphaNumeric = bool(0)
                        return isAlphaNumeric
                except:
                    pass
                return isAlphaNumeric
        except:
            print "\nexception 2"
    return isAlphaNumeric

def recordIncident(description, typekey=''):
    query = "insert into incidents (at_time, typekey, description) \
    values (to_date('%s','yyyy-mm-dd hh24:mi:ss'), '%s', '%s')" % (
            datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'), typekey, description )
    pmdb.commitQueryDB('pmeta',query)

def fileURL(fileType=''):
    """ URL to access the image and Javascript files """
    url = config.pandamon['url']
    print " pmUtils.238--------->  ",url
    fileurl = "%s/static" % url
    fileurl = "%s/%s" %  (fileurl, fileType)
    if not 'static' in fileurl: raise ValueError(fileurl) 
    return fileurl

def fileImageURL():
  return fileURL("images")

def fileScriptURL():
  return fileURL("js")

def fileScriptCSS():
  return fileURL("css")

def getModule(modname):
   """ Find, load, return the requested module """
   return pmstate().getModule(modname)

def addModule(modname):
    if not modname in config.modules: config.modules.append(modname)

def pageSection(text):
    """ JQuery UI '.ui-widget-header' page section separator """
    txt = "<p><table class='ui-corner-all ui-widget ui-widget-header' width='100%%'><thead><tr><th>%s</th></tr></thead></table><p>" % text
    return txt
    
def tableHeader(colnames):
    """ Standard table header """
    txt = "\n<table border=0 cellspacing=0 cellpadding=3>\n"
    txt += tableRow(colnames, trstyle="style='font-weight:bold'")
    return txt

def tableRow(cols, trstyle=''):
    """ Standard table row """
    txt = "<tr %s>\n" % trstyle
    for col in cols:
        txt += "    <td>%s</td>\n" % col
    txt += "</tr>\n"
    return txt

def sortDictList(slist, key):
    """ Sort a list of dictionaries based on dict key """
    da = []
    for d in slist:
        da.append((d, d[key]))
    da.sort(sorter)
    sortedd = []
    for d in da:
        sortedd.append(d[0])
    return sortedd

def sortDictListReverse(slist, key):
    """ Reverse sort a list of dictionaries based on dict key """
    da = []
    for d in slist:
        da.append((d, d[key]))
    da.sort(rsorter)
    sortedd = []
    for d in da:
        sortedd.append(d[0])
    return sortedd

def sorter(s2, s1):
    """ Sorter to sort a dictionary """
    comp = 0
    if s1[1] > s2[1]:
        comp = 1
    elif s1[1] < s2[1]:
        comp = -1
    else:
        comp = 0
    return comp

def rsorter(s2, s1):
    """ Sorter to sort a dictionary """
    comp = 0
    if s1[1] < s2[1]:
        comp = 1
    elif s1[1] > s2[1]:
        comp = -1
    else:
        comp = 0
    return comp

def addToWhereClause(where, txt):
    """ Add txt to the existing (or not) where clause, return the complete clause """
    if  where == None or where == '' :
        # strip off leading 'and' or 'or'
        pat = re.compile('\s*(AND|OR|and|or)\s+(.*)$')
        mat = pat.match(txt)
        if mat:
            result = mat.group(2)
        else:
            result = txt
    else:
        result = "%s %s" % ( where, txt )
    return result

def addToDescription(desc, par, val):
    res = " &nbsp; %s : %s &nbsp; " % ( par, val )
    res = "%s %s" % ( desc, res )
    return res

def addTimeConstraint(where, desc, tstart, tend, varname='TIME'):
    """ Add time constraint to where clause """
    if pmstate().jobarchive == 'SimpleDB':
        t1 = "'%s'" % toSDBTime(tstart)
        t2 = "'%s'" % toSDBTime(tend)
    else:
        t1 = "to_date('%s','yyyy-mm-dd hh24:mi:ss')" % tstart.strftime('%Y-%m-%d %H:%M:%S')
        t2 = "to_date('%s','yyyy-mm-dd hh24:mi:ss')" % tend.strftime('%Y-%m-%d %H:%M:%S')
    result = addToWhereClause(where, "AND %s >= %s AND %s <= %s" % ( varname, t1, varname, t2 ) )
    delt = tend - tstart
    ndays = delt.days
    nsecs = delt.seconds
    interval = ''
    if ndays > 0: interval = "%s days " % ndays
    if nsecs > 0:
        nhours = int(nsecs/3600)
        nmins = int((nsecs-nhours*3600)/60)
        if nhours > 0: interval += "%s hours " % nhours
        if nmins > 0: interval += "%s minutes " % nmins
    desc += "&nbsp; From %s to %s (%s)" % ( tstart.strftime('%Y-%m-%d %H:%M:%S'), tend.strftime('%Y-%m-%d %H:%M:%S'), interval )
    return result, desc

#___________________________________________________________________________________________________
def normalizeSchema(schema,skip=None):
   """ Normalize the Db schema """
   for i,c in enumerate(schema):
      nm = nmap.get(c)
#         if 'pandaid' in  nm.lower() or 'time' in  nm.lower(): continue
      if skip != None and nm.lower() in skip: continue
      schema[i] = nm
   return schema


#___________________________________________________________________________________________________
def normalizeDbSchema(db,schema,skip=['pandaid','metadata','jobparameters']):
   """ Normalize the Db schema """
   description =  db.describe('^%s$' % schema)
   params = {}
   ci = name2Index(description['header'],'column_name')
   for c in description['rows']:
      nm = nmap.get(c[ci])
      c[ci]  = nm
#         if 'pandaid' in  nm.lower() or 'time' in  nm.lower(): continue
      if nm.lower() in skip: continue
      params[nm] = None
   return (description,params)

#___________________________________________________________________________________________________
def zipo(dict,oracleDict=None,delim=' AND ', quote=True,ops=' = '):
   """ return the string with unique pairs from 'dict' connected with 'delim' """
   zipped = ''
   if dict != None and len(dict) > 0:
      d = []
      for i,(k,v) in enumerate(dict.iteritems()):
         if oracleDict!=None:
            varName = ':%s_%d' % (k,i)
            oracleDict[varName] = v
            d.append("%s%s%s" % (k,ops,varName))
         else:   
            if not quote or isinstance(v,int):
               d.append("%s%s%s" % (k,ops,v))
            else:   
               d.append("%s%s'%s'" % (k,ops,v))
      zipped = delim.join(set(d))
   return zipped
   
def atlasLogBook():
   return 'https://atlas-logbook.cern.ch/elog/ATLAS+Computer+Operations+Logbook'
