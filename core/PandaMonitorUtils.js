// $Id: PandaMonitorUtils.js 19632 2014-07-06 07:30:10Z jschovan $:

function binSearch(array, needle, f) {
   if (!array.length) return -1;
   if ( f == undefined) {
     f = function(a,b) { var cmp = 0; if (a>b) { cmp=1; } else if (b>a) { cmp = -1; } return cmp; };
   }

   var high = array.length - 1;
   var low = 0;
   var mid = 0;
   while (low <= high) {
      mid = parseInt((low + high) / 2);
      element = array[mid];
      var cmp =  f(element,needle);
      if (cmp > 0)  {
         high = mid - 1;
      } else if (cmp < 0 ) {
         low = mid + 1;
      } else {
         break;
      }
   }
   return mid;
}

//__________________________________________________________________________________________________
function PandaPlotPage(parent) {

}

//__________________________________________________________________________________________________
function PandaPad(parent) {

// placeholder for several Panda pads
/*
    this.fPadDiv  = ${"<div></div");
   this.fPadDiv.addClass("class_padDiv");
    this.fPadTable = $("<table></table>");
    this.fPadTitle = $("<tr></tr>");
   this.fPadTitle.addClass("class_padTitle");
   this.fPadTitle.appendTo(this.fPadTable);
   this.fPadTable.appendTo(this.fPadDiv);
    this.SetPad(this)
   if (parent != null)  {
       parent.append(this);
    }
   else  {
      .append(this);
   }
*/   
}

//__________________________________________________________________________________________________
PandaPad.prototype.gPad  = null;
//__________________________________________________________________________________________________
PandaPad.prototype.setPad = function(pad)
{
   PandaPad.prototype.gPad = pad;
}

//__________________________________________________________________________________________________
PandaPad.prototype.divide = function(cols,rows)
{
   // divide the current pad onto cols x rows subpads
}
//__________________________________________________________________________________________________
function FlotPlot() {
    this.plot = null;
    this.updateLegendTimeout = null;
    this.latestPosition = null;
    this.dataset = null;
    this.cleanLegend = false;
 }
 var plot2UpdateLegend = [];
//__________________________________________________________________________________________________
function updateLegends() {
   while ( plot2UpdateLegend.length > 0) {
      var plot = plot2UpdateLegend.pop();
      plot.updateLegend();
   }
}
//__________________________________________________________________________________________________
// helper for returning the weekends in a period
function weekendAreas(axes) {
   var markings = [];
   var d = new Date(axes.xaxis.min);
   // go to the first Saturday
   d.setUTCDate(d.getUTCDate() - ((d.getUTCDay() + 1) % 7))
   d.setUTCSeconds(0);
   d.setUTCMinutes(0);
   d.setUTCHours(0);
   d.setUTCHours(0);
   var i = d.getTime();
   do {
      // when we don't set yaxis, the rectangle automatically
      // extends to infinity upwards and downwards
      markings.push({ xaxis: { from: i, to: i + 2 * 24 * 60 * 60 * 1000 } });
      i += 7 * 24 * 60 * 60 * 1000;
   } while (i < axes.xaxis.max);
   return markings;
}
//__________________________________________________________________________________________________
 FlotPlot.prototype.roundLegend = function(y) {
   if ( y < 1)
      y = "" +  y.toFixed(2);
   else if (y < 1000)
      y =  "" +  Math.ceil(y);
   else if (y < 1000000)
      y = "" + (y/1000.).toFixed(1) + " K";
   else 
      y = "" + (y/1000000.).toFixed(1) + " M";
   return y;
}

//__________________________________________________________________________________________________
 FlotPlot.prototype.showTooltip= function(x, y, contents) {
     $('<div id="tooltip">'  + contents + '</div>').css( {
         position: 'absolute',
         display: 'none',
         top: y + 5,
         left: x + 5,
         border: '1px solid #fdd',
         padding: '2px',
         'background-color': '#fee',
         'font-size' :'0.6em' ,
         'font-family' : 'Verdana, sans-serif',
         opacity: 0.80
     }).appendTo("body").fadeIn(200);
   }
//__________________________________________________________________________________________________
 FlotPlot.prototype.updateLegend = function() {
   var plot = this;
   plot.updateLegendTimeout = null;
   var pos  = plot.latestPosition;
   var endOfLegend = /:{2}.*/;
   var t = $('#sitetable');
   var dt;
   if ( t != undefined) {  dt = $('#sitetable').dataTable();  }
   if (this.cleanLegend) {
      this.cleanLegend = false;
      var i, dataset = plot.plot.getData();
      for (i = 0; i < dataset.length; ++i) {
         var series = dataset[i];
         var intg = "::";
         if (series.integral != undefined  && series.integral !=0 ) {
            var head = "Total";
            var color = "black";
            if (series.integral < 1)  {
               head = "Average";
               color = "blue";
            }
            intg +=  "<b title='" + head + " number of entries'><font color=" + color + ">"+this.roundLegend(series.integral)+ "</font></b>";
         }
         if (plot.legends) {
            plot.legends.eq(i).html(series.label.replace(endOfLegend, intg));
         }
         if (t.length >0 && t.data("filter") ) { t.data("filter", false); dt.fnFilter('',0, false,false); }

      }
   } else {
      if (pos == null) return;
      var axes = plot.plot.getAxes();
      if (pos.x < axes.xaxis.min || pos.x > axes.xaxis.max ||
         pos.y < axes.yaxis.min || pos.y > axes.yaxis.max)
         return;
 
      var i, j, dataset = plot.plot.getData();
      var tooltip = '';
      for (i = 0; i < dataset.length; ++i) {
         var series = dataset[i];
 
         // find the nearest points, x-wise
         for (j = 0; j < series.data.length; ++j)
            if (series.data[j][0] > pos.x)
               break;            
         // now interpolate
         var y, p1 = series.data[j - 1], p2 = series.data[j];
         if (p1 == null)
            y = p2[1];
         else if (p2 == null)
            y = p1[1];
         else
            y = p1[1] + (p2[1] - p1[1]) * (pos.x - p1[0]) / (p2[0] - p1[0]);
         if (plot.legends) {
            plot.legends.eq(i).html(series.label.replace(endOfLegend, ":: " + this.roundLegend(y)));
         }
      }
      // draw the tooltip 
      if ( (plot.item != undefined ) && (plot.item != null ) )   {
          var xaxes = plot.plot.getXAxes();
          var mode =  xaxes[0].options.mode;
          if (mode == 'time') {
             tooltip = new Date(pos.x);
          } else if (mode=='name') {
             var names = xaxes[0].options.names;
             tooltip = names[Math.floor(pos.x)];
          } else {
             var x =   "x=" + Number(pos.x).toFixed(2) ;
             if (mode=='label') {
                var ticks = xaxes[0].options.ticks;
                if (ticks) {
                   var indx= binSearch(ticks, Math.round(Number(pos.x)), function(a,b) { var cmp = a[0] - b; if (cmp >0) {return 1;} if (cmp <0) {return -1;} return 0; }); 
                   var label = ticks[indx][1];
                   x = label;
                }
             }
             tooltip = x + " : y=" + Number(pos.y).toFixed(2);
          }
          plot.showTooltip(plot.item.pageX, plot.item.pageY, " " + tooltip);
          if (t.length >0) {   t.data("filter", true); dt.fnFilter(tooltip,0, false,false ); }
      }
   }
}
//__________________________________________________________________________________________________
function PageControl() {
}

//__________________________________________________________________________________________________
function utils() {
    if (document.pandaUtils ==undefined) {
        // alert("Error!!! PandaMonitorUtils was not initialzied yet !");
        new PandaMonitorUtils(document.pandaURL);
    }
    return document.pandaUtils;
}

//__________________________________________________________________________________________________
PageControl.prototype.fTotalPagesIDID="totalPagesID_";
PageControl.prototype.fCurrentPagesIDID="currentPageID_";

//__________________________________________________________________________________________________
function PandaMonitorUtils(url){
//  this.p_ds = /([^\.]+)\.([^\.]+)\.([^\.]+)\.([^\.]+)\.([^\.]+)\.([^\.]+)\.(.*)/;
  this.p_ds = /([^\.]+)\.([^\.]+)\.([^\.]+)\.([^\.]+)\.([^\.]+)\.(.*)/;
  this.p_tsname = /([^\.]+)\.([^\.]+)\.([^\.]+)\.([^\.]+)\.(.*)/;   // tasks have no the "format' field
  this.p_ds.compile(this.p_ds);
  this.p_tsname.compile(this.p_tsname);
  this.baseURL = url;
  this.fPlotTitles = [];
  if (parseInt(navigator.appVersion)>3) {
      if (navigator.appName=="Netscape") {
         this.IE = false;
      }
  }
 // this.hasAdd2Favorite = !this.IE;
//  if (this.hasAdd2Favorite ) { this.hasAdd2Favorite  = !(window.external== undefined || window.external.AddFavorite == undefined); }

  document.pandaUtils = this;
  // this.LoadJQuery();
}
//________________________________________________________________________________________
PandaMonitorUtils.prototype.baseURL = null;
PandaMonitorUtils.prototype.oldPandaHost='http://panda.cern.ch';
PandaMonitorUtils.prototype.newPandaHost='http://pandamon.cern.ch';
PandaMonitorUtils.prototype.JQueryLoaded = false;

PandaMonitorUtils.prototype.IE = true;

PandaMonitorUtils.prototype.hasAdd2Favorite =  window.external || window.sidebar || (window.opera && window.print);
PandaMonitorUtils.prototype.colorMap = {  nfinished: '#00CC00' 
                                        , finished : '#0000FF'  // panglia color '#0000FF' 
                                        , failed   : '#55FF00'  // panglia color '#FFFF00'
                                        , activated: '#000000'
                                        , defined  : '#787878' 
                                        , holding  : '#FFA600'  // panglia color '#FFA600'
                                        , running  : '#008800'  // panglia color '#008800'
                                        , sent     : '#AD3ACC'
                                        , assigned : '#00FFFF'
                                        , transferring:'#FF0000'
                                        , cancelled: '#FFFF00'  //  panglia color  '#FF0000'
                                        , nfailed  : '#FF6666' 
                                        , errorRate: '#0000FF'
                                        , CA       : '#FF1F1F'
                                        , CERN     : '#AE3C51'
                                        , CE       : '#AE3C51'
                                        , DE       : '#000000'
                                        , ES       : '#EDBF00'
                                        , FR       : '#0055A5'
                                        , IT       : '#009246'
                                        , ND       : '#6298FF'
                                        , NL       : '#D97529'
                                        , TW       : '#89000F'
                                        , UK       : '#356C20'
                                        , US       : '#00006B'
                                       };
PandaMonitorUtils.prototype.rgba = function(rgb,alpha) {
   // The alpha parameter is a number between 0.0 (fully transparent) and 1.0 (fully opaque).
   if (alpha === undefined) { alpha= 0.5 ; }
   if (rgb == undefined) { rgb =  this.colorMap['failed']; }
   var rgba = "rgba(" + parseInt(rgb.substring(1,3),16) + "," + parseInt(rgb.substring(3,5),16)+ "," + parseInt(rgb.substring(5,7),16) + "," + alpha.toFixed(2) + ")";
   return  rgba;
}
PandaMonitorUtils.prototype.timeUnitSize = {
         "second": 1000,
         "minute": 60 * 1000,
         "hour": 60 * 60 * 1000,
         "day": 24 * 60 * 60 * 1000,
         "month": 30 * 24 * 60 * 60 * 1000,
         "year": 365.2425 * 24 * 60 * 60 * 1000
      };   

PandaMonitorUtils.prototype.units = function(fieldname,globalUnit) 
{ // Returd the field units
      var units = globalUnit;
      if (units == undefined) {
         var fieldUnit  = { 
                              n        : "Jobs"
                            , t        : "mins"
                            , e        : "Rate"
                            , T        : "Errors/hour"
                            , nEvents  : "Events"
                            , tgetjob  : "secs"
                            , tstagein : "secs"
                            , tstageout: "secs"
                           }
         var firstChar =  fieldname.charAt(0);
         units = "Jobs";
         if (fieldUnit.hasOwnProperty(fieldname) ) {
            units =  fieldUnit[fieldname];      
         } else if (fieldUnit.hasOwnProperty(firstChar))  {
            units =  fieldUnit[firstChar];
         }
      }
      return units;
}                                      
PandaMonitorUtils.prototype.fPlotID="plotID";
PandaMonitorUtils.prototype.showTableTag = 'Show the table';
//________________________________________________________________________________________
 function  dateFormatter (v, axis) {
   // map of app. size of time units in milliseconds
   var timeUnitSize = {
      "second": 1000,
      "minute": 60 * 1000,
      "hour": 60 * 60 * 1000,
      "day": 24 * 60 * 60 * 1000,
      "month": 30 * 24 * 60 * 60 * 1000,
      "year": 365.2425 * 24 * 60 * 60 * 1000
   };
   var label = '';
   // --- original code from jquery.flot.js
   var d = new Date(v);
   var axisOptions = this;
   // first check global format
   if (axisOptions.timeformat != null)
       label = $.plot.formatDate(d, axisOptions.timeformat, axisOptions.monthNames);
   else {
      var t = axis.tickSize[0] * timeUnitSize[axis.tickSize[1]];
      var span = axis.max - axis.min;
      var suffix = (axisOptions.twelveHourClock) ? " %p" : "";
        
      if (t < timeUnitSize.minute)
          fmt = "%h:%M:%S" + suffix;
      else if (t < timeUnitSize.day) {
         if (span < 2 * timeUnitSize.day)
            fmt = "%h:%M" + suffix;
         else if (span < 3 * timeUnitSize.day) 
            fmt = "%b %d\n%hh" + suffix;
         else   
            fmt = "%d\n%hh" + suffix;
      }
      else if (t < timeUnitSize.month)
         fmt = "%b %d";
      else if (t < timeUnitSize.year) {
         if (span < timeUnitSize.year)
            fmt = "%b";
          else
            fmt = "%b %y";
      }
      else
         fmt = "%y";
        
      label =  $.plot.formatDate(d, fmt, axisOptions.monthNames);
   }
   var tickSize = axis.tickSize[0], unit = axis.tickSize[1];
   var step = tickSize * timeUnitSize[unit];
   if ( (v >= axis.max-step )  && this.title ) {
      label = label + " " + this.title;
   }
   return label;
}
 
