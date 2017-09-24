/* $Id: ajaxrender.js 15584 2013-05-22 23:16:22Z fine $ 
   Author: Valeri Fine (fine@bnl.gov) 16 July 2012
*/

var  tver_pattern  =/[\/]~([^\/]+)/g;
tver_pattern.compile(tver_pattern);

function AjaxRender(tag,render,query,params,host,refresh,delay) {
   /*  execute the function 'render" with the dynimically loaded  ajax data from 
                 http:<host>[/~<version>]/<query>[?params]
          the  execution can be delayed  if "delay==true" 
          and it can be refreshing  via 'refresh' security
          The success is to render its content with the "container" defined by "tag" parameter
   */   
   this.init(tag,render,query,params,host,refresh,delay);   
   this._jqxhr;
   this._timeout;
   this._maxRefreshCounter = 7;
   this._defaultDelay = 5;
   /* https://github.com/jakesgordon/javascript-state-machine/ */
   StateMachine.create({
             /* initial: 'none', */
             target: AjaxRender.prototype,
             events: [
               { name: 'delayRender',  from: 'none',                to: 'refreshed'},
               { name: 'downloaddata', from: [ 'none','nodata'
                                              ,'stop','refreshed'], to: 'waitdata' },
               { name: 'timeout',      from: 'waitdata',            to: 'refreshed'},
               { name: 'success',      from: ['none','waitdata'],   to: 'dataready'},
               { name: 'renderpage',   from: ['none','dataready'],  to: 'rendered' },
               { name: 'refresh',      from: 'rendered',            to: 'waitdata' },
               { name: 'done',         from: 'rendered',            to: 'stop'     },
               { name: 'failure',      from: 'waitdata',            to: 'nodata'   },
               { name: 'cancel',       from: '*',                   to: 'stop'     },
               { name: 'starup',       from: '*',                   to: 'none'     }
            ]});
   / *this._fsmstartup(); */
}
//___________________________________________________________________________________________________
//___________________________________________________________________________________________________
AjaxRender.prototype = {

   needRefresh: function() { if (this._refresh < 0) {return  true;}  return ( this._refresh && this._refresh>0 && this._maxRefreshCounter-- > 0) ; }

  ,onbeforedownloaddata: function(event, from, to,msg)  { this.doDownload();            } 
  ,onbeforerenderpage:   function(event, from, to,data) { this.doRender(data);          }
  ,onbeforerefresh:      function(event, from, to,msg)  { this.doTimeout();             } 
  ,onbeforedelayRender:  function(event, from, to,msg)  { this.doTimeout(this._delay);  } 
  ,onbeforesuccess:      function(event, from, to,data) { this._data = data;            } 
  ,onbeforecancel:       function(event, from, to,msg)  { 
                  if (this._timeout) { clearTimeout(this._timeout); this._timeout=undefined;} 
                  if (this._jqxhr)   { this._jqxhr.abort();                                 }  
               }
  ,onrefreshed:       function(event, from, to,msg)  { this.downloaddata();              } 
  ,ondataready:       function(event, from, to,msg)  { this.renderpage(this._data);      }
  ,onrendered:        function(event, from, to,msg)  { if ( this.needRefresh() ) {  this.refresh(); } else {this.done();}}
  ,onnodata:          function(event, from, to,msg)  { this.downloaddata();              } 

  ,download:   function(tag,render,query,params,host,refresh,delay)  {  
                  this.init(tag,render,query,params,host,refresh,delay); 
                  this.downloaddata();}
  ,delay:      function(tag,render,query,params,host,refresh,delaytime)  {  
                  this.init(tag,render,query,params,host,refresh,delaytime);
                  this.delayRender();
               }
  ,render:     function(data) { this.success(data);            }
  ,init:       function (tag,render,query,params,host,refresh,delay) { 
                     this._refresh =  refresh;
                     this._tag     =  tag;
                     this._render  =  render;
                     this._host    =  host;
                     if (params != undefined) { this._params = $.extend({},params); }
                     this._delay   =  delay;
                     if (this._options===undefined) {
                        this._options = {
                                type: "GET"
                              , cache: false
                              , dataType: 'json'
                        };
                     }
                     this.url(query,params,host);
               }
 

  /* onchangestate: function(event, from, to) { alert('all is clear'); }, */

  // my other prototype methods

  //___________________________________________________________________________________________________
  , url: function(query,params,host) {
      /* set the URL //host/~ver/query?params 
         if (host != undefined) - use JSONP protocol, otherwise JSON
      */ 
      var u =  '';
      if (host   != undefined)  {this._host=host;    } 
      if (query  != undefined)  {this._query=query;  } 
      if (params != undefined)  {this._params = $.extend({},params);} 
      if (this._host != undefined) { 
         u = '//';
         if (this._host.indexOf('http:') == 0 ||  this._host.indexOf('https:') == 0 ) { u = ''; }
         u+= this._host ; 
         protocol = 'jsonp'; 
      }
      else {protocol = 'json'; }
      var  ltver_pattern  =/[\/]~([^\/]+)/g
      var pn = ltver_pattern.exec(window.location.pathname);
      if (pn != null)                { u+= '/~'+ pn[1];      }
      else {
         var pm = $('body').data('Pm');
         if (pm!=undefined && pm._version.version != undefined) {u+= '/~'+pm._version.version; }
      }
      if (this._query !=  undefined) { u+= "/" +this._query; }
      if (this._params != undefined) { u+= "?" + $.param(this._params).replace('=undefined','='); }
      this._options['url'] = u;
      this._options.dataType = protocol;
      return u;
   }
  //___________________________________________________________________________________________________
  , cache : function(c) {
      /* c - true - enable the cache, false - disable the cache */
     var ca = this._options.cache;
     if ( c != undefined) {
        ca = this._options.cache = c;
     }
     return ca;
   }
  //___________________________________________________________________________________________________
  , doTimeout : function(time) {
     if ( time == undefined) { time = this._refresh;}
     if ( time == undefined) { time = this._defaultDelay; }
     var instance = this;
     if (time <0) {  time = -time; }
     this._timeout=setTimeout( function () { instance.timeout();}, time*1000); 
   }
  //___________________________________________________________________________________________________
  , doRender : function(data) {
     /* console.log(' doRender:' + JSON.stringify(data)); */
     var forceRefresh = undefined;
     if (data.params != undefined) {
         if (this._params == undefined) { this._params = {} ; }
         if ( data.params  != undefined && data.params.refresh != undefined) { forceRefresh = data.params.refresh; }
         $.extend(this._params,data.params);
     }
     if (forceRefresh !=undefined  ) {
        this._refresh = forceRefresh;
     } else if (this._maxRefreshCounter == undefined || this._maxRefreshCounter<=0 ) {
         this._refresh = undefined;
         this._params.refresh = undefined;
     }
     this.url();
     /* console.log(' doRender: tag=' + JSON.stringify(this._tag)  + '; params='+ JSON.stringify( this._params) + "; rednder="+ JSON.stringify(this._render)); */
     this._render(this._tag,data);
   }
  /* _____________________________________________________________________________*/
  , doDownload : function () {
      this._options['success'] = function(msg) { ajsuccess(msg); }
      this._jqxhr = $.ajax(this._options);
      var instance = this;
      /* __________________________________________________________________ */
      function ajsuccess(msg) {
         var response = msg.pm;
         /* console.log(" ------------- doDownload.ajsuccess Success:" + JSON.stringify(msg)); */
         for (var i in response) {
            var mn = response[i].json;
            if  ( mn == undefined ) { 
               /* if ( failure!= undefined) {  instance.failure(msg);} */
               continue;
            }
            instance.success(mn);
            break;
         }
      }
   }
}