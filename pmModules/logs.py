# logs.py
# Display Panda logger content
#
import re, os
from datetime import datetime, timedelta

import pmConfig.pmConfig as config
import pmUtils.pmUtils as utils
from pmUtils.pmState import pmstate
from  pmCore.pmModule import pmModule


logColumns = ( 'TIME', 'NAME', 'LEVELNAME', 'TYPE', 'MESSAGE' )
#knownKeys  = ( 'RELATIVECREATED', 'PROCESS', 'MODULE', 'FUNCNAME', 'MESSAGE', 'TYPE', 'BINTIME', 'FILENAME', 'LEVELNO',
#        'LINENO', 'ASCTIME', 'MSG', 'USER', 'ARGS', 'EXC_TEXT', 'ID', 'NAME', 'THREAD', 'CREATED', 'THREADNAME', 'MSECS',
#        'PATHNAME', 'EXC_INFO', 'LEVELNAME' )

knownKeys  = ( 'RELATIVECREATED', 'PROCESS', 'MODULE', 'FUNCNAME', 'BINTIME', 'FILENAME', 'LEVELNO',
        'LINENO', 'ASCTIME', 'MSG', 'USER', 'ARGS', 'EXC_TEXT', 'ID', 'THREAD', 'CREATED', 'THREADNAME', 'MSECS',
        'PATHNAME', 'EXC_INFO','PANDAID','ACTION','QUEUE','DN' )

def queryLogs(where, selection, db=''):
    """ pass user query to back end DB and return the results """
    results = []
    if db == '': db = pmstate().jobarchive
    if db == 'SimpleDB':
        import pmUtils.pmSimpleDB as sdb
        print "\n\n --- 21 ------- ", where, selection
        results = sdb.getLogRecords(filter=where, selection=selection, limit=3000)
    return results

def buildWhereClause(tstart,tend,hours,days,columns,where):
    """ Build complete where clause appropriate to the back end DB """
    desc = ''

    ## Add time constraints
    if days != None: hours = int(days)*24
    tstartv = None
    tendv = None
    if tstart==None:
      tstartv = datetime.utcnow() - timedelta(hours=hours)
    else:
      tstartv = utils.timeValue(tstart)
    if tend == None:
      tendv = datetime.utcnow()
    else:
      tendv = utils.timeValue(tend)
    wherev, desc = utils.addTimeConstraint(where, desc, tstartv, tendv)
    ## Add any additional selections appearing in the query
    # wherev = None
    if wherev != None:
       for p in columns:
           val =columns[p]
           if val == None: continue
           if p in logColumns:
               addpar = p
           elif p in knownKeys:
               addpar = p # p.replace('KEY:','')
           else:
               continue
           wherev = utils.addToWhereClause(wherev, "AND %s='%s'" % ( addpar, val ))
           desc = utils.addToDescription(desc, addpar, val)

    return wherev, desc, tstartv, tendv

def doQuery(url,tstart=None,tend=None,hours=None,days=None,columns=None, where=None,details=None):
    """ Process the query request """
    pmstate().windowTitle = "pLogs"
    title = 'Incident log'
    nav = None
    menuinfo = None
    maintxt = ''
    if len(pmstate().params) == 0:
        # Main page
        maintxt += logMain(url,hours=hours,details=details)
    else:
        # custom summary
        maintxt += logSummary(url,tstart,tend,hours,days,columns,where,details)
    return title, menuinfo, nav, maintxt, 'html'

def logMain(url,tstart=None,tend=None,hours=None,days=None,columns=None,details=None):
    txt = ''
    selection = 'NAME, TYPE, LEVELNAME'
    ## Distinct summaries for ERROR, WARNING, priority INFO, INFO+DEBUG, with different integration times

    hours = 3
    txt += utils.pageSection("Errors and warnings, last %s hours" % hours)
    where = "(LEVELNAME = 'ERROR' or LEVELNAME = 'WARNING')"
    where, desc, tstartv, tendv = buildWhereClause(tstart,tend,hours,days,columns, where)
    errorlogs = queryLogs(where, selection)
    txt += showLogs(errorlogs, tstartv, tendv,details,url)

    hours = 12
    txt += utils.pageSection("Logged incidents, last %s hours" % hours)
    where = "(NAME='panda.incident')"
    where, desc, tstart, tend = buildWhereClause(tstartv,tendv,hours,days,columns,where)
    priologs = queryLogs(where, selection)
    txt += showLogs(priologs, tstartv, tendv,details,url)

    hours = 1
    txt += utils.pageSection("All info and debug streams, last %s hour" % hours)
    where = "(LEVELNAME = 'INFO' or LEVELNAME = 'DEBUG')"
    where, desc, tstartv, tendv = buildWhereClause(tstartv,tendv,hours,days,columns,where)
    bulklogs = queryLogs(where, selection)
    txt += showLogs(bulklogs, tstartv, tendv,details,url)

    return txt

def logSummary(url,tstart=None,tend=None,hours=None,days=None,columns=None,where=None,details=None):
    ## Perform the query
    txt = ''
    selection = 'NAME, TYPE, LEVELNAME'
    if details!=None: selection += ",TIME, MESSAGE"
    pmstate().jobarchive = 'SimpleDB'
    wherev, desc, tstartv, tendv = buildWhereClause(tstart,tend,hours,days,columns,where)
    txt += utils.pageSection(desc)
    logs = queryLogs(wherev, selection)
    print "Retrieved %s log records" % len(logs)
    txt += showLogs(logs, tstartv, tendv,details,url)
    return txt

