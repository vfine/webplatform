// $Id: pmMonitor.js 17756 2013-12-16 19:53:42Z fine $
// $Id: pmMonitor.js 17756 2013-12-16 19:53:42Z fine $
// Author: Valeri Fine (fine@bnl.gov) July 5, 2011
var _xhr;
var category = {'modified'    : 'json'
            , 'dataready'     : 'javascript'
            , 'refreshscript' : 'javascript'
            , 'externalpage'  : 'link'
            , 'ready'         : 'render'
};

 var  tpattern  =/[\/]{0,1}~([^\/]+)/g;
 tpattern.compile(tpattern);
//______________________________________________________________
function PmElement(div) {
  this.appllist = {  alist : "" ,analytics : "", cloudsummary: ""  
 , dbstats: "" , debuginfo: ""  , describe: ""  , errorcodes: ""  
 , getJobs: ""  , hellodb: ""  , hellohi: ""  , hellohttps: ""  
 , hellojsonp: ""  , hellojson: ""  , hellojs: ""  , helloora: ""  
 , hello: ""  , jobinfo: ""  , joblfn: ""  , jobparam: ""  , listusers: ""  
 , login: ""  , logmonitor: ""  , logs: ""  , logsummary: ""  , mcore: ""  
 , old: ""  , pd2ptest: ""  , ppop: "" , ptimes: ""  , pyroot: ""  
 , releaseinfo: ""  , releases: ""  , reqtask1: ""  , schedcfg: ""  
 , taskBufferList: ""  , taskBuffer: ""  , useract: ""  , users: ""  
 , vcloud: "",  wnlist: ""
  };
  this._pm = $('body').data('Pm');
  this._framework = false;
  this._children = []
  this._className = 'PmElement';
  this._div = div;    
  this._id = $(div);
  this._id.data('pm',this);
  this.Log(this._className + ' delegate div='+ div);
  this._render = 'html'; 
  var pmEvent = $.Event('pmelement');
  /* this._id.bind('pmelement',function(event) {  $(this).log('pmelement event').data('pm').Proceed(event);});  */
  this._id.delegate('a','click', { link : this } , function (event) {  event.data.link.Link(this,event);  });
  /*
  this._id.delegate('form','submit', { link : this } , function (event) { 
               console.log('event='+ event);
               event.data.link.Submit(this,event);
               });               
  */
   // bind the form "submit" , "browser back" , "href" 
  if (this.Id() == "main" && false) {
     var refreshId = this.Id();
     if (refreshId[0]!="#" ) { refreshId = "#" + refreshId; }
     refreshId = "<a id=" + refreshId + "__refresh_id_></a>";
     this._refreshScript = $(refreshId);
     this._refreshScript.css("display","none");
     this._refreshScript.attr("href","Refresh " + this.Id());
     this._refreshScript.attr("title","Click this icon to reload the rendering function for the existing data for '" + this.Id()+  "' portion of layout");
     this._refreshScript.html('<span class="ui-icon ui-icon-refresh"></span>');
     this._refreshScript.showme = false;
  }
  /* this._refreshScript.html("Refresh " + this.Id()); 
  this._refreshScript.css({'font-size':'0.5em','background-color':'#F00'});
  */
}
//______________________________________________________________
PmElement.prototype.Url2Obj = function(url,convert,asis) {
   /* Input:
        - convert 'url' into the object if the type of url is "string'
        - convert 'url' into the string if cober is defuned and is not false
        See: http://www.joezimjs.com/javascript/the-lazy-mans-url-parsing/ 
        NB. Bug: protocol:///path is parsed as protocol://path/
        
   */
   //console.log(' Url2Obj:55: ' + convert+" "+ (typeof (url) == 'string' ) + url);
   var srcUrl = url; 
   var urlFields = 'protocol,hostname,port,pathname,search,hash,host'.split(',');
   /* var rootUrl; */
   if (typeof (url) == 'string' ) {
      /* if (url != '/') { rootUrl = this.Url2Obj('/'); } */
      function canonicalize(url) {
           var u = url;
           var pattern = ":///";
           var iHostn = url.indexOf(pattern);
           if ( iHostn  >= 0  && iHostn == url.indexOf("://") ) {
              var prot = url.substr(0,iHostn+1);
              var hostname = "//" + window.location.host 
              if (window.location.port != '') hostname += ':'  + window.location.port;
              if (iHostn == 0) {
                 prot = window.location.protocol;
              }
              u = prot+ hostname + url.substr(iHostn+pattern.length-1);
           }
           var div = document.createElement('div');
           div.innerHTML = "<a></a>";
           div.firstChild.href = u; // Ensures that the href is properly escaped
           div.innerHTML = div.innerHTML; // Run the current innerHTML back through the parser
           return div.firstChild.href;
       }
      function trimslash(name){
         var oname = name;
         if (typeof oname == 'string') {
            var vname =  name.split('/');
            var ostr = '';
            for (var i in vname) {
               if (i == 0 && vname[i]=='') continue;
               else if (i == vname.length-1 && vname[i] =='') continue;
               if (ostr != '') { ostr += '/'; }
               ostr += vname[i];
            }
            oname = ostr;
         }
         return oname;
      }      
      function stripnull(str) {
        var oStr = str;
        if (typeof str == 'string' ) {
           if (str.length == 0) { oStr = undefined; }
        }
        return oStr;
      }
      var parser;
      if ( asis != undefined && asis==true) {
         parser = new Uri(url.replace('@','_at_'));
      } else {
         var aparser =  document.createElement('a');
         if ( url == '/' ) {
            var lpn = trimslash(stripnull(window.location.pathname));
            if (lpn != undefined ) {    url += lpn;     }
         }
         aparser.href= canonicalize(url);
         parser = new Uri(aparser.href.replace('@','_at_'));
      }
      var pathname  = parser.path(); /* IE9 */
      var appupd = this.Path2Version(pathname);
      var version = appupd.version;
      var application = appupd.application;
      var pathname = appupd.pathname;
/*      
      if (pathname[0] == '/') { pathname = pathname.substr(1); }
      var  tpt =/[\/]{0,1}~([^\/]+)/g;
      console.log(" Url2Obj:112 "+pathname + '-->' + parser.toString() );
      var pn2 = tpt.exec(pathname);
      var version;
      if (pn2 != null) {
         version = pn2[1];
         pathname = pathname.replace(tpt,'');
      }
      if (pathname[0] == '/') { pathname = pathname.substr(1); }
      var vapp =  pathname.split('/');
      var application = undefined;
      if (vapp.length > 1) {
        pathname = vapp.slice(0,vapp.length-1).join('/');
        application = vapp.slice(vapp.length-1)[0];
      } else {
        application = vapp[0];
        pathname = undefined;
      }
*/
      /*  applicatiion double ?? 
      if ( pathname != undefined && rootUrl != undefined  ) { 
         var rpn = rootUrl.pathname;
         if (rootUrl.host == stripnull(parser.host) && rpn != undefined &&rpn !='' ) {
            var ipn = pathname.indexOf(rpn);
            if (ipn == 0 ) {pathname = pathname.substr(rpn.length); }
         }
      }
      */
      
      var urlpar =  parser.query().toString().replace('_at_','@');
      srcUrl= {
                  href       : stripnull(parser.toString().replace('_at_','@') ) 
                , protocol   : stripnull(parser.protocol()) // => "http:"
                , hostname   : stripnull(parser.host()) // => "example.com"
                , port       : stripnull(parser.port())     // => "3000"
                , version    : stripnull(version)         // => /~version
                , pathname   : stripnull(pathname)        // => "/pathname/"
                , application: stripnull(application)     // application 
                , search     : urlpar                     // => "?search=test"
                , hash       : stripnull(parser.anchor())     // => "#hash"
                , host       : stripnull(parser.host())     // => "example.com:3000"
         };
      if (srcUrl.pathname != undefined) { 
         srcUrl.pathname = stripnull( trimslash(srcUrl.pathname) ); 
      }
   } else if ( convert != undefined && convert != false) {
      srcUrl = "";
      if ( url.protocol != "" &&  url.protocol != undefined ) {
         srcUrl += url.protocol;
         if (srcUrl[srcUrl.length-1] != ':') { srcUrl += ':'; }
      }
      if ( url.host != "" &&  url.host != undefined ) {
         srcUrl += "//" + url.host;
      }
      if ( url.version != "" &&  url.version != undefined ) {
         if (url.version[0] != '/' ) { srcUrl += '/~'; }
         srcUrl += url.version;
      }
      if ( url.pathname != "" &&  url.pathname != undefined ) {
         if (url.pathname[0] != '/' ) { srcUrl += '/'; }
         srcUrl += url.pathname;
      }
      if ( url.application != "" &&  url.application != undefined ) {
         if (url.application[0] != '/' ) { srcUrl += '/'; }
         srcUrl += url.application;
      }
      if ( url.search != "" &&  url.search != undefined ) {
         if (url.search[0] != '?' ) { srcUrl += '?'; }
         srcUrl += url.search;
      }
      if ( url.hash != "" &&  url.hash != undefined ) {
         if (url.hash[0] != '#' ) { srcUrl += '#'; }
         srcUrl +=url.hash;
      }
   }
   return srcUrl;
}
//______________________________________________________________
PmElement.prototype.MergeSerach = function(upd,url) {
   /* merge the search paramters */
   return $.param.querystring (upd,url);
}