//________________________________________________________________________________________
function suffixFormatter(val, axis) {
   var label = '';
   var dec = axis.tickDecimals;
   var log = this.log;
   if (log) {
      if (this.first == undefined ) {
         this.first = val;
      } else {
         if ( val < this.first) { this.first = val; }
         else if ( val <= axis.max ) {
            var ratio = val/this.first;
            if (ratio < 10 ) return '';
            else { this.first = val; }
         } else {
           this.first = undefined;
         }
      }
   }
   if (dec == 0) dec = 1;
   if ( (val > axis.max )  && this.title ) {
      label = this.title;
   } else if (val >= 1000000.) {
      label = (val / 1000000.).toFixed(dec) + " M";
   } else if (val >= 1000.) {
      label = ( val / 1000.).toFixed(dec) + " K";
   } else {
      label = val.toFixed(dec);
   }
//   if (this.color) label = "<font color='" + this.color + "' >" + label + "</font>";
   return label;
}
//___________________________________________________________________________________________________
   PandaMonitorUtils.prototype.objLen =  function (object) {
   /* Calculate the number of the properties within the object */
      var count;
      if ( count == undefined) {
         count = 0;
         for (var i in object)  { ++count; }
      }
      return count;
   }

//________________________________________________________________________________________
PandaMonitorUtils.prototype.LoadScripts = function(scripts) {
   var h = document.getElementById("head");
   var len = scripts.length;
   for ( var i = 0; i < len; i++) {
      var s = document.createElement("script");
      s.setAttribute("type", "text/javascript");
      s.setAttribute("src", this.fileScriptURL() + "/" + scripts[i]);
      h.appendChild(s);
   }
}
//________________________________________________________________________________________
PandaMonitorUtils.prototype.LoadJQuery = function() {
   if (this.JQueryLoaded) return;
   // this.LoadScripts([ 'flot/jquery.js'
                     // , 'flot/jquery.flot.js'
                     // , 'flot/jquery.flot.crosshair.js'
                    // ]);
   // if  (this.IE) this.LoadScripts([ 'flot/excanvas.js']);
   if ($.support.cssFloat) this.LoadScripts([ "base64.js","canvas2image.js"]); 
   this.JQueryLoaded = true;
}
//________________________________________________________________________________________
PandaMonitorUtils.prototype.tablesort = function (tableid) {
      $("#" + tableid).tablesorter({widthFixed: true})
 }
//________________________________________________________________________________________
PandaMonitorUtils.prototype.datatable = function (tableid,option,ldefault) {
    var defflt =  -1;
    var pages = [ [ 35,50, 75, 100, 150, -1], [ 35, 50, 75, 100, 150,"ALL"] ];
    if (ldefault != undefined) {
       defflt = ldefault;
       pages =  [ [ defflt, 35,50, 75, 100, 150, -1], [ defflt, 35, 50, 75, 100, 150,"ALL"] ];
    }
    var opt =  {"bProcessing": true
                , "iCookieDuration": 1 
                /* , "bAutoWidth"   : false */
                , "iDisplayLength": defflt
                , "aLengthMenu"   : pages
                , "bStateSave"    : navigator.cookieEnabled === true
                , "bJQueryUI"     : true
                , "fnStateSave" : function (oSettings, oData) { 
                        localStorage.setItem( 'DataTables_'+window.location.pathname+tableid, JSON.stringify(oData) );
                     }
                , "fnStateLoad": function (oSettings) {
                       return JSON.parse( localStorage.getItem('DataTables_'+window.location.pathname+tableid));
                     }
                /* , "oSearch" : {
                   "sSearch" :"",
                   "bRegex": true, 
                   "bSmart": false } */
               };
   if ( option != undefined )  { $.extend(opt,option);   } 
   var dtab = $("#" + tableid).dataTable(opt);
   /*
   $(document).ready(function() {
      $(window).bind('resize', function () {
       dtab.fnAdjustColumnSizing();
     } );
   } );
   */
   return dtab;
 }
 //__________________________________________________________________________________________________
   PandaMonitorUtils.prototype.isFilled = function(item) {
      return item != undefined && item!= null && item != "" && item != 0;
   }

//________________________________________________________________________________________
   PandaMonitorUtils.prototype.fileURL = function (fileType) {
        // URL to access the image and Javascript files 
        return this.baseURL + fileType;
   }
         
//________________________________________________________________________________________
   PandaMonitorUtils.prototype.fileImageURL = function() {
      return this.fileURL("images");
   }

//________________________________________________________________________________________
   PandaMonitorUtils.prototype.fileScriptURL = function() {
      return this.fileURL("js");
   }

//__________________________________________________________________________________________________
   PandaMonitorUtils.prototype.renderCharts = function () {
      this.renderFlotChart();
      return;
      var chkBox = document.getElementById('checkbox_RenderID_0');
      if (chkBox) {
         if (document.getElementById('checkbox_RenderID_0').checked) {
            this.renderFlotChart();
         } else { 
            this.renderGoogleChart();
         }
      }
   }
//__________________________________________________________________________________________________
   PandaMonitorUtils.prototype.onResizeEnd = function (table) {
      // alert('Resize : ' + table + ' : ' + this.renderGoogleChart);
      if (this.renderGoogleChart) {
         this.renderGoogleChart();
      }
   }
//__________________________________________________________________________________________________
   PandaMonitorUtils.prototype.makeData = function (data) {
      this.data = data;
      this.dataRowInds = this.data.getSortedRows(0);  
      // ctreate the X- array
      this.xDataValues = [];
      for (var i = 0; i < this.dataRowInds.length; i++) {
         this.xDataValues.push(data.getValue(this.dataRowInds[i], 0).getTime());
      }
   }      
//__________________________________________________________________________________________________
   PandaMonitorUtils.prototype.makeHists = function (hists) {
      this.hists = hists;
   }
//__________________________________________________________________________________________________
   PandaMonitorUtils.prototype.siteStatsTable = function () {
      var table = document.getElementById('siteStats_div');
      return table;
   }
//__________________________________________________________________________________________________
   PandaMonitorUtils.prototype.windowSize = function () {
      var winW = 630, winH = 460;
      if ( this.IE) {
         winW = document.body.offsetWidth-20;
         winH = document.body.offsetHeight-20;
      }  else {
         winW = window.innerWidth-16;
         winH = window.innerHeight-16;
      }
      var winSize = new Array;
      winSize.push(winW); winSize.push(winH);   
      return winSize;
  }
//___________________________________________________________________________________________________
   PandaMonitorUtils.prototype.setDateRange = function(anchor) {
      var daterange = '';
      if (this.tstart) {
          var d =  new Date(this.tstart);
          daterange="&tstart=" + d.getFullYear() + "-" + (d.getMonth()+1) + "-" + d.getDate()+ "+" + d.getHours(); ; 
      }
      if (this.tend)    { 
         var d =  new Date(this.tend);
         daterange+="&tend=" + d.getFullYear() + "-" + (d.getMonth()+1) + "-" + d.getDate() + "+" + d.getHours(); 
      }
      anchor.href = $.param.querystring(anchor.href, daterange);
   }

//________________________________________________________________________________________
   PandaMonitorUtils.prototype.selectDateRange= function(tstart,tend,id) {
      if (tstart == undefined) tstart = '';
      if (tend   == undefined) tend = tstart;
      var html = $("<div class='ui-datepicker-inline ui-datepicker ui-widget ui-widget-content ui-helper-clearfix ui-corner-all' style='display: block;' id=" +id+ ">"
          + "<label for='from'> <b>From:</b> </label>" 
          + "<input type='text' id='from' name='tstart' value='" +tstart+ "' size='9'/>"
          + "<label for='to'> <b>to:</b> </label>"
          + "<input type='text' id='to' name='tend' value='" +tend+ "'  size='9'/>"
          + "</div>"); 
      this.calendar();
      return html
   }

//___________________________________________________________________________________________________
   PandaMonitorUtils.prototype.calendar = function() {
      this.tstart = undefined;
      this.tend   = undefined;
      var fromInitDate = $("#from");
      var toInitDate = $("#to");
      var anchor = $("a.pandaTimeBoundClass");
      var panda =  anchor.data("panda");
      if  ( panda != undefined) {
          anchor.die("click");
      }  else {
          $("a.pandaTimeBoundClass").data("panda",this);
          panda = this;
      }
      $("a.pandaTimeBoundClass").live("click", function() {
      panda = $(this).data("panda");
      panda.setDateRange(this);
    });
      var dates = $( "#from, #to" ).datepicker({
         dateFormat : 'yy-mm-dd 00', 
         showOn: "both", 
         buttonImage:  this.fileImageURL() + "/calendar.gif",
         buttonImageOnly: true,
         defaultDate: this.value ? this.value : "+1w",
         maxDate :    new Date(),
         minDate:    new Date(2009,0,1),
         changeMonth: true,
         changeYear: true, 
         numberOfMonths: 1,
         onSelect: function( selectedDate ) {
            var option = this.id == "from" ? "minDate" : "maxDate",
               instance = $( this ).data( "datepicker" ),
               date = $.datepicker.parseDate(
                  instance.settings.dateFormat ||
                  $.datepicker._defaults.dateFormat,
                  selectedDate, instance.settings );
            dates.not( this ).datepicker( "option", option, date );
            if (this.id == "from")  {
              panda.tstart = date;
            } else  {panda.tend=date; }
         }
      });
   };
   
//___________________________________________________________________________________________________
   PandaMonitorUtils.prototype.max = function( array ){
      var mx;
      if (array  != undefined) {
         var l = array.length;
         if (l >0) {
            var ic = 0;         
            for (var m in array) {
               if (m !=  undefined) {
                  mx = m; 
                  break;
               }
               ic++;
            }
            mx = array[0];
            for (var i=ic;i<l;++i) {
               var nx = array[i];
               if (nx == undefined) continue;
               if (nx > mx) {mx = nx;}
            }
         }
      }
      return mx;
   }

//___________________________________________________________________________________________________
   Array.min = function( array ){
      return Math.min.apply( Math, array );
   }

  //___________________________________________________________________________________________________
   function bin(i,m,s) {
   // Return the coordinate of the middle of the bin defined by its index
      return m + (i*s + s/2);
   }

//___________________________________________________________________________________________________
   PandaMonitorUtils.prototype.renderHistDataset = function (name, hists,min,step,cloudColor,un) 
   {
      //  return on FLOT dataset
       var label = name;
       var histObject =  hists[name];
       if (histObject == undefined) return histObject;
       var xBins;
       var metaList;
       for (var m in histObject) {
         var integral;
         if (m == 'data')  {
            xBins= histObject[m];
         } else if (m == 'meta') {
            metaList = histObject[m];
            for (var a in metaList) {
               if (a=='legend')
                  label = metaList[a];
            }
         }  else if (m == 'integral') {
            integral = histObject[m];
         }  else if (m == 'nentries') {
            nentries = histObject[m];
         }
       }
       var range = this.max(xBins);
       var yax = 1;
       if ( range !=undefined) { 
           yax  = (range <= 1.005) ? 2: 1;
       }
       var lPoints = xBins.length;
       var d = [];
       for (var k = 0; k < lPoints; ++k) {
          var x = xBins[k];
          if ( x == undefined) x = 0;
          d.push([un*bin(k,min,step),x]);
       }
       var intg = "00000000 M";
       var dataset = { data: d,
                  label: label + "::" + intg
                , yaxis: yax
                , lines : {   fill : 0.4
                            , fillColor: null
                          }
         };
      if  (integral != undefined )  { 
         dataset.integral = integral; 
      }
      label2Color = label;    
      // console.log('label =' + label, ' cloud color = ' + cloudColor +  ' mp=' + this.colorMap[label2Color]);
      if (cloudColor) label2Color = cloudColor
       if (this.colorMap[label2Color] != null) {
         dataset.color = this.colorMap[label2Color];
         // dataset.lines.fillColor = dataset.color;
         // console.log('label =' + label, ' cloud color = ' + cloudColor + ' ds = ', dataset.color);
       } else {
          // dataset.color = parseInt(label2Color[0]) & 255  + 255*(parseInt(label2Color[1]) + 255*parseInt(label2Color[2])) ;
       }
       return dataset;
   }

//___________________________________________________________________________________________________
   PandaMonitorUtils.prototype.pageControlHTML = function () {
   
   }
   //___________________________________________________________________________________________________
   PandaMonitorUtils.prototype.stringify = function(data) {
         return JSON.stringify(data).replace(/,null,/g,",,").replace(/,null,/g,",,");
   }
   //___________________________________________________________________________________________________
   PandaMonitorUtils.prototype.json = function (data) {
      var d = data;
      if (d == undefined) d = this.hists;
      location.href = 'data:application/json,' +  this.stringify(d);
   }

