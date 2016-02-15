"""
pandamon security related routines
"""

import urllib, re
import pmUtils as utils
from pmState import pmstate

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
    proceed = True
    for key in qdict:
        keyok = checkString(key)
        if not keyok in [0, 1]:
            newkey = keyok 
            qdict[newkey] = qdict[key]
            del qdict[key]
            keyok = True
        if keyok: 
            valok = checkString(qdict[key])
            if not valok in [0, 1]:
                qdict[key] = valok
                valok = True
            if not valok:
                qdicttxt =utils.cleanParamsUp(qdict[key])
                increport = "Invalid parameter value: [%s] for key: [%s]" % (qdicttxt, utils.cleanParamsUp(key))
                print increport
                try:
                   if key != 'errinfo': 
                       utils.recordIncident(increport, 'monsecurity')
                   utils.reportWarning(increport)
                except:
                   pass
                proceed = False
        else:
            if not str(qdict[key]) == '':
                utils.reportWarning("Invalid parameter key: %s" % utils.cleanParamsUp(key))
                proceed = False
    if proceed:
        return qdict
    else:
        return {}

def checkString(mystring):
    """ Alphanumeric checking to weed out hacker chaff """
    isAlphaNumeric = True
    # explicitly accept harmless value occurring in logging
    if mystring == '()': return True
    watchList = "HREF IMG XSS SCRIPT BODY URL JAVASCRIPT SCRIPTLET OBJECT EMBED HTML XML META HEAD CONTENT-TYPE STYLE FRAME IFRAME LINK LAYER ALERT ONLOAD BACKGROUND SRC".split()
    ## checks for uneven quotes ##
    tstring = mystring
    ismodified = False
    quotationCheckList = ['"', "'", '`']
    for xq in quotationCheckList:
        if tstring and (not tstring.count(xq)%2 == 0):
            tstring = tstring.replace(xq,'')
            ismodified = True
    mystring = tstring
    if ismodified: return mystring
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
                isAlphaNumeric = False
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
                isAlphaNumeric = False
                return isAlphaNumeric
        except:
            pass
    pat = re.compile('[\w\s\.-]')
    patOthers = re.compile('[~|#|$|^|(|)|{|}|;|?]+')
    if not pmstate().bypass:
        ## check for alphanumeric ##
        try:
            match = pat.match(mystring)
            ## matches pat (is string) ##
            if match != None:
                ## level 2 matching: check for other special characters ##
                matchOthers = patOthers.search(mystring)
                ## matches patOthers (not string) ##
                if matchOthers != None:
                    isAlphaNumeric = False
                    return isAlphaNumeric
            ## not pat (not string) ##
            else:
                ## this section handles url escape chars ##
                try:
                    tmpstring = urllib.unquote_plus(mystring)
                    matchOthers = patOthers.search(tmpstring)
                    ## matches patOthers (not string) ##
                    if not matchOthers == None:
                        isAlphaNumeric = False
                        return isAlphaNumeric
                except:
                    pass
                return isAlphaNumeric
        except:
            print "\nexception 2"
    return isAlphaNumeric