//______________________________________________________________
PmElement.prototype.URL = function(upd,tostring,url,asis) {
   /* Input:
        - convert 'url' and 'upd' into the object
        - use upd to extend the URL
        - tostring - to convert the "extended" url into the string
      Returns:
         - The 'url' extended by 'upd' if any and converted to string if needed
   */
   if (url==undefined) { url = '/'; }
   var srcUrl = typeof(url) ==='string'? this.Url2Obj(url) : url;
   // console.log('224: URL='+ (asis===true)+ ' ' + JSON.stringify(srcUrl));
   if ( upd != undefined ) {
      oUpd =   typeof(upd) ==='string'? this.Url2Obj(upd,false,asis===true) : upd;
      if ( oUpd.pathname != undefined && oUpd.pathname != '' && srcUrl.pathname != oUpd.pathname) {
            /* It will be the new applcation */
            delete srcUrl.pathname;
            delete srcUrl.search;
      } else if (srcUrl.search != undefined && srcUrl.search !='') {
         /*  We need to update the existing one */
         //console.log(" URL:210 " + JSON.stringify(srcUrl.search) + JSON.stringify(oUpd.search) );
         oUpd.search = $.param.querystring (srcUrl.search ,oUpd.search);
         //console.log(" URL:212 " + JSON.stringify(oUpd.search) );
      }
      delete oUpd.version; /* ignore the new version */
      //console.log(" URL:215 " + JSON.stringify(srcUrl) +  JSON.stringify(oUpd) );
      $.extend( srcUrl, oUpd); 
      if ( (oUpd.pathname == undefined || oUpd.pathname == '') && this.appllist[oUpd.application] != undefined) {  delete srcUrl.pathname; }
//       if (oUpd.application == undefined || oUpd.application == '') {  delete srcUrl.application;  }
//       if (oUpd.search == search || oUpd.search == '') {  delete srcUrl.search;  }
//       if (oUpd.hash == search || oUpd.hash == '') {  delete srcUrl.hash;  }
      
      //console.log(" URL:217 " + JSON.stringify(srcUrl) );
   }
   //console.log(" URL:219 " + JSON.stringify(srcUrl));
   if (tostring!= undefined && tostring===true) {
      srcUrl =  this.Url2Obj(srcUrl,tostring);
      //console.log(" URL:222 " + srcUrl);
   }
   return srcUrl;
}                  
//______________________________________________________________
PmElement.prototype.AbortAjax = function() {
   if (_xhr && _xhr.readyState != 4) { 
    _xhr.abort(); 
   }
   if (this._refreshScript != undefined) { 
     this._refreshScript.showme = false;
     this._refreshScript.hide(); 
   } 
}
//______________________________________________________________
PmElement.prototype.CleanLink = function(link) {
   var normalize = link.replace(window.location.href,"").replace(window.location.host,"").replace("http://","").replace("https://","").replace("#/","");
   return  normalize.replace(tpattern,'');
}
//______________________________________________________________
PmElement.prototype.Path2Version = function(pathname) {
   if (pathname[0] == '/') { pathname = pathname.substr(1); }
   var  tpt =/[\/]{0,1}~([^\/]+)/g;
   //console.log(" Path2Version:274 "+pathname  );
   var pn2 = tpt.exec(pathname);
   var version;
   if (pn2 != null) {
      version = pn2[1];
      pathname = pathname.replace(tpt,''); /* remove the version from the pathname */
   }
   /* find application  if any */
   if (pathname[0] == '/') { pathname = pathname.substr(1); }
   var vapp =  pathname.split('/');
   var application = undefined;
   if (vapp.length > 1) {
      pathname = vapp.slice(0,vapp.length-1).join('/');
      application = vapp.slice(vapp.length-1)[0];
   } else {
      application = vapp[0];
      pathname = undefined;
   }
   if (this.appllist[application] != undefined) {pathname=undefined;}
   //console.log(" Path2Version:274 " + JSON.stringify({version: version,pathname:pathname,application:application}));
   return {version: version,pathname:pathname,application:application};
}

