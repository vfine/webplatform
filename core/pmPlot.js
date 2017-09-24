/*
 $Id: pmPlot.js 18256 2014-02-08 20:57:08Z fine $
 Author: Valeri Fine (fine@bnl.gov)
 2012-05-31. Upton, NY
 */
/*_________________________________________________________________________________________________*/
function pmPlot(tag) {
   this.plot = null;
   this.updateLegendTimeout = null;
   this.latestPosition = null;
   this.dataset = null;
   this.cleanLegend = false;
   this.tooltip = null;
   this.logcheck = null;
   this.plot2UpdateLegend = [];
   this.tag =  utils().jqTag(tag);
   this.graphTag = undefined;
   this.style = null;
   this.lastProto = undefined;
   this.refTableId = "#sitetable";
   this.refTable = undefined;
   this.refTableData = undefined;
   this.refTableDataIndx = 0;
   this.crosshair = { mode: 'x' };
}
 /*_________________________________________________________________________________________________*/
   pmPlot.prototype.resetRefTable = function(refTable, refTableData, index) {
      this.refTableId    = refTable;
      this.refTableData  = refTableData;
      if (index && parseInt(index) >=0 ) {
         this.refTableDataIndx = parseInt(index);
      }
   }
   /*_________________________________________________________________________________________________*/
   pmPlot.prototype.resetProto = function(newproto) {
      var proto = this.lastProto;
      this.lastProto = newproto ? newproto : undefined;
      return proto;
   }
   /*_________________________________________________________________________________________________*/
   pmPlot.prototype.h1proto =  function (reset) {
   
   var proto = ( reset &&  this.lastProto && reset == true ) ? this.lastProto :
     {   
      attr: {  style: 
                      {
                         width   : 1
                       , pattern : 1
                      }
              , options: 'H'
              , name  :  ""
              , xaxis: {style: 
                                {
                                   division : 510
                                 , color    : "rgba(0,0,0,0.8)"
                                }
                        , name  : 'X'
                        , min   :  undefined
                        , max   :  undefined
                        , color : "rgba(0,0,0,0.8)"
                        , title : "<msub><mi>X</mi><mi>axis</mi></msub>"
                        , width : undefined /* It has to be calculated max-min/legth
                        , strip : true /* remove the leading / trailing zero values from the plots */
                        , labels: undefined
                        , logscale: undefined
                       }
              , title: "Plot Title"
              , yaxis:  { style: {
                                    division      : 510
                                 ,  color       : "rgba(0,0,0,0.8)",
                                 }
                         , name  :'Y'
                         , min   : 0
                         , max   : 1
                         , color : "rgba(0,0,0,0.8)"
                         , title : "<msub><mi>Y</mi><mi>axis</mi></msub>"
                         , width : 1.0
                         , labels: undefined
                         , logscale: undefined
                        }
               , dimension: 1
            }
       , data : {
              property : {  underflow: undefined
                          , overflow : undefined
                          , integral : undefined
                          , Total    : undefined
                          , rms      : undefined
                          , mean     : undefined
                          , xbound   : undefined
                         }
            , bins : []
         }
     };
      var style = proto.attr.style;
      style['marker-color']     = "rgba(0,0,0,0.8)";
      style["background-style"] = 1001;
      style["marker-pattern"]   = 21;
      style["background-color"] = "rgba(191,130,119,0.8)";
      style["marker-size"]      = 0.7;

      style = proto.attr.xaxis.style; 
      style["label-size"  ] = 0.035;
      style["label-font"  ] = 42;
      style["title-offset"] = 1.0;
      style["title-color" ] = "rgba(0,0,0,0.8)";
      style["label-offset"] = 0.005;
      style["title-size"  ] = 0.035;
      style["title-font"  ] = 42;
      style["label-color" ] = "rgba(0,0,0,0.8)";
      
      style = proto.attr.yaxis.style; 
      style["label-size"  ] = 0.035;
      style["label-font"  ] = 42;
      style["title-offset"] = 1.0;
      style["title-color" ] = "rgba(0,0,0,0.8)";
      style["label-offset"] = 0.005;
      style["title-size"  ] = 0.035;
      style["title-font"  ] = 42;
      style["label-color" ] = "rgba(0,0,0,0.8)";
      
      proto['class'] = 'h1f';

      return proto;
   }
   /*_________________________________________________________________________________________________*/
   pmPlot.prototype.roundLegend = function(y) {
      if ( y < 1)
         y = "" +  y.toFixed(2);
      else if (y < 1000)
         y =  "" +  Math.ceil(y);
      else if (y < 1000000)
         y = "" + (y/1000.0).toFixed(1) + " K";
      else 
         y = "" + (y/1000000.0).toFixed(1) + " M";
      return y;
   }

   /*_________________________________________________________________________________________________*/
   pmPlot.prototype.showTooltip= function(x, y, contents) {
      this.tooltip = 
         $('<div class="ui-widget ui-corner-all ui-widget-content" id="tooltip">'  + contents + '</div>').css( {
            position: 'absolute',
            display: 'none',
            top: y-20,
            left: x + 5,
            border: '1px solid #fdd',
            padding: '2px',
            'background-color': '#fee',
            'font-size' :'0.6em' ,
            'font-family' : 'Verdana, sans-serif',
            opacity: 0.7
         });
      this.tooltip.appendTo("body").fadeIn(200);
   }
   /*_________________________________________________________________________________________________*/
   pmPlot.prototype.propertyBox =  function() {
     /* This method was borrowed from plot insertLegend() one */
      if  (this.plot == undefined) return;
      var plot = this.plot;
      var options = plot.getOptions();
      if ( options.legend.show ) { return;  }
      var placeholder = plot.getPlaceholder();
      placeholder.find(".legend").remove();

      var fragments = [], rowStarted = false,
      pf = options.legend.propertyFormatter, s, property;
      var bcolor;
      for (var i = 0; i < series.length; ++i) {
         s = series[i];
         if (i==0) { bcolor=s.color; }
         var property = s.property;
         if (!property) {     continue; }
         label = s.label;
                
         if (i % options.legend.noColumns == 0) {
            if (rowStarted)
                  fragments.push('</tr>');
              fragments.push('<tr>');
              rowStarted = true;
         }
         if (pf) { propery = pf(propery, s); }
         for (var pr in property) {
            var fixed = 2;
            if ( pr.toLowerCase() =='underflow' ||  pr.toLowerCase() =='overflow' ||  pr.toLowerCase() =='xbound') { continue; }
            if (pr.toLowerCase() == 'entries') {fixed = 0; }
            fragments.push('<tr>');
            if (label) {
//                       + '<div class="legendColorBox"><div style="border:1px solid ' + options.legend.labelBoxBorderColor + ';padding:1px"><div style="width:4px;height:0;border:5px solid ' + s.color + ';overflow:hidden"></div></div></div>' 
               fragments.push('<tr><td colspan=2 style="padding:0px">'
                       + '<div class="legendLabel">' + label + '</div>'
                       + '</td></tr>'
                       );
            }
            fragments.push('<td class="propertyKeyBox" style="padding:0px">' + pr + ':</td>');
            fragments.push('<td class="propertyValueBox"style="padding:0px" >' +this.roundLegend(property[pr].toFixed(fixed))  + '</td>');
            fragments.push('</tr>');
         }
      }
      if (rowStarted) {  fragments.push('</tr>'); }
            
      if (fragments.length == 0) { return; }
      var margin = 0;
      var table = '<table style="border: 1px solid '+bcolor +'; border-style:outset; margin:'+margin+'px;font-size:smaller;color:' + options.grid.color + '">' + fragments.join("") + '</table>';
      if (options.legend.container != null)
         $(options.legend.container).html(table);
      else {
         var plotOffset = plot.getPlotOffset();
         var pos = "",
            p = options.legend.position,
            m = options.legend.margin;
         if (m[0] == null)
             m = [m, m];
         if (p.charAt(0) == "n")
            pos += 'top:' + (m[1] - plotOffset.top/2 + 2*margin) + 'px;';
         else if (p.charAt(0) == "s")
            pos += 'bottom:' + (m[1] + plotOffset.bottom) + 'px;';
         if (p.charAt(1) == "e")
            pos += 'right:' + (m[0] - plotOffset.right/2 + 2*margin) + 'px;';
         else if (p.charAt(1) == "w")
            pos += 'left:' + (m[0] + plotOffset.left) + 'px;';
         var legend = $('<div class="legend">' + table.replace('style="', 'style="position:absolute;' + pos +';') + '</div>').appendTo(placeholder);
         if (options.legend.backgroundOpacity != 0.0) {
              // put in the transparent background
              // separately to avoid blended labels and
              // label boxes
              var c = options.legend.backgroundColor;
              if (c == null) {
                  c = options.grid.backgroundColor;
                  if (c && typeof c == "string")
                      c = $.color.parse(c);
                  else
                      c = $.color.extract(legend, 'background-color');
                  c.a = 1;
                  c = c.toString();
              }
              var div = legend.children();
              $('<div style="position:absolute;width:' + div.width() + 'px;height:' + div.height() + 'px;' + pos +'background-color:' + c + ';"> </div>').prependTo(legend).css('opacity', options.legend.backgroundOpacity);
          }
      }
   }
   /*_________________________________________________________________________________________________*/
   pmPlot.prototype.updateLegends = function() {
      while ( this.plot2UpdateLegend.length > 0) {
         var plot = this.plot2UpdateLegend.pop();
         plot.updateLegend();
      }
   }
   /*_________________________________________________________________________________________________*/
   pmPlot.prototype.updateLegend = function() {
      var plot = this;
      plot.updateLegendTimeout = null;      
      var pos  = plot.latestPosition;
      var endOfLegend = /:{2}.*/;
      if (this.refTable === undefined ) {
         var t = $(this.refTableId);
         if ( t != undefined && t.length>0 ) {
            this.refTableId = t;
            this.refTable = this.refTableId.dataTable();
            if (this.refTableData == undefined) {
               this.refTableData = this.refTable.fnGetData();
            }
         }
      }
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
            if (this.refTable && this.refTableId .data("filter") ) { this.refTableId.data("filter", false); this.refTable.fnFilter('',this.refTableDataIndx, false,false); }
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
            var pnt;
            for (j = 0; j < series.data.length; ++j)
               pnt = series.data[j];
               if (pnt && (pnt[0] > pos.x) )
               {   break;                   }
            // now interpolate
            if (pnt === undefined) { break ; } 
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
         var x;
         if ( (plot.item != undefined ) && (plot.item != null ) )   {
             var xaxes = plot.plot.getXAxes();
             var mode =  xaxes[0].options.mode;
             if (mode == 'time') {
                tooltip = new Date(pos.x);
             } else if (mode=='name') {
                var names = xaxes[0].options.names;
                tooltip = names[Math.floor(pos.x)];
             } else {
                x =   "x=" + Number(pos.x).toFixed(2) ;
                if (this.refTableData !== undefined) {
                    x = this.refTableData[Math.ceil(Number(pos.x))][this.refTableDataIndx];
                } else if (mode=='label') {
                   var ticks = xaxes[0].options.ticks;
                   if (ticks) {
                      var indx= binSearch(ticks, Math.round(Number(pos.x)), function(a,b) { var cmp = a[0] - b; if (cmp >0) {return 1;} if (cmp <0) {return -1;} return 0; }); 
                      var label = ticks[indx][ticks[indx].length-1];
                      x = label;
                   }
                }
                tooltip = x /* + " : y=" + Number(pos.y).toFixed(2); */
             }
             plot.showTooltip(plot.item.pageX, plot.item.pageY, " " + tooltip);
             if (this.refTable) {  this.refTableId.data("filter", true); this.refTable.fnFilter(x,this.refTableDataIndx, false,false); }
         }
      }
   }
   /*_________________________________________________________________________________________________*/
   pmPlot.prototype.plotContainer = function (rhists,width,height,log) {
      this.logcheck = $("<input title='Check to set log scale' type='checkbox' id ='logcheckId' name='logscale'>");
      if (log != undefined ) { this.logcheck.prop('checked',log);} 
      var plotLayout = $("<table border=0 cellspacing=0 cellpadding=0></table>");
      var thead = $('<thead></thead>');
      var trHead = $('<tr></tr>');
      var attr = this.attr(rhists[0]);
      attr =  $.extend(true,{},this.h1proto().attr,attr);
      // console.log( ' plotContainer attr: ' + JSON.stringify(attr));
      var tdYAx = $("<td margin=0 style='vertical-align:bottom;text-align:left;'>"
                     +"<math xmlns='http://www.w3.org/1998/Math/MathML'><mrow>" 
                     +attr.yaxis.title+
                     "</mrow></math></td>");    
      trHead.append(tdYAx);
      if (this.style && this.style.title) {
         var plottit = attr.title;
         if (plottit==undefined) {plottit = '';}
         var thGrTitle = $("<th style='padding:0px;' id='plotTitleId'>" 
                        +plottit+
                        "</th>");
         thGrTitle.append(this.logcheck);
         trHead.append(thGrTitle);
      }
      thead.append(trHead);
      plotLayout.append(thead);
      
      var tbody = $('<tbody></tbody>');
      var grRow = $('<tr></<tr>');
      var grTd = $("<td colspan=2 style='padding:0px;' id='plotAreaId'></td>");
      var graphplace = $("<div></div>");
      if (width == undefined) { width = 600; }
      if (height == undefined) { height = 400; }
      graphplace.css("width", width);  graphplace.css("height", height);
      grTd.append(graphplace);
      grRow.append(grTd);
      var axRow = $('<tr></tr>');
      var axTd = $("<td colspan=2 style='padding:0px;vertical-align:top;text-align:right;' id='xTitleId'></td>");
      axTd.html( "<math xmlns='http://www.w3.org/1998/Math/MathML'><mrow>" +  attr['xaxis'].title + "</mrow></math>");
      axRow.append(axTd); 
      tbody.append(grRow); tbody.append(axRow);
      plotLayout.append(tbody);
      var thisPlot = this;
      this.logcheck.click(function () {thisPlot.renderRootHistClient(rhists,graphplace);});
      this.tag.append(plotLayout);
      // console.log('attr--->: ' +JSON.stringify(attr));
      this.renderRootHistClient(rhists,graphplace);           
      return plotLayout;
   }
   /*_________________________________________________________________________________________________*/
   pmPlot.prototype.attr =  function (hists) {
      /* Old schema / mew schema */
      return hists.attr ? hists.attr : hists.data;
   }

   /*_________________________________________________________________________________________________*/
   pmPlot.prototype.renderRootHistClient =  function (hists,graphtag) {
      //console.log("renderRootHistClient: " + JSON.stringify(hists));
      if (hists  && hists.length >0) {
         if (graphtag == undefined) {
            graphtag= this.graphTag ; 
         } else {
            graphtag = utils().jqTag(graphtag);
            graphtag.data("plot" , this);
            this.graphTag = graphtag;
         }
         var attr = this.attr(hists[0]);
         var op4hist = $.extend(true,{}, this.h1proto().attr,attr);
         if ( this.logcheck[0].checked) {  $.extend(true,op4hist, {yaxis: { logscale : true }} );  }
         op4hist['class'] = this.h1proto()['class'];
         var options = this.makeRootHistOptions(op4hist,op4hist['class'],hists[0].data.property);
         //console.log("Options: " + JSON.stringify(options));
         series = [];
         if (hists.length >1 ) { options.legend.show = true; }
         for (var h in hists) {
            op4hist =  h>0 ? $.extend(true,op4hist,this.attr(hists[h])) : op4hist;
            this.resetProto(op4hist);
            var opts = op4hist.options;
            var labeled = false;
            var stacked = opts && opts.toLowerCase().indexOf('s')>=0 ? 'S' : '';
            var dataplot = hists[h].data;
            // console.log("dataplot: " + JSON.stringify(dataplot));
            if ( (dataplot == undefined) && (hists[h]  instanceof Array) ) {
               dataplot =  hists[h];
            }
            //console.log("opts: " + JSON.stringify(opts));
            if (opts == undefined || opts == '') { opts = 'H'; }
            for (var c in opts ) {
               var opt = opts[c];
               if ('HLPB'.indexOf(opt.toUpperCase() ) >= 0) {
                  var dsext = this.makeRootHistDataset(dataplot,op4hist, hists[h]['class'],labeled,opt+stacked);
                  if (h == 0 && c == 0 && options.yaxis && options.yaxis.log) {
                     $.extend(true,options,{ yaxis : { min : op4hist.yaxis.min , max: null } } );
                  }
                  if (dsext) {
                     if (hists[0].data.property) { options['property'] = dataplot.property; }
                     series.push(dsext);
                     labeled = true;
                  }
               }
            }
         }
         graphtag.empty();
         //console.log("options: " + JSON.stringify(options));
         //console.log("series: " + JSON.stringify(graphtag));
         this.log = op4hist.yaxis.logscale;
         this.plot = $.plot(graphtag, series, options);
         this.animate(graphtag);
         this.propertyBox();
      }
   }
   /*_________________________________________________________________________________________________*/
   /* helper for returning the weekends in a period  */
   pmPlot.prototype.weekendAreas = function (axes) {
      var markings = [];
      var d = new Date(axes.xaxis.min);
      // go to the first Saturday
      d.setUTCDate(d.getUTCDate() - ((d.getUTCDay() + 1) % 7))
      d.setUTCSeconds(0);
      d.setUTCMinutes(0);
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

   /*_________________________________________________________________________________________________*/
   pmPlot.prototype.suffixFormatter= function(val, axis) {
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
      } else if (val >= 1000000.0) {
         label = (val / 1000000.0).toFixed(dec) + " M";
      } else if (val >= 1000.0) {
         label = ( val / 1000.0).toFixed(dec) + " K";
      } else {
         label = val.toFixed(dec);
      }
   //   if (this.color) label = "<font color='" + this.color + "' >" + label + "</font>";
      return label;
   }
   /*_________________________________________________________________________________________________*/
   pmPlot.prototype.crossHairMode= function(mode) {
      if (mode !== undefined) { 
          this.crosshair.mode = mode;
      }
      return this.crosshair;
   }

   /*_________________________________________________________________________________________________*/
   pmPlot.prototype.makeRootHistOptions= function(data,dataclass,property) {
      /* hist['class']; */
      if (dataclass != 'h1f') { return ; }
      var options = {};
      options['series'] =  {};
      options['legend'] = { backgroundOpacity:0.2 };
      options['legend'] = { show: false};
      var xaxes =  data['xaxis']; 

      options['xaxes'] = [
                        {   min  : xaxes.min
                          , max  : xaxes.max
                          , mode : null
                        } ];
      
      options['grid'] = { hoverable: true, autoHighlight: true };
      var xlabels = xaxes.labels;
      var nxLabels;
      if ( xlabels ) { nxLabels = xlabels.length; }
      var thisPlot = this;
      if (nxLabels && nxLabels>0) {
         if (property && property.xbound && nxLabels > property.xbound ) { 
           nxLabels = property.xbound;  options.xaxes[0].max=nxLabels; 
         } 
         var ticks = [];
         ticks.push([0,""]) ;
         var nxtck = 0.5;
         for (var k = 0; k < nxLabels; ++k) {
            if (property.xbound) {
               var t = '';
               if (k==0 || (k+1)%5 == 0) {
                  var q = k+1; t = q.toString();
               }
               ticks.push([nxtck,t, xlabels[k]] );
            } else {
               ticks.push([nxtck,xlabels[k]]) ;
            }
            nxtck++;
         }
         options.xaxes[0]['ticks'] = ticks; 
         options.xaxes[0].mode = "label";
        // console.log('OPTIONS='+ JSON.stringify(options));
      } else if (xaxes.time) {
         options.xaxes[0].mode = "time";
         var offset = 0;
         if (xaxes.offset) { offset = xaxes.offset; }
         options.xaxes[0].offset = offset;
         options.xaxes[0].min = (options.xaxes[0].min + offset)*1000;
         options.xaxes[0].max = (options.xaxes[0].max + offset)*1000;
         options.grid['markings'] = function (axes) { return thisPlot.weekendAreas(axes); }
      }
      var yaxes =  data['yaxis'];
      options['yaxes'] =  [
                        {     position: "left" 
                            , reserveSpace: true 
                            , tickFormatter : function(val,axis) { return thisPlot.suffixFormatter(val,axis) ; }
                        } ];                         
      if (yaxes.logscale) {
         options.yaxis = {
               log : true
            ,  transform: function (v) {
                  if (v == 0) { v = 0.0001; }
                  return Math.log(v);
              }
            , inverseTransform: function (v) { return Math.exp(v); }
         };
      }
      options['crosshair']= this.crosshair;
      options['selection']= { mode: "x" };
      return options;
   }
   /*_________________________________________________________________________________________________*/
   pmPlot.prototype.makeRootHistDataset= function(data,attr, dataclass,labeled,option) {
      // labeled == false - add the label to the plots
      // Options: H - histogram, B - bar , L - line, P - points, S - stacked
      // console.log("makeRootHistDataset: " +JSON.stringify(dataclass)+" opt=" + option);
      if (dataclass && dataclass != 'h1f') { return ; }
      if (labeled==undefined) { labeled = false; }
      var style = attr.style; 
      var xBins;
      if (data instanceof Array) { xBins =  data;}
      else {
         xBins = data ? data.bins : attr.bins;
      }
      var boundCut =  false;
      if (data.property && data.property.xbound) {
          if (xBins.length > data.property.xbound) { xBins =xBins.slice(0,data.property.xbound); boundCut=true;}
      }
      var dataset;
      if (xBins) {
         var myOptions = option;
         if (myOptions == undefined) {  myOptions = 'H'; }

         var xaxes =  attr['xaxis'];
         if (boundCut && xaxes.max!= undefined) { xaxes.max= undefined;}
         var range = utils().max(xBins);
         var yax = 1;
         var lPoints = xBins.length;
         var d = new Array(lPoints+1);
         var un  = 1;
         var offset = 0;
         var stripthreshold = (xaxes.strip==undefined || xaxes.strip===false) ? undefined : (xaxes.strip === true) ? 0 : xaxes.strip;
         var lstrip = (xaxes.strip==undefined || xaxes.strip===false) ? false : true;
         var strip  = lstrip;
         var rstrip = lPoints;
         if (xaxes.time) { 
            un = 1000; 
            if (xaxes.offset) {offset = xaxes.offset;}
         } 
         var m = xaxes.min   ? xaxes.min : 0 ;
         var s = xaxes.width && !boundCut ? xaxes.width : 1.0*(xaxes.max?xaxes.max:lPoints -m)/lPoints ;
         var a = 0;
         var p = myOptions.indexOf('P')>=0;
         var l = myOptions.indexOf('L')>=0;
         if (p || l) { a = s/2; }
         if ( strip !==false) {
            /* count the right strip position */
            for (var k = lPoints-1; k >= 0; --k) {
              if (xBins[k] > stripthreshold) { break;}
              rstrip = k; 
            }
          }
         var ymin;
         var y=0; 
         var ylogscale = attr.yaxis.logscale;
         for (var k = 0; k < lPoints; ++k) {
            y = 1.0*xBins[k];
            if ( y == undefined)  { y = 0; } 
            if ( strip===true && y  > stripthreshold )  { strip = false; }
            if ( k >= rstrip ) { --k; break; }
            if ( strip===false )  { 
               d[k] =[un*(m + (k*s+a) +offset),y]; 
               if (ylogscale) {
                  if (ymin == undefined && y > 0.0001) { ymin = y; }
                  else if (ymin > y ) { ymin = y; }
               }
            }
         }
         if (ymin !== undefined && ymin >0 ) { attr.yaxis.min = ymin ;  attr.yaxis.max = null; }
         d[k] = [un*(m + (k*s+a)+offset),y];
         // console.log(" points:" +JSON.stringify(d));

         var bstyle = style['background-style'];
         var dtitle;
         if (!labeled) { dtitle = attr.title; }
         dataset = { data: d
                   , label : dtitle
                   , yaxis : yax
                   , color : style.color  
                   , lines : {   show: myOptions.toLowerCase().indexOf('h') >=0 || l
                               , lineWidth : 2*style.width
                               , fill      : (style['background-color'] != 0)
                               , steps     : !l
                               , fillColor : style['background-color']
                             }
                   , points : {  show : p }
                   , bars   : {  show : myOptions.toLowerCase().indexOf('b') >=0
                               , barWidth: s*un
                              }
            };
            if (myOptions.toLowerCase().indexOf('s') >=0) {
               dataset.stack = true;
            }
            if (data.property) { dataset['property'] = data.property; }
         // console.log("makeRootHistDataset: dataset" +JSON.stringify(dataset));
      }
      return dataset;
   }
   /*_________________________________________________________________________________________________*/
   pmPlot.prototype.removeTip= function() {
      if ( this.tooltip) { this.tooltip.remove(); this.tooltip = null; }
   }
   /*_________________________________________________________________________________________________*/
   pmPlot.prototype.animate= function(graphtag) {
      this.cleanLegend = true;
      this.updateLegend();
      var plot = this;
      this.updateLegendTimeout = null;
      this.latestPosition      = null;
      graphtag.bind("mouseout",   function (event, pos, item) {
         plot.cleanLegend = true;
         plot.removeTip();
         plot.updateLegends();
       });                  
      graphtag.bind("plothover",   function (event, pos, item) {
         /* var plot = $(this).data("plot"); */
         if (!plot.updateLegendTimeout) {
            plot.latestPosition = pos;
            plot.item = item;
            plot.plot2UpdateLegend.push(plot);
            plot.updateLegendTimeout = setTimeout(function() {plot.updateLegends();}, 50);
            plot.removeTip();
         }
      });
   }
   /*_____________________________________________________________________*/
   pmPlot.prototype.plotList = function () {
      var selectors = $(this).parent().parent().children();
      var plotItems = [];
      var ploptions = '';      
      selectors.find('.pminput:checked').each(function (i) { plotItems.push($(this).val());});
      selectors.find('.pmplotoption:checked').each(function (i) { ploptions +=$(this).val();});
      this.plotpoints(plotItems,ploptions);
   }
   /*_____________________________________________________________________*/
   pmPlot.prototype.plotPoints = function  (header,plotItems,plotStyle,xtitle,ytitle) {
      /* Create the graph view of the  table columns defined by plotItems */
      var d2plot;
      if ( ( this.refTableData != undefined ) && plotItems && ( plotItems.length >0) ) {
         d2plot = new Array(plotItems.length);
         var stacked = plotStyle ? plotStyle.toLowerCase().indexOf('s') >=0 : undefined;
         for (var p in plotItems) {
            var ip = p; // stacked ? plotItems.length-p-1 : p;
            var i = utils().name2Indx(header,plotItems[ip]);
            var column = new Array(this.refTableData.length-1);
            for (var j = 0; j< this.refTableData.length-1; ++j) {
               column[j] = this.refTableData[j+1][i];
            }
            d2plot[p] = {data : column
                        ,attr : {  style : { color  : utils().rgba(utils().colorMap[plotItems[ip].toLowerCase()]) }
                                 , title : "The number of the '" +plotItems[ip] + "'" + ((xtitle!=undefined) ? " jobs per " + xtitle : '')
                                }
                        };
            if (p == 0) {
               var attr     = d2plot[p].attr;
               attr.options = plotStyle ? plotStyle : 'B';
               attr.style.color = utils().rgba(utils().colorMap[plotItems[ip].toLowerCase()],1.0); 
               if (ytitle != undefined) {
                   attr.yaxis   = { title : ytitle };
               }
               if ( xtitle != undefined ) { attr.xaxis   = { title : xtitle}; }
            }
         }
      }
      return d2plot;
   }
 
   

   /*_________________________________________________________________________________________________*/

/*
   var d = $("<div></div>");
   $(tag).empty();
   var lout= plotContainer(rhists, main.width, main.height,main.log);
   d.append(lout);
   $(tag).append(d);
  
*/
  
