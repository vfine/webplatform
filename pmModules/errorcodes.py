"""  List the <a href='https://twiki.cern.ch/twiki/bin/viewauth/AtlasComputing/PandaErrorCodes'>Panda error codes</a> </td><td>$Rev: 18146 $"""
# $Id: errorcodes.py 9690 2011-11-16 22:28:01Z fine $
from pmUtils.pmState import pmstate
from pmCore.pmModule import pmRoles
from  pmTaskBuffer.pmTaskBuffer import pmgrisliaskbuffer as gmt
import pmUtils.pmUtils as utils
from  monitor.ErrorCodes  import errorcodes as monitorerrors
from  monitor.nameMappings import nmap
from  pmCore.pmModule import pmModule

class errorcodes(pmModule):
   """  List the <a href='https://twiki.cern.ch/twiki/bin/viewauth/AtlasComputing/PandaErrorCodes'>Panda error codes</a> </td><td>$Rev: 18146 $"""

   #______________________________________________________________________________________
   def __init__(self,name=None,parent=None,obj=None):
      pmModule.__init__(self,name,parent,obj)
      self._errors = monitorerrors.getErrorList()
      self._errorFields, self._errorCodes, self._errorStages = monitorerrors.getErrorCodes()
      self._errorFields = list( self._errorFields)
      self._errorFields.append('transExit')
      self.publishUI(self.doJson)

   #______________________________________________________________________________________      
   def doJson(self,scope=None,doc=None,code=None):
      """ 
        List the <a href='https://twiki.cern.ch/twiki/bin/viewauth/AtlasComputing/PandaErrorCodes'>Panda error codes</a> 
        <ui>
        <li> scope  - scope: 'pilot','ddm' 'transExit','jobDispatcher',list the tasks requested for the last hours
        <li> doc    - pattern to filter the the code descriptions
        <li> code   - code
        </ul>
      """ 
      if scope == None:
         self.publishTitle('%s Codes' % 'PanDA Error')
      else:
         self.publishTitle('%s Codes' % scope)

      if scope == None: self.publish(self._errors)
      else:
         if not scope in self._errorFields: 
             raise KeyError(" Unknown scope %s . The list  of the valid scopes: %s " %(scope, self._errorFields))
         selescope = None
         if scope != 'transExit':
            searchScope = "%sErrorCode" % scope
         else:  
            searchScope = "%sCode" % scope         
         for j in self._errors:
            if j != searchScope: continue
            selescope = {j:self._errors[j]}
            break
         result =  { 'unknown':[ [-1,'unknown','unknown'] ]}
         if selescope != None:   
            if code == None: 
               result = selescope
            else:
               for cd in selescope:
                  codelines = selescope[cd]
                  for cordsc in codelines:
                     if code == cordsc[0]:
                        result = { cd : [cordsc] }
                        break
         self.publish(result)
      self.publish( "%s/%s" % (self.server().fileScriptURL(),"monitor/%s.js" % 'errorcodes' ),role=pmRoles.script())
      self.publish( {'s-maxage':6000,'max-age': 6000}, role=pmRoles.cache())