//______________________________________________________________
PmElement.prototype.Link = function(lnk,event) {
   /* link is an instance of the $('a')  */
   // add to history
   link= {
                  href       : lnk.href
                , protocol   : lnk.protocol   // => "http:"
                , hostname   : lnk.hostname   // => "example.com"
                , port       : lnk.port     // => "3000"
                , version    : undefined
                , pathname   : lnk.pathname        // => "/pathname/"
                , application: undefined     // application 
                , search     : lnk.search
                , hash       : lnk.hash    // => "#hash"
                , host       : lnk.host    // => "example.com:3000"
   };
   var path2ver = this.Path2Version(link.pathname);
   // console.log(" 320: LINK" +JSON.stringify({link:link,path2ver:path2ver},undefined,2));
   $.extend(link,path2ver);   
   // console.log(" 321: LINK" +JSON.stringify(link,undefined,2));
   if (path2ver.pathname == undefined) { delete link.pathname; }
   // console.log(" 324: LINK" +JSON.stringify(link,undefined,2));
   this.ClickURL(link,event);
}
//______________________________________________________________
PmElement.prototype.ClickURL = function(uri,event) {
  /*
    console.log(" 327: ClickURL" +JSON.stringify(uri,undefined,2) + JSON.stringify(window.location.href,undefined,2)  
       + " "+ window.location.host+ " " + (uri.host == window.location.host)
       + " "+ window.location.protocol+ " "+ (uri.protocol == window.location.protocol)
       );
   */
   if ( this._framework && uri.host == window.location.host && uri.protocol == window.location.protocol) {
      event._pm = this;
      event.preventDefault();
      event.stopPropagation();
      if ( uri.search.indexOf('Refresh') == -1 ) { 
           //console.log('ClickURL:271='+JSON.stringify(uri));
//           var toBoomark =this.CleanLink(this.NormalizePathname(uri));
           var toBoomark =this.NormalizePathname(uri);
//         var toBoomark =this.NormalizePathname(uri);
         this.Log("to bookmark:" + toBoomark);
         $('body').data('Pm')._hashLock = true; 
         $.bbq.pushState(toBoomark,2);// cause the second hash event sometimes to avoid !!!
         this.ChangeStatus('modified',toBoomark);
      } else {
         this.ChangeStatus('refreshscript');
      } 
   } else {
     if ( /* href != '' && */ false) { 
         event.preventDefault();
         event.stopPropagation();
         this.ChangeStatus('externalpage',href);
      }
     /* one can confine the third party Web page into Panda layout if needed */
     /* if target = "_self"|| "_blank" -> to "main" */
     /* otherwise load it as is */
   }
}

