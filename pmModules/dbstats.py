# dbstats.py
# Display DB status and stats
from pmUtils.pmState import pmstate
import pmUtils.pmSimpleDB as sdb
from  pmCore.pmModule import pmModule
from  pmCore.pmModule import pmRoles

class dbstats(pmModule):

   #______________________________________________________________________________________      
   def __init__(self,name=None,parent=None,obj=None):
      pmModule.__init__(self,name,parent,obj)
      self.publishUI(self.doQuery,role='html')
      self.publishUI(self.doJson)
      self.publishUI(self.doScript,role=pmRoles.script())

   #______________________________________________________________________________________      
   def doQuery(self):
       """ Process the query request
           This is the redundant method.
           It  was left here for the sake of the backward compatibiity 
       """
       title = 'Database status'
       nav = 'Archival job database in use is %s' % pmstate().jobarchive
       maintxt = ''
       dbstats = sdb.getDBStats()
       maintxt += "<p>Total size: %s MB" % dbstats['size']
       maintxt += "<p>Total items: %s M" % int(dbstats['items']/1000000)
       maintxt += "<p>Average item size: %s bytes" % dbstats['itemsize']
       maintxt += "<p>Number of domains: %s" % dbstats['ndomains']
       maintxt += "<p>Domain info:"
       dkeys = dbstats['domainstats'].keys()
       dkeys.sort()
       for d in dkeys:
           dinfo = dbstats['domainstats'][d]
           maintxt += "<br> &nbsp; &nbsp; %s: %2.1f M items &nbsp; %s MB &nbsp; %s bytes/item &nbsp; Attribute names: %s values: %s M" % \
                      ( d, dinfo['items']/1000000., dinfo['size'], dinfo['itemsize'], dinfo['attrnames'], int(dinfo['attrvalues']/1000000) )
                      
       self.publishPage(title,nav,maintxt)
       
   #______________________________________________________________________________________      
   def doTitle(self):
      self.publishTitle('Database status')

   #______________________________________________________________________________________      
   def doNavigation(self):
      self.publishNav('Archival job database in use is %s' % pmstate().jobarchive)
      
   #______________________________________________________________________________________      
   def doMain(self):
      dbstats = sdb.getDBStats()
      main = {}
      for i in ('items', 'size','itemsize','ndomains'):
         main[i] = dbstats[i]
      dkeys = dbstats['domainstats'].keys()
      dkeys.sort()
      dmain = []
      for d in dkeys:
           dinfo = dbstats['domainstats'][d]
           row = []
           row.append(d)
           for i in ('items', 'size','itemsize','attrnames','attrvalues'):
               row.append(dinfo[i])
           dmain.append(row)
      main['header'] = ['Jobs', 'Items (M)', 'MB', 'bytes/item', 'Attribute names (M)','Values (M)'];
      main['info'] = dmain
      self.publish(main)

   #______________________________________________________________________________________      
   def doJson(self):
      """ Combine together the json view of the 3 parts of the Web page layout """
      """ { "data" : %(main)s } is to be short cut for the [{ "id" : "main"  , "json" : %(main)s }] """
      self.doTitle()
      self.doNavigation()
      self.doMain()

   #______________________________________________________________________________________      
   def doLayout(self):
      """ specify the custom layout """
      pass

   #______________________________________________________________________________________      
   def doScript(self):
      # """ provides the javascript function to client-site data rendering 
        # function(tag, data) { . . . }
        # where tag - is the HTML tag (string in css notation) the data is to be rendered into
              # data - the data structure , the fucttion should render
         # The default version assumes the data is the "HTML" string to fill the innerHTML
         # of the tag provided         
      # """
      deffunc = """
         function (tag,data) {
             $(tag).empty();
             var thisTag =  $("<div></div>");
             thisTag.append("<p>Total size: " + data.size + "  MB"); 
             thisTag.append("<p>Total items: " + (data.items/(1024*1024)).toFixed() + "  MB");
             thisTag.append("<p>Average item size: " + data.itemsize + "  bytes"); 
             thisTag.append("<p>Number of domains: " + data.ndomains); 
             thisTag.append("<p>Domain info:");
             var table = $('<table cellpadding="2" cellspacing="2" border="1" class="display" id="dbstat_table"></table>');
             thisTag.append(table);
             var h = $("<thead></thead>");
             table.append(h);
             var hr = $("<tr></tr>");
             hr.css( {"text-decoration":"underline", "color":"blue", "cursor":"pointer"});
             h.append(hr);
             $.each(data.header, function(i,header) { hr.append($("<th>" +header + "</th>")); } );
             h = $("<tbody></tbody>");
             table.append(h);
             $.each(data.info, function(i,r) {
               var tr = $('<tr></tr>');
               tr.css("font-size","0.6em");
               h.append(tr);
               $.each(r, function(d,v) {
                  if (d == 1)      v = (v/100000).toFixed(2);
                  else if (d == 5) v = (v/100000).toFixed(1); 
                  var td = $("<td>" + v  + "</td>");
                  tr.append(td);
                  if ( d!=0) { td.css("text-align","right") ;}
               } );
             } );
             var h = $("<tfoot></tfoot>");
             table.append(h);
             var hr = $("<tr></tr>");
             h.append(hr);
             $.each( data.header , function(i,h) { hr.append($("<th>" + h + "</th>")); } );
             $(tag).append(thisTag);
             $('#dbstat_table').dataTable({"bProcessing": true,"bJQueryUI": true});
         }
      """
      self.publish(deffunc,role=pmRoles.script() )

   def leftMenu(self):
       """ Return html for inclusion in left menu """
       txt = "<a href='%s/dbstats'>DB 1 status</a>" % self.server().host()
       return txt
       
def leftMenu():
    """ Return html for inclusion in left menu """
    txt = "<a href='%s/dbstats'>DB 2 status</a>" % '' # "Dummy"
    
    return txt
