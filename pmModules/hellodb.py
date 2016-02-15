# $Id: hellodb.py 13701 2012-12-03 20:46:09Z fine $
# Display DB status and stats
from pmUtils.pmState import pmstate
import pmUtils.pmSimpleDB as sdb
import pmUtils.pmUtils as utils

from  pmCore.pmModule import pmModule

class hellodb(pmModule):

    #______________________________________________________________________________________      
   def __init__(self,name=None,parent=None,obj=None):
      pmModule.__init__(self,name,parent,obj)
      self.publishUI(self.doJson)

      # self.publishAuthor(name,email)
   def doMain(self):
      hellodb = sdb.getDBStats()
      main = {}
      for i in ('items', 'size','itemsize','ndomains'):
         main[i] = hellodb[i]
      dkeys = hellodb['domainstats'].keys()
      dkeys.sort()
      dmain = []
      for d in dkeys:
           dinfo = hellodb['domainstats'][d]
           row = []
           row.append(d)
           for i in ('items', 'size','itemsize','attrnames','attrvalues'):
               row.append(dinfo[i])
           dmain.append(row)
      main['header'] = ['Jobs', 'Items (M)', 'MB', 'bytes/item', 'Attribute names (M)','Values (M)'];
      main['info'] = dmain
      self.publish(main)

   def doJson(self):
      """ Combine together the json view of the 3 parts of the Web page layout """
      """ { "data" : %(main)s } is to be short cut for the [{ "id" : "main"  , "json" : %(main)s }] """
      self.publishTitle('Hello Database status')
      self.publishNav('"Archival job database in use is %s"' % pmstate().jobarchive)
      self.doMain()
      self.publish("%s/%s" % (self.server().fileScriptURL(),"hellodb.js"),role="script")

def leftMenu():
    """ Return html for inclusion in left menu """
    #Temporart to preserve the backward compatibility 
    txt = "<a href='%s/hellodb'>Hello DB status</a>" % self.server().branchUrl()
    return txt
