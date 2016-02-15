"""
pandamon SimpleDB routines
"""
import Queue, threading, time, sys
import boto
from pmConfig.pmAccess import SimpleDBAccess
import pmUtils as utils

upload_queue = Queue.Queue()
cleanup_queue = Queue.Queue()

sdbHandle = None
global alldomains, jobdomains, curdomain
alldomains = []
jobdomains = []
curdomain = None
results = {}

class ThreadedGetJobRecords(threading.Thread):
    """ Request job records from domains in parallel """
    def __init__(self, inqueue, outqueue):
        threading.Thread.__init__(self)
        self.queue = inqueue
        self.out_queue = outqueue

    def run(self):
        while True:
            try:
                # grabs domain name and query from queue and performs query on this domain
                dname, query, fields = self.queue.get()
                result = getJobRecordsFromDomain(dname, query, fields)
                results[dname] = result
                # save results for any post-processing
                self.out_queue.put(result)
                # signals to queue job is done
                self.queue.task_done()
            except:
                utils.reportError("Failure retrieving job records from domain %s" % dname)
                self.queue.task_done()

def initSDB(dbname='jobs', quiet=False):
    """ Connect to SimpleDB """
    global sdbHandle
    sdbHandle = boto.connect_sdb(SimpleDBAccess['akey'],SimpleDBAccess['skey'])
    global alldomains, jobdomains
    if dbname == 'jobs' and len(jobdomains) == 0:
        alldomains = sdbHandle.get_all_domains()
        for d in alldomains:
            if d.name.startswith('PandaJobs'):
                jobdomains.append(d)
    elif dbname != 'jobs':
        print "Open domain", dbname
        curdomain = sdbHandle.get_domain(dbname)

def getDBStats():
    initSDB()
    global sdbHandle, alldomains
    dbstats = {}
    dbstats['domains'] = alldomains
    dbstats['ndomains'] = len(alldomains)
    dbstats['domainstats'] = {}
    dstats = dbstats['domainstats']
    totalbytes = 0
    totalitems = 0
    for d in alldomains:
        dname = d.name
        meta = sdbHandle.domain_metadata(d)
        dstats[dname] = {}
        dstats[dname]['size'] = meta.attr_values_size/1000000
        dstats[dname]['items'] = meta.item_count
        dstats[dname]['attrnames'] = meta.attr_name_count
        dstats[dname]['attrvalues'] = meta.attr_value_count
        if meta.item_count > 0:
            dstats[dname]['itemsize'] = int(meta.attr_values_size/meta.item_count)
        else:
            dstats[dname]['itemsize'] = 0
        totalbytes += meta.attr_values_size
        totalitems += meta.item_count
        print "%s: items:%s cols:%s pairs:%s size:%s bytes/item:%s" % ( d.name, dstats[dname]['items'], dstats[dname]['attrnames'],
            dstats[dname]['attrvalues'], dstats[dname]['size'], dstats[dname]['itemsize'] )
    dbstats['size'] = totalbytes/1000000
    dbstats['items'] = totalitems
    print "Total size (MB):", totalbytes/1000000
    print "Total items:", totalitems
    if totalitems > 0:
        print "Bytes/item:", totalbytes/totalitems
        dbstats['itemsize'] = int(totalbytes/totalitems)
    else:
        dbstats['itemsize'] = 0
    return dbstats

def getRecords(domainName, query, limit=None):
    import xml.sax._exceptions
    #if limit: query += " LIMIT %s" % limit
    try:
        next_token = None
        res = []
        while True:
            r1 = sdbHandle.select(domainName, query, next_token)
            for r in r1:
                res.append(r)
            next_token = r1.next_token
            if next_token == None: break
    #except SAXParseException:
    #    pass
    except:
        utils.reportError("Error reading domain %s" % domainName)
        res = []
    if len(res) > 0:
        print "%s records from %s" % ( len(res), domainName )
    result = []
    for r in res:
        result.append(r)
    return result

def getLogRecords(tstart=None, tend=None, selection='*', filter='', limit=None):
    initSDB('PandaLog')
    if filter != '':
        where = ' where %s' % filter
    else:
        where = ''
    query = "select %s from PandaLog %s" % ( selection, where )
    res = getRecords('PandaLog', query, limit)
    return res

def getJobRecordsFromDomain(domainName, query, fields):
    """ Request job records matching the query. Returns all fields unless csv field list is provided. """
    fullquery = "select %s from %s where %s" % ( fields, domainName, query )
    res = getRecords(domainName, fullquery)
    return res

def getJobRecords(query, fields='*'):
    """ User routine to retrieve job records from SimpleDB """

    initSDB()
    tstart = time.time()

    # spawn a pool of threads, and pass them queue instance
    for i in range(len(jobdomains)):
        t = ThreadedGetJobRecords(upload_queue, cleanup_queue)
        t.setDaemon(True)
        t.start()

    # populate queue with data
    for d in jobdomains:
        domainTuple = ( d.name, query, fields )
        upload_queue.put(domainTuple)

    # wait on the queue until everything has been processed
    upload_queue.join()

    # process results
    total = []
    fkeys = results.keys()
    fkeys.sort()
    for f in fkeys:
        for fr in results[f]:
            total.append(fr)

    tend = time.time()
    print "Elapsed Time: %s" % (tend - tstart)

    return total

def getUserRecords(where, selection='*'):
    initSDB('PandaUsers')
    query = "SELECT %s from PandaUsers %s" % ( selection, where )
    print query
    res = getRecords('PandaUsers', query)
    return res

def getUserSummaryRecords(where, selection='*'):
    initSDB('PandaSummary')
    query = "SELECT %s from PandaSummary %s" % ( selection, where )
    print query
    res = getRecords('PandaSummary', query)
    return res

def __main__():
    getJobRecords("PANDAID = '1173664085'")

    sys.exit()
    for domain in jobdomains:
        fullquery = "select PANDAID from %s limit 5" % domain.name
        print fullquery
        res = sdbHandle.select(domain, fullquery)
