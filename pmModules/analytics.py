""" The Panitkin's Analytics  """
# $Id: analytics.py 9290 2011-10-07 03:12:24Z fine $
# Author: Valeri Fine (fine@bnl.gov) Sept 22, 2011
from pmCore.pmModule import pmModule
from pmCore.pmModule import pmRoles
import pmUtils.pmUtils as utils

#______________________________________________________________________________________      
class analytics(pmModule):
   """ The Panitkin's Analytics  """
   #______________________________________________________________________________________      
   def __init__(self,name=None,parent=None,obj=None):
      pmModule.__init__(self,name,parent,obj)
      self.publishUI(self.doQuery)
      self.publishUI(self.doScript,role=pmRoles.script())

   #______________________________________________________________________________________      
   def doQuery(self,site='ALL',From='Jun_2011',To='May_2012',type='7'):
      """ Process the query request 
         Arguments:
            site  -- the site name to present the analystics for site
            month --
            year  --
            type  --
      """
      data =  { "site" : site, "from" : From, "to" : To, "type" :  type }
      self.publishTitle("Panda Analytics %(type)s of %(site)s site from %(from)s to %(to)s" % data )

      types = ['filetype_jobsets', 'jobs_filetype' ,'filetype_popularity', 'jobs_per_jobset'] 
#       data["filename"] = self.server().fileImageURL() + "/analytics/pic/%(type)s_%(month)s_%(year)s_ANALY_%(site)s.png" % data
      files = []
      for type in types:
         files.append('%(site)s_%(type)s_%(from)s_%(to)s' % {'site': site, 'type' : type, 'from' : From, 'to' : To } )
      data["filenames"] = files
      # self.server().fileImageURL() + "/analytics/pic/%(type)s_%(month)s_%(year)s_ANALY_%(site)s.png" % data
      self.publishMain(main=data,role=pmRoles.object())
   #______________________________________________________________________________________      
   def doScript(self,site='ALL',From='Jun_2011',To='May_2012',type='7'):
      func = """
         function(tag,data) {
            var files = data.filenames;
            $(tag).empty();
            var table = "<table>";
            table += "<tbody>";
            for (var f in files) {
               if (!f%2 || true ) { table += "<tr>"; }
               table += "<th><img src='http://atlascloud.org/static/images/analytics/analysis_" +data['type'] +"/" +files[f]+ ".png' /></th>";
               if (f%2 || true ) { table += "</tr>"; }
            }
            table += "</tbody><table>";
            $(tag).html(table);
         }
      """
      self.publish(func,role=pmRoles.script())   
   
