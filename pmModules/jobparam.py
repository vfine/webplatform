""" Get the List of Panda id with either jobParameters or MetaData</td>,<td>$Rev: 17644 $ """
# $Id: jobparam.py 9690 2011-11-16 22:28:01Z fine $
# Display DB status and stats
from pmUtils.pmState import pmstate
from pmCore.pmModule import pmRoles
from  pmTaskBuffer.pmTaskBuffer import pmtaskbuffer as pmt
import pmUtils.pmUtils as utils

from  pmCore.pmModule import pmModule

class jobparam(pmModule):

    #______________________________________________________________________________________
   def __init__(self,name=None,parent=None,obj=None):
      pmModule.__init__(self,name,parent,obj)
      self.publishUI(self.doJson)

   #______________________________________________________________________________________      
   def doJson(self,params='loadrungridjob.C', jobs=None,days=1,limit=5, type='meta'):
      """ 
         Show  the list of Panda id with either jobParameters or MetaData matching the 'params' pattern and versa verse params by Panda IDs
         <ul>
         <li><code>params</code> - the search pattern for the jobParameters (may include * or % wild cards)
         <li><code>days</code>   - the time period in days (float number) 
         <li><code>jobs</code>   - the list of the comma separated Panda's job IDs
         <li><code>limit</code>  - the max number of the Db records to fetch 
         <li><code>type</code>   - the table type to lookup. <br> 
            <ul>
              <li><code>'meta'</code> is to look up  <code>'metatables'</code> Db tables<br>
              <li><code>'params'</code> is to look up  <code>'jobparamstable'</code> Db tables<br>
            </ul>
         </ul>
      """ 
      if self.server().protected() or jobs != None: 
         title = 'The list of files for the  '
         if params =='' : params = None
         if jobs =='': jobs = None
         if days ==''  : days=None
         if  params==None and jobs==None :
              self.publishTitle("There is lack of the information to fulfill this query: params=None and jobs=None.")
         else:
            if params != None:
               self.publishTitle("The list of the PANDA jobs with parameters matched the pattern '%s' type provided" % params)
            if jobs !=None:
               self.publishTitle("The list of the '%s' parameters for the the PANDA Job IDs provided" % jobs)
            main = {}
            if params and not '*' in params: params = '*' + params+ '*'
            r = pmt.jobParams(jobs,params,type,days=days,limit=limit)
            main['header'] = r['header']
            main['info']=r['rows']
            nav = " Look up the job <b>%s</b> data " % type
            if params and params.strip() != '': nav += " for the <b>%s</b> pattern" % params
            self.publishNav(nav)
            self.publish(main)
            self.publish( "%s/%s" % (self.server().fileScriptURL(),"hello/%s.js" % "helloora"),role="script")
      else:
         self.publishTitle(" please use 'https' to access the appclation")
