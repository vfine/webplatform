# $Id: describe.py 17799 2013-12-18 16:56:57Z fine $
# Display DB status and stats
from pmUtils.pmState import pmstate
from pmCore.pmModule import pmRoles
from  monitor.nameMappings import nmap
from  pmTaskBuffer.pmTaskBuffer import pmtaskbuffer as pmt
from  pmTaskBuffer.pmTaskBuffer import pmgrisliaskbuffer as gmt
try:
   from  pmTaskBuffer.pmTaskBuffer import pmdeftbuffer as pdf
except:
   pass
import pmUtils.pmUtils as utils
import pmUtils.Stopwatch as Stopwatch

from  pmCore.pmModule import pmModule

class describe(pmModule):

    #______________________________________________________________________________________
   def __init__(self,name=None,parent=None,obj=None):
      pmModule.__init__(self,name,parent,obj)
      self.publishUI(self.doJson)
      self._db = {}
      if pmt != None: self._db['pmt']=  pmt
      if gmt != None: self._db['gmt']=  gmt
      try:
         if jmt != None: self._db['jmt']=  pmt
      except:
         pass 
      try:
         if pdf != None: self._db['pdf']=  pdf
      except:
         pass      

   #______________________________________________________________________________________      
   def doJson(self,table=None,column=None,db='pmt',doc=None):
      """ 
          Describe the selected Panda table / column <br>
          <code>table  = the Db table name regexp comma-separated patterns to check</code><br>
          <code>column = the Db table column name regexp comma-separated patterns to find</code><br>
          <code>doc    = '*|all' - document all columns selected if available<br>
               = 'comma-separated list of the regexp' is to display the columns with  the comments matched the regexp provided
          </code><br>
      """ 
      title = 'Describe the Panda Db '
      inp = False
      if table != None  and table != 'None': 
         title += "'%s*'" % table
         inp = True
         title +=" table"
      else:   
         title +=" tables"
      if column != None and column !='None': 
          title += " with '%s*' column " % column
          inp = True
      main = {}
      if  inp:      
         self.publishTitle(title)
         timer = Stopwatch.Stopwatch()
         main["buffer"] = {}
         main["buffer"]["db"] = db
         dbAccess = self._db.get(db)
         if dbAccess != None:
            main["buffer"]["method"] = "describe"
            main["buffer"]["params"] = (table,column,doc) 
            main["buffer"]["type"] = False
            if not utils.isFilled(doc):
               tdes = dbAccess.describe(table,column)
               iclmn = utils.name2Index(tdes['header'],'COLUMN_NAME')
               rows = tdes['rows']
               for h in rows:
                  h[iclmn] = nmap.get(h[iclmn])
               main["buffer"]["data"] = tdes
            else:
               docrows = []
               if utils.isFilled(table):
                  tdoc = dbAccess.pandatabs(table,comments=doc,select="table_name,'Table Description' as COLUMN_NAME,comments")
                  iclmn = utils.name2Index(tdoc['header'],'COLUMN_NAME')
                  docrows = tdoc['rows']
                  for h in docrows:
                     h[iclmn] = nmap.get(h[iclmn])
               tcol = dbAccess.pandacols(column,table,select='TABLE_NAME,COLUMN_NAME,COMMENTS', comments=doc)
               iclmn = utils.name2Index(tcol['header'],'COLUMN_NAME')
               for h in tcol['rows']:
                  h[iclmn] = nmap.get(h[iclmn])
               tcol['rows'] += docrows
               main["buffer"]["data"] = tcol
               self.publish( {'s-maxage':60000,'max-age': 6000}, role=pmRoles.cache())
         else:
            self.publishTitle("Error: 'describe' -  unknown Db name '%s' has been provided" % db)
            self.publish( {'s-maxage':0,'max-age': 0}, role=pmRoles.cache())
      else:
         self.publishTitle("Error: 'describe' -  no parameter has been provided. Define one at least. It should be either 'column' or 'table'")
         self.publish( {'s-maxage':0,'max-age': 0}, role=pmRoles.cache())
      self.publish(main)
      self.publish( "%s/%s" % (self.server().fileScriptURL(),"taskBuffer/%s.js" % "describe"),role=pmRoles.script() )


def leftMenu():
    """ Return html for inclusion in left menu """
    #Temporary to preserve the backward compatibility 
    txt = "<a href='%s/describe'>Panda Db Table</a>" % self.server().branchUrl()
    return txt