//______________________________________________________________
PmElement.prototype.Submit = function(uri,event,host) {
   this.Log('Submit = ' + JSON.stringify(uri)+ "windors href=" + window.location.href );
   if (host == undefined) {
      host =  window.location.host;
   }
   uri = this.NormalizePathname(uri,true);
   this.ClickURL(uri,event);
}
//______________________________________________________________
PmElement.prototype.Find = function(child) {
   var found ;
   /* this.Log("Looking for " + child  + " from " + this.Id() ); */
   if ( this.Id() == child) {
     found =  this;
   } else {  
      for (var nxchild in this._children ) { 
         found = this._children[nxchild].Find(child); 
         if (found) break;
      }
   }
   /* this.Log("Looking for " + child + " is " + found); */
   if (found) found.Log('Found');
   return found;
}

//______________________________________________________________
PmElement.prototype.Append = function(child) {
   // Append PmElement to another PmElement
   this.Log('Appending');
   this._children.push(child);
   child.parent = this;
   child.Log('Appended');
}

//______________________________________________________________
PmElement.prototype.Parent = function() {
   // Find the parent 
   var myParentElement;
   if (this.parent)  {
      myParentElement=this.parent;
      this.Log('Parent child');
      myParentElement.Log("child's parent");
   }
   return myParentElement;
}

//______________________________________________________________
PmElement.prototype.GrandParent = function() {
   // Find the top parent 
   var myGrandParentElement = this.Parent();
   if (myGrandParentElement) {
      var nxParent; 
      while (nxParent=myGrandParentElement.Parent() ) {myGrandParentElement=nxParent;}   
   }
   return myGrandParentElement;
}

//______________________________________________________________
PmElement.prototype.ProcessDataTag = function(tags,textStatus,jqXHR,top) 
{
   this.Log("ProcessDataTag tags: "  + tags);
   var id;
   var data;
   var scriptUrl;
   var format='html';
   var nxtTag = tags;
   for (var tag in nxtTag) {
      var tagValue = nxtTag[tag];
      this.Log("nxtTag:" + tag + ' value: ' +  tagValue );
      if (tag == 'id') {
         id = tagValue;
      } else if (tag=='cache') {
         continue;
      } else {
         if (tag == 'json' || tag == 'text') {
            format = tag; 
         }
         if (tag != 'script') {
            data = tagValue;
         } else {
            scriptUrl = tagValue;
            this.Log(" ScriptURL=" + scriptUrl);
         }            
      }
   }
   var target = top.Find(id);   
   if (target==undefined) {
       this.Log(" DispatchData: New id to be created = " + id );
      // define it firstChild
      target = new PmElement('#'+id);
      top.Append(target);
   }
   target.Log('ProcessDataTag rendering: ' + id + ' format=' + format + ' data=' + data +' script='+scriptUrl);
   target.SetData(data,textStatus,jqXHR,format,scriptUrl);
}
//______________________________________________________________
PmElement.prototype.DispatchData = function(data,textStatus,jqXHR) {
   if (data == undefined) { return ; }
   var pm = data.pm;
   this.Log('DispatchData: ' +  pm +  '(' +  pm.length +')' );
   var top = this.GrandParent();
   if (top == undefined) top = this;
   top.Log('Dispatch');
   for (var tags in pm ) {
      this.Log("DispatchData: tags:" + tags +  " " + pm[tags]);
      this.ProcessDataTag(pm[tags],textStatus,jqXHR,top) ;
   }
}
//______________________________________________________________
PmElement.prototype.RenderData = function(tag,data) {
   if ( $(tag).attr('id') == 'title' ) {
      $(document).attr('title', data);
   }
   $(tag).html(data);
}

//______________________________________________________________
PmElement.prototype.ClearTag = function(tag,text) {
   if (tag == undefined) { tag =  this.id() ; }
   else { tag = $("#" + tag); }
   tag.empty();
   if (text != undefined) { this.id().text(text); } 
}