//___________________________________________________________________________________________________
  PandaMonitorUtils.prototype.renderJQPlotFHistClient = function (name, graph, opttxt) {
      var splitGraph      = document.splitGraph;
      var maxPlots        = document.maxPlots;
      var currentPlotPage = document.currentPlotPage;
      var totalPlotPages  = document.totalPlotPages;
      var nChartColumns   = document.nChartColumns;
      var nChartRows      = maxPlots/nChartColumns;
      var data            = this.hists;
      var scaleChecked    = false;
      var sC    = document.getElementById('form_scaleCheckBoxID_0');
      if (sC && sC.checked) {  scaleChecked = true;   }
      
      var chkBox = document.getElementById('checkbox_RenderID_0');
      var divBox0 = document.getElementById('form_scaleDivID_0');
      var divBox1 = document.getElementById('form_scaleDivID_1');
      if (chkBox && chkBox.checked) {
         chkBox  = true;
         if (divBox1 !=null &&  divBox1.style.visibility !='visible') {
             divBox1.style.visibility = 'visible';
             divBox0.style.visibility = 'visible';
         }
      } else {
         chkBox  = false;
         if (divBox1 !=null && divBox1.style.visibility =='visible') {
             divBox1.style.visibility = 'hidden';
             divBox0.style.visibility = 'hidden';
         }
      }
      var thisWindowSize = this.windowSize();
      // calculate the plot sizes;
      var plotWidth = Math.ceil(0.8 * thisWindowSize[0]/nChartColumns);
      var plotHeight = Math.ceil(thisWindowSize[0]/(2*nChartColumns)) + 74;
      document.getElementById('topPlotPageId').innerHTML='<center>Plots:</center>';
      document.getElementById('bottomPlotPageId').innerHTML='';
      var histogram = data.histogram;
      var mode = histogram.mode;
      var min  = histogram.min;
      var minDate  = min*1000;
      var max      = histogram.max;
      var maxDate  = max*1000;
      var step     = histogram.step;
      var inputSeries = data.series;
      var yaxis;
      if (histogram.yaxis != undefined) yaxis = histogram.yaxis;
      
      var nPlots = inputSeries.length;
      var grList = new Array;
      if (chkBox) {
         var onePlot = inputSeries[0];
         for (var o in onePlot) for (var g in onePlot[o])  grList.push(g);
         nPlots = grList.length;
      }      
      if (nPlots>0) {
         $.jqplot.config.enablePlugins = true;
         totalPlotPages = Math.ceil(1.0*nPlots/maxPlots);
         var title= this.plotTitle(0);
         for (var i=0; i< maxPlots;++i) {                     
            var graphId = name+ "_" + i + "_div";
            var plotCell = document.getElementById(graphId);
            if (plotCell) {plotCell.innerHTML = '';}
            var elm = document.getElementById(title + '_' + i + '_title');
            if (elm) elm.innerHTML = '';
            if ($.support.cssFloat) {
                $('#' + title + '_' + i + '_title').click(
                function() {
                     var div2PlotId =  $(this).next().attr('id');
                     var divobj = document.getElementById(div2PlotId);
                     var oImg = Canvas2Image.saveAsPNG(divobj.childNodes[0], false);
                     if (!oImg) {
                          alert("Sorry, this browser is not capable of saving PNG files!");
                     }
                 });
            }
            if (plotCell && elm ) {
               plotCell.style.width  = plotWidth;
               plotCell.style.height = plotHeight; 
               var j = i + (currentPlotPage-1)*maxPlots;              
               if (j>=nPlots)  {
                  continue;
               }
               // prepare the data for one frame
               var series = [];
               var y2axisColor = null;
               var yax  = 1;
               var seriesOption = null;
               if (!chkBox) {
                  var dataPlot = inputSeries[j];
                  for (var siteName in dataPlot) {
                     elm.innerHTML = siteName;
                     var padPlot   = dataPlot[siteName];
                     labels = new Array;
                     for (var gr in padPlot) {
                        series.push(padPlot[gr]);
                       if (this.colorMap[gr] != null) {
                           labels.push({ label : gr, color : this.colorMap[gr]});
                        } else {
                           labels.push({ label : gr });
                        }
                     }
                  }
               } else {
               }
               var plot = new FlotPlot;
               var timeAxisTitle = (new Date(maxDate)).getFullYear();
               var plotOptions = 
               {    
                    legend:{show:true, location:'ne'}
                  , title: siteName
                   , seriesDefaults:{
                            fillAlpha    : 0.4
                          , fill         : true   
                          , fillAndStroke: true   
                          , showMarker   : false
                          , showLine     : true                          
//                       , renderer     : $.jqplot.BarRenderer
//                        , rendererOptions:{barPadding: 8, barMargin: 20} 
                     }
                  , series:[ ]
                  , axes:  {
                           xaxis:{
                                renderer:$.jqplot.DateAxisRenderer
                              , min : minDate 
                              , max : maxDate
                              , label : timeAxisTitle
                              }
                         , yaxis:{
                              autoscale:true
                            , min:0
                            , label : 'Jobs'
                          } 
                       }
                };
               plotOptions.series = labels;
               plot.plot = $.jqplot(graphId, series, plotOptions);
            }
         }                
         document.currentPlotPage = currentPlotPage;
         document.totalPlotPages  = totalPlotPages;
                // alert('renderGoogleChart current ' + document.currentPlotPage + '; title="' + plotTitle(i) +'"');
      }
      
      if ( this.siteStatsTable() ) { 
         var showStats = document.getElementById('showStatsTableID');
         if ( showStats  &&  (showStats.innerHTML==this.showTableTag) ) {
             this.siteStatsTable().style.display = "none";
         }
      }
   }
//___________________________________________________________________________________________________
   PandaMonitorUtils.prototype.checkMobileDevice = function() {
       var r='iphone|ipod|android|palm|symbian|windows ce|windows phone|iemobile|'+
       'blackberry|smartphone|netfront|opera m|htc[-_].*opera';
       return (new RegExp(r)).test(navigator.userAgent.toLowerCase());
   }
//___________________________________________________________________________________________________
   PandaMonitorUtils.prototype.createUpdateButton = function (id,bodytxt) {
      // var me = $("#"+id);
      if (bodytxt == undefined)    {bodytxt = "Update"; }
      var u = this
      $("#"+id).bind('click', function() { u.Refresh();} );
      $("#"+id).css("cursor","pointer");
      $("#"+id).css("color","red");
      $("#"+id).html(bodytxt);
   }

//___________________________________________________________________________________________________
   PandaMonitorUtils.prototype.Refresh = function () {
   
      var url = location.href;
      if (url.indexOf("?") > 0) {
         if (url.indexOf("reload=yes") < 0)   {url += "&reload=yes"; }
         if (url.indexOf("&_time=") < 0 ) { url += "&_time=" + (new Date()).getTime(); }
      }
      location.href=url;
   }
//___________________________________________________________________________________________________
   PandaMonitorUtils.prototype.createBookmarkButton = function (id,urlAddress,pageName,bodytxt) {
      // var me = $("#"+id);
      if (!this.hasAdd2Favorite) { 
          $("#"+id).text("");
      } else  {
         if (urlAddress == undefined) {urlAddress = document.URL; }
         if (bodytxt == undefined)    {bodytxt = "Bookmark URL: "; }
         if (false) {
            bodytxt += urlAddress;
            var u = this;
            $("#"+id).bind('click', function()  { u.addToFavorites(urlAddress,pageName);} );
            $("#"+id).css("cursor","pointer");
            if (bodytxt.length > 80) { bodytxt = bodytxt.substr(0,50) + "... the URL is too long to display" ; }
            $("#"+id).html(bodytxt);
         } else {
            var addr = urlAddress;
            if (addr.length > 80) { addr = addr.substr(0,50) + "... the URL is too long to display. Get it by copying this link" ; }
             $("#"+id).html(bodytxt+ "<a href=" +urlAddress+ ">" +addr+ "</a>");
         }
      }
   }
   
   //___________________________________________________________________________________________________
   PandaMonitorUtils.prototype.linkUser = function (username,showtxt,hours) {
        /* Return the link to the user's page */
         var txt = "";
        if (utils().isFilled(username) ) {
           var cleanName = username.replace(/\s/g,"+");
           var userLikesDump = {
                "Lei Zhou" :  1
              , "Jahred Adelman" : 1
           }
           txt =  username;
           if (showtxt == undefined) showtxt = username;
           var hourtxt=''; if (hours != undefined) {hourtxt = '&hours='+hours;}
           var dumptxt = "&dump=no";
           if ( userLikesDump[username] == 1 ) {
              dumptxt = "&dump=yes";
           }
           try {
             /* txt = "<a href='"+ utils().oldPandaHost + "/?job=*&ui=user&name=" +username.replace(/\s/g,"+") + "'>" +showtxt+ "</a>" ;  */
             txt = "<a href='"+ utils().newPandaHost + "/jobinfo?limit=5000&prodUserName=" +cleanName +dumptxt+"&jobtype=all"+hourtxt+"'>" +showtxt+ "</a>" ; 
           } catch(err) {}
        }
        return txt;  
   }

   //___________________________________________________________________________________________________
   PandaMonitorUtils.prototype.linkLfn = function (lfn,guid,scope,tooltip,showtxt) {
        /* Retutrn the link to the file's page */
        if (lfn == null) return '';
        var guidtxt = ''; if (guid != undefined) { guidtxt = '&depth=fullarchive&guid='+ guid;}
        var scopetxt = ''; if (scope != undefined) { scopetxt = '&scope='+ scope;}
        var tooltiptxt = ''; if (tooltip!= undefined) {tooltiptxt = " title='"+tooltip+ "'"; }
        if (showtxt == undefined) showtxt = lfn;
        var txt = "<a " + tooltiptxt+ " href='"+ utils().oldPandaHost + "/?overview=findfile&archive=yes&lfn=" +lfn + guidtxt+ scopetxt + "'>" +showtxt+ "</a>" ;
        return txt   
   }

   //___________________________________________________________________________________________________
   PandaMonitorUtils.prototype.linkLog = function (log,showtxt) {
        /* Return link to cite info page  */
        var params = ["site","type","level","count","tend","tstart"]; 
        var txt='';
        for (var i in params) {
            var val = log[i];
            if (val != undefined) {
               if (i != 0) {txt +='&';}
               try { val = val.replace('blnk',''); }
               catch(err) { }
               txt += params[i]+ '=' + val;
            }
        }
        var level = log[2];
        if (showtxt == undefined) { showtxt = level;  }
        var color = 'darkgreen';
        if ( level == 'WARNING' ) {color = 'darkgoldenrod';}
        else if ( level == 'ERROR' ||level == 'CRITICAL') {color = 'red';}
        txt = "<a href='logmonitor?" +txt+ "'><span style=color:" +color+ ">" +showtxt+ "</span></a>" ;
        return txt
   }
//___________________________________________________________________________________________________
   PandaMonitorUtils.prototype.linkTransformation = function(trf) {
       /* Return link to transformation script */
       var txt = '';
       if (trf != undefined && trf != '') {
          var pat = /.*\/([^\/]*)$/; 
          var mat = pat.exec(trf);
          if (mat) {
               var trfname = mat[1].split(/\s/).join('; ');
               txt = "<a href='" + trf.split(/\s/).join('+') + "'>" +trfname+"</a>";
           } else {
               txt = trf;
           }
        }
        return txt;
   }
//___________________________________________________________________________________________________
   PandaMonitorUtils.prototype.getJobType = function (trf) {
        / * Return job type from transformation  */
      var  jobtype = '';
      if ( trf != undefined && trf.indexOf('http') ==0 ) { 
        var pat = /.*\/([^\/]*)$/;
        var mat = pat.exec(trf);
        if (mat) {
            jobtype = mat[1];
            pat = /([a-zA-Z\-_0-9]+)/;
            mat = pat.exec(jobtype);
            if ( mat) {jobtype = mat[1];}
        }
      }
      return jobtype;
   }
//___________________________________________________________________________________________________
   PandaMonitorUtils.prototype.linkCloud = function (cloud, showtxt,style) {
        // Return link to cite info page 
        if (showtxt == undefined) showtxt = cloud;
        if (style == undefined) { style = '';}
        else {style = "style='" + style+ "'"; }
        var txt = "<a " +style+" href='"+ utils().oldPandaHost + "?dash=clouds#" +cloud+ "'>" +showtxt+ "</a>" ;
        return txt;
   }
//___________________________________________________________________________________________________
   PandaMonitorUtils.prototype.linkPilots = function (site, showtxt,style) {
        // Return link to cite info page 
        if (showtxt == undefined) showtxt = site;
        if (style == undefined) { style = '';}
        else {style = "style='" + style+ "'"; }
        var txt = "<a " +style+" href='"+ utils().oldPandaHost + "?tp=pilots&accepts=" +site+ "'>" +showtxt+ "</a>" ;
        return txt;
   }
//___________________________________________________________________________________________________
   PandaMonitorUtils.prototype.linkSite = function (site, showtxt,style,tooltip) {
        // Return link to cite info page
        if (showtxt == undefined) showtxt = site;
        if (style == undefined) { style = '';}
        else {style = "style='" + style+ "'"; }
        var tooltiptxt = '';  
        if ( tooltip == undefined) { tooltip="Show the PanDA site " + site+ " status";}
        tooltiptxt = " title='" +tooltip+"' ";
        var txt = "<a  " +style+tooltiptxt+ " href='"+ utils().oldPandaHost + "?mode=site&site=" +site+ "'>" +showtxt+ "</a>" ;
        return txt;
   }
//___________________________________________________________________________________________________
   PandaMonitorUtils.prototype.getDatasetForFile  = function (fname){
        /* Infer dataset name from filename  */
      var m_ds = this.p_ds.exec(fname);
      var ds = undefined;
      if (m_ds) {
         ds = {};
         ds['project'] = m_ds[1];
         ds['num'] = m_ds[2];
         ds['physics'] = m_ds[3];
         ds['stage'] = m_ds[4];
         ds['format'] = m_ds[5];
         ds['rel'] = m_ds[6];
         if (ds['format'] == 'HITS' && ds['stage'] == 'simul') {ds['stage'] = 'digit'; }
      }
      return ds;
   }
