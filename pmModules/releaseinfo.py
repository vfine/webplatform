""" Display the Releases  </td><td>$Rev$"""
# $Id: releaseinfo.py 17501 2013-11-26 16:13:01Z fine $
# Display Releases

from datetime import datetime
from pmUtils.pmState import pmstate
from pmCore.pmModule import pmRoles
import pmUtils.pmUtils as utils
import pmUtils.Stopwatch as Stopwatch
from  pmTaskBuffer.pmTaskBuffer import pmtaskbuffer as pmt

from  pmCore.pmModule import pmModule

class releaseinfo(pmModule):

    #______________________________________________________________________________________
   def __init__(self,name=None,parent=None,obj=None):
      pmModule.__init__(self,name,parent,obj)
      self.publishUI(self.doJson)
      
   #______________________________________________________________________________________      
   def compress(self,header,rows,cachenone=False):
      ih = {}
      for ix,h in enumerate(header): ih[h.lower()] = ix;
      sited = {}
      isite      = ih['siteid']
      icloud     = ih['cloud']
      icmtconfig = ih['cmtconfig'] 
      irelease   = ih['release'] 
      icache     = ih['cache'] 
      for r in rows:
         site = r[isite]
         cloud = r[icloud]
         if cloud==None: continue
         suffix = ''
         if r[icmtconfig] != None and  r[icmtconfig] != '' and r[icmtconfig] != 'None':  suffix = ": "+ r[icmtconfig]
         try: # https://savannah.cern.ch/bugs/index.php?99027
            rel = r[irelease] + suffix
         except:
            r[irelease] = "unknown"
            rel = r[irelease] + suffix
         if not sited.has_key(cloud):            sited[cloud] = {};
         if not sited[cloud].has_key(site):      sited[cloud][site] = {} ;
         if not sited[cloud][site].has_key(rel): sited[cloud][site][rel] = []
         cache=r[icache]
         if cachenone or (cache!=None and cache != "None") :
            if cache == None: cache='Undefined'
            cache = cache.replace('AtlasProduction-','')
            sited[cloud][site][rel].append([r[irelease],r[icache]])
      return sited      

   #______________________________________________________________________________________      
   def doJson(self,release=None,cloud=None,site=None,cache=None,cmt=None):
      """ 
          Release information displays <br><ul>
          <li><code>release = release comma-separated regex name pattern </code>
          <li><code>cloud = cloud abbreviation to narrow the search </code>
          <li><code>site = siteid to select the release info for that Panda site</code>
          <li><code>cache = cache name </code>
          <li><code>cmt = cmtconfig comma-separated regex pattern </code>
          </ul>
      """ 
      if release != None and site == None:
         title = "Sites holding release %s" % release
      else:
         title = "Release availability "
      
      if   site  != None: title += " from site: %s" % site
      elif cloud != None: 
          if release == None: title += " at sites "
          title += " from cloud: %s" % cloud
      else: title += " at sites"
      
      if cache!=None : title += ", cache %s" % cache
      self.publishTitle(title)

      q = pmt.getReleases(release,cloud,site,cache,cmt)
      header =  q['header']
      rows =  q['rows']
      main = {}
      main['header'] = header if len(rows) >0 else []
      main['info'] = self.compress(header,rows,cache=="None")
      main['time'] = {}
      main['params'] = {'release':release,'cloud':cloud,'site':site,'cache':cache}
      self.publish(main)
      self.publish( "%s/%s" % ( self.server().fileScriptURL(),"monitor/%s.js" % "releaseinfo" ),role=pmRoles.script())
      self.publish( {'s-maxage':3600,'max-age': 3600}, role=pmRoles.cache())