def showLogs(logs, tstart, tend,details,url):
    html = ''
    logd = {}
    for l in logs:
        if not l['NAME'] in logd: logd[l['NAME']] = {}
        if not l['TYPE'] in logd[l['NAME']]: logd[l['NAME']][l['TYPE']] = {}
        if not l['LEVELNAME'] in logd[l['NAME']][l['TYPE']]: logd[l['NAME']][l['TYPE']][l['LEVELNAME']] = 0
        logd[l['NAME']][l['TYPE']][l['LEVELNAME']] += 1

    html += "<table border=0 cellpadding=2><tr style='font-weight: bold'><td>Category</td><td>Type</td><td>Level</td><td>Count</td></tr>"
    catkeys = logd.keys()
    catkeys.sort()
    for c in catkeys:
        nc = 0
        cat = logd[c]
        typekeys = cat.keys()
        typekeys.sort()
        for t in typekeys:
            nt = 0
            typ = cat[t]
            for l in ('INFO','DEBUG','WARNING','ERROR','CRITICAL'):
                if not typ.has_key(l): continue
                if nc == 0:
                    cattxt = c
                else:
                    cattxt = '&nbsp'
                if nt == 0:
                    typtxt = t
                else:
                    typtxt = '&nbsp'
                nc += 1
                nt += 1
                levelcount = typ[l]
                color = 'darkgreen'
                if l == 'WARNING':
                    color = 'darkgoldenrod'
                elif l == 'ERROR' or l == 'CRITICAL':
                    color = 'red'
                ltxt = "<a href='%s/logs/?DETAILS&NAME=%s&TYPE=%s&LEVELNAME=%s&tstart=%s&tend=%s'><div style='color: %s'>%s</div></a>" % \
                    ( url, c, t, l, tstart, tend, color, l )
                html += "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td>" % ( cattxt, typtxt, ltxt, levelcount)
    html += "</table>"


    if  details == None: return html

    html += "<table border=0 cellpadding=3><tr><td><b>Time</b></td><td><b>Message</b></td></tr>"
    sortedLogs = utils.sortDictList(logs,'TIME')
    for l in sortedLogs:
        msg = decorateMessage(l['MESSAGE'], l['TYPE'], tstart, tend,url)
        html += "<tr><td>%s</td><td>%s</td></tr>" % ( utils.fromSDBTime(l['TIME']), msg )        
    html += "</table>"
    return html

def decorateMessage(msg, type, tstart, tend,url):
    """ Add links to message based on keys """
    txt = msg
    pat = '([a-zA-Z0-9\_\-\.]+)\s*\=\s*([a-zA-Z0-9\_\-\.]+)'
    matches = re.finditer(pat, txt)
    for mat in matches:
        keyorig = mat.group(1)
        key = keyorig.upper()[:127]
        val = mat.group(2)
        u = "%(url)s/logs/?DETAILS&TYPE=%(type)s&%(key)s=%(val)s&days=14" % {"url" : url, "type": type, "key" : key, "val" : val }
#        u = "%s/logs/?TYPE=%s&%s=%s&tstart=%s&tend=%s" % ( self.server().branchUrl(), type, key, val, tstart, tend )
        link = "%s=<a href='%s'>%s</a>" % ( key, u, val )
        m = re.search('(%s\s*\=\s*%s)' % (keyorig, val), txt)
        if m:
            repl = m.group(1)
            txt = txt.replace(repl, link)
        else:
            print "Could not match %s=%s in %s" % ( keyorig, val, txt)

    # Turn bug references into links
    elogMatch = re.search('elog[^0-9]*([0-9]+)',txt.lower())
    ggusMatch = re.search('ggus[^0-9]*([0-9]+)',txt.lower())
    rtMatch = re.search('rt[- \.:]([0-9]+)',txt.lower())
    logid=''
    if elogMatch:
        logid = elogMatch.group(1)
        txt = txt.replace(logid,
            ": <a href='%s/%s'>%s</a>" \
            % ( config.logbook, logid, logid ) )
    elif ggusMatch:
        logid = ggusMatch.group(1)
        txt = txt.replace(logid, "<a href='%s?ticket=%s'>%s</a>" \
            % ( config.ggus, logid, logid ) )
    elif rtMatch:
        logid = rtMatch.group(1)
        txt = txt.replace(logid, "<a href='%s?id=%s'>%s</a>" \
            % ( config.bnl_rt, logid, logid ) )

    return txt

def leftMenu():
    """ Return html for inclusion in left menu """
    txt = "<a href='%s/logs'>Incidents</a>" % self.server().branchUrl()
    return txt

def topMenu():
    """ Return html for inclusion in top menu """
    
class logs(pmModule):
   #______________________________________________________________________________________      
   def __init__(self,name=None,parent=None,obj=None):
      pmModule.__init__(self,name,parent,obj)
      params = {}
      for c in knownKeys: params[c] = None
      self.publishUI(self.doQuery,role='html',params=params)
      
   #______________________________________________________________________________________      
   def doQuery(self,tstart=None,tend=None,hours=3,days=None,TIME=None, NAME=None, LEVELNAME=None, TYPE=None, MESSAGE=None,where=None,DETAILS=None):
      columns = {'TIME': TIME, 'NAME':NAME, 'LEVELNAME':LEVELNAME, 'TYPE':TYPE, 'MESSAGE':MESSAGE }
      extra = self.extraValues()
      columns.update(extra)
      (title, menuinfo, nav, maintxt, role) = doQuery(self.server().script(),tstart,tend,hours,days,columns,where,DETAILS)
      self.publishPage(title=title, main=maintxt) 

    