//___________________________________________________________________________________________________
   PandaMonitorUtils.prototype.linkJobDataset = function (dsname, compsite, showtxt,style,tooltip,version, vuid, site, showtxt, 
                    opt, showsub, pandaid,dashboard) {
      /* Return link to dataset info page  */
      if (dsname  == undefined)  return '';
      if (opt     == undefined)  {opt = '';}
      if (showsub == undefined)  {showsub = 0; }
      if (showtxt == undefined)  {showtxt = dsname; }
      if (site    != undefined)  {opt += '&site='    + site;    }
      if (version != undefined)  {opt += "&version=" + version; }
      if (vuid    != undefined)  {opt += "&dset="    + vuid;    }
      if (pandaid != undefined)  {opt += "&job="     + pandaid; }
      if (compsite!= undefined)  {opt += '&compsite='+ compsite;}
      var tooltiptxt = '';  
      if ( tooltip == undefined) { tooltip="Show the PanDA dataset " + dsname+ " status";}
      /* for subdatasets, trim off the _sub so the link is to the parent dataset */
      var dstxt = dsname;
      if (showsub == 0) {
         var isub =  dsname.indexOf('_sub');
         if  ( isub > 0) {
            dstxt = dsname.substr(0,isub);
         } else {
            isub = dsname.indexOf('_dis');
            if (isub > 0) {
               dstxt = dsname.substr(0,isub);
            }
         }
      }
      var txt = "<a title='"+tooltip+"' href='"+ utils().oldPandaHost+"?dataset="+ dstxt+opt+"'>"+showtxt+"</a>";
     /*
     if dashboard and dashboard==True:
        txt += " <a title='CERN Dashboard Analysis Task Monitor' href='https://dashb-atlas-task.cern.ch/templates/task-analysis/#task=%(container)s'><b>Monitor</b></a>" %{'container': dstxt }
     */
     return txt;
   }   
//___________________________________________________________________________________________________
   PandaMonitorUtils.prototype.linkDataset = function (ds, showtxt,style,tooltip) {
        // Return link to PanDA dataset info page
        if (showtxt == undefined)  {
           if  (ds.indexOf('http:') >=0 )       { showtxt= 'HTTP';}
           else if  (ds.indexOf('https:') >=0 ) { showtxt= 'HTTPS';}
           else if  (ds.indexOf('.py') >0 )     { showtxt= 'PYTHON';}
        }
        if (showtxt == undefined) {
           var dst = this.getDatasetForFile(ds);
           if (dst!=undefined) { showtxt = dst.format;}
           if (showtxt == undefined) showtxt = ds;
        }
        if (style == undefined) { style = '';}
        else {style = "style='" + style+ "'"; }
        var tooltiptxt = '';  
        if ( tooltip == undefined) { tooltip="Show the PanDA dataset " + ds+ " status";}
        tooltiptxt = " title='" +tooltip+"' ";
        var txt = "<a  " +style+tooltiptxt+ " href='"+ utils().oldPandaHost + "?mode=dset&name=" +ds+ "'>" +showtxt+ "</a>" ;
        return txt;
   }
   
//___________________________________________________________________________________________________
   PandaMonitorUtils.prototype.linkQueue = function (nickname, showtxt,style,tooltip) {
        // Return link to cite info page
        if (showtxt == undefined) showtxt = nickname;
        if (style == undefined) { style = '';}
        else {style = "style='" + style+ "'"; }
        var tooltiptxt = '';  
        if ( tooltip == undefined) { tooltip="Show the PanDA queue " + nickname+ " status";}
        tooltiptxt = " title='" +tooltip+"' ";
        var txt = "<a  " +style+tooltiptxt+ " href='"+ utils().oldPandaHost + "/server/pandamon/query?tp=queue&id=" +nickname+ "'>" +showtxt+ "</a>" ;
        return txt;
   }
//___________________________________________________________________________________________________
   PandaMonitorUtils.prototype.linkJob = function (jobid, taskID,showtxt, tooltip,newhost) {
        // Return link to job info page 
        if (showtxt == undefined) { showtxt = jobid; }
        var tasktxt = '';
        if ( taskID != undefined) { 
            if (typeof taskID ==='string' && taskID[0] =='#')  { 
               tasktxt = taskID;
            } else {
               tasktxt = '&taskID=' + taskID ; 
            }
        }
        var tooltiptxt = '';  
        if ( tooltip == undefined) { tooltip="Show the the classic PanDA page for the job #" + jobid;}
        tooltiptxt = " title='" +tooltip+"' ";
        var txt = "<a " +tooltiptxt;
        if (newhost==undefined) {
           txt += " href='"+ utils().oldPandaHost + "?job=" +jobid+tasktxt ;
        }
        txt += "'>" +showtxt+ "</a>"
        return txt;
   }
//___________________________________________________________________________________________________
   PandaMonitorUtils.prototype.linkRelease = function (release, showtxt) {
        // Return link to job info page
        txt = '';
        if ( release != undefined) {
           if (showtxt == undefined) { showtxt = release; }
           r=release.replace('Atlas-','');
           txt = "<a href='releaseinfo?release=" +r+ "'>" +showtxt+ "</a>" ;
        }
        return txt;
   }

//___________________________________________________________________________________________________
   PandaMonitorUtils.prototype.linkTName= function (tabname,tooltip,showtxt,doc,db) {
     if (showtxt == undefined) { showtxt = tabname; }
     var tabnametxt = '';  if ( tabname != undefined) { tabnametxt = '?table=' +tabname ; } else { showtxt='ALL'; }
     var tooltiptxt = '';  
     if ( tooltip == undefined) { tooltip="Show " +tabname+ " definition";}     
     tooltiptxt = " title='" +tooltip+"' ";
     var doctxt = '';
     if (doc != undefined) { 
         if  (tabname == undefined) { doctxt = '?' } else { doctxt = '&'; }
         doctxt += 'doc='+doc;
     }
     var dbtxt = ''; if (db!=undefined) {dbtxt = '&db='+db; }
     var txt = "<a href='describe" +tabnametxt+ doctxt+ dbtxt+"'" +tooltiptxt+ ">" +showtxt+ "</a>" ;
     return txt;
   }
//___________________________________________________________________________________________________
   PandaMonitorUtils.prototype.linkCName= function (colname,tooltip,showtxt,doc,db) {
     if (showtxt == undefined) { showtxt = colname; }
     var colnametxt = '';  if ( colname != undefined) { colnametxt = '?column=' +colname ; } else { showtxt='ALL'; }
     var tooltiptxt = '';  
     if ( tooltip == undefined) { tooltip="Show " +colname+ " definition";}
     tooltiptxt = " title='" +tooltip+"' ";
     var doctxt = '';
     if (doc != undefined) { 
         if  (colname == undefined) { doctxt = '?' } else { doctxt = '&'; }
         doctxt += 'doc='+doc;
     }     
     var dbtxt = ''; if (db!=undefined) {dbtxt = '&db='+db; }
     var txt = "<a href='describe" +colnametxt+ doctxt+ dbtxt+"'" +tooltiptxt+ ">" +showtxt+ "</a>" ;
     return txt;
   }
//___________________________________________________________________________________________________
   PandaMonitorUtils.prototype.linkWnlist= function (site,tooltip,showtxt) {
     if (showtxt == undefined) { showtxt = site; }
     var sitetxt = '';  if ( site != undefined) { sitetxt = '?site=' +site ; } else { showtxt='ALL'; }
     var tooltiptxt = '';  
     if ( tooltip == undefined) { tooltip="Show the status of the site " +site+ " worker nodes";}
     tooltiptxt = " title='" +tooltip+"' ";
     var txt = "<a href='http://pandamon.cern.ch/wnlist" +sitetxt+ "'" +tooltiptxt+ ">" +showtxt+ "</a>" ;
     return txt;
   }
//___________________________________________________________________________________________________
PandaMonitorUtils.prototype.linkJobs= function (cloud,type,jobStatus,hour, site, showtxt,style,modificationHost,walltime,srclabel,vo,plot,job,task,jobsetid,newHost,coreCount,forceOldMon) {
        /* Return link to job info page  */
        /* http://panda.cern.ch/server/pandamon/query?job=*&cloud=CA&type=production&jobStatus=assigned&hours=12 */
        var siteLabel = 'site'; var typeLabel = 'type';
        if (newHost != undefined) {
             siteLabel='computingSite'; 
             typeLabel = 'jobtype';
        } 
        if (showtxt == undefined) showtxt = cloud;
        if (job == undefined) { job = '*';}
        if (style == undefined) { style = '';}
        else {style = "style='" + style+ "'"; }
        var plottxt = '';       if ( plot != undefined) {plottxt = '&plot=' +plot ; }
        var votxt = '';         if ( vo != undefined) { votxt = '&vo=' +vo ; }
        var cloudtxt = '';      if ( cloud != undefined) { cloudtxt = '&cloud=' +cloud ; }
        var modificationHosttxt = '';  if ( modificationHost != undefined) { modificationHosttxt = '&modificationHost=' +modificationHost ; }
        var typetxt = '';       if ( type != undefined)  { typetxt = '&'+ typeLabel+'=' +type ; }
        var jobStatustxt = '';  if ( jobStatus != undefined) { jobStatustxt = '&jobStatus=' +jobStatus ; }
        var hourtxt = '';       if ( hour != undefined) { hourtxt = '&hours=' +hour ; }
        var sitetxt = '';       if ( site != undefined) { sitetxt = '&'+siteLabel+'=' +site ; }
        var tasktxt = '';       if ( task != undefined) { tasktxt = '&taskID=' +task ; }
        var jobsettxt = '';     if ( jobsetid != undefined) { jobsettxt = '&jobsetID=' +jobsetid ; }
        var walltimetxt = '';   if ( walltime != undefined) { walltimetxt = '&walltime=' +walltime ; }
        var prodLabeltxt = '';  if ( srclabel != undefined) { prodLabeltxt = '&prodSourceLabel=' +srclabel ; }
        var coreCounttxt = '';  if ( coreCount != undefined) {coreCounttxt = '&coreCount=' +coreCount ; }
        var txt = '';
        if ( job === '*') {
         if (forceOldMon === true){
                txt = "<a " +style+ "href='"+ utils().oldPandaHost + "?job=*" +cloudtxt+typetxt+jobStatustxt+hourtxt+sitetxt+modificationHosttxt+walltimetxt+prodLabeltxt+votxt+tasktxt+jobsettxt+plottxt+"'>" +showtxt+ "</a>" ;
         } else {
           if (newHost == undefined) {
                txt = "<a " +style+ "href='"+ utils().oldPandaHost + "?job=*" +cloudtxt+typetxt+jobStatustxt+hourtxt+sitetxt+modificationHosttxt+walltimetxt+prodLabeltxt+votxt+tasktxt+jobsettxt+plottxt+"'>" +showtxt+ "</a>" ;
            } else {
                txt = "<a " +style+ "href='"+ utils().newPandaHost + "/jobinfo?" +cloudtxt+typetxt+jobStatustxt+hourtxt+sitetxt+modificationHosttxt+walltimetxt+coreCounttxt+prodLabeltxt+votxt+tasktxt+jobsettxt+plottxt+"'>" +showtxt+ "</a>" ;
                txt = txt.replace('?&','?');
            }            
         }
                } else {
           txt = "<a " +style+ "href='"+ utils().oldPandaHost + "?job=" +job+ "'>" +showtxt+ "</a>" ;
        }        
        return txt
   }

//___________________________________________________________________________________________________
   PandaMonitorUtils.prototype.isJob = function(job,jobtype) {
      /* Check the job type [ production | 'analysis" | None ]  */
      if (jobtype==undefined) { jobtype = 'analysis'; }
      var isJb = false;
      if (job.prodSourceLabel != undefined) {
         var label = job.prodSourceLabel.toLowerCase();
         var tp = $.trim(type.toLowerCase());
         var lb = (label=='user'  || label=='panda')
         if (tp=='analysis') {
            isJb =  lb;
         } else if ( tp =='production') {
           isJb =  !lb;
         }
      }
      return isJb
   }

//___________________________________________________________________________________________________
   PandaMonitorUtils.prototype.addToFavorites = function (urlAddress,pageName) {
      if  (! this.hasAdd2Favorite) {
         alert("Sorry! Your browser doesn't support 'Add to Favorite' function."); 
      } else {
         if ( urlAddress == undefined)  { urlAddress = document.URL;   }
         if ( pageName == undefined )   { pageName   = document.title; }
          try {
            if (this.IE ) { // location.href
               window.external.AddFavorite(urlAddress,pageName) ;
            } else if(window.sidebar) { // firefox
               window.sidebar.addPanel(pageName, urlAddress, "");
            } else if(window.opera && window.print) { // opera
               var elem = document.createElement('a');
               elem.setAttribute('href',urlAddress);
               elem.setAttribute('title',pageName);
               elem.setAttribute('rel','sidebar');
               elem.click(); // this.title=document.title;     
            } 
         } catch(ex){
            alert("Sorry! Your browser doesn't support 'Add to Favorite' function."); 
         }
      }
   }