//______________________________________________________________
PmElement.prototype.RenderText = function(tag,data) {
   var alext = '<div class="ui-widget">\
           <div class="ui-state-error ui-corner-all" style="padding: 0 .7em;">\
           <p><span class="ui-icon ui-icon-alert" style="float: left; margin-right: .3em;"></span><span id="errorpanleId"><pre>'
   alext +=  data;
   alext +=    '\n</pre></span></p></div>'
   var alert = $(alext);
   $(tag).append(alert);
}

//______________________________________________________________
PmElement.prototype.Render = function() {
   var data   = this._data.data;
   var format = this._data.format;
   //var status = this._data.status;
   this.Log('Render:' +  data  +  '(' +  data.length +')');
   this.Log('rendering: ' + format +" data=" + data);
   var  renderCallback = this._render;
   if (renderCallback) {
      renderCallback('#' + this.Id(),data);
      if ( this._refreshScript != undefined && this._refreshScript.showme) {
          this.id().append(this._refreshScript);
          this._refreshScript.show(); 
      }
   }
   /*
   this._refreshScript.position( {
     my : "center",
     at : "center",
     of : "#" + this.Id()
   });
   */
   this.ChangeStatus('ready');
}
//______________________________________________________________
PmElement.prototype.Status = function() { return this._status; }
//______________________________________________________________
PmElement.prototype.GoogleTrack= function(evt) {
    return; /* Google analytic slows down us significantly */
    if (_gaq !=undefined ) {
       var action = this.Status();
       var label = evt.pmUrl;
       _gaq.push(['_trackEvent', category[action], action, label]);
   /* _trackEvent(category, action, opt_label, opt_value, opt_noninteraction); */
   }
}
//______________________________________________________________
PmElement.prototype.Proceed = function(evt) {
  evt.preventDefault();  evt.stopPropagation();
  this.GoogleTrack(evt);
  this.Log('Proceed: ' + this._status );
  if ( this.IsStatus('modified') )          { this.QueryData  (evt.pmUrl); }
  else if ( this.IsStatus('dataready') )    { this.QueryScript(evt.pmUrl); }
  else if ( this.IsStatus('refreshscript') ){ this.QueryScript(evt.pmUrl); }
  else if ( this.IsStatus('externalpage') ) { this.QueryPage  (evt.pmUrl); }
}
//______________________________________________________________
PmElement.prototype.SetData=function(data,textStatus,jqXHR,format,scriptUrl) {
   this._data = {  "data"   : data
                  ,"status" : textStatus
                  ,"XHR"    : jqXHR
                  ,"format" : format
                };
   if   ( (scriptUrl != undefined) && (scriptUrl != '') ) {
      this._data.script = scriptUrl;
   }
   this.ChangeStatus('dataready'); // do we know the URL ?
}
//______________________________________________________________
PmElement.prototype.AcceptData=function(data,textStatus,jqXHR) {
   this.Log('AcceptData: ' + textStatus + ' element status: ' + this.Status());
   this.ClearTag("nav");
   if (this.IsStatus('pending'))  {
      if (data.redirect) {
        $(document).attr('title', 'Redirecting to ' + data.redirect);
        window.location.replace(data.redirect);
      } else if (textStatus == "parsererror" || textStatus == 'error')  {        
         this.Log("error response: " + data.responseText );
         this.Log("error message: " + jqXHR.message );
         // use id -mainWindow to glue the wrong json. Do we need such hack ?
         data = { "pm" : [ { "id" : "nav", "text" : jqXHR + " : " +  data.responseText } ] };
      }
      if (textStatus=='success' || textStatus=='parsererror' || textStatus == 'error') {
         this.DispatchData(data,textStatus,jqXHR);
      }
   } else {
      this.Log (" AcceptData Wrong Status " + this._status  + " data status: "+ textStatus);
   }
}

//______________________________________________________________
PmElement.prototype.AcceptPage=function(data,textStatus,jqXHR) {
   this.Log('AcceptPage: ' + textStatus + ' element status: ' + this.Status());
   this.ClearTag("nav");
   if (this.IsStatus('pending'))  {
      if (textStatus == "parsererror" || textStatus == 'error')  {        
         this.Log("error response: " + data.responseText );
         this.Log("error message: " + jqXHR.message );
         // use id -mainWindow to glue the wrong json. Do we need such hack ?
         data = { "pm" : [ { "id" : "nav", "text" : jqXHR + " : " +  data.responseText } ] };
      }
      if (textStatus=='success') {
            data = { "pm" : [ { "id" : "main", "html" : data } ] };
      }
      this.DispatchData(data,textStatus,jqXHR);
   } else {
      this.Log (" AcceptPage Wrong Status " + this._status  + " data status: "+ textStatus);
   }
}

