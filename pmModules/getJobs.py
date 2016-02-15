# $Id: getJobs.py 9690 2011-11-16 22:28:01Z fine $
# Display getJobs information
from pmUtils.pmState import pmstate
from pmCore.pmModule import pmRoles
import pmTaskBuffer.pmTaskBuffer as pmTaskBuffer
import pmUtils.pmUtils as utils
import pmUtils.Stopwatch as Stopwatch

from  pmCore.pmModule import pmModule

class getJobs(pmModule):

    #______________________________________________________________________________________
   def __init__(self,name=None,parent=None,obj=None):
      pmModule.__init__(self,name,parent,obj)
      self.publishUI(self.doJson)
      self.publishUI(self.doScript,role=pmRoles.script())

      # self.publishAuthor(name,email)
   #______________________________________________________________________________________      
   def doMain(self,nJobs,siteName,prodSourceLabel,cpu,mem,diskSpace,modificationHost,timeout,computingElement,
                atlasRelease,prodUserID,getProxyKey,countryGroup,workingGroup,allowOtherCountry):
      connectionTime = Stopwatch.Stopwatch()
      p = pmTaskBuffer.pmTaskBuffer(dbhost=None,dbpasswd=None,dbuser=None,dbname=None)
      timer = Stopwatch.Stopwatch()
      jobs=p.getJobs(nJobs,siteName,prodSourceLabel,cpu,mem,diskSpace,modificationHost,timeout,computingElement,
                atlasRelease,prodUserID,getProxyKey,countryGroup,workingGroup,allowOtherCountry)
      main = {}
      main["buffer"] = {}
      main["buffer"]["method"] = 'getJobs'
      main["buffer"]["params"] = (nJobs,siteName,prodSourceLabel,cpu,mem,diskSpace,modificationHost,timeout,computingElement,
                atlasRelease,prodUserID,getProxyKey,countryGroup,workingGroup,allowOtherCountry)
      main["buffer"]["data"] = jobs
      
      main['time'] = {}
      main['time'] ['fetch'] = "%s" % timer
      main['time'] ['query'] = "%s" % connectionTime

      self.publish(main)

   #______________________________________________________________________________________      
   def doJson(self,nJobs=10,siteName='ANALY_VICTORIA-WG1',prodSourceLabel='user',cpu=0,mem=0,diskSpace=0,modificationHost='',timeout=0,computingElement=None,
                atlasRelease='no use',prodUserID=None,getProxyKey=None,countryGroup='',workingGroup='',allowOtherCountry=True):
      """ 
          Invoke the TaskBuffer.getJobs method of <a href="https://svnweb.cern.ch/trac/panda/browser/panda-server/current/pandaserver/taskbuffer/TaskBuffer.py">TaskBuffer</a><br>
      """
      self.publishTitle('Get jobs from Task Buffer from pid: %s !!!' % self.server().getpid() )
      timer = Stopwatch.Stopwatch()
      self.doMain(nJobs,siteName,prodSourceLabel,cpu,mem,diskSpace,modificationHost,timeout,computingElement,
                atlasRelease,prodUserID,getProxyKey,countryGroup,workingGroup,allowOtherCountry)
      self.publishNav('The TaskBuffer.getJobs  from CERN: "%s".  "%s"' % ( ( nJobs,siteName,prodSourceLabel,cpu,mem,diskSpace,modificationHost,timeout,computingElement,
                atlasRelease,prodUserID,getProxyKey,countryGroup,workingGroup,allowOtherCountry), timer ) ) # I know the cyber security will be mad ;-) VF.

   #______________________________________________________________________________________      
   def doScript(self,nJobs=10,siteName='ANALY_VICTORIA-WG1',prodSourceLabel='user',cpu=0,mem=0,diskSpace=0,modificationHost='',timeout=0,computingElement=None,
                atlasRelease='no use',prodUserID=None,getProxyKey=None,countryGroup='',workingGroup='',allowOtherCountry=True):
      func = """
         function(tag,main) {
            $(tag).empty();
            var dt = false;
            var time = main.time;
            var method = main.buffer.method;
            var params = main.buffer.params;
            var data = main.buffer.data;
            var d = $('<div></div>');
            var query = "<P>The server spent <b>" + time.query + "</b> to access the CERN Oracle server";
            var fetch = " and <p><b>" + time.fetch + "</b> to execute the TaskBuffer.%s:%s query"; 
            d.html(query + fetch);
            var tdiv = $("<div></div>");
            var tline = '<p><b>' + method + '(' +JSON.stringify(params)+ '): </b><br>';
            dt = true;
            tline += '<hr>';
            tline += '<table id="TaskBuferTableId" class="display"><thead><tr><th>Parameter</th><th>Value</th></thead><tbody>';
            for (var i in data) {
               var num = data[i];
               tline += "<tr><td>" +  i + "</td><td>" +  JSON.stringify(num) + "</td></tr>";
            }
            tline += "<tbody></table>";
            tdiv.html(tline);
            d.append(tdiv);
            $(tag).append(d);
            if (dt) {
               $(document).ready(function(){   
                   $('#TaskBuferTableId').dataTable( { "bJQueryUI": true });
               } );
            }
         }
      """ % ('getJobs', ( nJobs,siteName,prodSourceLabel,cpu,mem,diskSpace,modificationHost,timeout,computingElement,
                atlasRelease,prodUserID,getProxyKey,countryGroup,workingGroup,allowOtherCountry))
      self.publish(func,role=pmRoles.script())   

def leftMenu():
    """ Return html for inclusion in left menu """
    #Temporary to preserve the backward compatibility 
    txt = "<a href='%s/getJobs'>Hello Panda TaskBuffer.getJobs</a>" % self.server().branchUrl()
    return txt
