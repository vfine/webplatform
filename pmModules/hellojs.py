# $Id: hellojs.py 9690 2011-11-16 22:28:01Z fine $

from pmCore.pmModule import pmRoles    # load the list of roles 
import pmUtils.pmUtils as utils        # load the collection of the util functions
from  pmCore.pmModule import pmModule  # load the base class definition

class hellojs(pmModule): 
   """ The class name defines the Web application name. 
       The name of this class should match the name of the python source file,
       i.e. the filename  should be 'hellojs.py'
   """    
   #______________________________________________________________________________________
   def __init__(self,name=None,parent=None,obj=None):
      """ Construct the custom web 'hellojs' application """
      pmModule.__init__(self,name,parent,obj) # Initialize the base class
      self.publishUI(self.doJson)             # Publish the method 'doJson' to delivery 
                                              # the Web application  content
                                              
      self.publishUI(self.doScript,role=pmRoles.script()) # Publish the method 'hellojs.doScript'
                                                          # to delivery the JavaScript function
                                                          # to render the content published by 'hellojs.doJson'

   #______________________________________________________________________________________      
   def doJson(self,script=None):
      """ 
         doJson(self,script=None) defines the Web API list of parametes and its default values
          
         <p>This Python DocString is to automatically published by Web Server the Web API Help widget
         
         The Web Browser user will be able to access it by clicking the "?" button onto the page menu bar.
         The string may contain the regular HTML markups.

         script -  the file name to download and execute . <br>
                  It should contain the Javascript function `
         <pre>
            function _fun_(tag,content) { . . . . }
         </pre>
      """ 
      self.publishTitle('Hello JavaScript') # short cut for 
      self.publishNav("Load and Execute the '%s' Javascript " % ( script if script!= None else 'Embedded' ) )
      if script != None: 
         """ publish the reference to the external JavaScript if any """
         self.publish( "%s/%s" % (self.server().fileScriptURL(),"%s.js" % script ),role=pmRoles.script())
      """ Create the custom content to be published """   
      content = {"Hello" : "This is my own content to be published from %s " % utils.lineInfo() }
      self.publish(content)
      self.publish({'s-maxage':340,'max-age': 200},role=pmRoles.cache())
      
   #______________________________________________________________________________________      
   def doScript(self,script='hellojs'):
      """ 
         doScript(self,script=None) publishes the Javascript function to render the content onto the client Web browser
        
         The content is to be published by doJson 
         NB.The signatures (list of parameters) of the doJson and doScript should be the same
      """   
      javascript = """
         function _anyname_(tag,content) {
             /* Render the "content" */
             var thisTag =  $("<div style='padding:4px' class='ui-widget ui-widget-content ui-corner-all'></div>");
             thisTag.append("<ul>");
             for (var i in content) {  thisTag.append("<li>" + i + ": " + JSON.stringify(content[i])); }
             thisTag.append('</ul>');

             $(tag).empty(); /* Clear the HTML tag from the previouse content */
             $(tag).append(thisTag);
         }
      """
      self.publish(javascript,role=pmRoles.script())