//___________________________________________________________________________________________________
   PandaMonitorUtils.prototype.renderFlotHistClient = function (name, graph, opttxt) {
      var splitGraph      = document.splitGraph;
      var maxPlots        = document.maxPlots;
      var currentPlotPage = document.currentPlotPage;
      var totalPlotPages  = document.totalPlotPages;
      var nChartColumns   = document.nChartColumns;
      var nChartRows      = maxPlots/nChartColumns;
      var data            = this.hists;
      var scaleChecked    = false;
      var yaxisGlobalTitle;
      if (location.href.indexOf("_json") != -1  && this.IE == false )  {
         this.json();
      }
      var sC    = document.getElementById('form_scaleCheckBoxID_0');
      if (sC && sC.checked) {  scaleChecked = true;   }
      
     var chkBox = document.getElementById('checkbox_RenderID_0');
      if (chkBox && chkBox.checked) {
         chkBox  = true;
      } else {
         chkBox  = false;
      }
      var thisWindowSize = this.windowSize();
      var histogram = data.histogram;
      var mode = histogram.mode;
      var un = (mode == 'time') ? 1000 : 1;
      var min  = histogram.min;
      var minDate  = min*un;
      var max      = histogram.max;
      var maxDate  = max*un;
      var step = histogram.step;
      var inputSeries = data.series;
      
      // calculate the plot sizes;
      var plotWidth = Math.ceil(0.8 * thisWindowSize[0]/nChartColumns);
      var plotHeight = Math.ceil(thisWindowSize[0]/(2*nChartColumns)) + 74;
      // restrict the plotHeight with 640 px at most
      if (nChartColumns > 1) {
         plotHeight = plotHeight > 640 ? 640:plotHeight;
       } else {
         plotHeight = plotHeight > 480  ? 480:plotHeight;
       }
      minDateObject = new Date(minDate);
      maxDateObject = new Date(maxDate);
      
      var timeTitle = (new Date(maxDate)).getFullYear();
      var durationmsecs = maxDateObject.getTime() - minDateObject.getTime();
      var durationDays = (durationmsecs/this.timeUnitSize.day).toFixed() ;
      var plotDurationTitle='';
      if (mode == 'time') {
        plotDurationTitle='<br><font size = -1>'
         if (durationDays > 3 ) {
            plotDurationTitle = durationDays + " days";
         } else if (durationDays > 2 ) {
            plotDurationTitle = durationDays + " days";
         } else {
            var durationHours = durationmsecs/this.timeUnitSize.hour;
            plotDurationTitle = durationDays + " hour";
            if  (durationHours>1) {  plotDurationTitle += "s";}
         }
         plotDurationTitle +=  " from ";
         plotDurationTitle +=  minDateObject.getFullYear()+"-"; 

         plotDurationTitle += (minDateObject.getMonth()+1) + "-" + minDateObject.getDate();
         plotDurationTitle += " to " + maxDateObject.getFullYear()+"-"+ (maxDateObject.getMonth()+1) + "-" + maxDateObject.getDate();
         plotDurationTitle += '</font>'         
      }

      $('#topPlotPageId').html('<center>Plots:' + plotDurationTitle + '</center>');
      $('#bottomPlotPageId').html('<center>Append <b>&amp;layout=c [ x row]</b> URL parameter to change the layout. For example: append <b><font=+2><it>&amp;layout=6x2</it></font></b> to get 6 columns 2 rows per Web page</center>');
      if (histogram.yaxis != undefined) yaxisGlobalTitle = histogram.yaxis;
      
      var legendSize = 0;
      var nPlots = inputSeries.length;
      var grHash = new Object;
      var grList = new Array;
      if (chkBox) {
         // Count all plots
         for (var sites in inputSeries) {
            var thisPlots = 0;
            for (var plts in inputSeries[sites]) {
                thisPlots += 1;
               for (var g in inputSeries[sites][plts]) {
                   grHash[g] = 1;
               }
            }
            if (thisPlots > legendSize) { legendSize = thisPlots; }
         }
         for (var g in grHash ) grList.push(g);  
         // grList =  grHash.keys();   
         nPlots = grList.length;
      }      
      if (nPlots>0) {
         totalPlotPages = Math.ceil(1.0*nPlots/maxPlots);
         var title= this.plotTitle(0);
         for (var i=0; i< maxPlots;++i) {                     
            var graphId = name+ "_" + i + "_div";
            var plotCell = document.getElementById(graphId);
            if (plotCell) {plotCell.innerHTML = '';}
            var elm =  $('#' + title + '_' + i + '_title');
            if (elm) elm.html('');
            if ($.support.cssFloat) {
                elm.click(
                function() {
                     var div2PlotId =  $(this).next().attr('id');
                     var divobj = document.getElementById(div2PlotId);
                     var oImg = Canvas2Image.saveAsPNG(divobj.childNodes[0], false);
                     if (!oImg) {
                          alert("Sorry, this browser is not capable of saving PNG files!");
                     }
                 });
            }
            if (plotCell && elm ) {
               plotCell.style.width  = plotWidth;
               plotCell.style.height = plotHeight; 
               var j = i + (currentPlotPage-1)*maxPlots;              
               if (j>=nPlots)  {
                  continue;
               }
               // prepre the data for one frame
               var series = [];
               var y2axisColor = null;
               var yax  = 1;
               var seriesOption = null;
               var barOffset  = 0;
               axisTitle =  '';
               ya = 0
               if (!chkBox) {
   //-------
                  var dataPlot = inputSeries[j];                  
                  for (var siteName in dataPlot) {
                     elm.html(siteName);
                     var padPlot   = dataPlot[siteName];
                     var nser = this.objLen(padPlot);
                     for (var gr in padPlot) {
                        var dataset = this.renderHistDataset(gr,padPlot,min,step,gr,un); 
                        if (dataset == undefined) continue
                        if ( nser > 1 ) { ya = ya | dataset.yaxis; }
                        else { dataset.yaxis  = 1 ;}
                        if (y2axisColor == null && dataset.yaxis == 2)   y2axisColor = dataset.color;
                        else {
                           myUnit = this.units(gr,yaxisGlobalTitle);
                           if (axisTitle.search(myUnit) == -1) {
                              axisTitle += this.units(gr,yaxisGlobalTitle) + "<br>";
                           }
                        }
                        series.push(dataset);
                     } 
                  }
                  var lineWidth = 2;
                  if (dataset.data.length > plotWidth/2) {
                     lineWidth = 1;
                     dataset.lines.fill = 0.7;
                  }
                  if (scaleChecked) {
                     seriesOption = {
                            bars :
                             {
                                  show     : (yax == 1)
                                , lineWidth: lineWidth
                                , barWidth : step*un 
                                , align : "center"
                              }
                            , stack : scaleChecked
                        };
                  } else {
                     seriesOption = {
                            bars :
                             {
                                  show     : (yax == 1)
                                , lineWidth: lineWidth
                                , barWidth : step*un 
                                , align : "center"
                              }
                        };

                  }
   //-------            
               } else {
                  barOffset = un*step/2;
                  var gr = grList[j];
                  axisTitle = this.units(gr,yaxisGlobalTitle);
                  elm.html(gr);
                  for (var siteIndx=0;siteIndx<inputSeries.length;++siteIndx)  {
                     var dataPlot = inputSeries[siteIndx];
                     for (var siteName in dataPlot) {
                        if (siteName =='None') continue;
                        if (siteName.lastIndexOf('*') != -1) continue;
                        var padPlot   = dataPlot[siteName];
                        if (padPlot) {
                           var dataset = this.renderHistDataset(gr,padPlot,min,step,siteName,un);
                           if (dataset == undefined) continue 
                           ya = ya | dataset.yaxis;
                           var intg = "000000";
                           if ( dataset.integral != undefined ) {
                              intg = dataset.integral;
                           }
                           dataset.label = siteName + ":: <b>" + intg + "</b>"; 
                           if (y2axisColor == null && dataset.yaxis == 2)   {
                              // Ignore the second axis for the combined views
                              dataset.yaxis =  1;
                              y2axisColor = dataset.color;
                           }
                           series.push(dataset);
                        }
                     }                     
                  }
                  legendSize = series.length;
                  var lineWidth = 3
                  if (series.length > 12)
                     lineWidth = 0;
                  else if (series.length > 6) 
                     lineWidth = 1;
                  else if (series.length > 3) 
                     lineWidth = 2;
                  else   
                     lineWidth = 3;
                     
                  if (scaleChecked) {
                     seriesOption = {
                            bars :
                             {
                                  show     : (yax == 1)
                                , lineWidth: lineWidth
                                , barWidth : step*un 
                                , align : "center"
                              }
                           , stack : scaleChecked
                        };
                  } else {
                     seriesOption = {
                            lines : 
                              {
                                   lineWidth :2*lineWidth + 1
                                 , fill : 0.05
                              }
                        };
                  }
               }
//-------            
               var plot = new FlotPlot;
               var timeAxisTitle = (new Date(maxDate)).getFullYear();
               var plotXTitle = $('.' + name + '_caption');
               var tickFontSize = 12;
               if ( plotHeight > 600 ) {
                   tickFontSize = 24;
                   plotXTitle.css('font-size','2em');
               } else if ( plotHeight > 400 ) {
                  tickFontSize = 20;
                  plotXTitle.css('font-size','1.6em');
               }
               var tickFactor = 0.3; // see flot.
               if ( plotWidth > 700 ) {
                  tickFactor = 0.3; // see flot.
               } else if ( plotWidth > 400 ) {
                  tickFactor = 0.22;
               }
               var plotOptions = { 
                    xaxes: [
                     {   min :  minDate+barOffset
                       , max :  maxDate-barOffset
                       , mode : mode
                       , ticks: tickFactor * Math.sqrt(plotWidth)
                       , font : { size : tickFontSize}
                     } ]
                 , yaxes: [
                     {    title :axisTitle
                         , show : true
                         , position: "left" 
                         , reserveSpace: false 
                         , tickFormatter : suffixFormatter
                         , font : { size : tickFontSize }
                     } 
                   , 
                     {   //title : "<b>" + "Rate" + "</b>" 
                          color : "blue"
                        , position: "right" 
                        , reserveSpace: false 
                     }
                   ]
                 , legend : 
                     {   show : true
                       , position: "ne"
                       , noColumns: 1    // number of colums in legend table
                       , backgroundOpacity : 0.5 
                     }  
                  , series: { }
                  , crosshair: { mode: "x" }
                  , selection: { mode: "x" }
                  , grid: { hoverable: true, autoHighlight: true }
                  };
                  if (mode == 'time') { 
                     if (ya  & 1 ) { plotOptions.grid.markings = weekendAreas; }
                     if ( maxDate - minDate <  this.timeUnitSize.year ) {
                         var mxDt = new Date(maxDate);
                         var timeAxisTitle =mxDt.getFullYear();
                         if (maxDate - minDate <  this.timeUnitSize.month) {
                           timeAxisTitle += "/" + (mxDt.getMonth()+1);
                         }
                         if (maxDate - minDate <=  this.timeUnitSize.day) {
                           timeAxisTitle += "/" + mxDt.getDate();
                         }
                         plotOptions.xaxes[0].tickFormatter = dateFormatter;
                         var capId = name+ "_" + i + "_caption";
                         $("#" + capId).html(timeAxisTitle);
                         // plotOptions.xaxes[0].title =  timeAxisTitle;
                     }
                  } else if (mode == 'name' && histogram.names != undefined ) {
                      plotOptions.xaxes[0].names = histogram.names;
                  } else if (histogram.xaxis != undefined && histogram.xaxis != '') {
                     var capId = name+ "_" + i + "_caption";
                     $("#" + capId).html(histogram.xaxis);
                  }
               var legendId = "#" + name+ "_" + i + "_legend_div";
               var qLegend =  $(legendId);
               if  (legendSize > 6) {
                  plotOptions.legend.container = qLegend;
                  if ( plotWidth > 620) {
                     plotOptions.legend.noColumns = 6;
                  } else if ( plotWidth > 540) {
                     plotOptions.legend.noColumns = 5;
                  } else if ( plotWidth > 410) {
                     plotOptions.legend.noColumns = 4;
                  } else  {
                     plotOptions.legend.noColumns = 3;
                  }
                  qLegend.show();               
               } else {
                  qLegend.hide(); 
               }
   
               var overviewOptions = { 
                    xaxis: 
                     {   mode:  mode
                       , min :  minDate+barOffset
                       , max :  maxDate-barOffset
                       , ticks: []
                       , font : { size : 14 }
                     }
                  , yaxis: { ticks: []
                             , min: 0
                             , autoscaleMargin: 0.1
                             , reserveSpace: false 
                             , font : { size : 14 }
                             }
                  , series: { lines: { show: true, lineWidth: 1 }
                            , shadowSize: 0
                     }
                  , selection: { mode: "x" }
                  };
               if (y2axisColor) {
                 plotOptions.yaxes[1].color = y2axisColor;
                 if ( series.length <= 1 ){ plotOptions.yaxes[0].show = false; }
               }
               plotOptions.series  = seriesOption;

               plot.plot = $.plot($("#"+graphId), series, plotOptions); 
               if ( plotHeight > 600 ) { 
                    $('div.tickLabels').css('font-size', '10pt'); //  plotHeight/'18');
               }
               
               if  (legendSize > 6) {
                  plot.legends = $(legendId +" .legendLabel");
                  var lcell = Math.floor(0.7*plotWidth/plotOptions.legend.noColumns);
                  plot.legends.each(function () {
                   // fix the widths so they don't jump around
                  $(this).css('width', lcell);
                 });
               } else {
                  plot.legends = $("#"+graphId +" .legendLabel");
                  plot.legends.each(function () {
                   // fix the widths so they don't jump around
                  $(this).css('width', $(this).width());
                 });
               }
               plot.cleanLegend = true;
               plot.updateLegend();
               
               plot.updateLegendTimeout = null;
               plot.latestPosition      = null;
               $("#"+graphId).data("plot" , plot);   
               $("#"+graphId).bind("mouseout",   function (event, pos, item) {
                  var plot = $(this).data("plot");
                  plot.cleanLegend = true;
                  $("#tooltip").remove();
                  updateLegends();
                });                  
               $("#"+graphId).bind("plothover",   function (event, pos, item) {
                  var plot = $(this).data("plot");
                  if (!plot.updateLegendTimeout) {
                     plot.latestPosition = pos;
                     plot.item = item;
                     plot2UpdateLegend.push(plot);
                     plot.updateLegendTimeout = setTimeout(updateLegends, 50);
                     $("#tooltip").remove();
                  }
               });
            }
         }
         document.currentPlotPage = currentPlotPage;
         document.totalPlotPages  = totalPlotPages;
                // alert('renderGoogleChart current ' + document.currentPlotPage + '; title="' + plotTitle(i) +'"');
      }
      
      if ( this.siteStatsTable() ) { 
         var showStats = document.getElementById('showStatsTableID');
         if ( showStats  &&  (showStats.innerHTML==this.showTableTag) ) {
             this.siteStatsTable().style.display = "none";
         }
      }         
   } 