//______________________________________________________________
PmElement.prototype.EvalScript=function(data,textStatus,jqXHR) {
   /* Wrap the user function */
   var fun = data.replace(/\s*function\s+.*\(/," function(");
   var renderFunction = " { $('body').data('Pm')._setFunction('"+ this.Id() + "'," + fun  +");}";
   jQuery.globalEval(renderFunction);
}

//______________________________________________________________
PmElement.prototype.AcceptScript=function(data,textStatus,jqXHR) {
   this.Log('AcceptScript: ' + textStatus + ' element status: ' + this.Status());
   if (this.IsStatus('pending'))  {
      if (data == undefined || textStatus.indexOf("error") >=0 )  {
         this.ClearTag("nav");
         var restxt = 'Communication cross-server error: No script body received from the server';
         if (data) {
            if (data.responseText != '') { 
               restxt = data.responseText;
            }
            this.Log("error script response: " + restxt);
         }
         this.Log("error script message: " + jqXHR.message );
         // use id -mainWindow to glue the wrong json. Do we need such hack ?
         data = { "pm" : [ { "id" : "nav", "text" : JSON.stringify(jqXHR) + " : " +  restxt } ] };
         this.DispatchData(data,textStatus,jqXHR);
      } else  if (data.redirect) {
        $(document).attr('title', 'Redirecting to ' + data.redirect);
        window.location.replace(data.redirect);
      } else if  (textStatus=='success' ) {
         // Move function to the destination
         try {
            if (this._data.script != undefined) {
               this.EvalScript(data,textStatus,jqXHR);
            } else {
               var rfn =  this._pm._topElement._render;
               this._pm._topElement_render = undefined;
               this._render = rfn;
            }
            this.Render();
         } catch(err) {
             data = { "pm" : [ { "id" : "nav", "text" : "JavaScript Error: "+err+"\n\n "+ JSON.stringify(jqXHR) + "\n ----- \n\n  Call Stack: \n" +  err.stack + "\n    " + new Date() + " \n ----"} ] };
             this.DispatchData(data,textStatus,jqXHR);  
         }
      }
   } else {
      this.Log (" AcceptScript Wrong Status " + this._status  + " data status: "+ textStatus);
   }
}
//______________________________________________________________
PmElement.prototype.NormalizeScriptURL=function(scriptUrl) { 
    /* Make sure the script host matches the page host */
   var oUrl = scriptUrl;
   var hash = this.Url2Obj(scriptUrl).hash;
   //console.log (" 605: "+JSON.stringify({ NormalizeScriptURL:'NormalizeScriptURL',hash:hash} ) );   
   if (hash !=undefined && hash != '') { 
      oUrl = this.URL(hash,true,undefined,true);
   } else {
      oUrl = this.URL(scriptUrl,true);
   }
   //console.log(' NormalizeScriptURL:584: ' + oUrl);
   this.Log({NormalizeScriptURL:'NormalizeScriptURL',scriptUrl:scriptUrl,oUrl:oUrl});
   return oUrl;  
}
//______________________________________________________________
PmElement.prototype.QueryScript=function(scriptUrl) {
   this.Log('QueryScript: ' + scriptUrl);
   var norefresh = !this.IsStatus('refreshscript');
   if ( this.IsStatus('dataready') || !norefresh )  {
      this._render = undefined;
      var format = this.Format();
      if (norefresh && ( format == undefined || format == "html") ) {
         // it is a plain html, execute it with no script 
         this._render = $.proxy(this.RenderData,this._id);
         this.Render();
      } else if (norefresh && (format == "text")) {
         this._render = $.proxy(this.RenderText,this._id);
         this.Render();
      } else {
         this.ChangeStatus('pending');
         var script = this.Script();
         
         if  ( script != undefined ) { 
            scriptUrl = script;
         }
         var acceptscript = $.proxy(this.AcceptScript,this);
         this.AbortAjax();
         // see http://jsperf.com/url-parsing
         if (this._refreshScript != undefined) { this._refreshScript.showme = true; }           
/*         
          It sounds like we can not get scritp acrossof domain. Smells like the JQuery bug 
         _xhr = $.ajax({
                    url        : scriptUrl
                  , dataType   : "script"
                  , crossDomain: true
                  , converters : { text_script : function() { console.log("Dummy converter") ;  } }
                  , headers     : {'pmMonitor_class': this.Class() } 
               })
         .success(acceptscript)
         .error(acceptscript);
 */

         _xhr = $.getScript(this.NormalizeScriptURL(scriptUrl), { 
                converters : { text_script : function() { console.log("Dummy converter") ;  } }
               ,headers: {'pmMonitor_class': this.Class() } 
             }
          )
         .success(acceptscript)
         .error(acceptscript);
      }
   } else {
      this.Log (" QueryScript Wrong Status " + this._status);
   }
}

//______________________________________________________________
PmElement.prototype.ChangeStatus= function(status,url) {
   if (!this.IsStatus(status) || this.IsStatus('refreshscript')) {
      this._status = status;
      if (status != 'pending' ) {
         if (url == undefined) { 
            if (this._pm.lastUrl == undefined) {
               url = document.URL;
            } else {
               this.Log('last URL ='+ this._pm.lastUrl);
               url = this._pm.lastUrl;
            }
         }
         this.Log('this URL ='+ url);
         var e = jQuery.Event("pmelement");
         this._pm.lastUrl = url;
         e.pmUrl = url;
         if  (false ) {
           $('#urlIconId').attr("title","This page URL: '" + url+"' Click to toggle."); 
            var u = $("#url_text_id").text(url);
            var qr = u.html();
            u.text(url);
            $('#url_qr_id').empty();
            if (qr.length < 200) {
               $('#url_qr_id').qrcode({
                   width: 64,height: 64,
                  /*  render: "table",  "canvas" */
                   text : qr
                  });
            }
         }
         var that =  this;
         setTimeout(function(){ that.Proceed(e);},0);
         /* this._id.trigger(e); */ 
      }
   }
}
//______________________________________________________________
PmElement.prototype.Data   = function()      { return this._data;              }
//______________________________________________________________
PmElement.prototype.Format = function()      { return this._data.format;       }
//______________________________________________________________
PmElement.prototype.Script = function()      { return this._data.script;       }
//______________________________________________________________
PmElement.prototype.Attr   = function(attr)  { return this.id().attr(attr);    }
//______________________________________________________________
PmElement.prototype.Log    = function(text)  { this.id().log(JSON.stringify(text,undefined,2));}
//______________________________________________________________
PmElement.prototype.Id     = function()      { return this.Attr('id');         }
//______________________________________________________________
PmElement.prototype.id     = function()      { return this._id;                }
//______________________________________________________________
PmElement.prototype.div    = function()      { return this._div;               }
//______________________________________________________________
PmElement.prototype.Class  = function()      { return this.Attr('class');      }
//______________________________________________________________
PmElement.prototype.IsStatus= function(status){ return  status == this._status;}
//______________________________________________________________
PmElement.prototype.NormalizePathname = function(url,obj) {
   /* move hash field to pathname field */
   if (obj==undefined) {obj = true; }
   var oUrl=url;
   var srcUrl = this.Url2Obj(url);
   var hash = srcUrl.hash;
   if (typeof hash == 'string' &&  hash != '') { 
      // console.log(" 737: "+hash);
      oUrl = this.URL(hash,obj,undefined,true);
      //console.log(" 739: -> "+ JSON.stringify({oUrl:oUrl}));
   } else {
      //console.log(" 701: "+JSON.stringify({hash:hash,srcUrl:srcUrl}));
      //console.log(JSON.stringify(url) + ":: " +JSON.stringify({protocol:srcUrl.protocol,version:srcUrl.version, pathname: srcUrl.pathname, application: srcUrl.application,search: srcUrl.search, hash:srcUrl.hash},undefined,2));
      oUrl = this.URL(srcUrl,obj);
      //console.log(" 704: "+JSON.stringify(oUrl));
   }
   return oUrl;
}
//______________________________________________________________
PmElement.prototype.QueryData = function(jsonUrl) {
   // query the json data for the 'div'
   if ( this.IsStatus('modified') ) {
      this.ChangeStatus('pending');
      this.Log("JSON URL = " + jsonUrl);      
      jsonUrl = this.NormalizePathname(jsonUrl);
      this.Log("Normalized JSON URL = " + jsonUrl);      
      var acceptdata = $.proxy(this.AcceptData,this);
      this.AbortAjax();
      /*
      _xhr = $.getJSON(jsonUrl,{"pmMonitor_location":this.Id(), acceptdata)
            .error(acceptdata);
      */
      _xhr =  $.ajax({
                url: jsonUrl
              , dataType: 'json'
              , data : {'_get' : 'json' }
              , headers : {"pmMonitor_location":this.Id(),"pmMonitor_class": this.Class() }
              , success: acceptdata
            })
            .error(acceptdata);
   }
}
//______________________________________________________________
PmElement.prototype.QueryPage = function(pageUrl) {
   // query the cross doman page 'main'
   if ( this.IsStatus('externalpage') ) {
      this.ChangeStatus('pending');
      /* this.Log('URL=' + document.URL); */
      var querypage = $.proxy(this.AcceptPage,this);
      this.AbortAjax();
      _xhr = $.ajax({
            url: pageUrl
          , crossDomain: true
          , success: function (data) { 
                 $("#main").html(data); 
            }
          , dataType: 'jsonp text'
      })
      .error(querypage);
   }
}

//  find the parent "div", find href ; make sure it has no http :
//  json it 
//
//______________________________________________________________
function Pm(url,staticUrl) {
 // class Panda Monitor
  $('body').log("Body").data('Pm',this);
  this._baseURL = document.URL;
  this._staticUrl = staticUrl;
  this._hashLock = false;
  this._topElement =new PmElement("<div id=monitorRoot class=PandaMonitor>Hello Monitor</div>");
  // $('body').append(this._topElement._id);
  var pmRef = this._topElement;
  this._version = pmRef.Path2Version(location.pathname);
  this._setFunction = function(id,f) {
      var el = pmRef.Find(id);
      if (el==undefined) {
         el = new PmElement('#'+id);
         pmRef.Append(el);
      }
      el._render = f;
      // el.Log(" ---- > New Element found ---> " + el._render);
  }
  pmRef.Log(' My id =' + pmRef.Id());
  $('table').delegate('a','click', { link : pmRef },  function (event) {
     console.log('click = ' +  $(this).html()  + " href=" +this.href ); var res = event.data.link.Link(this,event);
   });
   /*
  $('#formid').delegate('form','submit', { link : pmRef },  function (event) { 
            console.log('submit = ' +  $(this).html()  + this.href ); 
            return event.data.link.Submit(this); 
            });
   */
   
// connect timer to the leftbox
/*    var loading = $("<div id=loading><img src='" +document.pandaURL+ "images/ajax-loader.gif'></div>"); */
/*    var divLoading = $("<div><center><table><tr><td><font size=-2>&nbsp;</td><td><span id=loading style='display:none;'><font size=-2 color=blue>...loading... </span></td><td><font size=-2>&nbsp;</td></tr></table></font></center></div>"); */
   var divLoading = $("<div><center><table><tr><td><font size=-2>&nbsp;</td><td><span id=loading > &nbsp; </td><td><font size=-2>&nbsp;</td></tr></table></font></center></div>");
   var timer = undefined;
   if (pmRef._framework) {  
      var leftbox = $('#homeup');
      var timer = $("<div id=leftboxtimer style='{font-size:0.75em }'>Time 0 secs</div>");
      leftbox.append(timer);
   }
   var loadingbox = $('#homedown');
   loadingbox.append(divLoading);
   $(document).ajaxSend(function(){ 
         var loading = $("#loading");
         var ajdata = loading.data('ajdata');
         if (ajdata == undefined) { ajdata = 0; }
         ajdata++;loading.data('ajdata',ajdata);         
         /* $(this).show(); */
   //       $(this).html("<img src='" +document.pandaURL+ "images/ajax-loader.gif'>");
          if (! $("body").hasClass('wait') ) {
               loading.html("<tiny><it>....dowloading .... </it></tiny>");
               $("#savejsonID").hide();
               $("body").addClass('wait');
          }
       });
       $(document).ajaxComplete(function(){ 
         /* $(this).hide();  */
          var loading = $("#loading");
          var ajdata = loading.data('ajdata');
          ajdata--;loading.data('ajdata',ajdata);
          if ( ajdata <=1) {
                loading.html("&nbsp;");
                $("#savejsonID").show();
                $("body").removeClass('wait');
          }
   });
     
   /* $("#urlIconId").click(function()       { $("#urlID").toggle('slide');   } ); */
   $("#navhelpbuttonId").click(function() { $("#navhelp").toggle('slide'); } );
   $("#savejsonID").click(function() { 
         var d = pmRef.Find("main").Data();
         var data =  d.data;
         if (d.format !='json') { 
            data= {};
            data[d.format]= d.data;
         }
         utils().json(data);} 
      );
    $(window).bind('hashchange', function (evt) {
      // do some magic      
      var pm=pmRef;
      evt.preventDefault();
      evt.stopPropagation();
      var hashLock =  $('body').data('Pm')._hashLock;
      if (hashLock) { $('body').data('Pm')._hashLock = false; }
      if (evt._pm == undefined  && !hashLock) {
         var href = window.location.href;
         var search = window.location.search;
         var pathname = window.location.pathname;
         var hindex =  href.indexOf("#");
         var hindex =  href.indexOf("#");
         var hindexPath =  href.indexOf("#/");
         if (hindex >=0 ) {
            if (hindexPath == hindex) { href = href.replace(pathname,"") ;}
            /* href = href.replace(search,"").replace("#",""); */
            pm.Log("HasH EVENT adjuested href: " + href);
         }
         pm.ChangeStatus('modified',href);
      }
    });
    if (timer != undefined) { 
       var today = new Date();
       timer.data('startTime', today.getTime());
       $('#leftboxtimer').everyTime(2500, function() {
            var today = new Date();
            var i =  (today.getTime()- $(this).data('startTime'))/1000;
            var mins = Math.floor(i/60);
            var secs = (i%60).toFixed();
            var hours = Math.floor(i/3600).toFixed();
            var mins = (mins % 60).toFixed();;
            out =  'duration: ';
            if (hours > 0) { out += hours ;  out+= '<font size=-2>h</font> ';}
            if  (mins > 0 || hours > 0 ) { out += mins; out += '<font size=-2>m</font>'; }
            out += secs; out += '<font size=-2>s</font>';
           $(this).html(out);
       }, 0);
    }
   jQuery.ajaxSetup({
         accepts: {
         script: "text/javascript, application/javascript"
    } } );
 //  this._topElement.ChangeStatus('modified');
 //---------------
 // testing
 /*
  var tr = new PmElement('<div id=try></div>');
  this._topElement.Append(tr);
  tr.Parent();
  var top = tr.GrandParent();
  top.Log('GrandParent');
  var mn = top.Find('try');
  mn.Log("found");
  mn = top.Find('monitorRoot');
  mn.Log("found");
  learn: 
  http://www.asual.com/jquery/address/docs/ 
  http://alexgorbatchev.com/SyntaxHighlighter/
  http://phpjs.org/functions
*/
}
