""" Contact The Panda Help desk """
# $Id:$
from pmCore.pmModule import pmRoles
import pmUtils.pmUtils as utils
from pmTaskBuffer.pmTaskBuffer import pmtaskbuffer as pmt
from pmCore.pmModule import pmModule
from datetime import datetime

class contactus(pmModule):
   """ Send e-mail to the Monitor support """

    #______________________________________________________________________________________
   def __init__(self,name=None,parent=None,obj=None):
      pmModule.__init__(self,name,parent,obj)      
      self.publishUI(self.doJson)  
      self.publishUI(self.doScript,role=pmRoles.script())
   #______________________________________________________________________________________      
   def message(self, pandaid, message=None,host=None,timestamp=None,errorcode=None):
      # http://panda.cern.ch/server/pandamon/query?overview=viewlogfile&nocachemark=yes&guid=f2faca03-d2c2-46b6-ac4d-70ea625e26f9&lfn=log.01220398._099983.job.log.tgz.1&site=AGLT2_PRODDISK
      # https://pandamon.atlascloud.org/logmonitor?site=panda.mon.prod&message=1770799963*
      if message == None: message = ''
      jobfiles = 'http://pandamon.cern.ch/joblfn?jobs=%d&type=*' % int(pandaid[0])
      joblink =  'http://pandamon.cern.ch/jobinfo?job=%d' % int(pandaid[0])
      tasklink  = ''
      errorLink = ''
      try:
         tasklink =  '"http://pandamon.cern.ch/jobinfo?jobsetID=%(taskid)s&prodUserName=%(user)s&jobStatus=failed&hours=100"' % {  'taskid': pandaid[1], 'user': pandaid[2] }
         errorLink = 'http://pandamon.cern.ch/jobs/joberror?jobtype=*&item=jobsetID&prodUserName=%(user)s&hours=72&opt=sum+item+time' %  { 'user': pandaid[2] }
      except:
         pass
      msg = 'Dear DAST Helpers.\r\nI do not understand the reason of the job error: \r\n%s. \r\n %s \r\n See: %s \r\n     %s \r\n      %s \r\n with %s files.\r\n' % (errorcode, message,  joblink, tasklink, errorLink, jobfiles)
      msg += '\nThe page was produced by %s PanDA Monitor host at %s\r\n' % (host,timestamp)
      return msg
   #______________________________________________________________________________________      
   def subject(self, note):
      return 'Help Request with the Job %s' %  note[0]

   #______________________________________________________________________________________      
   def signature(self):
      msg  = "\r\nThank you, %s \n%s UTC" %(self.server().user(),  datetime.utcnow().strftime("%m-%d %H:%M:%S") )
      msg += "\n----\nCheck the user's section https://twiki.cern.ch/twiki/bin/viewauth/AtlasComputing/AtlasDAST#What_do_we_need_to_know_Support "
      msg += "\nPlease subscribe to the DAST mailing list for followups: https://groups.cern.ch/group/hn-atlas-dist-analysis-help/default.aspx"
      msg += "\n---\n     Sent from my Panda Monitor Web Page"
      return msg

   #______________________________________________________________________________________      
   def doJson(self, pandaid, message=None,host=None,timestamp=None,errorcode=None,test=None):
      """  Contact Us Panda Monitor Modules """ 
      usr = self.server().user()
      pandaid = utils.parseArray(pandaid)
      plid =  len(pandaid)
      main = {}
      if plid >= 1:  main['pandaid'] = pandaid[0]
      if plid >= 2:  
         main['taskid']  = pandaid[1]
         if plid == 2 and usr != None:
             pandaid.append(usr)
      plid =  len(pandaid)
      if plid >= 3:
         pandaid[2] = pmt.cleanUserID(pandaid[2]).replace(' ','+')
         main['user']    = pandaid[2]
      if usr != None:
         mail = self.server().email()
         if mail == None and test != None: 
            mail = 'val.fine@gmail.com'
         main['username']= usr
         if mail != None:
            main['mail']= mail
            msg = self.message(pandaid, message, host,timestamp,errorcode);
            msg += self.signature()
            subject = self.subject(pandaid)
            toaddrs = ''
            if test == None: toaddrs = 'atlasdast@gmail.com hn-atlas-dist-analysis-help@cern.ch '
#            toaddrs+='%s %s %s' % ('Alden.Stradling@cern.ch', 'val.fine@gmail.com', mail)
            toaddrs+='%s %s' % ( 'val.fine@gmail.com', mail)
            main['message'] = msg;
            main['subject'] = subject if test==None else 'Test: %s ' % subject
            main['toaddrs'] = toaddrs
            response = pmt.sendmail(msg,subject,toaddrs,fromaddr=mail)
            main['response'] = response
            self.publishTitle("User %s sent support mail from %s" % (usr,mail) )
         else:   
            self.publishTitle("User %s wanted to send the support mail " % usr )
            self.publish(main)
      else:
         self.publishTitle("Unknown user, please use the Web https protocol.")
      self.publish(main)
      self.publish( {'s-maxage':0,'max-age': 0}, role=pmRoles.cache())
   #______________________________________________________________________________________      
   def doScript(self, pandaid, message=None,host=None,timestamp=None,errorcode=None,test=None):
      """  Contact Us Panda Monitor Modules Render""" 
      javascript = """  
         function _anyname_(tag,content) { 
            $(tag).empty();
            $(tag).html('<pre>\n'+JSON.stringify(content,undefined,2)+'\n</pre>');
         }
      """
      self.publish(javascript,role=pmRoles.script())