//____________________________________________________________________________________________________
   PandaMonitorUtils.prototype.toggleRender = function(checkbox) {
      var id = checkbox.id;
      if ( id == 'checkbox_RenderID_0') { 
         document.getElementById('checkbox_RenderID_1').checked = checkbox.checked;          
      } else {
         document.getElementById('checkbox_RenderID_0').checked = checkbox.checked;
      }
      this.renderCharts();       
  } 

 //____________________________________________________________________________________________________
   PandaMonitorUtils.prototype.togglePlotScale = function(checkbox) {
      var id = checkbox.id;
      if ( id == 'form_scaleCheckBoxID_0') { 
         document.getElementById('form_scaleCheckBoxID_1').checked = checkbox.checked;
      } else {
         document.getElementById('form_scaleCheckBoxID_0').checked = checkbox.checked;
      }
      this.renderCharts();       
  } 
//____________________________________________________________________________________________________
   PandaMonitorUtils.prototype.setPlotTitles = function(titles) {
      this.fPlotTitles = titles;
  }
//____________________________________________________________________________________________________
   PandaMonitorUtils.prototype.plotTitle =  function(i) {
      // Return the title of the plot defined by its seq number
      return this.fPlotTitles[i];
   }
//____________________________________________________________________________________________________
   PandaMonitorUtils.prototype.createSelector =  function(selector, currentValue, maxValue) {
      if (currentValue > maxValue) return;
      var l  =  selector.length;
      if ( l < maxValue) {
         // increase if needed
         for ( var i=l; i <maxValue; ++i) {
            var o=document.createElement('option');
            var num=new Number(i+1);
            o.text = num.toString();
            if (this.IE ) {
               selector.add(o);
            } else  {
               selector.add(o,null);
            }
         }
      }         
      // find and change the selected
      var opt = selector.options;
      // alert("len=" + selector.length + ", current value:" + currentValue + ", maxvalue: " + maxValue);
      for (var i=0; i< selector.length; ++i) {
         if (opt[i].selected == "selected") {
            if ( i != currentValue-1) {
               opt[i].selected ='';
               break;    
            }
         }
      }
      opt[currentValue-1].selected="selected";            
   }
//____________________________________________________________________________________________________
   PandaMonitorUtils.prototype.showPlotControlPage = function () {
      // alert('current ' + document.currentPlotPage + '; total =' + document.totalPlotPages);
      this.renderCharts();
      for (var i=0;i<2;++i) {               
//       document.getElementById('currentPageID_'+i).innerHTML=document.currentPlotPage + ' :';
         this.createSelector( document.getElementById('currentPageID_'+i), document.currentPlotPage, document.totalPlotPages );
         document.getElementById('totalPagesID_'+i).innerHTML=document.totalPlotPages; 
      }
   }
//____________________________________________________________________________________________________
   PandaMonitorUtils.prototype.showSelectedPage = function (selector){
      var currentPlotPage = selector.options.selectedIndex+1;
      if( currentPlotPage  > 0 ) 
      {
         if ( currentPlotPage != document.currentPlotPage )
         {
            document.currentPlotPage = currentPlotPage;
            this.showPlotControlPage();  
         }
      }
   }         
//____________________________________________________________________________________________________
   PandaMonitorUtils.prototype.showNextPage = function() 
   {
      var totalPlotPages  = document.totalPlotPages;
      var currentPlotPage = document.currentPlotPage; 
      if ( currentPlotPage < totalPlotPages ) 
      {
         document.currentPlotPage = currentPlotPage+1;
         this.showPlotControlPage();
      }
   }
//____________________________________________________________________________________________________
   PandaMonitorUtils.prototype.showPreviousPage =  function () {
      var currentPlotPage = document.currentPlotPage; 
      if (currentPlotPage >  1 ) { 
         document.currentPlotPage = currentPlotPage-1;
         this.showPlotControlPage();
      }
   }
//____________________________________________________________________________________________________
   PandaMonitorUtils.prototype.creatSelector =  function (fields,id) {
      var plotDiv = document.getElementById(id);
      if (plotDiv==null) {
         plotDiv= document.createElement('div');
         plotDiv.id = id;
      }
      var selector = document.createElement('select');
      plotDiv.appendChild(selector);
      for ( var i=0; i <fields.length; ++i) {
         var o= document.createElement('option');
         o.text = fields[i];
         if (this.IE ) {
            selector.add(o);
         } else {
            selector.add(o,null);
         }
      }
      return plotDiv;
   }
//____________________________________________________________________________________________________
   PandaMonitorUtils.prototype.submit = function(tag,submit,event) {
      var host = submit.host;
      var uri;
      if  (host == undefined ) {
         uri = submit;
      } else {
          uri = submit.uri;
      }
      var pmElement = this.jqTag(tag).data("pm") ;      
      if (pmElement != undefined ) {
        if (uri.indexOf('?')< 0) { uri = "?" +  uri; }
        pmElement.Submit(uri,event,host);
      } else {
         /* use the default */
      }
   }

//____________________________________________________________________________________________________
   PandaMonitorUtils.prototype.showTableView = function(button) {
     // Show / Hide the statistic table
     statTable = this.siteStatsTable();
     if (statTable) {
        if (button.innerHTML == this.showTableTag ) {
           statTable.style.display = '';      
           button.value='Hide the table';
           button.innerHTML='Hide the table';
           button.title='Hide the statistic table';
        } else {
           statTable.style.display = 'none';      
           button.value=this.showTableTag;
           button.title='Show the statistic  table';
           button.innerHTML=this.showTableTag;
        }
     }
   }
//____________________________________________________________________________________________________
   PandaMonitorUtils.prototype.createFieldSelector =  function (fields,defaultFields,id) {
      var fieldsDiv = document.getElementById(id);
      if (fieldsDiv == null) {
         fieldsDiv = document.createElement('div');
         fieldsDiv.id = id;
      }
      var table = document.createElement('table');
         fieldsDiv.appendChild(table);
      var row = table.insertRow(0);
         var fullList     = row.insertCell(0);
             fullList.appendChild(this.creatSelector(fields,id));
         var buttons      = row.insertCell(1);
            var buttonTable  = document.createElement('table');
            buttons.appendChild(buttonTable);
            var buttonArray = ["&lt;-", "-&gt;"];
            for (var i=0; i < buttonArray.length; ++i) {
               var btton  = document.createElement('button');
               btton.value=buttonArray[i];
               t.insertRow(0).insertCell(0).appendChild(btton);            
            }
         var selectedList = row.insertCell(2);
             selectedList.appendChild(this.creatSelector(defaultFields));
      return fieldsDiv;
   }
   //___________________________________________________________________________________________________
   PandaMonitorUtils.prototype.exChangeColumn2Plot =  function (add) {
      var srcList = document.getElementById('srcColumns2PlotID');
      var selList = document.getElementById('selectedColumns2PlotID');
      var move = function(from,to,MS) {
         var indx = from.selectedIndex;
         if (MS) {
            var thing = from.options(indx);
            from.options.remove(indx);
            to.add(thing);
         } else {
            var thing = from.options[indx];
            from.options[indx] = null;
            to.add(thing,null);
         }            
      }
      if (add) move(srcList,selList,this.IE);
      else     move(selList,srcList,this.IE);
   }
   
//___________________________________________________________________________________________________
   PandaMonitorUtils.prototype.addColumn2Plot =  function () {
      this.exChangeColumn2Plot(true);
   }
//___________________________________________________________________________________________________
   PandaMonitorUtils.prototype.removeColumn2Plot =  function () {
      this.exChangeColumn2Plot(false);
   }
//___________________________________________________________________________________________________
   PandaMonitorUtils.prototype.jqTag = function(tag) {
      var t;
      // return '#' + myid.replace(/(:|\.)/g,'\\$1'); from JQuert Web 
      if (typeof tag == 'string') { t = $(tag); }
      else { t = tag; }
      return t;
   }
//___________________________________________________________________________________________________
   PandaMonitorUtils.prototype.renderAlert = function(tag,data) {
   var t = this.jqTag(tag);
   var alext = '<div class="ui-widget">\
           <div class="ui-state-error ui-corner-all" style="padding: 0 .7em;">\
           <p><span class="ui-icon ui-icon-alert" style="float: left; margin-right: .3em;"></span><span><pre>'
   alext +=  data;
   alext +=    '\n</pre></span></p></div>'
   var alert = $(alext);
   t.append(alert);
}
//___________________________________________________________________________________________________
   PandaMonitorUtils.prototype.renderJson = function(json) {
      /* Return the <span> with the syntax highlighted json object */
       /* http://stackoverflow.com/questions/4810841/json-pretty-print-using-javascript */
       /*
       pre {outline: 1px solid #ccc; padding: 5px; margin: 5px; }
.string { color: green; }
.number { color: darkorange; }
.boolean { color: blue; }
.null { color: magenta; }
.key { color: red; }

       */
      if (typeof json != 'string') {
            json = JSON.stringify(json, undefined, 2);
       }
       json = json.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
       return json.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, 
         function (match) {
            var cls = 'number';
            if (/^"/.test(match)) {
               if (/:$/.test(match)) {
                  cls = 'key';
               } else {
                  cls = 'string';
               }
            } else if (/true|false/.test(match)) {
               cls = 'boolean';
            } else if (/null/.test(match)) {
               cls = 'null';
            }
            return '<span class="' + cls + '">' + match + '</span>';
         }
       );
   }
//___________________________________________________________________________________________________
   PandaMonitorUtils.prototype.renderHighlight = function(tag,data) {
   var t = this.jqTag(tag);
   var alext = '<div class="ui-widget ui-state-highlight ui-corner-all style="padding: 0 .3em;">\
           <p> <table><tr><td><span class="ui-icon ui-icon-info ui-state-highlight" style="margin-right: .1em;"></span></td><td>'
   alext +=  data;
   alext +=    '</td></tr></table></p></div>'
   var alert = $(alext);
   t.append(alert);
}
//___________________________________________________________________________________________________
   PandaMonitorUtils.prototype.renderText = function(tag,data) {
   var t = utils().jqTag(tag);
   var alext = '<div class="ui-widget">\
           <div class="ui-widget-content ui-corner-all" style="padding: 0 .7em;">\
           <p><span class="ui-icon ui-icon-script" style="float: left; margin-right: .3em;"></span><span><pre>'
   alext +=  data;
   alext +=    '\n</pre></span></p></div>'
   var alert = $(alext);
   t.append(alert);
}
//___________________________________________________________________________________________________
PandaMonitorUtils.prototype.pageSectionButton  = function(text,id) {
    /* JQuery UI '.ui-widget-header' button section separator */
    txt = "<p><table class='ui-corner-all ui-widget ui-widget-header' width='100%'><thead><tr><th align=left>"
    txt += "<button class='ui-button ui-widget ui-state-default ui-corner-all ui-button-text-only' "
    if (id !=undefined) {  txt +=  " id='" +id+ "'"; }
    txt += " width=100%>" +text+ "</button>";
    txt += "</th></tr></thead></table><p>";
    return $(txt);
}

//___________________________________________________________________________________________________
PandaMonitorUtils.prototype.pageSection  = function(text) {
    /* JQuery UI '.ui-widget-header' page section separator */
    txt = $("<p><table class='ui-corner-all ui-widget ui-widget-header' width='100%'><thead><tr><th align=left>" +text+ "</th></tr></thead></table><p>");
    return txt;
}
//___________________________________________________________________________________________________
   PandaMonitorUtils.prototype.renderHtml = function(tag,html) {
   var t = utils().jqTag(tag);
   var alext = '<div class="ui-widget"><div class="ui-widget-content ui-corner-all" style="padding: 0.5em;"><div>';
   alext +=  html;
   alext +=    '</div></div></div>'
   var alert = $(alext);
   t.append(alert);
}

//___________________________________________________________________________________________________
   PandaMonitorUtils.prototype.renderScript = function(tag,html) {
   var t = this.jqTag(tag);
   var alext = '<div class="ui-widget">\
           <div class="ui-widget-content ui-corner-all" style="padding: 0 .7em;">\
           <span class="ui-icon ui-icon-script" style="float: left; margin-right: .3em;"></span><div>'
   alext +=  html;
   alext +=    '</div></div>'
   var alert = $(alext);
   t.append(alert);
}
//___________________________________________________________________________________________________
   PandaMonitorUtils.prototype.len =  function (obj) {
   /* Calculate the number of the properties within the object */
      var count;
      if ( obj != undefined) {  count = obj.length;  }
      if ( count == undefined) {
         count = 0;
         try {
            Number(obj);
            count = 1;
         } catch (e) {
             for (var i in obj) {++count;}
         }
      }
      return count;
   }
//___________________________________________________________________________________________________
   PandaMonitorUtils.prototype.openTableHeader =  function (labels) {
      var dtHeader = new Array(labels.length);
      for (var l in labels) { dtHeader[l] = {"sTitle": "<small>"+labels[l]+"</small>" }; }
      return dtHeader;
   }
//___________________________________________________________________________________________________
   PandaMonitorUtils.prototype.name2Indx =  function (array,name) {
      var indx;
      if (name == undefined) {
         indx = {};
      }
      for ( var i in array) {
         if (name != undefined) {
            if ((array[i]+'').toLowerCase() == (name+'').toLowerCase())  {
               indx = parseInt(i);
               break;
            }
         } else {
            indx[array[i]] = parseInt(i);
         }
      }
      return indx;
   }
//___________________________________________________________________________________________________
   PandaMonitorUtils.prototype.renderDebugInfo = function(tag,main) {
      var t = utils().jqTag(tag);
      var timestamp = new Date(main._system.timing.timestamp*1000);
      var params  = main.params;
      var data = main.data;
      var header = data.header;
      var rows = data.rows;
      var d = $('<div></div>');
      var tdiv = $("<div></div>");
      var total = utils().len(rows);
      var hdclass = ' ui-widget-header ui-widget ';
      if ( (total == undefined) || (total == 0)) {
          hdclass += ' ui-corner-top ';
      } else {
          hdclass += ' ui-corner-all ';
      }
      tdiv.append("<div class='" +hdclass+ "'>Debug info at " +timestamp /* .format("yyyy-mm-dd HH:MM:ss")*/+' UTC</div>');
      var refresh =  params.refresh;
      if (refresh != undefined && refresh >0 ) { tdiv.append('autorefresh in ' + (refresh/60).toFixed(2)+ 'min'); }
      var table;
      var tableid;
      if ( (total == undefined) || (total == 0)) {
         table = $("<div class='ui-state-highlight u-widget ui-widget-content ui-corner-bottom'></div>");
         table.html(' There is no debug information.');
      } else if ( total == 1) {
         table = $("<div class='ui-widget ui-corner-all'></div>")
         head = $("<div class='ui-widget-header ui-widget-content ui-corner-top'></div>");
         head.html(' Job ' +utils().linkJob(rows[0][0]));
         data =  $("<div class='ui-widget-content ui-corner-bottom'></div>");
         data.html('<pre>' +rows[0][1]+ '</pre>');
         table.append(head);
         table.append(data);
      } else {
         tableid = 'debugInfo_'+rows[0][0]+ 'Id';
         table = $('<table id="' +tableid+ '" class="display"></table>'); 
      }
      tdiv.append(table);
      d.append(tdiv);
      t.empty();
      t.append(d);  
      if ( total > 1) {
        utils().datatable(tableid,tbFunc(), 25 );
      }
      /* __________________________________________*/
      function tbFunc() {
         var options = {};
         if (total > 64) {
              var displayTotal =  total;
              if (total>300) displayTotal = 300; 
              var half = displayTotal/2;
              options= { "iDisplayLength": displayTotal
                       , "aLengthMenu": [ [displayTotal, -1,half], [displayTotal, "ALL" ,half] ]
                       };
         } else {
             options={ "bPaginate": false,"bLengthChange": false, "bInfo": false };
         }
        options["aoColumnDefs"] = [ 
                              { "sWidth": "5%", "aTargets":  [ 0 ] } 
                             ,{ "sWidth": "95%", "aTargets": [ 1 ] }
                          ];
         var dtHeader = utils().openTableHeader(header);
         var dtRows = rows;
         options["aaData"]    = dtRows;
         options["aoColumns"] = dtHeader;
         options["fnRowCallback"]= function( nRow, aData, iDisplayIndex, iDisplayIndexFull ) 
            {
               $('td:eq(0)', nRow).html(utils().linkJob(aData[0])); 
               $('td:eq(1)', nRow).html('<pre>' +aData[1]+ '</pre>');
               return nRow;
            };
         return options;
      }
      /* --------- continue ---------- */
      if (refresh != undefined && refresh >0 ) {
         var renderDebugInfo = function(t,m) { utils().renderDebugInfo(t,m); }
         utils().ajax(refresh,tag,'debuginfo',params,main._host,renderDebugInfo,undefined,true);
      }
   };



/* _____________________________________________________________________________*/
   PandaMonitorUtils.prototype.ajax = function (refresh,tag,query,params,host,success,failure,delay) {
      /*  execute the function 'success" with the dynimically loaded  ajax data from 
                 http:<host>/<query>?<params
          the  execution can delyed  if "delay==true 
          and it can be refreshing  via 'refresh' security
          The success is to render its content with the "container" defined by "tag" parameter
      */          
      if ( delay == undefined || !delay ) {
        this.download(tag,query,params,host,success,failure);
      }
      if  ( refresh && refresh > 0 ) {
         var download = function (t,q,p,h,s,f) { utils().download(t,q,p,h,s,f); };
         setTimeout( function() { download(tag,query,params,host,success,failure);}, refresh*1000);
      }
   }

/* _____________________________________________________________________________*/
   PandaMonitorUtils.prototype.download = function (tag,query,params,host,success,failure) {
         var url =  '';
         if (host != undefined) { url='http://'+host ; protocol = 'jsonp'; }
         else {protocol = 'json'; }
         if (query !=  undefined) url+= "/" +query;
         if (params != undefined) url+= "?" + $.param(params);
         var options = {
             type: "GET"
            , url:url
            , dataType: protocol
            , cache: false
            , success:  function(msg) { ajsuccess(msg); }
         };
         $.ajax(options);
         /* __________________________________________________________________ */
         function ajsuccess(msg) {
            var response = msg.pm;
            for (var i in response) {
               var mn = response[i].json;
               if  ( mn == undefined ) { 
                  /* console.log("failure: " + i+ " response: " +JSON.stringify(response[i])); */
                  if ( failure!= undefined) { failure(msg);}
                  continue;
               }
               mn["_host"] = host;
               success(tag,mn);
               break;
            }
         }
      }

//___________________________________________________________________________________________________
   PandaMonitorUtils.prototype.json2Date =  function (date) {
     /* convert the string 2012-04-17 17:00:05 to JS Date */
      var jdate = date.replace(" ","T");
      return new Date(jdate);    
   }
//___________________________________________________________________________________________________
   PandaMonitorUtils.prototype.rebuidPlots =  function () {
      // add fields from selectedColumns2PlotID
      var selectedColumns = document.getElementById('selectedColumns2PlotID');
      var form = document.getElementById('form_2DefineColumns2PlotID');
      if (selectedColumns != null &&  selectedColumns.length >0) {
         var fields = '';
         for (var i=0; i<selectedColumns.length; ++i) {
            if ( i != 0)  {
               fields += ",";
            }
            if (this.IE) {
               fields += selectedColumns.options(i).text;
            } else { 
               fields += selectedColumns.options[i].text;
            }
         }
         var binField = document.getElementById('input_binfactorID');
         // alert(" Binfactor =" + binField);
         var binfactor=0;
         if (binField != null) {
            binfactor = binField.value;
            // alert(" Binfactor =" + binfactor);
         }
         var sel    = document.getElementById('select_timebinunitID');
         // alert(" Binfactor =" + sel);
         var timebinunit;
         if (sel != null ) {
            if (this.IE) {
               timebinunit =  sel.options(sel.selectedIndex).text;
            } else {
               timebinunit =  sel.options[sel.selectedIndex].text;
            }
         }
         var count =0;
         for (var i =0; (i<form.length) && (count < 3); ++i)  {
            var el = form.elements[i];
            if (el.id == 'inputSelectedFieldsID') {
               el.value = fields;
                // alert ( "1. " + el.value  + " " + count + " f=" + form.length);
               ++count;
            }  else if ( binField != null && el.name == 'binfactor') {
               el.value = binfactor;
               // alert ( "2. " + el.value  + " " + count + " f=" + form.length);
               ++count;
            }  else if (timebinunit != null && el.name == 'timebinunit') {
               el.value = timebinunit;
               // alert ( "3. " + el.value  + " " + count + " f=" + form.length );
               ++count;
            }
         }
         form.submit();
      }
   }
//___________________________________________________________________________________________________
   PandaMonitorUtils.prototype.renderTable =  function (tag,header,rows,doc,db) {
     /* quick way to draw the Db table with the header generated by pmTaskBuffer */
      var t = this.jqTag(tag);
      var total = utils().len(rows);
      if ( total == undefined || total <=0 ) {
         utils().renderHighlight(t,"There is no data to show");
         return;
      }
      if (total > 64) {
           var displayTotal =  total;
           if (total>300) displayTotal = 300; 
           var half = parseInt(displayTotal/2)+1;
           options= { "iDisplayLength": displayTotal
                    , "aLengthMenu": [ [displayTotal, -1,half], [displayTotal, "ALL" ,half] ]
                    , "aoColumnDefs": [ { "sWidth": "5em", "aTargets": [ 0 ] } ]
                    };
      } else {
          options={ "bPaginate": false,"bLengthChange": false, "bInfo": false };
      }
      var lpars = $.deparam.querystring();
      tpars = {};
      var tApi = ['hours', 'days', 'tstart', 'tend'];
      for (var titem in tApi )  {
          var tt = tApi[titem];
          tpars[tt] = lpars[tt];
      }
      var dtHeader = new Array(header.length);
      var pIndx = -1;
      var timeIndx = -1;
      var nIndx = -1;
      var kIndx = -1;
      var fIndx = -1;
      var sIndx = -1;
      var scpIndx = -1;
      var dIndx = -1;
      var tIndx = -1;
      var cIndx = -1;
      var rIndx = -1;
      var uIndx = -1;
      var lIndx = -1;
      var jIndx = -1;
      var gIndx = -1
      var clouldIndx = -1;
      var transIndx = -1;
      var setIndx = -1;
      var reqIndx = -1;
      var tskpIndx = -1;
      var tasknmIndx = -1;
      var nFilesIndx = [];
      for (var h in header)  {
         var hh = header[h];
         if ( timeIndx  < 0 && (hh.toLowerCase() =='modificationtime' || hh.toLowerCase() ==='creationtime'  || hh.toLowerCase() === 'creationdate' )  )  { timeIndx = h;}
         if ( clouldIndx  < 0 && hh.toLowerCase() =='cloud' )  { clouldIndx = h;}
         if ( transIndx  < 0 && hh.toLowerCase() =='transpath' )  { transIndx = h;}
         if ( kIndx  < 0 && hh.toLowerCase() =='nickname' )  { kIndx = h;}
         if ( nIndx  < 0 && hh.toLowerCase() =='siteid' )    { nIndx = h;}
         if ( pIndx  < 0 && hh.toLowerCase()== 'pandaid')    { pIndx = h;} 
         if ( fIndx  < 0 && hh.toLowerCase()== 'guid')       { gIndx = h;} 
         if ( scpIndx  < 0 && hh.toLowerCase()== 'scope')       { scpIndx = h;} 
         if ( tIndx  < 0 && hh.toLowerCase()== 'table_name') { tIndx = h;} 
         if ( cIndx  < 0 && hh.toLowerCase()== 'column_name'){ cIndx = h;} 
         if ( lIndx  < 0 && hh.toLowerCase()== 'lfn')        { lIndx = h;} 
         if ( sIndx  < 0 && hh.toLowerCase().indexOf('site')>=0)  { sIndx = h;}
         if ( dIndx  < 0 && hh.toLowerCase().indexOf('dataset') >=0) { dIndx = h;} 
         if ( setIndx  < 0 && hh.toLowerCase().indexOf('jobset') >=0) { setIndx = h;} 
         if ( tasknmIndx  < 0 && hh.toLowerCase().indexOf('taskname') >=0) { tasknmIndx = h;} 
         if ( tskpIndx  < 0 && hh.toLowerCase().indexOf('task_param') >=0) { tskpIndx = h;} 
         if ( reqIndx  < 0 && hh.toLowerCase().indexOf('reqid') >=0) { reqIndx = h;} 
         if ( rIndx  < 0 && (  hh.toLowerCase().indexOf('release')>=0 ||  hh.toLowerCase().indexOf('transuses')>=0 ) )  { rIndx = h;} 
         if ( uIndx  < 0 && hh.toLowerCase().indexOf('user')>=0)     { uIndx = h;} 
         if ( jIndx  < 0 && hh.toLowerCase()== 'jeditaskid') { jIndx = h;} 
         if ( hh.toLowerCase().indexOf('nfiles') === 0) { nFilesIndx.push(h);} 
         dtHeader[h]= {"sTitle":hh };
      }   
      if (kIndx >=0 && nIndx <0) { kIndx=-1; }      
      dtRows = rows;
      // console.log("renderTable="+this.stringify(dtHeader));
      // console.log("renderTable:rows="+this.stringify(rows));
      options["aaData"]    = dtRows;
      options["aoColumns"] = dtHeader;
      options["fnRowCallback"]= function( nRow, aData, iDisplayIndex, iDisplayIndexFull ) 
         {
            /* hyperlink for PandaId */
            if ( pIndx>=0 ) {
               var cell = aData[pIndx];
               $('td:eq(' +pIndx+ ')', nRow).html("<b>" +utils().linkJob(cell)+"</b>" );
            }
            if ( setIndx>=0 ) {
               var cell = aData[setIndx];
               $('td:eq(' +setIndx+ ')', nRow).html("<b>" +views().linkJobInfoPars(cell, {jobsetID:cell},undefined,"Show the list of the jobs from " +cell+ " jobset ")+"</b>" );
            }
            if ( tasknmIndx>=0 ) {
               var cell = aData[tasknmIndx];
               $('td:eq(' +tasknmIndx+ ')', nRow).html("<b>" +views().linkJobInfoPars(cell, {jobName:cell},undefined,"Show the list of the jobs from " +cell+ " jobset ")+"</b>" );
            }
            if ( reqIndx>=0 ) {
               var cell = aData[reqIndx];
               if ( cell === undefined || cell==null || cell == 'null' || cell==0 || cell=='0' )  {
                  cell = ' ';
                  $('td:eq(' +reqIndx+ ')', nRow).html(cell);
               } else {
                 var href = "<a title='Future DEFT Table. Under construction. ' href='http://pandamon.cern.ch/deft/dftask?TASK_ID="+ cell+ "'>"+cell+"; </a><br>";
                 /* var href = "<a title='Future DEFT Table. Under construction. ' href='http://pandamon.cern.ch/deft/dftask?'>DEFT="+cell+"; </a><br>";*/
                  $('td:eq(' +reqIndx+ ')', nRow).addClass("right").html("<b>" +href+"</b>" );
               }
            }
            if ( tskpIndx>=0 ) {
               var cell = aData[tskpIndx];
               if ( cell === undefined || cell==null || cell == 'null' || cell==0 || cell=='0' )  {
                  cell = ' ';
                  $('td:eq(' +tskpIndx+ ')', nRow).html(cell);
               } else {
                 /*  var href = "<a title='Future DEFT Table. Under construction. ' href='http://pandamon.cern.ch/deft/dftask?taskID="+ cell+ "'>DEFT="+cell+"; </a><br>"; */
                 /* cell = JSON.stringify(cell,main,undefined,2); */
                  $('td:eq(' +tskpIndx+ ')', nRow).html("<textarea rows='2' cols='50' readonly>"+cell+"</textarea>");
               }
            }
            /* hyperlink for SiteId */
            if ( nIndx>=0 ) {
               var cell = aData[nIndx];
               $('td:eq(' +nIndx+ ')', nRow).html("<b>" +utils().linkWnlist(cell)+"</b>" );
            }
            if ( kIndx>=0 ) {
               var cell = aData[kIndx];
               $('td:eq(' +kIndx+ ')', nRow).html("<b>" +utils().linkQueue(cell)+"</b>" );
            }
            if ( sIndx>=0 ) {
               var cell = aData[sIndx];
               $('td:eq(' +sIndx+ ')', nRow).html("<b>" +utils().linkSite(cell)+"</b>" );
            }
            if ( tIndx>=0 ) {
               var cell = aData[tIndx];
               $('td:eq(' +tIndx+ ')', nRow).html("<b>" +utils().linkTName(cell,undefined,undefined,doc,db)+"</b>" );
            }
            if ( cIndx>=0 ) {
               var cell = aData[cIndx];
               $('td:eq(' +cIndx+ ')', nRow).html("<b>" +utils().linkCName(cell,undefined,undefined,doc,db)+"</b>" );
            }
            if ( dIndx>=0 ) {
               var cell = aData[dIndx];
               if (typeof cell ==='string') {
                   $('td:eq(' +dIndx+ ')', nRow).html("<b>" +utils().linkDataset(cell)+"</b>" );
               }
            }
            if ( rIndx>=0 ) {
               var cell = aData[rIndx];
               $('td:eq(' +rIndx+ ')', nRow).html("<b>" +utils().linkRelease(cell)+"</b>" );
            }
            if ( uIndx>=0 ) {
               var cell = aData[uIndx];
               $('td:eq(' +uIndx+ ')', nRow).html("<b>" +utils().linkUser(cell)+"</b>" );
            }
            if ( lIndx>=0 ) {
               var cell = aData[lIndx];
               var guid=(gIndx >=0)? aData[gIndx]:undefined;
               var scope=(scpIndx >=0)? aData[scpIndx]:undefined;
               $('td:eq(' +lIndx+ ')', nRow).html("<b>" +utils().linkLfn(cell,guid,scope)+"</b>" );
            }
            if ( jIndx>=0 ) {
               var cell = aData[jIndx];
               var td = $('td:eq(' +jIndx+ ')', nRow);td.empty();
               td.append("<div class='ui-icon ui-icon-transferthick-e-w' style='display:inline;cursor:pointer;verticalAlign:center;'>"+ views().linkJobInfoPars('&nbsp;&nbsp;&nbsp;&nbsp; ',$.extend({},{JediTaskID:cell},tpars),undefined,"Show the PanDA jobs for the Jedi task #" + cell )+"</div>" );
               td.append("<b>" + views().linkJediInfo(cell,{task:cell},cell,"Show the Jedi task parameters") +"</b>");
               td.append("<div class='ui-icon ui-icon-lightbulb' style='display:inline;cursor:pointer;verticalAlign:center;'>"
                          + views().linkDefTaskListPars( '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ', {taskID:cell},"Click to see "+ cell+" DEFT task status")
                          + "</div>")
            }

            if ( transIndx>=0 ) {
               var cell = aData[transIndx];
               $('td:eq(' +transIndx+ ')', nRow).html("<b>" + utils().linkTransformation(cell)+"</b>" );
            }
            if ( timeIndx>=0 ) {
               var cell = aData[timeIndx];
               var tm = parseInt(cell);
               try {
                 if (tm != NaN) { cell = new Date(cell*1000).format("yyyy-mm-dd HH:MM"); } 
               } catch (err) {}
               $('td:eq(' +timeIndx+ ')', nRow).addClass('pmDate').html(cell);
            }
            if ( nFilesIndx.length>0 ) {
                for (var nf in nFilesIndx) {
                  var nfi = nFilesIndx[nf];
                  $('td:eq(' +nfi+ ')', nRow).addClass('right');
                }
            }
            return nRow;
         };
             
      var table = $('<table cellpadding="0" cellspacing="0" border="0" class="display" width=100%></table>');
      t.append(table);
      return this.datatable(table.uid(),options, 25 );
   }
//___________________________________________________________________________________________________
   PandaMonitorUtils.prototype.showImage =  function (gangilahost, path,analysis ) {
     var img = $('#gangilaplotId'); var site = $('#siteId').val(); var  time = $('#timeId').val(); var task = $('#taskId').val();
     var size = 'medium';
     if (task == 'summary') {
        path = "summary/day-summary.php?";
        img.attr('src',gangilahost + path + 'SIZE=' +size);
     } else if (path == 'analy') { 
        var checked = $('#largeCheckId').attr('checked');
        if (checked) { size = "large"; }
        else { size = "medium"; }
        var loc = gangilahost + path + '/'  +analysis+ '-summary.php?SIZE=' +size;
        if (checked) { 
           document.location=loc;
        } else {
            img.attr('src',loc);
        }
     } else { 
        img.attr('src',gangilahost + path + 'SIZE=' +size+ '&TIME=' +time+ '&TASK=' +task+ '&SITE=' +site);
     }
   }

//___________________________________________________________________________________________________
   PandaMonitorUtils.prototype.openAccordion = function(id){
      var accord =  $('<div class="ui-accordion ui-widget" title= "Select the item you need and click to expand">');
      accord.attr("id",id);
      return accord;
   }
   //___________________________________________________________________________________________________
   PandaMonitorUtils.prototype.activateAccordion = function(index,id) {
      if (id==undefined ) { id = '#pandaLeftMenuId' ;}
      var selector = $(id);
      // var active = selector.accordion('option', 'active');
      // if (active == index) { selector.accordion( "activate" , index+1 ); }
      selector.accordion( "activate" , index );

        //.focus( delay [, callback ] )
        // effect 
   }
//___________________________________________________________________________________________________
   PandaMonitorUtils.prototype.addAccordion = function(accord,header,body,extra,tag,button) {
      /* Create JQuery UI accordion entry 
          button should be the dict {"href": url, "html", body, "title" : title } 
      */
      var button = '';
      if (tag == undefined) { tag = 'h3';}
      if (extra == undefined) { extra = '';}
      if (button == undefined) { button = '';}
      if ( button != '' ) {
         var title = button['title'] ?  button['title'] : "Click me";
         button = $("<span>&nbsp;&nbsp;&nbsp;" +
            + "<span style=\"text-decoration:underline; color:blue; cursor:pointer;\" title=\""+title
            + " onclick=\"location.href='" +button['href']+"'>"
            + button['html']+ "</span></span>");
      }
     // var html = $("<div></div>");
      var tg = $("<"+tag+" class='ui-accordion-header'></" +tag+ ">");
      var tit =$("<a></a>");
      tit.append("&nbsp;"+header); tit.append(button);
      tg.append(tit);
      var cont = $('<div class="ui-accordion-content ui-widget-content" '+extra+ "></div>");
      cont.append(body);
      accord.append(tg);
      accord.append(cont);
      // accord.append(html);          
      return accord;
   }
//___________________________________________________________________________________________________
   PandaMonitorUtils.prototype.login =  function () {
     /*Secure login via CERN SSO  */
      window.location = 'https://pandamon.cern.ch/login?'+window.location;
   }
//___________________________________________________________________________________________________
   PandaMonitorUtils.prototype.contactUs =  function (pandaid, taskid,error,host,timestamp,jobusr) {
      if (error == undefined) { error='' }

      function showmail(tag,data) {
         var r = $("<div></div>");
         var opt =  {  
                    resizable:false 
                  , buttons: {} 
                  , overlay: { backgroundColor: "#000", opacity: 0.5 }
                  , close:  function() { r.dialog("destroy");  }
                 };
         var user    = data.username;
         var mail    = data.mail;
         var msg     =  data.message;
         var toaddrs =  data.toaddrs;
         var error = 10;
         if (user != undefined)  {
             if (mail != undefined) {
                 error = 0;
             } else {
                 error=20;
             }
         } 
         if (error == 0) {
            opt["title"] = " Your 'Help Request' has been processed";
         } else {
            opt["title"] = "'Help Request' can not be propcessed";
        }
         usr = (user == undefined) ? "Unknown User" : user;
         main = {'pandaid' : pandaid }
         var confirmation = "Dear " + usr+ "!";          
         confirmation += "\nThank you for using PanDA 'Help Request' facility.";
         if (error==0) {
             confirmation +="\nYour message has been sent to &lt;"+toaddrs+"&gt;"
         } else { 
             confirmation +="\nUnfortunately your message can not be sent out.";
             if (error==10) { confirmation += " due lack of your account username"; }
             else if ( error == 20) { confirmation +=" due lack of your  e-mail address recorded"; }
         }
/*          r.html("<textarea cols=44 rows=3>"+confirmation +"</textarea><hr><pre>\n"+ JSON.stringify(data,undefined,2)+"\n</pre>"); */
         r.html("<textarea cols=44 rows=3>"+confirmation +"</textarea><hr>");
         r.dialog(opt);
      }


      var contactClass = 'contactPar';
      var size = 48;
      var maxlength = 4000;
      var fields = {  Summary: 'Provide a descriptive summary of the issue if any.'
                    , Regression: 'Describe circumstances where the problem occurs or does not occur, such as software versions or specific sites if any'
                    , Notes :  'Under Construction yet ! Provide additional information if any.         '};
      var dlg = (error==undefined) ? "" : "<center><b>"+error+"</b></center><p>" ;
      for (var f in fields)  {
         var tit = fields[f] + " (" +maxlength+ " characters at most)";
         dlg += f + ": <textarea class=" +contactClass+" type='text' title='"+tit+"' name=" +f+ " placeholder='" + tit+  "' cols="+size+" rows=2 required maxlength="+maxlength +"/><br>";
      }
      var pid = pandaid; 
      if (taskid != undefined && taskid != '') { pid += ',' + taskid; }
      if (jobusr != undefined && jobusr != '') { pid += ',' + jobusr; }
      var lpars = {pandaid:pid, message:undefined, errorcode:error, host:host,timestamp:timestamp};
      var r = $("<div style='padding:4px;'></div>");
      r.append(dlg);
      var opt =  {  resizable:false 
                  , buttons: {}
                  , width : 350 
                  , overlay: { backgroundColor: "#000", opacity: 0.5 }
                  , close:  function() { r.dialog("destroy");  }
                 };
      function sendmail () {
                   var msg = '';
                  $('.'+contactClass).each(function() { 
                      var v = $(this).attr('value');
                      var nm = $(this).attr('name');
                      if (fields[nm] != v && v != "" ) {
                          msg += "\r\n" + nm + ': ' + v +  "\r\n"; 
                      }
                   });
                  lpars['message'] = "\r\n" + msg; 
                  r.dialog("close");
                  var aj = new AjaxRender();
                  aj.download("float",showmail, "system/contactus",lpars,"https://pandamon.cern.ch"); 
              };
      opt["title"] = " Request Help with " +pid+ " Job Error ";
      opt['buttons']["Send"]  = function() { lpars['test']=undefined; sendmail(); };
      opt['buttons']["Test"]  = function() { lpars['test']='test';    sendmail(); };
      opt['buttons']["Cancel"]  =  function () {  r.dialog("close");  };
      r.dialog(opt);
   }

//___________________________________________________________________________________________________
   PandaMonitorUtils.prototype.zip = function(header,data) {
      var dict = {};
      for (var h in header ) {
         dict[header[h]] = data[h];
      }
      return dict;
   }

//___________________________________________________________________________________________________
   PandaMonitorUtils.prototype.version =  function (query) {
      var u = '';
      var pm = $('body').data('Pm');
      if (pm!=undefined && pm._version.version != undefined) { u = '/~'+pm._version.version; }
      if ( query != undefined ) {
          u+="/"+query;
      }
      return u;
   }

//___________________________________________________________________________________________________
   PandaMonitorUtils.prototype.getAddressInfo =  function () {
       var hostname = undefined;
       var address = undefined;

      try {
         var sock = new java.net.Socket();
         sock.bind(new java.net.InetSocketAddress('0.0.0.0', 0));
         sock.connect(new java.net.InetSocketAddress(document.domain, (!document.location.port)?80:document.location.port));
         hostname = sock.getLocalAddress().getHostName();
         address = sock.getLocalAddress().getHostAddress(); 
       } catch (e) {}

       return {hostname: hostname, address: address};
   }
