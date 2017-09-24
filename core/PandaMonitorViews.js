// $Id: PandaMonitorViews.js 19632 2014-07-06 07:30:10Z jschovan $:
//__________________________________________________________________________________________________
function views() {
    if (document.pandaViews ==undefined) {
        new PandaMonitorViews(document.pandaURL);
    }
    return document.pandaViews;
}

//__________________________________________________________________________________________________
function PandaMonitorViews(url){
  this.baseURL = url;
  this.fPlotTitles = [];
  if (parseInt(navigator.appVersion)>3) {
      if (navigator.appName=="Netscape") {
         this.IE = false;
      }
  }
 // this.hasAdd2Favorite = !this.IE;
//  if (this.hasAdd2Favorite ) { this.hasAdd2Favorite  = !(window.external== undefined || window.external.AddFavorite == undefined); }

  document.pandaViews = this;
  // this.LoadJQuery();
}
//________________________________________________________________________________________
PandaMonitorViews.prototype.baseURL = null;
PandaMonitorViews.prototype.JQueryLoaded = false;
PandaMonitorViews.prototype.AtlasTwiki = 'https://twiki.cern.ch/twiki/bin/viewauth/AtlasComputing';
PandaMonitorViews.prototype.PandaPilotTwiki = 'PandaPilot';
PandaMonitorViews.prototype.PandaTwiki = 'https://twiki.cern.ch/twiki/bin/view/PanDA';
PandaMonitorViews.prototype.PandaPlatformTwiki = 'PandaPlatform';

PandaMonitorViews.prototype.IE = true;

PandaMonitorViews.prototype.hasAdd2Favorite =  window.external || window.sidebar || (window.opera && window.print);
PandaMonitorViews.prototype.colorMap = {  nfinished: '#00CC00' 
                                        , finished : '#00CC00'  // panglia color '#0000FF' 
                                        , failed   : '#FF6666'  // panglia color '#FFFF00'
                                        , activated: '#A0A0A0'
                                        , defined  : '#787878' 
                                        , holding  : '#FFFF33'  // panglia color '#FFA600'
                                        , running  : '#DDFFBB'  // panglia color '#008800'
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
                                        , RU       : '#66008D'
                                       };
PandaMonitorViews.prototype.timeUnitSize = {
         "second": 1000,
         "minute": 60 * 1000,
         "hour": 60 * 60 * 1000,
         "day": 24 * 60 * 60 * 1000,
         "month": 30 * 24 * 60 * 60 * 1000,
         "year": 365.2425 * 24 * 60 * 60 * 1000
      };   

PandaMonitorViews.prototype.units = function(fieldname,globalUnit) 
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
PandaMonitorViews.prototype.fPlotID="plotID";
PandaMonitorViews.prototype.showTableTag = 'Show the table';
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
PandaMonitorViews.prototype.printObj = function(obj) {
  console.log(JSON.stringify(obj,undefined,2));
}


//________________________________________________________________________________________
PandaMonitorViews.prototype.autocomplete = function(tag,extralist) {
   var termslist = {
         jobStatus: ['defined', 'pending', 'waiting', 'assigned', 'activated', 'sent', 'starting', 'running', 'holding'
                 ,'transferring', 'finished', 'failed', 'cancelled','retried','wn','factory']
       , jobtype : [ 'production','analysis','install','test','jedi','prod_test' ]
       , status: [ 'registered', 'waiting','defined', 'pending', 'assigning', 'ready'
                    , 'scouting',  'running', 'holding', 'merging','prepared'
                    , 'finished',  'aborting','aborted', 'finishing', 'broken', 'failed'
                  ]
       , cloud: ['US','TW','CA','ND','ES','CERN','FR','IT','DE','RU','UK','NL','OSG','CMS']
       , computingSite: ['ANALY_RHUL_SL6','ANALY_ARC','ANALY_IHEP','ANALY_INFN-MILANO-ATLASC'
      ,'ANALY_ORNL_Titan','ANALY_GRIF-LAL','ANALY_QMUL_HIMEM_SL6','ANALY_IFIC'
      , 'BNL_PROD','ANALY_INFN-NAPOLI','IllinoisHEP','ANALY_DUKE'
      ,'FMPhI-UNIBA','RAL-LCG2_HIMEM_SL6','WEIZMANN-LCG2','ANALY_MCGILL_TEST','ANALY_TOKYO_HIMEM'
      ,'UKI-SCOTGRID-GLASGOW_SL6','UKI-LT2-RHUL_SL6','INFN-LECCE','CERN-PROD','ANALY_ECDF'
      ,'SLACXRD','GRIF-LAL','RRC-KI-T1','ANALY_INFN-LECCE','BNL_Test_2_CE_1','HEPHY-UIBK','UKI-SCOTGRID-ECDF'
      ,'ANALY_BNL_DDM_Test','NIKHEF-ELPROD_LONG','ANALY_IN2P3-CC-T2_TEST','wuppertalprod'
      ,'RU-Protvino-IHEP','ANALY_INFN-COSENZA','TRIUMF_MCORE'
     
      ,'ANALY_SARA_bignode','BEIJING_MCORE','ANALY_LBNL_TEST_CLOUD2','ANALY_T2_FR_GRIF_IRFU','CERN-PROD_CLOUD_MCORE'
      ,'Nebraska_SBGRID','UKI-NORTHGRID-MAN-HEP_MCORE'
      ,'AGLT2_MCORE','ANALY_IL-TAU-HEP-CREAM','ANALY_DESY-ZN','ARC-T2','ANALY_OU_OCHEP_SWT2','ANALY_RAL_SL6'
      ,'JINR-LCG2','UTA_SWT2','LPC','RAL-LCG2_MCORE','ANALY_MANC_SL6','UKI-LT2-Brunel_SL6','ANALY_OX_SL6'
      ,'SARA-MATRIX','ANALY_NECTAR','ANALY_INFN-ROMA2','ANALY_IN2P3-CC_VM2','Australia-NECTAR','CA-SCINET-T2'
      ,'SWT2_CPB','INFN-MILANO-ATLASC'

      ,'ANALY_TAIWAN_PNFS','ANALY_ECDF_SL6','ROMANIA02','BEIJING','ANALY_RALPP','CPPM','FZK-LCG2_MCORE','CA-JADE'
      ,'LRZ-LMU_TEST','ANALY_CERN_SLC6','ANALY_SARA_hpc_cloud_rfio'
      ,'ANALY_BNL_CLOUD','ANALY_IN2P3-CC_VM','ANALY_IN2P3-CC_TEST1','IN2P3-CC_VVL','wuppertalprod_MCORE','BNL_SITE_GK02'
      ,'UAM-LCG2','ANALY_T2_FR_GRIF_LLR','ANALY_T2_IT_Bari','BNL_OSG_1','UTA_PAUL_TEST'
      ,'WQCG-Harvard-OSG_SBGRID','ANALY_T1_US_FNAL','ANALY_IAAS','ANALY_IEPSAS-Kosice','AGLT2_SL6','ANALY_FREIBURG'
      ,'ANALY_CAM_SL6','ANALY_GRIF-IRFU','ANALY_IN2P3-CC-T2','MPPMU','ANALY_AGLT2_SL6'
      ,'ANALY_RALPP_SL6','CERN-P1','ANALY_QMUL_SL6','ANALY_INFN-ROMA3','ANALY_GOEGRID','UKI-NORTHGRID-SHEF-HEP_SL6'
      ,'BNL_CLOUD','UKI-LT2-IC-HEP_SL6','ANALY_CPPM','RRC-KI','IN2P3-CC-T2'
      ,'Moscow-FIAN','NIKHEF-ELPROD','ANALY_VICTORIA_TEST','UKI-NORTHGRID-MAN-HEP_SL6','ANALY_LPSC','INFN-GENOVA'
      ,'ANALY_UAM','LRZ-LMU_HI','ZA-UJ','UKI-SOUTHGRID-OX-HEP_TEST','DESY-HH'
      ,'ANALY_IllinoisHEP','UKI-LT2-QMUL_HIMEM_SL6','ANALY_RAL_MCORE','IN2P3-LPSC','ANALY_MANC_TEST','ANALY_SARA_hpc_cloud_xrootd'
      ,'ANALY_CERN_CLOUD','praguelcg2_TEST','ANALY_INFN-BOLOGNA-T3','SLACXRD_MP8','ANALY_BNL_Test_2_CE_1'
      ,'UNI-SIEGEN-HEP','ANALY_T2_DE_RWTH','ANALY_T2_ES_CIEMAT','ANALY_T2_KR_KNU','ANALY_T2_UK_SGrid_RALPP','ANALY_T2_US_Caltech'
      ,'ANALY_T2_US_MIT','ANALY_T2_IT_Pisa','TRIUMF','ANALY_SLAC','ANALY_BNL_LONG'
      ,'UKI-NORTHGRID-LANCS-HEP_MCORE','UKI-NORTHGRID-LANCS-HEP_SL6','CERN-DIRECTIO','ANALY_FZK','ANALY_SWT2_CPB','OU_OSCER_ATLAS'
      ,'DESY-ZN','INFN-FRASCATI','TOKYO_HIMEM','TR-10-ULAKBIM','LRZ-LMU'
      ,'ANALY_JINR','CA-MCGILL-CLUMEQ-T2','ANALY_BNL_SE_Test','ANALY_FMPhI-UNIBA','OPENSTACK_CLOUD','ROMANIA16'
      ,'ANALY_MWT2','ANALY_IN2P3-CC','IN2P3-CC','ANALY_NIKHEF-ELPROD','ANALY_CSCS'
      ,'NCG-INGRID-PT_SL6','INFN-NAPOLI-ATLAS','SARA-MATRIX_MCORE','PSNC','IL-TAU-HEP','ANALY_HEPHY-UIBK'
      ,'ANALY_TECHNION-HEP-CREAM','ANALY_TR-10-ULAKBIM','praguelcg2','ROMANIA14','TUDresden-ZIH'
      ,'ZA-WITS-CORE','ANALY_DESY-HH_TEST','ANALY_IN2P3-CC-T2_RD','wuppertalprod_HI','BNL_PROD_MCORE','pic_MCORE'
      ,'OU_OSCER_ATLAS_OPP','ANALY_SARA_hpc_cloud','ANALY_ANLASC','ANALY_T2_CH_CSCS','ANALY_T2_EE_Estonia'
      ,'ANALY_T2_IT_Legnaro','Firefly_SBGRID','NERSC-PDSF','Harvard-East_SBGRID','Harvard-Exp_SBGRID','ANALY_UCSC'
      ,'ANALY_IAAS_TEST','ANALY_IFAE','IAAS','BNL_ATLAS_DDM','ANALY_LIV_SL6'
      ,'ANALY_FZU','ROMANIA07','ANALY_DESY-HH','ANALY_PIC_SL6','INFN-COSENZA','ANALY_INFN-FRASCATI'
      ,'GRIDPP_CLOUD','Taiwan-LCG2','ANALY_SFU','ANALY_MPPMU','UKI-SOUTHGRID-RALPP_SL6'
      ,'UKI-SOUTHGRID-SUSX_SL6','ANALY_NCG-INGRID-PT_SL6','ANALY_NICS_Kraken','ANALY_GLASGOW_SL6','UKI-SCOTGRID-ECDF_SL6','UKI-SCOTGRID-GLASGOW_MCORE'
      ,'ANALY_SLAC_LMEM','INFN-NAPOLI-RECAS','LAPP','ANALY_UCL','ANALY_INFN-PAVIA'
      ,'FZK-LCG2_TEST','LIP-COIMBRA_SL6','ANALY_Tufts_ATLAS_Tier3','ARC_MCORE','ITEP','IFAE'
      ,'LRZ-LMU_C2PAP','ANALY_BHAM_SL6','MWT2_MCORE','ANALY_BNL_T3','CERN_8CORE'
      ,'UKI-LT2-UCL-HEP','INFN-ROMA2','ANALY_BU_ATLAS_Tier2_SL6','FZK-LCG2','ANALY_MWT2_SL6','UKI-SOUTHGRID-BHAM-HEP_SL6'
      ,'ANALY_DRESDEN','ANALY_INFN-GENOVA','ANALY_TAIWAN_SL6','ANALY_SCINET_TEST','Australia-ATLAS'
      ,'INFN-ROMA3','UKI-SCOTGRID-DURHAM_SL6','CA-VICTORIA-WESTGRID-T2','UKI-SOUTHGRID-OX-HEP_SL6','ANALY_MWT2_CLOUD','UKI-NORTHGRID-MAN-HEP_TEST'
      ,'SARA-MATRIX_LONG','CSCS-LCG2','UKI-NORTHGRID-LIV-HEP_SL6','Lucille_CE','INFN-T1_4CORE'
      ,'UNI-FREIBURG_MCORE','IN2P3-CC_VM','UKI-SCOTGRID-DURHAM','ANALY_ZA-WITS-CORE','IN2P3-CC_MCORE','ANALY_LBNL_TEST_CLOUD'
      ,'ANALY_T2_US_Nebraska','UW_VDT_ITB','Prairiefire_SBGRID','ANALY_VICTORIA','ANALY_INFN-T1'
      ,'ANALY_MCGILL','MWT2','ANALY_BNL_SHORT','ANALY_SARA','INFN-T1','UKI-SOUTHGRID-CAM-HEP_SL6'
      ,'SLACXRD_LMEM','ANALY_SCINET','ANALY_LPC','ANALY_LANCS_SL6','INFN-BOLOGNA-T3'
      ,'RAL-LCG2_SL6','ANALY_CERN_XROOTD','TOKYO','ANALY_LONG_BNL_LOCAL','ANALY_QMUL_TEST','ANALY_CYF'
      ,'OPENSTACK_CLOUDSCHEDULER','GoeGrid','UKI-LT2-QMUL_SL6','ANALY_TAIWAN_PNFS_SL6','ANALY_SHEF_SL6'
      ,'AGLT2_TEST','AM-04-YERPHI','ANALY_RRC-KI','ANALY_UTFSM','EELA-UTFSM','ANALY_GR-01-AUTH'
      ,'FZK-LCG2_HI','GR-01-AUTH','ANALY_CERN_GLEXECDEV','INFN-ROMA1','ANALY_BNL_LOCAL'
      ,'ANALY_LRZ','BNL_ATLAS_2','UKI-SOUTHGRID-RALPP','CSCS-LCG2_TEST','ANALY_AM-04-YERPHI','ANALY_TAIWAN_TEST'
      ,'ANALY_T2_UK_London_IC','HU_ATLAS_Tier2','LBNL_DSD_ITB','BU_ATLAS_Tier2_SL6','ANALY_T2_CH_CERN'
      ,'ANALY_T2_US_UCSD','ANALY_TRIUMF','ARC','ANALY_TOKYO','ANALY_INFN-ROMA1','ANALY_ROMANIA02'
      ,'ANALY_LAPP','ANALY_wuppertalprod','ANALY_DUKE_CLOUD','ANALY_ROMANIA07','ANALY_AUSTRALIA'
      ,'INFN-PAVIA','ANALY_INFN-FRASCATI_PODtest','GRIF-IRFU','CYFRONET-LCG2','TW-FTT_SL6','ANALY_GRIF-LPNHE'
      ,'ORNL_Titan','ANALY_TAIWAN_XROOTD_SL6','GRIF-LPNHE','pic','SFU-LCG2'
      ,'ANALY_WEIZMANN-CREAM','ANALY_SLAC_SHORT_1HR','OU_OCHEP_SWT2','ANALY_T2_DE_DESY','INFN-NAPOLI-SCOPE','IFIC'
      ,'CERN-PROD_SLC6','ANALY_ZA-UJ','UNI-DORTMUND','TECHNION-HEP','UKI-SCOTGRID-GLASGOW_TEST'
      ,'MWT2_SL6','ANALY_OX_TEST','ANALY_LIP-Coimbra_SL6','UNI-FREIBURG','ANALY_SFU_TEST','CERN-P1_MCORE'
      ,'ANALY_FZU_TEST','ANALY_DESY-ZN_XRD','UKI-SCOTGRID-ECDF_8CORE','CSCS-LCG2_MCORE','CERN-RELEASE'
      ,'Taiwan-LCG2_VL','ANALY_T2_IT_Rome','ANALY_HU_ATLAS_Tier2','BNL_ATLAS_1']
   , processingType: [ 'gangarobot-rctest','jedi-athena','pile','pathena','pandamover','reco'
                     , 'jedi-athena-trf','gangarobot','hammercloud','gangarobot-pft','hammercloud-fax'
                     , 'merge','reprocessing','evgen','gangarbt-rctest','simul','usermerge','prun'
                     , 'validation','ganga','gangarobot-nightly']
    , workingGroup:  ['AP_Exotics','AP_Reprocessing','GP_JetMet','localuser','AP_Generators','AP_JetEtMiss','GP_trig-hlt','poweruser0'
                     , 'GP_SM','AP_Trigger','AP_Physics','perf-flavtag','GP_Susy','AP_Higgs','AP_SM','AP_EGamma','GP_Top','GP_Btagging'
                     , 'phys-exotics','det-indet','GP_Higgs','AP_Top','phys-susy','phys-higgs','GP_Exotics','perf-egamma','AP_Validation','AP_Susy'
                     , 'AP_HeavyIon','AP_BPhysics','GP_EGamma','phys-valid' ]
   , prodSourceLabel: ['ddm','rc_test','managed','panda','prod_test','user','test','install','ptest']
   , dump:            ['yes','no']
   }
   if  (extralist !== undefined) {
       $.extend(termslist,extralist);
   }
   termslist['site'] = termslist.computingSite;
   termslist['region'] = termslist.cloud;
   var  thisTag =  views().jqTag(tag);
   var label = thisTag.attr('name');
   if ( termslist[label] === undefined )  {  
          thisTag.attr('onchange',thisTag.attr( "onchangeme" ));
          return;  
   }
   function acompete(tg,atags) {
      var thisTag =  tg;
      thisTag.data('ui-autocomplet_function',this); /* to hold it on */
      function split( val ) {
         return val.split( /,\s*/ );
      }
      function extractLast( term ) {
         return split( term ).pop();
      }
      thisTag
      // don't navigate away from the field on tab when selecting an item
      .bind( "keydown", function( event ) {
         if ( event.keyCode === $.ui.keyCode.TAB &&
         $( this ).data( "autocomplete" ).menu.active ) {
            event.preventDefault();
         } else if ( event.keyCode !== $.ui.keyCode.ENTER ) {
             $(this).attr('comleteselect',false);
         } else if ($(this).attr('comleteselect')) {
            $(this).change(); 
         }
      })
      .on( "change", function( event ) {
         var that = $(this);
         if ( that.data( "autocomplete" ).menu.active ) {
            /* wait the change to be done via blur  */
            event.preventDefault();
         } else {
            if (that.attr( "onchangeme" ) ) {
               eval(that.attr( "onchangeme" ));
            }
         }
      })
      .on( "blur", function( event ) {
         var that = $(this);
         if ( that.data( "autocomplete" ).menu.active ) {
            /* wait the change to be done via blur  */
            event.preventDefault();
         } else {
            eval(that.attr( "onchangeme" ));
         }
      })
      .autocomplete({
           availableTags: atags
         , source: 
            function( request, response ) {
              var availableTags = this.options.availableTags;
             // delegate back to autocomplete, but extract the last term
               response( $.ui.autocomplete.filter(
               availableTags, extractLast( request.term ) ) );
             /*
               $.getJSON( "search.php"
                    , { term: extractLast( request.term )  }
                    , response );
              */
            }
         , search: 
            function() {
               // custom minLength
               var term = extractLast( this.value );
               if ( term.length < 1 ) {
               return false;
               }
            }
         , focus: 
            function() {
            // prevent value inserted on focus
               return false;
            }
         , select: 
            function( event, ui ) {
              $(this).focus();
               var terms = split( this.value );
               // remove the current input
               terms.pop();
               // add the selected item
               terms.push( ui.item.value );
               // add placeholder to get the comma-and-space at the end
               // terms.push( "" );
               this.value = terms.join( "," );
               this.comleteselect = true;
               return false;
            }
      });
   }
   new acompete(thisTag,termslist[label].slice());
}

//________________________________________________________________________________________
function suffixFormatter(val, axis) {
   var label = '';
   var dec = axis.tickDecimals;
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
  
//________________________________________________________________________________________
PandaMonitorViews.prototype.LoadScripts = function(scripts) {
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
PandaMonitorViews.prototype.LoadJQuery = function() {
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
PandaMonitorViews.prototype.tablesort = function (tableid) {
      $("#" + tableid).tablesorter({widthFixed: true})
 }
//________________________________________________________________________________________
PandaMonitorViews.prototype.header2Plot = function (header,plot,style,handler) {
   /* Create the header with selectable columns */
   var thead = $("<thead></thead>");
   var trow = $("<tr class='ui-widget-header'></tr>");
   for (var l in header) { 
      // renderRootHistClient(d2plot)
      var nxthead = $("<th aligh=center></th>");
      if ( l>0 ) {
         nxthead.attr('title','Check to plot the "'+header[l]+ '" jobs');
         var checkbox = $("<input type='checkbox' class='pminput'>");
         checkbox.attr("value",header[l]);
         checkbox.attr('checked', (utils().name2Indx(plot,header[l]) != undefined));
         checkbox.attr('title','Check to plot the "'+header[l]+ '" jobs');
         checkbox.click(handler);
         nxthead.append(checkbox);
      } else {
         nxthead.attr('title','Check the plot option to change the rendering style');
         var plotOptions = { 'B' : 'Plot the "B"ar at each point'
                        ,'L' : 'Connect the dots with  the straight "L"ine'
                        ,'S' : '"S"tack the multiply plots '
                        ,'H' : 'Use "H"istogram style'
                        ,'P' : 'Draw the marker for each "P"oint'
                        };
         for (var st in plotOptions) {
            var checkbox = $("<input type='checkbox'class=pmplotoption display=inline></input>");
            checkbox.attr("value",st);
            checkbox.attr("title",plotOptions[st]);
            checkbox.attr('checked', (utils().name2Indx(style,st) != undefined));
            checkbox.click(handler);
            nxthead.append(checkbox);nxthead.append("<font size=-3>"+st+"</font>");
         }
      }
      trow.append(nxthead);
   }
   thead.append(trow);
   trow = "<tr>";
   for (var l in header) { trow += "<th>"+header[l] + "</th>"; }
   trow += "</tr>";
   thead.append(trow);
   return thead;
} 
//________________________________________________________________________________________
PandaMonitorViews.prototype.datatable = function (tableid,option,ldefault) {
    var defflt =  -1;
    var pages = [ [ 35,50, 75, 100, 150, -1], [ 35, 50, 75, 100, 150,"ALL"] ];
    if (ldefault != undefined) {
       defflt = ldefault;
       pages =  [ [ defflt, 35,50, 75, 100, 150, -1], [ defflt, 35, 50, 75, 100, 150,"ALL"] ];
    }
    var opt =  {"bProcessing": true
                , "iCookieDuration": 1
                , "iDisplayLength": defflt
                , "aLengthMenu"   : pages
                , "bStateSave"    : true
                , "bJQueryUI"     : true
                /* , "oSearch" : {
                   "sSearch" :"",
                   "bRegex": true, 
                   "bSmart": false } */
               };
   opt = $.extend(opt,option);    
   $("#" + tableid).dataTable(opt);
 }
//________________________________________________________________________________________
   PandaMonitorViews.prototype.fileURL = function (fileType) {
        // URL to access the image and Javascript files 
        return this.baseURL + fileType;
   }
         
//________________________________________________________________________________________
   PandaMonitorViews.prototype.fileImageURL = function() {
      return this.fileURL("images");
   }

//________________________________________________________________________________________
   PandaMonitorViews.prototype.fileScriptURL = function() {
      return this.fileURL("js");
   }

//__________________________________________________________________________________________________
   PandaMonitorViews.prototype.renderCharts = function () {
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
   PandaMonitorViews.prototype.onResizeEnd = function (table) {
      // alert('Resize : ' + table + ' : ' + this.renderGoogleChart);
      if (this.renderGoogleChart) {
         this.renderGoogleChart();
      }
   }
//__________________________________________________________________________________________________
   PandaMonitorViews.prototype.makeData = function (data) {
      this.data = data;
      this.dataRowInds = this.data.getSortedRows(0);  
      // ctreate the X- array
      this.xDataValues = [];
      for (var i = 0; i < this.dataRowInds.length; i++) {
         this.xDataValues.push(data.getValue(this.dataRowInds[i], 0).getTime());
      }
   }      
//__________________________________________________________________________________________________
   PandaMonitorViews.prototype.makeHists = function (hists) {
      this.hists = hists;
   }
//__________________________________________________________________________________________________
   PandaMonitorViews.prototype.siteStatsTable = function () {
      var table = document.getElementById('siteStats_div');
      return table;
   }
//__________________________________________________________________________________________________
   PandaMonitorViews.prototype.windowSize = function () {
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
   PandaMonitorViews.prototype.setDateRange = function(anchor) {
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
   PandaMonitorViews.prototype.selectDateRange= function(tstart,tend,id) {
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
   PandaMonitorViews.prototype.calendar = function() {
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
   PandaMonitorViews.prototype.max = function( array ){
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
   PandaMonitorViews.prototype.renderHistDataset = function (name, hists,min,step,cloudColor,un) 
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
   PandaMonitorViews.prototype.pageControlHTML = function () {
   
   }
   //___________________________________________________________________________________________________
   PandaMonitorViews.prototype.stringify = function(data) {
         return JSON.stringify(data).replace(/,null,/g,",,").replace(/,null,/g,",,");
   }
   //___________________________________________________________________________________________________
   PandaMonitorViews.prototype.json = function (data) {
      var d = data;
      if (d == undefined) d = this.hists;
      location.href = 'data:application/json,' +  this.stringify(d);
   }

//___________________________________________________________________________________________________
   PandaMonitorViews.prototype.checkMobileDevice = function() {
       var r='iphone|ipod|android|palm|symbian|windows ce|windows phone|iemobile|'+
       'blackberry|smartphone|netfront|opera m|htc[-_].*opera';
       return (new RegExp(r)).test(navigator.userAgent.toLowerCase());
   }
//___________________________________________________________________________________________________
   PandaMonitorViews.prototype.createUpdateButton = function (id,bodytxt) {
      // var me = $("#"+id);
      if (bodytxt == undefined)    {bodytxt = "Update"; }
      var u = this
      $("#"+id).bind('click', function() { u.Refresh();} );
      $("#"+id).css("cursor","pointer");
      $("#"+id).css("color","red");
      $("#"+id).html(bodytxt);
   }

//___________________________________________________________________________________________________
   PandaMonitorViews.prototype.Refresh = function () {
   
      var url = location.href;
      if (url.indexOf("?") > 0) {
         if (url.indexOf("reload=yes") < 0)   {url += "&reload=yes"; }
         if (url.indexOf("&_time=") < 0 ) { url += "&_time=" + (new Date()).getTime(); }
      }
      location.href=url;
   }
//___________________________________________________________________________________________________
   PandaMonitorViews.prototype.createBookmarkButton = function (id,urlAddress,pageName,bodytxt) {
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
   PandaMonitorViews.prototype.linkUser = function (username,showtxt,tooltip) {
        /* Return the user link tfor the new platform the user's page */
        if (showtxt == undefined) showtxt = username;
        var tooltiptxt = ''; if (tooltip!= undefined) {tooltiptxt = " title='"+tooltip+ "'"; }
        var txt = "<a "+tooltiptxt+" href='"+utils().version()+"/listusers?PRODUSERNAME="+username.replace(/\s/g,"+")+ "'>" +showtxt+ "</a>";
        return txt;
   }
   //___________________________________________________________________________________________________
   PandaMonitorViews.prototype.linkUserJob = function (username,showtxt,tooltip) {
        /* Return the user link tfor the new platform the user's page */
        if (showtxt == undefined) showtxt = username;
        var tooltiptxt = ''; if (tooltip!= undefined) {tooltiptxt = " title='"+tooltip+ "'"; }
        var txt = "<a "+tooltiptxt+" href='"+utils().version()+"/listusers?PRODUSERNAME="+username.replace(/\s/g,"+")+ "'>" +showtxt+ "</a>";
        return txt;
   }

   //___________________________________________________________________________________________________
   PandaMonitorViews.prototype.linkPilotLog = function (fn,showtxt,suffix) {
      if (suffix === undefined) {suffix = 'out'}
      if (showtxt === undefined) { showtxt = suffix;}
      var lnk = "<a href='"+fn.replace('.out','.'+suffix) + "'>" +showtxt+ "</a>";
      return lnk;
   }
   //___________________________________________________________________________________________________
   PandaMonitorViews.prototype.linkLog = function (log,showtxt) {
        /* Return link to cite info page  */
        var params = ["site","type","level","count","tstart","tend"]; 
        var txt='';
        for (var i in params) {
            if (i == 3){continue;} /* skip count */
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
   PandaMonitorViews.prototype.linkCloud = function (cloud, showtxt) {
        // Return link to cite info page 
        if (showtxt == undefined) showtxt = cloud;
        var txt = "<a href='http://panda.cern.ch/server/pandamon/query?dash=clouds#" +cloud+ "'>" +showtxt+ "</a>" ;
        return txt;
   }
//___________________________________________________________________________________________________
   PandaMonitorViews.prototype.linkSite = function (site, showtxt) {
        // Return link to cite info page 
        if (showtxt == undefined) showtxt = site;
        var txt = "<a href='http://panda.cern.ch?mode=site&site=" +site+ "'>" +showtxt+ "</a>" ;
        return txt;
   }
   
//___________________________________________________________________________________________________
   PandaMonitorViews.prototype.linkHelpRequest = function (job, errortx,host,timestamp,tooltip) {
      var stcolors = { "finished": "#52D017", "failed" : "#ff6666", "running" : "#C3FDB8", "holding" : "#ffff33", "cancelled": "#FFFF00" };
      var josetid = job.jobsetID;
      if (josetid==undefined) { josetid = job.taskID; }
      if (josetid === 'None') { josetid = undefined; }
      if (josetid === undefined) { josetid = 'undefined'; }
      var user = "'"+job.prodUserID+"'"; /* utils().cleanUserID(job.prodUserID); */ 
      var txt = $("<div class='ui-icon ui-icon-mail-closed' style='cursor:pointer;display:inline-block;'>&nbsp;</div>");
      txt.attr("title", tooltip);
      errtx = "'"+ errortx.replace(/'/g, '&quot;').replace(/"/g, '&quot;') + "'";
      host = "'"+ host.replace(/'/g, '&quot;').replace(/"/g, '&quot;') + "'";
      var date =  "'"+ (new Date(1000*parseInt(timestamp))).format("yy-mm-dd HH")+ "'";
      var lparstxt = [''+job.PandaID, ''+josetid,errtx,host,date,user].join(',');
      var onclick = "{var protocol = location.protocol;\
         if ( protocol.indexOf('https:') < 0 ) {\
            var loc = ''+location;\
            loc = loc.replace('http:','https:');\
            location.replace(loc);\
         }\
         else {\
            utils().contactUs("+lparstxt +");\
         }\
      }";
      /* console.log('onclick='+ onclick); */ 
      txt.attr("onclick", onclick);
      var span = $("<span style='display:inline'></span>"); 
      span.append(utils().linkJob(job.PandaID,'#ErrorDetails',"&nbsp;"+errortx,"Click to navigate to the Find and View Log Files page"));
      //span.attr("title", tooltip);
      //span.attr('onclick',onclick);
      return [txt,span];
   }
  
//___________________________________________________________________________________________________
   PandaMonitorViews.prototype.linkWnList = function (site, jobtype,days,details, showtxt,plot,tooltip, jobstatus) {
        // Return link to job info page 
        params = {};
        if (showtxt == undefined) showtxt = site;
        if ( site != undefined)    { params['site']= site; }
        if ( jobtype != undefined) { params['jobtype']=jobtype; }
        if ( days != undefined)    { params['days']=days ;}
        if ( details != undefined && details != NaN) { params['details']=details; }
        if ( plot != undefined) { params['plot']=plot; }
        if ( jobstatus != undefined) { params['jobStatus']=jobstatus; }
        var tooltiptxt = ''; if ( tooltip != undefined) { tooltiptxt = " title='"+tooltip+"'"; }
        var txt = "<a "+tooltiptxt+" href='"+utils().version()+"/wnlist";
        if (utils().len(params) > 0)  { txt +="?"+$.param(params); }
        txt += "'>" +showtxt+ "</a>" ;
        return txt;
   }
//___________________________________________________________________________________________________
   PandaMonitorViews.prototype.addToFavorites = function (urlAddress,pageName) {
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
/* ___________________________________________________________________________________________________*/
   PandaMonitorViews.prototype.renderRootHistClient = function (hist) {
  /*
["Histogram",
   {"data":{"style":{ "width":1,"marker-color":"#000000","color":"#000099","pattern":1
                     ,"background-style":1,"marker-pattern":1,"background-color":"#000099","marker-size":1}
            ,"name":"h1f"
            ,"title":"Testrandomnumbers"
            ,"x-axis":{
                   "style":{"title-offset":1,"division":510,"label-size":0.03500000014901161,"title-font":42,"label-font":42,"title-color":"#000000","color":"#000000","title-size":0.03500000014901161,"label-offset":0.004999999888241291,"label-color":"#000000"}
                   ,"name":"xaxis"
                   ,"title":""
                   ,"color":"#000000"
                   ,"max":10
                   ,"min":0}
            ,"y-axis":{
                   "style":{"title-offset":1,"division":510,"label-size":0.03500000014901161,"title-font":42,"label-font":42,"title-color":"#000000","color":"#000000","title-size":0.03500000014901161,"label-offset":0.004999999888241291,"label-color":"#000000"}
                   ,"name":"yaxis"
                   ,"title":""
                   ,"color":"#000000"
                   ,"max":1
                   ,"min":0}
            ,"dimension":1
            ,"bins":[0,66,63,66,79,68,51,69,50,67,67,60,60,57,59,41,66,54,63,48,63,71,55,60,53,43,49,44,46,53,48,54,34,51,49,47,36,38,39,45,32,42,27,32,43,35,46,41,38,25,30,47,44,55,34,52,51,51,59,50,79,58,65,63,78,87,104,90,102,100,105,117,119,118,129,131,132,121,161,145,134,132,142,165,171,149,156,135,160,154,155,170,133,123,125,121,130,122,131,116,96,116,97,110,84,98,83,85,93,68,60,65,63,48,50,46,51,34,30,49,36,33,21,30,22,18,10,13,16,14,14,9,11,12,9,12,19,10,6,9,15,7,12,8,9,3,8,9,16,6,5,12,8,9,7,9,12,8,7,11,9,10,5,9,9,3,7,12,10,6,4,7,5,8,4,6,3,3,9,7,2,4,3,1,2,1,2,0,0,0,2,0,0,3,2,1,4,2,0,3]
           }
      ,"class":"h1f"}
   ]
   */
      var type = hist['class'];
      if (type != 'h1f') { return ; }
      var data = hist['data'];
      var style = data['style'];
      var xBins = data['bins'];
      
      var options = {};
      /*
      options['color'] = style['color'];
      options['series']['lines'] = { lineWidth  : style['width']
                                    , fill      : (style['background-style'] != 0 ) 
                                    , fillColor : style['background-color']
                                    , step      : true
                                    };
      var xaxes =  data['x-axis'];                              
      options['xaxes'] = [
                     {    show : true
                       , title: xaxes['name']
                       , min  : xaxes['min']
                       , max  : xaxes['max']
                       , color: xaxes['color']
                       , mode : null
                       , ticks: tickFactor * Math.sqrt(plotWidth)
                       , font : { size : tickFontSize}
                     } ];
      var yaxes =  data['y-axis'];
      options['yaxes'] =  [
                     {    title  :yaxes['name']
                         , show  : true 
                         , color : yaxes['color']                         
                         , position: "left" 
                         , reserveSpace: false 
                     } ];                                    
      options['crosshair']= { mode: "x" };
      options['selection']= { mode: "x" };
      options['grid'] = { hoverable: true, autoHighlight: true };
      
       var range = this.max(xBins);
       var yax = 1;
       var lPoints = xBins.length;
       var d = [];
       var un  = 1;
       for (var k = 0; k < lPoints; ++k) {
          var x = xBins[k];
          if ( x == undefined) x = 0;
          d.push([un*bin(k,min,step),x]);
       }
       var dataset = { data: d,
                , yaxis: yax
                , lines : {   fill : 0.4
                            , fillColor: null
                          }
         };
         
      var series = [];
      series.push(dataset);
      var plot = new FlotPlot;
      plot.plot = $.plot($("#"+graphId), series, options); 
      */
     
   } 
//___________________________________________________________________________________________________
   PandaMonitorViews.prototype.renderFlotHistClient = function (name, graph, opttxt) {
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
                     for (var gr in padPlot) {
                        var dataset = this.renderHistDataset(gr,padPlot,min,step,gr,un); 
                        if (dataset == undefined) continue
                        ya = ya | dataset.yaxis;
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
   PandaMonitorViews.prototype.toggleRender = function(checkbox) {
      var id = checkbox.id;
      if ( id == 'checkbox_RenderID_0') { 
         document.getElementById('checkbox_RenderID_1').checked = checkbox.checked;          
      } else {
         document.getElementById('checkbox_RenderID_0').checked = checkbox.checked;
      }
      this.renderCharts();       
  } 

 //____________________________________________________________________________________________________
   PandaMonitorViews.prototype.togglePlotScale = function(checkbox) {
      var id = checkbox.id;
      if ( id == 'form_scaleCheckBoxID_0') { 
         document.getElementById('form_scaleCheckBoxID_1').checked = checkbox.checked;
      } else {
         document.getElementById('form_scaleCheckBoxID_0').checked = checkbox.checked;
      }
      this.renderCharts();       
  } 
//____________________________________________________________________________________________________
   PandaMonitorViews.prototype.setPlotTitles = function(titles) {
      this.fPlotTitles = titles;
  }
//____________________________________________________________________________________________________
   PandaMonitorViews.prototype.plotTitle =  function(i) {
      // Return the title of the plot defined by its seq number
      return this.fPlotTitles[i];
   }
//____________________________________________________________________________________________________
   PandaMonitorViews.prototype.createSelector =  function(selector, currentValue, maxValue) {
      if (currentValue > maxValue) return;
      var l  =  selector.length;
      if ( l < maxValue) {
         // increase if needed
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
   PandaMonitorViews.prototype.showPlotControlPage = function () {
      // alert('current ' + document.currentPlotPage + '; total =' + document.totalPlotPages);
      this.renderCharts();
      for (var i=0;i<2;++i) {               
//       document.getElementById('currentPageID_'+i).innerHTML=document.currentPlotPage + ' :';
         this.createSelector( document.getElementById('currentPageID_'+i), document.currentPlotPage, document.totalPlotPages );
         document.getElementById('totalPagesID_'+i).innerHTML=document.totalPlotPages; 
      }
   }
//____________________________________________________________________________________________________
   PandaMonitorViews.prototype.showSelectedPage = function (selector){
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
   PandaMonitorViews.prototype.showNextPage = function() 
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
   PandaMonitorViews.prototype.showPreviousPage =  function () {
      var currentPlotPage = document.currentPlotPage; 
      if (currentPlotPage >  1 ) { 
         document.currentPlotPage = currentPlotPage-1;
         this.showPlotControlPage();
      }
   }
//____________________________________________________________________________________________________
   PandaMonitorViews.prototype.creatSelector =  function (fields,id) {
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
   PandaMonitorViews.prototype.showTableView = function(button) {
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
   PandaMonitorViews.prototype.createFieldSelector =  function (fields,defaultFields,id) {
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
   PandaMonitorViews.prototype.exChangeColumn2Plot =  function (add) {
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
   PandaMonitorViews.prototype.addColumn2Plot =  function () {
      this.exChangeColumn2Plot(true);
   }
//___________________________________________________________________________________________________
   PandaMonitorViews.prototype.removeColumn2Plot =  function () {
      this.exChangeColumn2Plot(false);
   }
//___________________________________________________________________________________________________
   PandaMonitorViews.prototype.jqTag = function(tag) {
      var t;
      if (typeof tag == 'string') {  if (tag[0] != '#') { tag = '#'+ tag;}  t = $(tag); }
      else { t = tag; }
      return t;
   }
//___________________________________________________________________________________________________
   PandaMonitorViews.prototype.renderAlert = function(tag,data) {
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
   PandaMonitorViews.prototype.renderHighlight = function(tag,data) {
      var t = this.jqTag(tag);
      var alext = '<div class="ui-widget ui-state-highlight ui-corner-all style="padding: 0 .3em;">\
              <p> <table><tr><td><span class="ui-icon ui-icon-info ui-state-highlight" style="margin-right: .1em;"></span></td><td>'
      alext +=  data;
      alext +=    '</td></tr></table></p></div>'
      var alert = $(alext);
      t.append(alert);
}
//___________________________________________________________________________________________________
   PandaMonitorViews.prototype.renderText = function(tag,data) {
      var t = this.jqTag(tag);
      var alext = '<div class="ui-widget">\
              <div class="ui-widget-content ui-corner-all" style="padding: 0 .7em;">\
              <p><span class="ui-icon ui-icon-script" style="float: left; margin-right: .3em;"></span><span><pre>'
      alext +=  data;
      alext +=    '\n</pre></span></p></div>'
      var alert = $(alext);
      t.append(alert);
}

//___________________________________________________________________________________________________
   PandaMonitorViews.prototype.renderDebugInfo = function(tag,main) {
      var t = this.jqTag(tag);
      var timestamp = new Date(main._system.timing.timestamp*1000);
      var params  = main.params;
      var data = main.data;
      var header = data.header;
      var rows = data.rows;
      var d = $('<div></div>');
      var tdiv = $("<div></div>");
      var total = this.len(rows);
      var hdclass = ' ui-widget-header ui-widget ';
      if ( (total == undefined) || (total == 0)) {
          hdclass += ' ui-corner-top ';
      } else {
          hdclass += ' ui-corner-all ';
      }
      tdiv.append("<div class='" +hdclass+ "'>Debug info at " +timestamp.format("yyyy-mm-dd HH:MM:ss")+' UTC</div>');
      var refresh =  params.refresh;
      if (refresh != undefined && refresh >0 ) { tdiv.append('autorefresh in ' + (refresh/60).toFixed(2)+ 'min'); }
      var table;
      if ( (total == undefined) || (total == 0)) {
         table = $("<div class='ui-state-highlight u-widget ui-widget-content ui-corner-bottom'></div>");
         table.html(' There is no debug information.');
      } else if ( total == 1) {
         table = $("<div class='ui-widget ui-corner-all'></div>")
         head = $("<div class='ui-widget-header ui-widget-content ui-corner-top'></div>");
         head.html(' Job ' +views().linkJob(rows[0][0]));
         data =  $("<div class='ui-widget-content ui-corner-bottom'></div>");
         data.html('<pre>' +rows[0][1]+ '</pre>');
         table.append(head);
         table.append(data);
      } else {
         table = $('<table class="display"></table>'); 
      }
      tdiv.append(table);
      d.append(tdiv);
      t.empty();
      t.append(d);  
      if ( total > 1) {
        this.datatable(table.uid(),tbFunc(), 25 );
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
               $('td:eq(0)', nRow).html(views().linkJob(aData[0])); 
               $('td:eq(1)', nRow).html('<pre>' +aData[1]+ '</pre>');
               return nRow;
            };
         return options;
      }
      /* --------- continue ---------- 
      if (refresh != undefined && refresh >0 ) {
         var renderDebugInfo = function(t,m) { views().renderDebugInfo(t,m); }
         views().ajax(refresh,tag,'debuginfo',params,main._host,renderDebugInfo,undefined,true);
      }
      */
   };
   /* _________________________________________________________________________ */
   PandaMonitorViews.prototype.basename = function (path, suffix) {
      // Returns the filename component of the path
      //
      // version: 1107.2516
      // discuss at: http://phpjs.org/functions/basename // + original by: Kevin van Zonneveld (http://kevin.vanzonneveld.net)
      // + improved by: Ash Searle (http://hexmen.com/blog/)
      // + improved by: Lincoln Ramsay
      // + improved by: djmix
      // * example 1: basename('/www/site/home.htm', '.htm'); // * returns 1: 'home'
      // * example 2: basename('ecra.php?p=1');
      // * returns 2: 'ecra.php?p=1'
         var b = path.replace(/^.*[\/\\]/g, '');
         if (typeof(suffix) == 'string' && b.substr(b.length - suffix.length) == suffix) {
            b = b.substr(0, b.length - suffix.length);
         }
         return b;
      }
   /* _________________________________________________________________________ */
   /* -------------------------  linkModule  ------------------------------- */   
   PandaMonitorViews.prototype.linkModule = function(module, job, items,showtxt,tooltip) {
        /* Merge the URL parameters and function ones */
         var sumtxt = ''
         var aitems = [];
         if (typeof(items) ==='string') { aitems[0] = items ; }
         else { aitems = items; } 
         var item0 = aitems[0];
         if (item0 != undefined &&  job[item0]!=undefined) {
            var lpars = $.deparam.querystring();
            if ( lpars['summary'] != undefined) {
                 lpars['summary']  = undefined;
                 if ( lpars.jobparam != undefined) { lpars.jobparam = undefined;}
                 if ( lpars.limit != undefined) { lpars.limit = undefined;}
            }
            /* exclude panda id if present */
            if ( lpars.job != undefined) { lpars.job = undefined;}
            for (var item in aitems) {
               var it = aitems[item];
               if (it != undefined && it != 'undefined' && it != '') {
                  var j = job[it];
                  if (j != undefined && j != 'undefined' && j != '')  {
                     lpars[it]=j;
                  } else if ( lpars[it] != undefined ) { 
                     lpars[it] = undefined; 
                  }
               }
            }
            if (showtxt==undefined || showtxt=='') { showtxt=job[item0] ; }
            var tooltiptxt = '';  if ( tooltip != undefined) { tooltiptxt = " title='" +tooltip+"' "; }
            sumtxt= "<a "+tooltiptxt+" href='"+utils().version(module)+ "?"+$.param(lpars).replace('=undefined','=') +"'>"+showtxt+"</a> ";
         }
         return sumtxt;
      }

   /* _______________________________linkModulePars ________________________________ */
   PandaMonitorViews.prototype.linkModulePars = function(module, value, pars,showtxt,tooltip) { 
      var sumtxt = '';
      var p = views().extractTimeParams();
      $.extend(p,pars);
      if (showtxt==undefined || showtxt=='') { showtxt=value; }
      if (value != undefined && value != '' && value != 0) {
         if (showtxt==undefined || showtxt=='') { showtxt=value; }
         var tooltiptxt = '';  if ( tooltip != undefined) { tooltiptxt = " title='" +tooltip+"' "; }
         sumtxt= "<a "+tooltiptxt+" href='"+utils().version(module)+ "?"+$.param(p).replace('=undefined','=') +"'>"+showtxt+"</a> ";
      } else if ( showtxt!=undefined && showtxt!=0 ) { 
         sumtxt= showtxt;
      } 
      return sumtxt;
   }      
  /* _______________________________linkTaskPars ________________________________ */
   PandaMonitorViews.prototype.linkTaskListPars = function(value, pars,tooltip) {
      return views().linkModulePars('tasks/listtasks1',value, pars,undefined,tooltip);
   }      
  /* _______________________________linkTaskPars ________________________________ */
   PandaMonitorViews.prototype.linkDefTaskListPars = function(value, pars,tooltip) {
      return views().linkModulePars('tasks/listtasks',value, pars,undefined,tooltip);
   }
   /* _______________________________linkJobMergingPars ________________________________ */
   PandaMonitorViews.prototype.extractTimeParams = function(skip) {
      /* skip defines an array of the timeparams to skip */ 
      var tkeys = ['hours','days','tstart','tend'];
      var params =$.deparam.querystring();
      var tpars = {};
      for (var tk in tkeys) {
         var curKey = tkeys[tk];
         if (curKey != undefined && $.inArray(curKey,skip) < 0 && (params[curKey] !== undefined) ) { 
            tpars [curKey] = params[curKey];
         }
      }
      return tpars;
   }

   /* _______________________________linkJobMergingPars ________________________________ */
   PandaMonitorViews.prototype.linkMergingJobPars = function(value, pars,showtxt,tooltip) {
     if (pars === undefined) { pars = {}; }
     pars.processingType='usermerge';
     return views().linkModulePars('jobinfo',value, pars,showtxt,tooltip);
   }      

   /* _______________________________linkJobInfoPars ________________________________ */
   PandaMonitorViews.prototype.linkJobInfoPars = function(value, pars,showtxt,tooltip) {
      return views().linkModulePars('jobinfo',value, pars,showtxt,tooltip);
   }      
   /* _________________________________linkJobInfo____________________________ */
   PandaMonitorViews.prototype.linkJobInfo = function(job, items,showtxt,tooltip) {
         return views().linkModule('jobinfo', job, items,showtxt,tooltip);
   }
   /* _________________________________linkJob ____________________________ */
   PandaMonitorViews.prototype.linkJob = function(job,showtxt,tooltip) {
         return views().linkModulePars('jobinfo', job, {job:job},showtxt,tooltip);
   }
   /* ______________________  linkJediInfo ___________________________________*/
   PandaMonitorViews.prototype.linkJediInfo = function(value, pars,showtxt,tooltip) {   
         return views().linkModulePars('jedi/taskinfo',value, pars,showtxt,tooltip);   
   }
   /* _________________________________showPandaJobStatus____________________________ */
   PandaMonitorViews.prototype.showPandaJobStatus = function(tg,maindata,jedi) {
            var th = views().jqTag(tg);
            var jobtype = maindata.jobtype;
            var status = "States";
            var refresh =  maindata.refresh;
            if (refresh == undefined) {refresh = -35; }
            var delay =  maindata.delay;
            var hours =  maindata.hours; 
            if (jobtype != undefined) { status = jobtype; }
            th.empty();
            var dashboard  = $("<div class='ui-widget ui-content ui-corner-all'>Loading . . . "+status+"</div>");
            th.append(dashboard);
            var lpars = { summary:true, limit:undefined}
            if (jedi == undefined) { lpars['jobparam']= 'jobStatus'; }
            else {lpars['taskparam']= 'status'; } 
            if ( jobtype != undefined ) { lpars['jobtype']=jobtype ; }
            if ( hours != undefined ) { lpars['hours']=hours; }
            function appendJobSum(tag,main) {
               var _js =[ [status, jedi == undefined ? "jobStatus" : "status" ] ];
               var prerunLabel = ['defined','assigned','waiting','activated','pending','sent','starting'];
               var finishingLabel = ['holding','transferring','merging'];
               var _jobsummary = {};
               for (var r in _js) { 
                 var rr = _js[r];
                 var key = rr[0];
                 var val = rr[1];
                _jobsummary[key] = val;  
               }
               /*______________________________________________________________________________________________________*/
               function preRun(infostat,labels) {
                  /* Define the 'Pre-Run' job table meta field  */                 
                  var prerun = 0;
                  for (var  i in infostat) {
                     var nxt = infostat[i];
                     if ( jQuery.inArray(nxt[0],labels) >=0 ) { prerun+=nxt[1]; }
                  }
                  return prerun;
               }
               if (main.info.length > 0 &&  main.header != undefined ) {
                  var info = main.info;
                  var infoArray = [['prerun',preRun(info,prerunLabel)]];
                  for (var i in info) {
                     var nxt = info[i];                      
                     if ( jQuery.inArray(nxt[0],prerunLabel) <0 ) {
                        if ( nxt[0] === 'running' )  {
                           infoArray.push( nxt ) ;
                           infoArray.push(['finishing',preRun(info,finishingLabel)]);
                        } else if ( jQuery.inArray(nxt[0],finishingLabel) <0 ) {
                           infoArray.push( nxt ) ;
                        }
                      }
                  }
                  var dinfo  = {
                                "data"   : infoArray
                               ,"header" : main.header
                               ,"jobsummary" : _jobsummary
                               ,"module"  : main.module
                              };
                  var renPars = $.extend({},lpars);
                  renPars['summary']  = undefined;
                  if (jedi==undefined) {
                     renPars['jobparam'] = undefined;
                  } else {
                     renPars['taskparam'] = undefined;
                  }
                  renPars['limit']    = 200;
                  var nxdiv = views().renderJobSummary(dashboard,dinfo,renPars,jedi);
                  nxdiv.show();
                  //$.sparkline_display_visible();
               }
            }
            var aj = new AjaxRender();
            th.data('ai',aj);
            var module = jedi == undefined ? 'jobinfo' : 'jedi/taskinfo'; 
            aj.download('jobsummaryid',appendJobSum, module ,lpars,undefined, refresh,delay);
         }

   /* _____________________________ renderJobFiles _________________________________ */
   PandaMonitorViews.prototype.renderJobFiles = function(tag,data,job) 
   {
      var aj = new AjaxRender();
      th.data('ai',aj);
      var module = jedi == undefined ? 'jobinfo' : 'jedi/taskinfo'; 
      aj.download('jobsummaryid',appendJobSum, module ,lpars,undefined, refresh,delay);
   }
 /* _____________________________ renderMemoryPlots _________________________________ */
   PandaMonitorViews.prototype.renderMemoryPlots = function(tag,data,lpars) {
      var checkbox = $("<input type='checkbox'>"); 
      function plothist(tg,hsts,w,h){ 
            var pl = new pmPlot(tg);                  
            pl.style = {title:checkbox.prop('checked') };
            pl.plotContainer(hsts, w, h,checkbox.prop('checked'));
      }
      var thisWindowSize = utils().windowSize();
      var nChartColumns = 2;
      var plotWidth  = Math.ceil(0.8 * thisWindowSize[0]/nChartColumns);
      var plotHeight = plotWidth/1.9; /*  Math.ceil(thisWindowSize[0]/(3*nChartColumns)) + 90; */
      var thisTag =  views().jqTag(tag);
      thisTag.empty();
      var width = plotWidth; 
      var height = plotHeight;
      var topPlot = $("<div class='ui-widget ui-widget-content'></div>");
      /* topPlot.append(checkbox); */
      topPlot.css('width','97%').css('height',''+2*height+'px').css('overflow','auto');
      topPlot.resizable( { handles: "se, sw, s"});

      var topTable = $("<table width=100%></table>");
      topPlot.append(topTable);
      var colspan = "";
      var etimefactor  = 1.;
      var errfactor= 2.0;
      var vmPeakMean  = $("<td colspan='2'></td>");   
      var vmPeakMax  = $("<td  colspan='2'></td>"); 
      var RSSMean  = $("<td colspan='3'></td>"); 
      var peakrow = $("<tr></tr>"); 
      var rssrow  = $("<tr></tr>"); 
      peakrow.append(vmPeakMean); peakrow.append(vmPeakMax);
      rssrow.append(RSSMean);
      topTable.append(peakrow); topTable.append(rssrow);
      views().showSelection(tag,undefined,'jobs/jobram')
      thisTag.append(topTable);
      var hists = data.hist;
      function fixlabel(h,title) {
         h.attr.yaxis.title = 'Jobs';
         h.attr.xaxis.title = title == undefined? 'min' : title;
      }
      if ( hists != undefined ) {
         if (hists.vmPeakMean != undefined) { fixlabel(hists.vmPeakMean, 'Gb'); plothist(vmPeakMean,[hists.vmPeakMean],etimefactor*width,height); }
         if (hists.vmPeakMax  != undefined) { fixlabel(hists.vmPeakMax,'Gb'); plothist(vmPeakMax,[hists.vmPeakMax],etimefactor*width,height); }
         if (hists.RSSMean    != undefined) { fixlabel(hists.RSSMean,'Gb');plothist(RSSMean,[hists.RSSMean],errfactor*width/2,height); }
      }   
      if ( hists == undefined || hists.lenghth <=0) {
         views().renderHighlight(thisTag,'There was no Panda Job Metric to report');
      }
   }

  
   /* _____________________________ renderTimingPlots _________________________________ */
   PandaMonitorViews.prototype.renderTimingPlots = function(tag,data,lpars) {
      var checkbox = $("<input type='checkbox'>"); 
      function plothist(tg,hsts,w,h){ 
            var pl = new pmPlot(tg);                  
            pl.style = {title:checkbox.prop('checked') };
            pl.plotContainer(hsts, w, h,checkbox.prop('checked'));
      }
      var thisWindowSize = utils().windowSize();
      var nChartColumns = 2;
      var plotWidth  = Math.ceil(0.8 * thisWindowSize[0]/nChartColumns);
      var plotHeight = plotWidth/1.9; /*  Math.ceil(thisWindowSize[0]/(3*nChartColumns)) + 90; */
      var thisTag =  views().jqTag(tag);
      thisTag.empty();
      var width = plotWidth; 
      var height = plotHeight;
      var topPlot = $("<div class='ui-widget ui-widget-content'></div>");
      /* topPlot.append(checkbox); */
      topPlot.css('width','97%').css('height',''+2*height+'px').css('overflow','auto');
      topPlot.resizable( { handles: "se, sw, s"});
      views().showSelection(tag,undefined,'jobs/jobtiming')
      var topTable = $("<table width=100%></table>");
      topPlot.append(topTable);
      var colspan = "";
      var etimefactor  = 1.;
      var errfactor= 1.4;
      var getjob   = $("<td colspan='2'></td>");   
      var stagein  = $("<td  colspan='2'></td>"); 
      var execute  = $("<td colspan='3'></td>"); 
      var stageout = $("<td colspan='2'></td>"); 
      var setup    = $("<td colspan='2'></td>"); 
      var cpu      = $("<td colspan='3'></td>"); 
      var exerow = $("<tr></tr>"); 
      var stagerow  = $("<tr></tr>"); 
      exerow.append(execute); exerow.append(cpu);
      stagerow.append(setup); stagerow.append(stagein);stagerow.append(stageout);
      topTable.append(exerow); topTable.append(stagerow);
      thisTag.append(topTable);
      var hists = data.hist;
      function fixlabel(h,title) {
         h.attr.yaxis.title = 'Jobs';
         h.attr.xaxis.title = title == undefined? 'min' : title;
      }
      if ( hists != undefined ) {
         if (hists.execute != undefined) { fixlabel(hists.execute, 'hours'); plothist(execute,[hists.execute],etimefactor*width,height); }
         if (hists.cpu     != undefined) { fixlabel(hists.cpu,'hours');      plothist(cpu,[hists.cpu],etimefactor*width,height); }
         if (hists.setup   != undefined) { fixlabel(hists.setup);            plothist(setup,[hists.setup],errfactor*width/2,height); }
         if (hists.stagein != undefined) { fixlabel(hists.stagein);          plothist(stagein,[hists.stagein],errfactor*width/2,height); }
         if (hists.stageout != undefined) { fixlabel(hists.stageout);        plothist(stageout,[hists.stageout],errfactor*width/2,height); }
      }   
      if ( hists == undefined || hists.lenghth <=0) {
         views().renderHighlight(thisTag,'There was no Panda Job Pilot Timing to report');
      }
   }

   /* _____________________________ renderErrorPlots _________________________________ */
   PandaMonitorViews.prototype.renderErrorPlots = function(tag,data,lpars) {
      /* ------------------------------------------
      #      all       -  time
      #                -  errors
      #      errors    -  exe (thisError)
      #                -  job
      #                -  pilot
      #                -  . . .
      #      item      -  (itm,e,errorcode)
      #      opt       -  sum  (boolean)
      #                -  item (boolean)
      #                -  time (boolean)
      # ------------------------------------------
      */
      var checkbox = $("<input type='checkbox'>"); 
      function plothist(tg,hsts,w,h){ 
            var pl = new pmPlot(tg);                  
            pl.style = {title:checkbox.prop('checked') };
            pl.plotContainer(hsts, w, h,checkbox.prop('checked'));
      }
      var thisWindowSize = utils().windowSize();
      var optsum  = true;  var optitem = false; var opttime = false; var opterr = false;
      if (data.opt != undefined) {
         optsum  = data.opt.sum;
         optitem = data.opt.item;
         opttime = data.opt.time;       
         opterr  = data.opt.error;
      }
      var order = data.order;
      var nChartColumns = 4;
      var plotWidth  = Math.ceil(0.8 * thisWindowSize[0]/nChartColumns);
      var plotHeight = plotWidth/1.6; /*  Math.ceil(thisWindowSize[0]/(3*nChartColumns)) + 90; */
      var thisTag =  views().jqTag(tag);
      thisTag.empty();
      var module = "jobs/joberror";
      if ( document.location.pathname.indexOf(module)>=0 ) {
         views().showSelection(tag,undefined,module);
      }
      var width = plotWidth; 
      var height = plotHeight;
      var topPlot = $("<div class='ui-widget ui-widget-content'></div>");
      /* topPlot.append(checkbox); */
      var thisfunc = this;
      /* checkbox.on('click', function() {thisfunc(tag,data);} ); */
      topPlot.css('width','97%').css('height',''+2*height+'px').css('overflow','auto');
      topPlot.resizable( { handles: "se, sw, s"});
      var errcodesref = $("<div><a href='http://pandamon.cern.ch/errorcodes'>Error Codes</a></div>");
      topPlot.append(errcodesref); 

      var topTable = $("<table width=100%></table>");
      topPlot.append(topTable);
      var colspan = "";
      var etimefactor  = 1;
      var errfactor  = 1.95;
      if (!opttime) { 
          colspan = " colspan='2'";
          etimefactor = errfactor;
      }             
      var errrow = $("<td colspan='2'></td>");
      var timerow = $("<tr></tr>"); 
      var htime = $("<td></td>"); 
      var eitems = $("<td></td>"); 
      var etime = $("<td"+colspan+"></td>");
      if (opttime) { timerow.append(htime); }
      if (opterr)  { timerow.append(eitems); }
      timerow.append(errrow);
      timerow.append(etime);
      topTable.append(timerow);

      thisTag.append(topTable);
      var hists = data.hist;
      if ( hists != undefined ) {
         var allhists = hists.all;
         if (allhists != undefined) {
            if (allhists.errors != undefined) { plothist(errrow,[allhists.errors],errfactor*width,height); }
            if (allhists.time   != undefined) { plothist(htime, [allhists.time],width,height);   }
            if (allhists.items  != undefined) { plothist(eitems,[allhists.items],width,height);   }
         }
         var allerr = hists.errors;
         if ( allerr != undefined ) {
              var histsarray = [];
              for (var nxhist in allerr) {
                  histsarray.push(allerr[nxhist]);
              }
              if (histsarray.length > 0) {
                plothist(etime,histsarray,etimefactor*width,height);
              }
         }
         var rowcount = 0;
         var itemrow = undefined;
         /* ---------------------- */
         function selecth(hs) {
            var nxitem =  hists[hs];
            var histsarray = [];
            for (var nxhist in nxitem) {
                if ( nxhist != 'time' && nxhist != 'errors') {
                    histsarray.push(nxitem[nxhist]);
                }
            }
            if (histsarray.length > 0) {
               if (rowcount ==0 ) {
                  itemrow = $("<tr></tr>");
                  topTable.append(itemrow);
               }
               var td = $("<td></td>"); itemrow.append(td);
               plothist(td,histsarray,width,height);
               if ( rowcount == ( nChartColumns-1) )  { rowcount = 0;}
               else {rowcount += 1;}
            } else if (h != 'all') {
               /*
               thisTag.append("<span class='ui-icon ui-icon-info' style='display:inline'>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span><span style='display:inline'> &nbsp;&nbsp;There was no <b>" +h+ "</b> error to report. &nbsp;&nbsp;&nbsp;  </span>");
               */
            }
         }
         /* ========================= */

         if (order != undefined && order.length >0) {
            for (var nxhist in order) {
               h = order[nxhist];
               selecth(''+h);
            }  
         } else {            
            for (var h in hists) {
               if ( (h == 'all') || (h=='errors' )) { continue; }
               selecth(h);
            }
         }
      }   
      if ( hists == undefined || hists.lenghth <=0) {
         views().renderHighlight(thisTag,'There was no Panda Job error to report');
      }
   }

   /* _____________________________ renderErrorPlots _________________________________ */
   PandaMonitorViews.prototype.showSelection = function(tag,selection,module, ncols,extralist) {
      /* if (selection === undefined) { return; } */ 
      if (ncols === undefined) { ncols = 4;} 
      var p = $('<p>');p.css('padding','0px');
      var puid = p.uid();
      var lpars = $.deparam.querystring();
      if (selection !== undefined) {
         var s= selection;
         if ( lpars.prodUserName == undefined) {
            p.append($(utils().linkJobs(s.cloud, lpars.jobtype, s.jobStatus, lpars.hours, s.computingSite
                ,'<b>The classic Panda Page is available here</a>' 
                , undefined, s.modificationHost
                , undefined
                , s.prodSourceLabel,undefined
                , lpars.plot
                , lpars.job
                , lpars.taskID
                , lpars.jobsetID
                )));
          }
         if ( selection.dump != undefined ) { selection = {dump:selection.dump} ;} 
         else {  selection = {};   }
      }
      var t = $("<table class='ui-corner-all ui-widget ui-widget-header' width='100%' bgcolor=lightblue></table>");
      var tuid = t.uid();
      t.data('lpars',$.extend({},lpars));
      var rcounter =  0;
      var nrows    = 0;
      var r;
      var range = {};
      var selector =  $.extend({},lpars);
      /* exclude plot */
      $.extend(selector, selection);
      if (selector.plot !== undefined) {selector.plot = undefined;}
      var helpicon =  $("<div class='ui-icon ui-icon-help  ui-corner-all ui-widget ui-help-clearfix ui-widget-header' style='cursor:help;display:inline-block;padding:0 0 1 1;' title='Click to see the Web API doc'/>");
      var crossicon = $("<div class='ui-icon ui-icon-close ui-corner-all ui-widget ui-help-clearfix ui-widget-header' style='display:inline-block;cursor:pointer;padding:0 0 1 1;' title='Click to close this bar '/>");
      for (var s in selector) {
         var val = selector[s];
         if (val === undefined) { continue; }
         if (('tstart' == s) || ('tend' == s)) {
            try {
            val = new Date(val).format("yy-mm-dd HH");
            range[s]=val;
            } catch (err) {} 
         }
         var q = $("<td></td>"); q.css('font-size','85%').css('padding','0px');
         var txtbox = $("<input class='ui-corner-all ui-widget ui-widget-highlight ui-help-clearfix' style='padding: 3px;' title='Edit the value (or comma-separated values) of the <"+s+"> filter' type='text' name='"+s+ "' value='"+val+"' size='" +val.length+"'>");
         txtbox.uid();
         var cbox =  $("<input title='Uncheck the box to remove the <"+s+"> filter' type='checkbox' name='"+s+ "' value='"+val+"'>");
         cbox.prop("checked",true);
         var cbui = cbox.uid();
         var onlclick = "{ \
               var t = $('#"+tuid+"');\
               var lptext = $.extend({},t.data('lpars'));\
               var tb = $('#"+tuid+" input:text');\
               tb.each( function() { var s = $(this).attr('name'); var v = $(this).attr('value');  var lp = lptext; var sl = s.toLowerCase(); lp[s] = 'undefined'; if (sl == 'jeditaskid') {lp['task']='undefined';lp[s]=v;} else if (sl=='pandaid'){lp['job']=v;} else { lp[s]=v; }  } );\
               tb = $('#"+tuid+" input:not(:checked):not(:text)');\
               var lpcheck = {};\
               tb.each( function() {  var s = $(this).attr('name'); var v = $(this).attr('value'); var lp = lpcheck; var sl = s.toLowerCase(); if (sl == 'jeditaskid') {lp['task']='undefined';} else if (sl=='pandaid'){lp['job']='undefined';} lp[s]='undefined'; } );\
               var lp =  $.extend({},lptext);\
               $.extend(lp,lpcheck);\
               for (var p  in lp) { if (lp[p]==='undefined') {lp[p]=undefined;}} \
               var aj = t.data('aj');\
               if (aj == undefined) {\
                 aj = new AjaxRender();\
                 t.data('aj',aj);\
               } else {\
                 aj.cancel();\
               }\
               var newloc =aj.url('"+module+"',lp);\
               window.location=newloc;\
               }";
              /* aj.download('"+tag+"',views().renderJobInfo,'jobinfo',lp); */
               
         cbox.attr("onclick",onlclick);
         txtbox.attr("onchangeme", onlclick);

         q.append(cbox); q.append(txtbox); q.append("<b>&nbsp;:&nbsp; " +s+ "</b> ");
         if  (rcounter%ncols==0) {
           nrows += 1;
           r = $("<tr></tr>");
           var q1 = $("<td style='padding:0'></td>");
           r.append(q1);
           t.append(r);
           if (rcounter===0) {
              q1.append(helpicon);
              helpicon.on('click', function() { $("#navhelp").clone().dialog({width:'740px'}); });
              /* helpicon.button({icons: { primary: "ui-icon-help" } }); */ 
           } 
         }
         rcounter++;
         r.append(q);
         if (nrows === 1 && rcounter == ncols)  {
            var q1 = $("<td style='padding:0;'></td>");
            q1.append(crossicon);
            r.append(q1);
            crossicon.attr('onclick', "$('#"+puid+"').hide();" );
         }
         views().autocomplete(txtbox,extralist);
      }
      /*
      if (nrows >1) {
       helpicon.attr('rowspan',nrows).css('vertical-align','center');
       var addcols =  ncols - rcounter%ncols;
       for (var i =0; i < addcols; i++) {r.append("<td></td>");} 
      }
      */
      t.append(r);
      p.append(t);
      if (range.tstart != undefined) {
         p.append($("<p>"));
         p.append(utils().selectDateRange(range.tstart ,range.tend,"datarangeID"));
      }
      if (tag != undefined ) {
        var thisTag =  views().jqTag(tag);
        thisTag.append(p);
      }
      return p;
   }

   /* _____________________________ renderJobInfo _________________________________ */
   PandaMonitorViews.prototype.renderJobInfo = function(tag,main,lpars) {
      var buildJob_color = '#ffcc99';
      var runJob_color = '#ffffbb';
      var module = main.module == undefined? "jobinfo" : main.module;
      var _js = main.jobsummary;
      var _jobsummary = {};
      if (lpars == undefined) {
         lpars = $.deparam.querystring();
      }
      var VO = lpars.VO==undefined ? 'ATLAS' : lpars.VO.toUpperCase();
      for (var r in _js) { 
           var rr = _js[r];
           var key = rr[0];
           var val = rr[1];
          _jobsummary[key] = val;  
      }
      var stcolors = { "finished": "#52D017", "failed" : "#ff6666", "running" : "#C3FDB8", "holding" : "#ffff33", "cancelled": "#FFFF00" };
      /*______________________________________________________________________________________________________*/
      function showPandaId(pandaid) {
         var a = $("<a>");
         a.attr("href",utils().version("jobinfo?job=" + pandaid));
         a.html(pandaid);
         return a;
      }
      /*______________________________________________________________________________________________________*/
      function showUserName(username,text) {      
        var lpars = $.deparam.querystring();
        lpars['prodUserName']=username;
        a= views().linkJobInfoPars(username,lpars,undefined,"Click to fetch the " +username+"'s jobs"); 
        //var a = views().linkUser(username);
        if (text==undefined || text ==false) {
           a =  $(a);
         }
         return a;
      }
      /*______________________________________________________________________________________________________*/
      function cleanJob(job,keepTime) {
         /*  Tidy up the job record */
         if (job.jobsetID==undefined && job.jobDefinitionID) { job.jobsetID = job.jobDefinitionID;  }
         if ( job.prodUserName==undefined && job.prodUserID) { job.prodUserName = job.prodUserID; }
         if ( job.prodDBlock==undefined ) { job.prodDBlock = '';}
          /*  Convert times to real times */
         if (keepTime == undefined || keepTime==false) {
            var timeFields = ['modificationTime', 'creationTime', 'startTime', 'endTime' ];
            for ( var p in timeFields)  {
               var inx = timeFields[p];
               if ( job[inx] != undefined) {
                  itime = job[inx]*1000;
                  t = new Date(itime);             
                  job[inx] = t;
               }
            }
         }
      }
      /*______________________________________________________________________________________________________*/
      function formatSecs(msecs) {
         var secs = (msecs/1000).toFixed(0);
         var mins = (secs/60).toFixed(0);;
         secs = secs % 60;         
         var hours = (mins/60).toFixed(0);;
         mins = mins % 60;
         var days = (hours / 24).toFixed(0);
         hours = hours % 24;
         var out = '';
         if  (days && days >=1)   { out += days  + "d "; }
         if  (hours && hours>=1)  { out += hours.toFixed(0) + ":"; }
         else { out += '00:'} 
         if  (mins&& mins>=1)   { out += mins.toFixed(0) ; }
         else { out += '00'} 
         if  (secs >= 1) { out += ":"+ secs.toFixed(0); }
         return out;
      }
      /*______________________________________________________________________________________________________*/
      function label(job) {
        var typetxt='';
        var lbl = job['prodSourceLabel'];
        var thisjobtype  = utils().getJobType(job.transformation);
        if ( lbl == 'user' ||  thisjobtype.indexOf('runAthena') == 0) {
             typetxt = 'analysis-run';
         } else if ( lbl == 'panda' || thisjobtype.indexOf('buildJob') == 0 ) {
            typetxt = 'analysis-build';
         } else if ( lbl == 'managed') {
            typetxt = 'production';
         } else {
            typetxt = lbl;
         }
         return  typetxt;
      }
      /*______________________________________________________________________________________________________*/
      function preRun(status) {
         /* Define the 'Pre-Run' job table meta field  */
         var prerunLabel = ['defined','assigned','waiting','activated'];
         var prerun = 0;
         for (var l in prerunLabel) {
            var lbl = prerunLabel[l];
            if (status[lbl] != undefined) { prerun += status[lbl] }
         }
          /* + status.stagein + status.staged */
         if (status.starting != undefined) { prerun +=  status.starting; }
         return prerun;
      }
      /*______________________________________________________________________________________________________*/
      function countSetStatus(set) {
         var jobs =  set.jobs;
         var status = {};
         var iStatus = set.header['jobStatus'];
         if (iStatus == undefined) {
             iStatus =   set.header['status'];
         }
         var all = 0;
         for (var i in jobs) {
            all++;
            var job = jobs[i];
            var sname = job[iStatus];
            if (status[sname] === undefined) {status[sname] = 0;}
            status[sname]++;
         }
         status['all'] = all;
         status['pre'] = preRun(status);
         return status;
      }
      /*______________________________________________________________________________________________________*/
      function rowSetSummary(setid,set) {
         var row = new Array(13);
         row[0]  = {sid: setid,set: set};
         row[1]  = set.created; 
         row[2]  = set.latest
         sts = countSetStatus(set);
         var njobs = sts.all;
         row[3]  = njobs;
         row[4]  = sts.pre == undefined ? 0 : sts.pre ;
         row[5]  = sts.running == undefined ? 0 : sts.running;
         row[6]  = sts.holding == undefined ? 0 : sts.holding;
         row[7]  = sts.finished == undefined ? 0 : sts.finished;
         row[8]  = sts.failed == undefined ? 0 : sts.failed;
         row[9]  = sts.cancelled == undefined ? 0 : sts.cancelled;
         row[10] = set.mergingJobs == undefined ? 0 : (set.mergingJobs.all === undefined ? 0:set.mergingJobs.all) ;
         row[11] = set.build== undefined ? '' :  set.build;
         row[12] = set.site == undefined || set.site == null || set.site=='null' ? ' '  : set.site;
         return row;
      }
      
      /*_________________________________________________________________*/      
      function showJobSummary(job) {
         cleanJob(job);
         var row = $("<tr></tr>");
         var extraspan = 2;
         if (job.jobStatus == 'failed' ||   job.jobStatus == 'cancelled') {extraspan=3;}
         var id      = $("<td align=center rowspan="+extraspan+"></td>"); row.append(id);
         var jobname = $("<td></td>");     row.append(jobname);
         var status  = $("<td></td>");     row.append(status);
         var created = $("<td></td>");     row.append(created);
         var tostart = $("<td style='text-align:center;'></td>");     row.append(tostart);
         var duration= $("<td style='text-align:center;'></td>");     row.append(duration);
         var ended   = $("<td></td>");     row.append(ended);
         var site    = $("<td></td>");     row.append(site);
         var priority= $("<td></td>");     row.append(priority);
         id.append(showPandaId(job.PandaID)); id.append($("<br>")); id.append(showUserName(job.prodUserName)); 
         if ( job.workingGroup != undefined && job.workingGroup != '') { id.append($("<br>")); id.append("<b>" +linkJobInfo(job,['workingGroup'])+ "</b>");}
         var trans  = job.transformation;
         if (trans == undefined || trans == null) { trans = 'unknown'; job.transformation = trans; }
         var lbl    = job.prodSourceLabel;
         var pkg    = job.homepackage;
         var name   = job.jobName;
         var attempt= job.attemptNr;
         var tlink = utils().getJobType(trans);
         if (tlink != undefined && tlink != '') {
            if (job.jobsetID != undefined && job.jobsetID != '') {
              var jobsetid =linkJobInfo(job,['jobsetID','prodUserName'],undefined,'Click to fetch the jobs from '+ job.jobsetID+ " jobset for "+ job.prodUserName);
              jobname.append("jobsetID="+jobsetid); 
            } 
            if (tlink != '' && tlink != undefined) {
               jobname.append(" <a href='"+trans+ "'>"+tlink+"</a>");
            }
            if (VO != 'ATLAS' && name != undefined && name != '') {
              jobname.append('<br>'+name);
            }
         } else if (lbl != 'managed'  && trans !== undefined && trans !== null && trans.indexOf('http') != 0 )  {
            var ttxt = trans.replace('share/','');
            if (VO ==='ATLAS') {
                jobname.append("trans=" +ttxt+ ", pkg=" +pkg);
            } else {
               jobname.append("trans=" +ttxt);
            }
         } else if (  trans !== undefined && trans !== null && trans.indexOf('http') == 0) {
            var script = views().basename(trans);
            jobname.append("trans=user script <a href='" +trans+ "'>" +script+ "</a>");
         } else {
            jobname.append(linkJobInfo(job, ['jobName','taskID'] )+ " " +attempt);
         }
         if (utils().getJobType(job.transformation).indexOf('buildJob') == 0) {
            jobname.css('background-color',buildJob_color);
         } else {
            jobname.css('background-color',runJob_color);
         }
         status.css('text-align','center'); 
         if (stcolors[job.jobStatus]) {status.css("background-color",stcolors[job.jobStatus]); } 
         if ( job.taskBufferErrorCode == 106 || job.taskBufferErrorCode == 107 ) { 
            if (job.attemptNr != undefined) {
               status.append(job.attemptNr+1+" retried"); 
            } else {
               status.append("retried"); 
            }
         }
         else { status.append(job.jobStatus); } 
         created.append(job.creationTime.format("yyyy-mm-dd HH:MM"));
         tostart.append(formatSecs(job.startTime - job.creationTime));
         if (job.endTime == undefined || job.endTime ==0) {job.endTime =job.modificationTime; }
         var endTime =  job.endTime < job.modificationTime ? job.endTime : job.modificationTime;
         duration.append(formatSecs(endTime-job.startTime));
         ended.append(endTime.format("yyyy-mm-dd HH:MM")) ; /* .format("yyyy-mm-dd HH:MM")); */
         if (VO === 'ATLAS') {
             site.append(utils().linkCloud(job.cloud) +"/ "+utils().linkPilots(job.computingSite)+", " + label(job)); /*linkJobInfo(job,'processingType')); */
         } else {
             site.append(VO+"/ "+utils().linkPilots(job.computingSite)); /*linkJobInfo(job,'processingType')); */
         }
         priority.append(job.currentPriority);
         return row;
      }
      /*_________________________________________________________________*/      
      function dtJobSummaryTitle(foot) {
        /* Create thead for job summary table  */
        /*  <b>Showing jobset modified from %s to %s<b> </td>" % (stime, etime) */
        var header = [ "<small><center>PandaID</small>"
                      ,"<small><center>Job</center></small>"
                      ,"<small><center>Status</center></small>"
                      ,"<small><center>Created</center></small>"
                      ,"<small><center>Time to Start</center></small>"
                      ,"<small><center>Duration</center></small>"
                      ,"<small><center>Ended/ Modified</center></small>"
                      ,"<small><center>Cloud / Site,type</center></small>"
                      ,"<small><center>Priority</center></small>"
                      ,"<small><center>Data</center></small>"
                      ,"<small><center># r</center></small>"
                      ];
         var dtHeader = utils().openTableHeader(header);
         return dtHeader;
      }

      /*_________________________________________________________________*/      
      function dtSummaryTitle(foot) {
        /* Create thead for job summary table  */
        /*  <b>Showing jobset modified from %s to %s<b> </td>" % (stime, etime) */
        var header = [ "User:jobsetID</small>"
                      ,"Created"
                      ,"Latest"
                      ,"Jobs"
                      ,"Pre-run"
                      ,"Running"
                      ,"Holding"
                      ,"Finished"
                      ,"Failed"
                      ,"Cancelled"
                      ,"Merging"
                      ,"buildJob"
                      ,"Site"
                      ];
         var dtHeader = utils().openTableHeader(header);
         return dtHeader;
      }
 /*_________________________________________________________________*/      
   function makeJoblist(tgj,dsset) {
      var set = dsset.set;
      var sid = dsset.sid;
      var dtHeader = dtJobSummaryTitle();
      var dtRows = [];
      var header = set.header;
      var jobs = set.jobs;
      var setCount = 0;
      var userid = sid.split(':');
      var jobsetID = undefined; var taskID = undefined; var JediTaskID = undefined;
      if (userid[1]='A') { jobsetID = userid[2]; }
      else if ( userid[1]='J') { JediTaskID = userid[2]; }
      else { taskID =  userid[2]; }
      for (var pandaid in jobs) {
         var j = jobs[pandaid];
         var job = {PandaID:parseInt(pandaid),jobsetID:jobsetID, taskID: taskID, JediTaskID:JediTaskID};
         for (var h in header)  {
            job[h] = j[header[h]];
         }
         var row =  rowjobSummary(job);
         dtRows.push(row);
      }
      setCount = dtRows.length;
       /* ------ tbFunc --------- */ 
      function tbFunc() {
         var options = {};
         if (setCount > 64) {
              var displayTotal =  setCount;
              if (setCount>300) displayTotal = 300; 
              var half = displayTotal/2;
              options= { "iDisplayLength": displayTotal
                       , "aLengthMenu": [ [-1,half], ["ALL" ,half] ]
                       };
         } else if (setCount > 6){
             options={ "bPaginate": false,"bLengthChange": false, "bInfo": false };
         } else {
             options={ "bPaginate": false,"bLengthChange": false, "bInfo": false,"sDom":'<"H"r>t<"F">' };
         }
         /*
        options['bPaginate']=false;
        var thisWindowSize = utils().windowSize();
        options['sScrollY']=Math.ceil(0.95*thisWindowSize[1]);
        options['bScrollCollapse'] = true;
        */
        options["aoColumnDefs"] = [ 
                              { sWidth: "2em;", aTargets: [ 0 ] }
                             ,{ sWidth: "6em;", aTargets: [ 1 ] , sClass: "pmWide"}
                             ,{ sWidth: "6em;", aTargets: [ 2 ] }
                             ,{ sWidth: "4em;", aTargets: [ 3 ], sClass: "pmDate" }
                             ,{ sWidth: "4em;", aTargets: [ 4 ], sClass: "alignRight"  }
                             ,{ sWidth: "4em;", aTargets: [ 5 ], sClass: "alignRight" }
                             ,{ sWidth: "4em;", aTargets: [ 6 ], sClass: "pmDate" }
                             ,{ sWidth: "4em;", aTargets: [ 7 ], sClass: "alignRight" }
                             ,{ sWidth: "4em;", aTargets: [ 8 ], sClass: "alignRight" }
                             ,{ "bVisible": false, "aTargets": [ 9 ] }
                             ,{ "bVisible": true, "aTargets": [ 10 ], sClass: "alignRight" } /* attemptNr to do yet */
                          ];
         options['bAutoWidth'] = false;
         options["aaData"]    = dtRows;
         options["aoColumns"] = dtHeader;
         options["fnRowCallback"]= function( nRow, aData, iDisplayIndex, iDisplayIndexFull ) 
            {
               $('td:eq(0)', nRow).html(showPandaId(aData[0]));
               var job = aData[9];
               $('td:eq(2)', nRow).css("background-color",stcolors[aData[2]]).css('text-align','center');
               if (job.jobStatus =='failed' ||   job.jobStatus  == 'cancelled')  {
                  var valstat = job.jobStatus;
                  if ( job.taskBufferErrorCode == 106 || job.taskBufferErrorCode == 107 ) { 
                      valstat = "retried"; 
                     if (job.attemptNr != undefined) {
                        svalstat = job.attemptNr+1+" "+valstat; 
                     }
                  }
                  var span =  "<span class='ui-icon ui-icon-alert' style='float: left; margin-right: .3em;'></span><span>"+utils().linkJob(job.PandaID,'#ErrorDetails','<b title="Click to navigate to the Find and View Log Files page">'+valstat+'</b></span>');
                  // var help = views().linkHelpRequest(job,errcode.join(': '),main._system.host[0],main._system.timing.timestamp,'Click to send the Help Request E-mail.');
                  // for (var h in help) {  span.append(help[h]);  }
                  $('td:eq(2)', nRow).html(span);
               }
               if (utils().getJobType(job.transformation).indexOf('buildJob') == 0) {
                  $('td:eq(1)', nRow).css('background-color',buildJob_color);
               } else {
                  $('td:eq(1)', nRow).css('background-color',runJob_color);
               }
               $('td:eq(10)', nRow).attr("title","the number of the job re-submits");
               return nRow;
            };
         return options;
      }
      var tb = $('<table cellpadding="0" cellspacing="0" border="0" class="display" width=100%></table>');       
      tgj.append(tb);
      var dialog = $('<div></div>');
      var dtb =utils().datatable(tb.uid(),tbFunc(), setCount );
      // return dtb;
      $('#'+ tb.uid() + ' tbody tr').each( function () {
         var aPos = dtb.fnGetPosition( this ); 
         var aData = dtb.fnGetData( aPos );
         var job = aData[9];
         var status = job.jobStatus;
         if (status == 'failed' ||   status  == 'cancelled')  {
            var bkcolor = stcolors[status];
            var tbl = $("<table border=0 cellpadding=0 cellspacing=0 width=100%></table>");
            var ierrrow = $("<tr></tr>");
            var ierr = $("<td style='color:red;'></td>");ierr.css('color','red').css('background-color',bkcolor);
            var errcode = findError(job,main.errorCodes);
            var getfiles = $('<div>Error details:&nbsp;</div>');getfiles.css({ display:'inline',cursor:'pointer','font-weight':'bold','text-decoration':'underline'});
            var filedialog =  $('<div></div>').css('display','none'); filedialog.uid();
            getfiles.uid();
            getfiles.attr('title',"Click to navigate to the Find and View Log Files page");
            getfiles.attr('onclick',"var tg = $('#" +filedialog.uid()+"'); views().queryJobFiles(tg,"+JSON.stringify(job)+",true);");
            ierr.append(getfiles);ierr.append(filedialog);
            var help = views().linkHelpRequest(job,errcode,main._system.host[0],main._system.timing.timestamp,'Click to send the Help Request E-mail.');
            for (var h in help) {  ierr.append(help[h]);  }
            tbl.append(ierrrow);ierrrow.append(ierr); 
            dtb.fnOpen( this ,tbl.get(0).outerHTML,  "info_row" );
         }
        } );
      return dtRows.length;
   }
/*_________________________________________________________________*/      
   function rowtaskSummary(task) {
      cleanJob(task,true);
      var row = new Array(10);
      row[0]     = task.JediTaskID;
      var name   = task.jobName;
      var trans  = task.transPath;
      var lbl    = task.prodSourceLabel;
      var pkg    = task.transUses;
      var name   = task.taskname;
      var tlink = utils().getJobType(trans);
      var jobname = ''
      if (tlink != undefined && tlink != '') {
         if (task.jobsetID != undefined && task.jobsetID != '') {
           var jobsetid =linkJobInfo(task,['jobsetID','prodUserName']);
           jobname += "jobsetID="+jobsetid; 
         } 
         if (tlink != '' && tlink != undefined) {
            jobname += " <a href='"+trans+ "'>"+tlink+"</a>";
         }
         if (VO != 'ATLAS' && name != undefined && name != '') {
           jobname += '<br>'+name;
         }
      } else if (lbl != 'managed'  && trans.indexOf('http') != 0 )  {
         var ttxt = trans.replace('share/','');
         if (VO ==='ATLAS') {
             jobname += "trans=" +ttxt+ ", pkg=" +pkg;
         } else {
            jobname += "trans=" +ttxt;
         }
      } else if ( trans.indexOf('http') == 0) {
         var script = views().basename(trans);
         jobname += "trans=user script <a href='" +trans+ "'>" +script+ "</a>";
      } else {
         jobname += linkJobInfo(task, ['jobName','taskID'] );
      }
      row[1]=jobname;
      
      row[2] = task.jobStatus;
      row[3] = task.creationTime;
      row[4] = task.tostart;
      row[5] = task.duration;
      row[6] = task.endt;
      if (VO === 'ATLAS') {
         row[7] = utils().linkCloud(task.cloud) +"/ "+utils().linkPilots(task.computingSite)+", " + label(task); /*linkJobInfo(job,'processingType')); */
      } else {
         row[7] = VO+"/ "+utils().linkPilots(task.computingSite); /*linkJobInfo(job,'processingType')); */
      }
      row[8] = task.currentPriority;
      row[9] = task;
      return row;
   }
 /*_________________________________________________________________*/      
   function rowjobSummary(job) {
      cleanJob(job,true);
      var row = new Array(10);
      row[0]     = job.PandaID;
      var name   = job.jobName;
      var trans  = job.transformation;
      var lbl    = job.prodSourceLabel;
      var pkg    = job.homepackage;
      var attempt= job.attemptNr;     
      var tlink = utils().getJobType(trans);
      var jobname = ''
      if (tlink != undefined && tlink != '') {
         if (job.jobsetID != undefined && job.jobsetID != '') {
           var jobsetid =linkJobInfo(job,['jobsetID','prodUserName']);
           jobname += "jobsetID="+jobsetid; 
         } 
         if (tlink != '' && tlink != undefined) {
            jobname += " <a href='"+trans+ "'>"+tlink+"</a>";
         }
         if (VO != 'ATLAS' && name != undefined && name != '') {
           jobname += '<br>'+name;
         }
      } else if (lbl != 'managed' &&  trans !== undefined && trans !== null && trans.indexOf('http') != 0 )  {
         var ttxt = trans.replace('share/','');
         if (VO ==='ATLAS') {
             jobname += "trans=" +ttxt+ ", pkg=" +pkg;
         } else {
            jobname += "trans=" +ttxt;
         }
      } else if ( trans !== undefined && trans !== null &&trans.indexOf('http') == 0) {
         var script = views().basename(trans);
         jobname += "trans=user script <a href='" +trans+ "'>" +script+ "</a>";
      } else {
         jobname += linkJobInfo(job, ['jobName','taskID'] )+ " " +attempt;
      }
      row[1]=jobname;
      
      row[2] = job.jobStatus;
      row[3] = job.creationTime;
      row[4] = job.tostart;
      row[5] = job.duration;
      row[6] = job.endt;
      if (VO === 'ATLAS') {
         row[7] = utils().linkCloud(job.cloud) +"/ "+utils().linkPilots(job.computingSite)+", " + label(job); /*linkJobInfo(job,'processingType')); */
      } else {
         row[7] = VO+"/ "+utils().linkPilots(job.computingSite); /*linkJobInfo(job,'processingType')); */
      }
      row[8] = job.currentPriority;
      row[9] = job;
      row[10]=attempt;
      return row;
   }
 /*_________________________________________________________________*/      
   function makeJobsets(tag,din) {   
     /* Can we use it ? */
      var info   = din.jobsets;
      var header = din.header;
      var l = utils().len(info);
      var selection = $("<div></div>");
      var counter = $("<div></div>");
      selection.append(counter);
      var setTable  = $("<div></div>");
      selection.append(setTable);
      var p = $("<p>");
      counter.append(p);
      if (l <= 0) {
         counter.html("No jobsets matched selection");
      } else {
         var dtHeader = dtSummaryTitle();
         var setCount = 0;
         var jobIndx =  utils().name2Indx(header);
         var dtRows = [];
         for (var j in info)  {
            setCount++;
            var set = info[j];
            set['header'] = jobIndx;
            dtRows.push(rowSetSummary(j,set));
         }
         counter.html("<p title='The list may be limited. Append the &limit=N parameter to increase it'>" + setCount + " sets matched selection");
         function pasreUsrds(idcolumn)  {
            var setid = idcolumn.sid;
            var usrsetid = setid.split(":");
            return usrsetid;
         }
         function usrsetids(idcolumn)  {
            var set = idcolumn.set;
            var usrsetid = pasreUsrds(idcolumn);
            var htmlcol =  showUserName(usrsetid[0],true); 
            if (usrsetid[1]==='A') {
               htmlcol +=  '<br>'+ linkJobInfo({'jobsetID': usrsetid[2],'prodUserName':usrsetid[0] },['jobsetID','prodUserName'],undefined,'Click to fetch the jobs from '+ usrsetid[2]+ ' jobset for '+ usrsetid[0]);
            } else if (usrsetid[1]==='J') {
               htmlcol +=  '<br>'+ linkJobInfo({'JediTaskID': usrsetid[2],'prodUserName':usrsetid[0] },['JediTaskID','prodUserName'],undefined,'Click to fetch the jobs from the Jedi Task #' + usrsetid[2]+ ' for '+ usrsetid[0]);
            } else   {
               htmlcol +=  '<br>'+ linkJobInfo({'taskID': usrsetid[2],'prodUserName':usrsetid[0] },['taskID','prodUserName'],undefined,'Click to fetch the jobs from '+ usrsetid[2]+ ' task for '+ usrsetid[0]); 
            }
            if ( set.workingGroup != undefined && set.workingGroup != '') { 
               htmlcol += '<b>:  ' +linkJobInfo({'workingGroup':  set.workingGroup},['workingGroup'],undefined,'Click to fetch the jobs for '+set.workingGroup+ ' working group')+ '</b>';
            }
            return htmlcol;
         }
         var aoColumnDefs = [ 
                              {  sWidth: "9em", sClass: "pmWide"} 
                             , { sWidth: "5.2em",  sClass: "pmDate" }
                             ,{ sWidth: "5.2em",  sClass: "pmDate"  }
                             ,{ sWidth: "3.5em",  sClass: "alignRight" }
                             ,{ sWidth: "4em",  sClass: "alignRight"  }
                             ,{ sWidth: "4em",  sClass: "alignRight" }
                             ,{ sWidth: "4em",  sClass: "alignRight" }
                             ,{ sWidth: "4em",  sClass: "alignRight" }
                             ,{ sWidth: "4em",  sClass: "alignRight" }
                             ,{ sWidth: "4em",  sClass: "alignRight" }
                             ,{ sWidth: "4em" }
                             ,{ sWidth: "4em" }
                             ,{ sWidth: "10em" }
                          ];
         var header = [ "User:jobsetID"
                      ,"Created"
                      ,"Latest"
                      ,"Jobs"
                      ,"Pre-run"
                      ,"Running"
                      ,"Holding"
                      ,"Finished"
                      ,"Failed"
                      ,"Cancelled"
                      ,"Merging"
                      ,"buildJob"
                      ,"Site"
                      ];

         var tbtxt = ' <table cellpadding="0" cellspacing="0" border="0" class="display">';
         tbtxt += '<thead>';
         for ( var r in header) {
              tbtxt += '<th class="'+ aoColumnDefs[r].sClass+' ">' + header[r] + '</th>'; 
         }
         tbtxt += "</thead><tbody>";
         for (var r in dtRows) {
          tbtxt += '<tr>';
          tbtxt += '<td>' + dtRows[r].join('</td><td>') + '</td>';
          tbtxt += '</tr>';
         }
         tbtxt += '</tbody></table>';
         var tb = $(tbtxt);      
         selection.append(tb);
         $(tag).append(selection);
         var tbuid = tb.uid();
         
      /* ------ endOfRunning --------- */ 
      function endOfRunning(status,label, allstatus) {
      /* Generate the html code with the label followed by the color  bar  */
         var cancelled = status.cancelled != undefined  ? status.cancelled  :0;
         var failed    = status.failed  != undefined  ? status.failed  :0;
         var finished  = status.finished != undefined  ? status.finished  :0;
         var all       = status.all  != undefined  ? status.all  :0;
         var running   = status.running  != undefined  ? status.running  :0;
         var total     = failed + finished + cancelled + running;
         var field     = '&nbsp;';
         var processing = all>total;
         if ( total>0 ) { 
            running   = 100*running/all;
            cancelled = 100*cancelled/all;
            failed    = 100*failed/all;
            finished  = 100*finished/all;
            total     = failed + finished + cancelled + running;
            if (total < 100) { /* rounding */
               if  ( running   > 0)   {  running   +=1; total += 1; }
               else if (total < 100 && finished > 0 ) { finished +=1; total += 1; }
               else if (total < 100 && finished > 0 ) { finished +=1;total += 1; }
               else if (total < 100 && cancelled > 0) { cancelled +=1; }
            }
            if (label == undefined) { if (running>0 || processing ) {label = ''+ status.running; } else { label='end';} }
            field = "<center title='"+status.all+ " jobs (the entire jobset) were completed'><b><font size='-2'>"+label+"</font><b></center>";
            function pandaColor(colorCode) {
               var code = '';
               if ( colorCode.length > 0) {
                  code = "http://pandamon.cern.ch/static/images/Panda";
                  if (colorCode.length > 1 ) {
                     code +=colorCode[0].toUpperCase() + colorCode.substring(1);
                  } else {   
                     code +=colorCode[0].toUpperCase();
                  }
                  code += "Color.png";
               }
               return code;
            }
         /* ______________________________________________________________________________________________________ */
            function  colorHtml(color,value) {
               var fld = '<img title="About '+value.toFixed(1)+'% of all jobs '+color+'" style="padding:0px;" src="'+pandaColor(color)+'" height=10px width="'+parseInt(value)+'%">';
               return fld;
            }
            field += "<center>";
            if (status.finished == all ) {
               field +=  colorHtml('Finished',finished) ;
            } else {   
               if (running >0 )
                  field +=  colorHtml('Running',running) ;
               if (finished >0 )
                  field +=  colorHtml('Finished',finished) ;
               if (failed >0)
                  field +=  colorHtml('Failed',failed) ;
               if (cancelled >0)
                  field +=  colorHtml('Cancelled',cancelled);
            }
            field += "</center>";
      } else if (allstatus && all>0 ) {
            field = "<center title='"+status.all+" jobs have been submitted'>"+label+"</center>";
      }
      return field;
   }
    
      /* ------ tbFunc --------- */ 
         function tbFunc() {
            var options = {};
            if (setCount > 64) {
                 var displayTotal =  setCount;
                 if (setCount>300) displayTotal = 300; 
                 var half = displayTotal/2;
                 options= { "iDisplayLength": displayTotal
                          , "aLengthMenu": [ [displayTotal, -1,half], [displayTotal, "ALL" ,half] ]
                          };
            } else if ( setCount > 10) {
                options={ "bPaginate": false,"bLengthChange": false, "bInfo": false };
            } else {
                options={ "bPaginate": false,"bLengthChange": false, "bInfo": false,"sDom":'<"H"r>t<"F">' };
            }
            var sparkOpt = {       width:'8em'
                                  ,type:'pie'
                                  ,sliceColor:[stcolors['holding'],stcolors['running'], stcolors['finished'], stcolors['failed']]
                           };
            options["bPaginate"]=false;
            var thisWindowSize = utils().windowSize();
            /*   http://stackoverflow.com/questions/13178039/datatables-header-alignment-issue */
            if (navigator.userAgent.indexOf('Firefox') >=0 && false) {
               /*   http://stackoverflow.com/questions/13178039/datatables-header-alignment-issue */
               options['sScrollY']=Math.ceil(0.95*thisWindowSize[1]);
               if  ( dtRows.length > 60) { options['bScrollCollapse'] = true; }
            }           
            options['iDisplayLength'] = undefined;
            options['aLengthMenu'] = undefined;
            options['bLengthChange'] = undefined;
            options['bAutoWidth'] = false;
            /* 
                http://datatables.net/forums/discussion/comment/48037
                https://datatables.net/forums/discussion/16147/header-width-alignment
            */
            
            var aoColumnDefs = [ 
                                 {   sClass: "pmWide"} 
                                , {   sClass: "pmDate" }
                                ,{  sClass: "pmDate"  }
                                ,{  sClass: "alignRight" }
                                ,{ sClass: "alignRight"  }
                                ,{ sClass: "alignRight" }
                                ,{ sClass: "alignRight" }
                                ,{  sClass: "alignRight" }
                                ,{  sClass: "alignRight" }
                                ,{  sClass: "alignRight" }
                                ,{ }
                                ,{ }
                                ,{   sClass: "pmWide"}
                             ];
            if (navigator.userAgent.indexOf('Firefox') >=0 || true ) {
               for (var df in aoColumnDefs) {
                 /*  aoColumnDefs[df]['sTitle'] = header[df]; */ 
                   aoColumnDefs[df]['aTargets'] = [parseInt(df)];
               }
               options["aoColumnDefs"] = aoColumnDefs; 
            }
            options["aaData"]    = dtRows;
            options["fnRowCallback"]= function( nRow, aData, iDisplayIndex, iDisplayIndexFull ) 
               {  
                  var set = aData[0].set;
                  
                  var njobs  = aData[3]; var prerun  = aData[4]; var running = aData[5]; 
                  var holding= aData[6]; var finished= aData[7]; var failed  = aData[8];
                  var cancelled = aData[9]; var retried = set.retried;
                  var merging = aData[10];
                  var totaljobs = finished+failed+cancelled;
                  var pievalues = [ 
                     njobs - running -finished-failed-cancelled
                   , running
                   , finished
                   , failed+cancelled
                  ];
                  var status = {cancelled:cancelled
                          ,failed:failed
                          ,all:njobs
                          ,total:totaljobs
                          ,finished:finished
                          ,running:running
                          };
                          
                  var plus = $('<span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span>').addClass('ui-icon').addClass('ui-icon-circle-plus').css('display','inline');
                  plus.css("position: absolute; float:right;");
                  set['uid'] = plus.uid();
                  set['tbuid'] = tbuid;
                  var usrdv = $("<div title='Click to see the datasets and the job list'>"+usrsetids(aData[0])+"</div>").css('cursor','pointer');
                  usrdv.append(plus);
                  usrdv.css('word-wrap','break-word');

                  $('td:eq(0)', nRow).html(usrdv);
                  $('td:eq(1)', nRow).css("background-color",runJob_color).html(set.created);
                  $('td:eq(2)', nRow).html(set.latest);
                  if (prerun == undefined || prerun ==0)   { $('td:eq(4)', nRow).empty(); }
                  if (njobs == undefined  || njobs == 0)   { $('td:eq(3)', nRow).empty();  }
                  else if (retried != undefined  && retried > 0 ) {
                     var u = pasreUsrds(aData[0]);
                     var njobcols  =$('td:eq(3)', nRow);
                     njobcols.empty();
                     njobcols.append("<div>"+(njobs-retried)+ "</div");
                     var tpars = {};
                     if  (u[1]==='P' ) { tpars['taskId'] = u[2]; }
                     else if  (u[1]==='J' ) { tpars['JediTaskID'] = u[2]; }
                     else if  (u[1]==='A' ) { tpars['jobsetID'] = u[2]; }
                     tpars['prodUserName']=u[0];
                     tpars['jobStatus']='retried';
                     njobcols.append("<div title='failed and retried jobs'><small>+"+views().linkJobInfoPars(retried, tpars,retried,"Show the failed retired jobs")+ "</small></div");
                  }
                  if (lpars.jobStatus == undefined) {
                      var tcell =  endOfRunning(status);
                      $('td:eq(5)', nRow).html(tcell);
                  } else if (running >0)  {
                     $('td:eq(5)', nRow).css({'background-color':stcolors['running'],'text-align':'center'});
                  } else { $('td:eq(5)', nRow).empty(); }
                  /*
                  var pieid = tbuid+"_"+iDisplayIndexFull;
                  var pie = "<span style='display:inline' id='"+pieid+"'></span>";
                  var runningdiv = "<div>"+ ( running>0?running:'') + "</div>";
                  runningCell = pie+runningdiv;
                  $('td:eq(5)', nRow).html(runningCell);
                  */
                  if (holding  >0) { $('td:eq(6)', nRow).css("background-color",stcolors['holding']);  } else { $('td:eq(6)', nRow).empty();  }
                  if (finished >0) { $('td:eq(7)', nRow).css("background-color",stcolors['finished']); } else { $('td:eq(7)', nRow).empty();  }
                  if (failed   >0) { $('td:eq(8)', nRow).css("background-color",stcolors['failed']);   } else { $('td:eq(8)', nRow).empty();  }
                  if (cancelled>0) { $('td:eq(9)', nRow).css("background-color",stcolors['cancelled']);} else { $('td:eq(9)', nRow).empty();  }
                  if (merging >0)  { 
                     var u = pasreUsrds(aData[0]);
                     var tpars = {};
                     if  (u[1]==='P' ) { tpars['taskId'] = u[2]; }
                     else if  (u[1]==='J' ) { tpars['JediTaskID'] = u[2];  }
                     else if  (u[1]==='A' ) { tpars['jobsetID'] = u[2];    }
                     tpars['prodUserName']=u[0];
                     $('td:eq(10)', nRow).html(views().linkMergingJobPars(merging, tpars,merging,"Show the merging jobs' status"));
                  } else { 
                      $('td:eq(10)', nRow).empty();  
                  }
                  $('td:eq(12)', nRow).css("background-color",runJob_color).html(utils().linkPilots(set.site));
                  var build = aData[11];
                  if (build != undefined && build !='') {
                     $('td:eq(11)', nRow).css("background-color",buildJob_color).html(showPandaId(build));
                  }
                 //  $('#'+pieid).sparkline([1,2,3,4,5]); // sparkOpt);
                  return nRow;
               };
            return options;
         }
         /* $("#id_jobsummary_table").dataTable({"bProcessing": true,"bJQueryUI": true});*/
      }
      var dtb =utils().datatable(tbuid,tbFunc(), 25 );
      /* dtb.fnAdjustColumnSizing( false ); */
      var olddsinfo = undefined;
      var  dsinfo =  undefined;
      $('#'+ tbuid + ' tbody tr').on('click',function () {
         if ( olddsinfo != undefined && dtb.fnIsOpen(olddsinfo) ) { 
              dsinfo.hide('slow');
              dtb.fnClose(olddsinfo); 
              dsinfo.remove();
              dsinfo = undefined;
              olddsinfo = undefined;
         }
         if (!dtb.fnIsOpen(this) ) {
               olddsinfo = this;
               var aPos = dtb.fnGetPosition( this ); 
               // Get the data array for this row
               var aData = dtb.fnGetData( aPos );  
               var set = aData[0];
               var tdid= $('#'+ set.set.tbuid);
               var olduid = tdid.data('olduid');
               if (olduid != undefined && olduid != set.set.uid  ) { 
                 $('#'+olduid).show();
               }
               olduid = set.set.uid;
               tdid.data('olduid', olduid);
               $('#'+olduid).hide();
               var addDsI = $(addDsInfo(set));
               dsinfo = $("<div style='padding:0px;'></div>");
               dsinfo.attr('title','Click the folder icon to manage the job table');
               var dsatble = $("<div id=setIdDsInfoDiv style='padding:0px;'>"+addDsI.get(0).outerHTML+"</div>");
               dsinfo.append(dsatble);
               var jbtabl = $("<div id=setIdInfoDiv></div>");
               dsinfo.append(jbtabl);
               dtb.fnOpen( this ,dsinfo.get(0),  "info_row" );
               /* jbtabl.hide(); */ 
               var njobs = makeJoblist(jbtabl,set);
               $('#setIdInfoIconId').attr('title','Click to  toggle the '+ njobs+ ' job'+  ((njobs>1)?'s':'') + ' list table');
               $('#setIdInfoIconId').on('click',function()
                  { 
                     if ( jbtabl.is(':hidden') ) {
                        $(this).removeClass('ui-icon-folder-collapsed').addClass('ui-icon-folder-open');
                     } else {
                       $(this).removeClass('ui-icon-folder-open').addClass('ui-icon-folder-collapsed');
                     }
                     jbtabl.toggle('slow');
                  }
               );
               / *$('#setIdInfoIconId').click(); */
         }
        } );
      if  ( dtRows.length == 1) { $('#'+ tbuid + ' tbody tr').click(); }
      return selection;  
   }
   /*_________________________________________________________________*/      
   function addDsInfo(dtset) {
      var set = dtset.set;
      var io = "<table border=0 cellpadding=1 cellspacing=0 width=100% id=setIdInfo>";
      var trcount =0;
      if ( set.build != undefined) { 
         io += "<tr style=background-color:"  +buildJob_color+ "><td style='padding:0;'><span id=setIdInfoIconId  title='Click to toggle the job list table' style='cursor:pointer;display:inline;padding:3px;' class='ui-icon ui-icon-folder-open'>&nbsp;&nbsp;&nbsp;&nbsp;</span></td><td>";
         io += "<b>libDS:&nbsp;</b>" + utils().linkJobDataset(set.libDS,set.site);
         io += "</td>";
         io += "</tr>";
         trcount++;
      } else {
         if  (set.inDS != undefined &&  set.inDS != "") {
            var rowspan = '';
            if  (set.outDS != undefined &&  set.outDS != "") {
               rowspan = ' rowspan=2 ';
            }
            io += "<tr style='background-color:" +runJob_color+";' >"
            io += "<td" +rowspan+ " style='padding:0px 0px 0px 8px;'><span  id=setIdInfoIconId title='Click to toogle the job list table' style='display:inline;padding:3px;cursor:pointer;' class='ui-icon ui-icon-folder-open'>&nbsp;&nbsp;&nbsp;</span></td>"
            io += "<td>";
            io += "<b>In:&nbsp;</b>" + utils().linkJobDataset(set.inDS,set.site);
            io += "</td>";
            io += "</tr>";
            trcount++;
         }
         if  (set.outDS != undefined &&  set.outDS != "") {
            io += "<tr style=background-color:" +runJob_color+">"
            if  (set.inDS == undefined ||  set.inDS == "") {
               io += "<td style='padding:0;'><span id=setIdInfoIconId  title='Click to toogle the job list table' style='display:inline;padding:3px;cursor:pointer;' class='ui-icon ui-icon-folder-open'>&nbsp;&nbsp;&nbsp;&nbsp;</span></td>"
            }
            io += "<td>";
            io += "<b>Out:&nbsp;</b>" + utils().linkJobDataset(set.outDS,set.site);
            io += "</td>";
            io += "</tr>";
            trcount++;
         }
         if (trcount === 0) {
            io += "<tr style=background-color:red><td style='padding:0;'><span id=setIdInfoIconId  title='Click to toogle the job list table' style='cursor:pointer;display:inline;padding:3px;' class='ui-icon ui-icon-folder-open'>&nbsp;&nbsp;&nbsp;&nbsp;</span></td><td>";
            io += "<b>The Job definition is corrupted. Neither output nor input DS are provided </b>";
            io += "</td>";
            io += "</tr>";
         }
      }
      io += "</table>";
      return io;
   }
      /*_________________________________________________________________*/      
      function jobSummaryTitle(foot) {
        /* Create thead for job summary table  */
         var ttitle = (foot == undefined || foot == false) ? $("<thead></thead") : $("<tfoot></tfoot")
         var row = $("<tr></tr>");
         var cols = [  $("<th class='ui-state-default' align=center><small>PandaID, Owner, Working group</small></th>"),$("<th class='ui-state-default' align=center><small>Job</small></th>")
                      ,$("<th class='ui-state-default' align=center><small>Status</small></th>")         ,$("<th class='ui-state-default' align=center><small>Created</small></th>")
                      ,$("<th class='ui-state-default' align=center><small>Time to start</small></th>")  ,$("<th class='ui-state-default' align=center><small>Duration</small></th>")
                      ,$("<th class='ui-state-default' align=center><small>Ended/Modified</small></th>") 
                      ,$("<th class='ui-state-default' align=center><small>" + (VO ==='ATLAS'? 'Cloud /site, type' : 'VO / site')+"</small></th>")
                      ,$("<th class='ui-state-default' align=center><small>Priority</small></th>") 
                     ];
         for (var c in cols) { row.append(cols[c]); }
         ttitle.append(row);
         return ttitle;
      }
      /* _______________________________________________________________*/      
      function jobSummaryTable() {
         var title = $("<table border=1 cellpadding=2 cellspacing=0 class='display' id='id_jobsummary_table' width='100%'></table>");
         title.append(jobSummaryTitle());
         return title;
      }
      /*_________________________________________________________________*/      
      function findError(job,err) {
         var errarray = [];
         for (var c in err) {
            var joberror = job[c];
            if (joberror != undefined && joberror != '' && joberror !=0) {
               var errrval = err[c][joberror]
               if (errrval == undefined) { errrval = ' &nbsp;<b>'+c + ': </b>' + joberror; }
               else {errrval =  ' &nbsp;<b>'+ errrval[0]  + ': </b>' +  errrval[1]; } 
               errarray.push(errrval);
            }
         }
         if (errarray.length>0) {
            return errarray.join(";&nbsp; ");
         } else {   
            return  "unknown: It is unknown why the job "+job.PandaID+ " was "+ job.jobStatus;
         }
      }
      /*_________________________________________________________________*/      
      function checkPars (header) {
          var checked = true;
          var minset = "jobsetID jobDefinitionID prodUserName prodUserID prodDBlock transformation jobStatus PandaID workingGroup creationTime endTime modificationTime startTime cloud computingSite processingType currentPriority destinationDBlock".split(' '); 
          for (var h in minset) {
             if ( $.inArray(minset[h],header) == -1) { checked = false; break;}
          }
          return checked;
      }
      /*_________________________________________________________________*/      
      function showJob(tableBody,job) {
         tableBody.append(showJobSummary(job));
         if ( job.jobStatus == 'failed' ||   job.jobStatus == 'cancelled')  {
            var row = $("<tr></tr>");row.css('color','red');
            var ierr      = $("<td colspan=8></td>"); 
            var errcode = findError(job,main.errorCodes);
            var getfiles = $('<div>Error details:&nbsp;</div>');getfiles.css({ display:'inline',cursor:'pointer','font-weight':'bold','text-decoration':'underline'});
            var filedialog =  $('<div></div>').css('display','none'); filedialog.uid();
            getfiles.uid();
            getfiles.attr('title',"Click to navigate to the Find and View Log Files page");
            getfiles.attr('onclick',"var tg = $('#" +filedialog.uid()+"'); views().queryJobFiles(tg,"+JSON.stringify(job)+",true);");
            ierr.append(getfiles);ierr.append(filedialog);
            /* ierr.append("<b>&nbsp;&nbsp;"+errcode.join(':&nbsp;') +"</b>"); */
            var help = views().linkHelpRequest(job,errcode,main._system.host[0],main._system.timing.timestamp,'Click to send the Help Request E-mail.');
            for (var h in help) {  ierr.append(help[h]);  }
            row.append(ierr);
            tableBody.append(row);    
         }
         var row = $("<tr></tr>");
         var io      = $("<td colspan=8></td>"); row.append(io);
         var ds = '';
         if ( utils().getJobType(job.transformation).indexOf('buildJob') == 0) {
           io.css('background-color',buildJob_color);
           ds += "<b>libDS:&nbsp;</b>" + utils().linkJobDataset(job.destinationDBlock,job.computingSite);
         } else {
            io.css('background-color',runJob_color);
            if  (job.prodDBlock != undefined &&  job.prodDBlock != "") {
               ds += "<b>In:&nbsp;</b>" + utils().linkJobDataset(job.prodDBlock,job.computingSite);
            }
            if  (job.destinationDBlock != undefined &&  job.destinationDBlock != "") {
               if (ds != '') {ds += "<br>";}
               ds += "<b>Out:&nbsp;</b>" + utils().linkJobDataset(job.destinationDBlock,job.computingSite);
            }
         }
         io.html(ds);
         tableBody.append(row);
      }

      /*_________________________________________________________________*/      
      function showJobsFromSet(set) {
        /* Can we use it ? */
         var jobs   = set.jobs;
         var header = set.header;
         var statCounters= countSetStatus(set);
         var l = statCounters.all;
         var selection = $("<div></div>");
         var p = $("<p>");
         selection.append(p);
         if (l <= 0) {
            selection.html("No job matched selection");
         } else {
            if (l > 1) {
               selection.html("<p title='The list may be limited. Append the &limit=N parameter to increase it'>" + l+ " jobs matched selection");
            } else if (l == 1) {
               selection.html("<p>" + l+ " job matched selection");
            }
            var jobTable = jobSummaryTable();
            selection.append(jobTable);
            var tableBody = $("<tbody></tbody>"); 
            jobTable.append(tableBody);
            for (var j in info)  {
               var thisInfo = info[j];
               var job = utils().zip(header,thisInfo);
               showJob(tableBody,job);
            }

            if (l > 10) { jobTable.append(jobSummaryTitle(true)); /* Add the footer the long table */ }
            /* $("#id_jobsummary_table").dataTable({"bProcessing": true,"bJQueryUI": true}); */
         }
         return selection;
      }
      /*_________________________________________________________________*/      
      function showJobs(din) {
        /* Can we use it ? */
         var info   = din.data;
         var header = din.header;
         var l = info.length;
         var selection = $("<div></div>");
         var p = $("<p>");
         selection.append(p);
         if (l <= 0) {
            selection.html("No job matched selection");
         } else {
            if (l > 1) {
               selection.html("<p title='The list may be limited. Append the &limit=N parameter to increase it'>" + l+ " jobs matched selection");
            } else if (l == 1) {
               selection.html("<p>" + l+ " job matched selection");
            }
            var jobTable = jobSummaryTable();
            selection.append(jobTable);
            var tableBody = $("<tbody></tbody>"); 
            jobTable.append(tableBody);
            for (var j in info)  {
               var thisInfo = info[j];
               var job = utils().zip(header,thisInfo);
               showJob(tableBody,job);
            }

            if (l > 10) { jobTable.append(jobSummaryTitle(true)); /* Add the footer the long table */ }
            /* $("#id_jobsummary_table").dataTable({"bProcessing": true,"bJQueryUI": true}); */
         }
         return selection;
      }
      /* ---------------------  linkJobInfo  ------------------------- */
      function linkJobInfo(job, items,showtxt,tooltip) {
         return views().linkJobInfo(job, items,showtxt,tooltip)
      }
     /* ---------------------  appendJobSummary ---------------------- */   
      function appendJobSummary(tag,main) {
         var dhead = main.header;  
         if (main.info.length > 0 && dhead != undefined ) {
            var dinfo    = {  
                          data      : main.info
                         ,module    : main.module
                         ,rows      : main.info
                         ,header    : dhead 
                         ,jobsummary: _jobsummary
                        };
            var tg = dhead[0] + "_"+tag;
            var nxdiv = views().renderJobSummary(tg,dinfo);
            nxdiv.show();
            $.sparkline_display_visible();
         }
       }
     /* ---------------------  fetchUserStat ---------------------- */   
      function fetchUserStat(tag,usernames) {
          var userstat = $("<div>. . . Loading the user job summary . . . </div>");
          var old = $("<div><b>Click to access the <a href='"+ utils().oldPandaHost + "?job=*&ui=user&name="+ usernames.replace(/\s/g,'+')+ "'><b>" +usernames+ "'s</b></a> page from the classic Panda</b></div>");
          var thisTag = views().jqTag(tag);
          old.css('color','red');
          thisTag.append(userstat);
          thisTag.append(old);
          function appendUserStat(tag,data) {
            var udata = data.buffer.data;
            if (udata != undefined && udata.rows.length > 0 && udata.rows[0].length > 0) {
               var user  = utils().zip(udata.header,udata.rows[0]);
               var line = "<b>"
                          + user.NAME  
                          + ": " + user.NJOBSA 
                          + " jobs </b> in the last week, latest at " 
                          + user.LATESTJOB +"; <b><a href='https://twiki.cern.ch/twiki/bin/viewauth/AtlasComputing/PandaAthena#Job_priority'>Usage (CPU hrs):</a> 1 day: "+ (parseInt(user.CPUA1)/3600).toFixed(1)
                          + " hour;  7 days: " +(parseInt(user.CPUA7)/3600).toFixed(1) + ' hour</b>';
               tag.html(line);
               tag.attr('title','Usage table stats are updated hourly. Usage calculation for purposes of quota is calculated independently, in real time.');
            } else {
               tag.html(" &nbsp; ");
            }
          }
        /* http://pandamon.cern.ch/listusers?name=Aliaksei+Hrynevich */     
           var aj = new AjaxRender();
           var module = 'listusers';
           aj.download(userstat,appendUserStat, module,{name:usernames});
      }

     /* ---------------------  fetchJobSummary ---------------------- */   
      function fetchJobSummary(jobsummary) {
         if (jobsummary != undefined) {
            var lpars = $.deparam.querystring();
            lpars['summary']=true;
            lpars['limit'] = 'undefined';
            var jobtype = module == "jobinfo" ? 'jobtype' : 'tasktype';
            for (var js in jobsummary) {
               var lpars = $.deparam.querystring();
               lpars['summary']=true;
               lpars['limit'] = 'undefined';
               var aj = new AjaxRender();
               var jsum = jobsummary[js];
               if  (module == "jobinfo") {
                   lpars['jobparam'] = jsum;
                   lpars['taskparam'] = undefined;
               } else {
                   lpars['taskparam'] = jsum;
                   lpars['jobparam'] = undefined;
               }
               if (jsum == 'jobsetID')    { 
                  lpars[jobtype] = 'analysis';
               } else if (jsum == 'taskID') { 
                  lpars[jobtype] = jobtype=='jobtype'?'production': 'prod';
               } 

               aj.cache(true);
               aj.download('jobsummaryid',appendJobSummary, module,lpars);
            }
         }
      }
   /* ---------------------  Entry point ---------------------- */   
   var thisTag =  $(tag);
   thisTag.empty();
   var desc = main.Description;
   /*console.log("Enter again the user function:" + this +' main =' + JSON.stringify(main,undefined,2)+ desc); */
   if (desc != undefined) {
      $(tag).html(desc);
   } else {
      var selection = main.Selection;
      /* Check user page */
      var lupars = $.deparam.querystring();
      if (lupars.prodUserName != undefined) {
          fetchUserStat(tag,lupars.prodUserName);
      }
      if (lupars.dump == undefined) {
         if (selection === undefined) { selection = {}; }
         if (selection.dump === undefined) { selection['dump']='no'; }
      }
      views().showSelection(tag,selection,module);
      var dhead = main.header;  
      if (dhead != undefined ) {
         var dinfo    = {  
                           data      : main.info
                         , header    : dhead
                         , jobsummary: _jobsummary
                         , module    : main.module
                         , module    : main.module
                        };
         if (dhead.indexOf("TOTAL_JOBS")>=0) {
            views().renderJobSummary(thisTag,dinfo);
         } else {
            if (main.info.length > 1 ) {
               var divs = "<div id=jobsummaryid class='ui-corner-all ui-widget ui-widget-content' style='padding:4px;'>";
               divs += "<div id='api_help_jobsummaryid' class='ui-icon ui-icon-help ui-widget-header' style='float:left;padding:0px;cursor:help;' title='Click to get the GUI help' onClick='views().renderUISummaryHelp();'></div>";
               for (var jsumdiv in _js) {
                  divs += "<div id='"+_js[jsumdiv][1]+"_jobsummaryid' style='display:none'></div>";
               }
               divs += "</div>";
               thisTag.append(divs);
               var jobsumobj = $('#jobsummaryid');
               var height = module == "jobinfo" ? '300px' : '200px';
               jobsumobj.css('width','97%').css('height',height).css('overflow','auto');
               jobsumobj.resizable( { handles: "se, sw, s"});
               fetchJobSummary(_jobsummary);
               if (main.jobset != undefined && checkPars(dhead) ) {
                  makeJobsets(thisTag,main.jobset);
               }
            }
            if (checkPars(dhead) ) {
                if (main.info.length == 1  || ( main.jobset==undefined && main.info.length >= 1) ) {  thisTag.append(showJobs(dinfo)); }
            } else if (main.info.length > 1)  {
               var jobpardiv = $("<div></div>");
               thisTag.append(jobpardiv);
               utils().renderTable(jobpardiv,dhead,main.info);
            }
            if (main.info.length == 1 )
            { 
               views().renderPandaJob(thisTag,main);
            } else if ( main.info.length == 0 ) {
               views().renderAlert(thisTag, "No Job has been selected");
            }
         }
         $.sparkline_display_visible();
      }
   }
} 

   /* _____________________________renderUISummaryHelp_________________________________ */
   PandaMonitorViews.prototype.renderUISummaryHelp = function()
   {
      var r = $("<div><img src='"+utils().version("static/images/DrillDownControl.png") + "' width='100%'/></div>");
      var opt =  { buttons: {} 
                 , overlay: { backgroundColor: "#000", opacity: 0.5 }
                 , close:  function() {  r.dialog("destroy");  }
                 };
      r.dialog(opt);
   }
   /* _____________________________renderJobSummary_________________________________ */
   PandaMonitorViews.prototype.renderJobSummary = function(tag,summary,lpars,jedi) {
      var module = summary.module;
      if (module == undefined) {
         module = jedi?"jedi/taskinfo" : "jobinfo";
      }
      var _jobsummary = summary.jobsummary;
      var _rjobsummary = {};
      for (var r in _jobsummary) { _rjobsummary[ _jobsummary[r]] = r;  }
      var stcolors = { "finished": "#52D017", "failed" : "#ff6666", "running" : "#C3FDB8", "holding" : "#ffff33", "cancelled": "#FFFF00" };
      var jheader = summary['header'];
      var sdata =   summary['data'];
      if (sdata == undefined) {sdata=summary['rows']; }
      if (lpars == undefined) { 
         lpars = $.deparam.querystring(); 
         if (lpars['summary'] != undefined  && lpars['summary'] != 'undefined') {
                 lpars['summary']  = 'undefined';
                 lpars['jobparam'] = 'undefined';
                 lpars['limit']    = 'undefined';
         }
      }
      var div = views().jqTag(tag);
      var plotdiv = $("<div style='display:none'></div>"); 
      var plotdivuid= plotdiv.uid();
      /*div.addClass("pmJobSummary");  */
      /* div.addClass(jheader[0]); */
      div.data('summary',summary);
      div.data('sdata',sdata.slice(0));
      var sumtitle= _rjobsummary[jheader[0]];
      var sumtxttitle = $("<div style='font-weight:bold;display:inline;'></div>");  
      var sumuid = sumtxttitle.uid();
      var tspan = $("<span></span>");
      var ticonspan = $("<span style='display:inline;'>&nbsp;&nbsp;&nbsp;&nbsp;</span>");
      var ticonspanid = ticonspan.uid();
      var uidtspan = tspan.uid();
      sumtxttitle.append(ticonspan);sumtxttitle.append(tspan);      
      var usersum=false; var transum=false;  var setssum=false;  var statssum=false; var taskidsum = false; var sitesum = false;var cloudsum = false;
      var jedisum= false;
      if ( sumtitle != undefined )  {
         usersum = (sumtitle=='Users');
         transum = (sumtitle=='Transformations');
         setssum = (sumtitle=='Jobsets');
         statssum =  (sumtitle=='States' || sumtitle.toLowerCase()=='analysis' ||  sumtitle.toLowerCase()=='production');
         cloudsum =  (sumtitle=='Clouds');
         taskidsum =  (sumtitle=='Task ID');
         jedisum =  (sumtitle=='Jedi ID') || (sumtitle=='Jobs');
         sitesum  = (sumtitle =='Sites');
       } else {
         sumtitle = jheader[0];
      }
      tspan.html(sumtitle);
      if (lpars.jobStatus != undefined && ( lpars.jobStatus=='failed' || lpars.jobStatus =='cancelled'  || lpars.jobStatus =='retried') ) {
         div.data('errors',0);
         var spars = $.extend({},lpars);         
         function appendErrorPlots(t,data){
             div.data('errors',data);
             var txtspan = $('#'+uidtspan);
             var topuid= $('#'+sumuid);
             var iid = $('#'+ticonspanid);
             txtspan.css("background-color","red").css('cursor','pointer').css('text-decoration','underline');
             txtspan.attr('title',"Click to collapse / expand the 'Error Plots' panel");
             iid.addClass('ui-icon ui-icon-image');
             var ppuid = $('#'+plotdivuid);
             txtspan.on('click', function() {ppuid.toggle('slow')});
             if (t != undefined && t.length >0 ) {
                data['order'] = t;
             }
             views().renderErrorPlots(ppuid,data);
         }
         spars['plot'] = undefined;
         spars['limit'] = undefined;
         if (spars.hours == undefined) {spars['hours'] = 71; }
         if (!statssum) { spars['opt']    = 'item';  }     
         if (setssum)   { spars['jobtype']='analysis'; } 
         if (statssum) {spars['item'] = 'cloud'; spars['opt'] = 'sum' }
         else if (taskidsum) { 
            spars['item'] = 'taskID';spars['jobtype']='production'; 
            if (sdata != undefined && sdata.length > 0) {
               var stasks = sdata.slice(0);
               stasks.sort(function(a,b){
                      return b[1]-a[1];
                  });
               var tids = [];   
               for  (var t in stasks)    {
                  if (t > 20) break;
                  var desc = stasks[t];
                  tid = desc[0];
                  tids.push(desc[0]);
               }
               if (tids.length > 0) {
                  spars['taskID']=tids.join(',');
               }
            }
         }
         else if (sitesum) {spars['item'] = 'computingSite';}
         else if (usersum) {spars['item'] = 'prodUserName' ;}
         else if (cloudsum){spars['item'] = 'cloud' ;}
         else if (jedisum) {spars['item'] = 'JediTaskID'; if (sumtitle=='Jobs') { spars.status=undefined; } }
         if ( spars.jobtype == undefined  && spars.prodUserName != undefined ) { spars['jobtype'] = 'all'; }
         if ( spars.item != undefined) {
            var aj = new AjaxRender();
            aj.cache(true);
            if ( tids != undefined && tids.length >0) {
               /* spars['hours'] = 'undefined'; */
               spars['edge'] = 0;
               spars['minerrs'] = 0;
               aj.download(tids,appendErrorPlots, "jobs/joberror",spars);
            } else { 
               aj.download(undefined,appendErrorPlots, "jobs/joberror",spars);
            }
         }
      }
      /* ---------------------  showSummaryItems ---------------------- */   
         function showSummaryItems(toptag,maxs) {
            sparkvalues = [];
            var sumdata = div.data('summary');
            var sdata = sumdata.data;
            var comp = div.data('comp'); var dsc = div.data('dsc');
            if (comp == undefined) {comp  = 1;}
            if (dsc == undefined) {dsc = 0;}
            var sumtxt = undefined;
            if  (toptag != undefined) {
                sumtxt = toptag; 
                sumtxt.empty();
            } else { 
                sumtxt = $("<div style='display:inline;'></div>");
            }
            var cursum = $("<span style='display:inline;'></span>");
            var sparklinetag = $("<span style='display:inline;'>&nbsp; </span>");
            sumtxt.append(sparklinetag);
            sumtxt.append(cursum);
            var jcount = 0;
            if (maxs== undefined) {  maxs = 50; }
            var htag = tag+"_hidden";
            var onclick = '$("#' +htag+  '").toggle();';            
            if ( toptag != undefined) {
               if (dsc != 0) {
                   /* ---------------------  sort items ------------------- */   
                  sdata.sort(function(a,b){ 
                     var ta = a[comp]; var tb = b[comp];
                     var diff = 0;
                     if (typeof(ta) == 'string') {
                        ta = ta.toLowerCase();
                        tb = tb.toLowerCase();
                        var diff = 0;
                        if (  ta<tb ) { 
                          diff = -1;
                        } else if (ta>tb) { 
                          diff = +1;
                        } else {
                          diff = 0;
                        }
                     } else {
                        diff = ta-tb;
                     }
                     return dsc < 0 ?diff : -diff;  
                  });
               } else {
                  sdata =  div.data('sdata');
               }
            }
            for (var s in  sdata) {
               if (s > maxs && onclick != undefined) {
                  var sumtxth = "<div title='There  are " + (sdata.length-s)+ " hidden entries. Click to show the entire entry' style='cursor:pointer;display:inline;text-decoration:underline' onclick='" +onclick+  "'>";
                  sumtxth += "&nbsp;&hellip;&nbsp;"+ (sdata.length-s)+ "&nbsp;&hellip;&nbsp; </div>" ;
                  sumtxth = $(sumtxth);
                  sumtxt.append(sumtxth);              
                   sumtxth = $("<div id='"+ htag+ "' style=display:none;>");
                  sumtxt.append(sumtxth);
                  cursum = sumtxth
                  onclick = undefined;
               }
               var item = sdata[s];
               // console.log('1620: item: ' + JSON.stringify(item) +JSON.stringify(jheader[0]) +" toptag="+toptag) ;
               lpars[jheader[0]] = item[0];
               var sumitem = '';
               // console.log('1621: item: ' + usersum+" " +transum+" " +setssum+" " +statssum+" " +taskidsum +" cloudsum=" +cloudsum+ " sitesum="+sitesum);
               if (usersum) {
                  sumitem += views().linkUser(item[0]);
               } else if (transum) {
                  sumitem += utils().linkTransformation(item[0]);
               } else if (statssum) {
                  var statcolor = stcolors[item[0]];
                  if ( statcolor == undefined) {
                     sumitem += item[0];
                  } else  {
                     sumitem += "<span style='display:inline;background-color:"+statcolor+";'>"+item[0]+"</span>";
                  }
               } else if (cloudsum) {
                  var statcolor = utils().colorMap[item[0]];
                     if ( statcolor == undefined) {
                        sumitem += item[0];
                     } else {
                       sumitem += "<span style='display:inline;color:"+statcolor+";'>"+item[0]+"</span>";
                     }
               } else if ( taskidsum) {   
                  sumitem += "#"+views().linkTaskListPars(item[0], {tidm:[item[0],item[0]].join(',') },"Click to see this task status");
               } else if ( sitesum) {
                   var wdays = lpars.days;
                   if ( ( wdays == undefined  || wdays == null ) && lpars.hours != undefined ) {
                     wdays = parseInt(lpars.hours)/24.;
                   }
                   if ( wdays != undefined  &&  wdays != null )  {
                     wdays = parseFloat(wdays).toPrecision(4);
                   } else {
                     wdays = undefined;
                   }
                   var plot= lpars.jobStatus;
                   sumitem += views().linkWnList(item[0],lpars.jobtype,wdays,undefined,item[0],plot,"Click to get the job states for each node of the "+item[0]+ " site" ,'wn');
               } else if ( jedisum ) { 
                   var wpars = {task:item[0]};
                   wpars.hours = lpars.hours; wpars.days = lpars.days; wpars.tstart = lpars.tstart; wpars.tend= lpars.tend;
                   if (lpars.jobtype=='production') { wpars.tasktype = 'prod'; }
                   sumitem += "#"+views().linkJediInfo(item[0], wpars,item[0],'Click to get the JEDI task table');
                   if (lpars.status!=undefined) { lpars.status=undefined; }
               } else if ( setssum) { 
                sumitem += "#"+ item[0];
               } else {
                  // console.log('2885: item: ' + JSON.stringify(item) +JSON.stringify(jheader[0])) ;
                  sumitem += item[0];
               }
               /*----> Right portion of the job info ---*/
               jcount += item[1];
               // console.log('1644: count: ' + jcount) ;
               sumitem+= ":";
               if  (setssum || taskidsum) {
                  if (setssum) { 
                     lpars['jobtype']='analysis'
                  } else {
                     lpars['jobtype']='production'
                  }
               }
               sumitem+= " <a title='Click to select the PanDA jobs with "+sumtitle+"="+item[0]+"' href='"+utils().version()+"/"+module+"?"+$.param(lpars).replace('=undefined','=')+"'>"+item[1]+"</a>&nbsp; ";
               cursum.append(sumitem);
               if (onclick != undefined) { sparkvalues.push(item[1]); }
            } 
            if (sparkvalues.length > 2) {
              sparklinetag.sparkline(sparkvalues,{ width:'8em'});
            }
            return [sumtxt,jcount];
         }
      var comp= -1; var dsc= 0;
      div.data('comp',comp); div.data('dsc',dsc);
      var ss = showSummaryItems();
      var sumtxt = ss[0];
      var jcount = ss[1];
         /* ---------------------  click handler ------------------- */ 
         function sortClick(tee) {
            var tee = $(this);
            var mycomp = tee.data('comp');
            div.data('comp',mycomp);
            var ddsc = div.data('dsc')-1;
            if (ddsc == -2) {ddsc=1;} 
            div.data('dsc',ddsc);
            var sortClass = ddsc <0 ? 'ui-icon-triangle-1-w': ddsc > 0? 'ui-icon-triangle-1-e': 'ui-icon-carat-2-e-w';
            tee.removeClass('ui-icon-triangle-1-w ui-icon-triangle-1-e ui-icon-carat-2-e-w').addClass(sortClass);
            var control = tee.data('control');
            control.removeClass('ui-icon-triangle-1-w ui-icon-triangle-1-e ui-icon-carat-2-e-w').addClass('ui-icon-carat-2-e-w');
            var tag =  tee.data('tag');
            /* tee.css('cursor','wait');control.css('cursor','wait'); */
            showSummaryItems(tag);
            /* control.css('cursor','pointer');tee.css('cursor','pointer'); */
         }
         if (sdata.length > 1) {
            var divsorname = $("<span title='Sort the selection by name' class='ui-icon' style='padding-left:0px;padding-right:15px;display:inline;cursor:pointer;'></span>");
            var divsorjobs = $("<span title='Sort the selection by  the number of the jobs' class='ui-icon' style='padding-left:2px;padding-right:12px;display:inline;cursor:pointer;'></span>");
            sumtxttitle.append("<span style='display:inline; style='padding:0px'>&nbsp;(</span>");
            var sortClass = comp == 0 ? dsc ? 'ui-icon-triangle-1-w': 'ui-icon-triangle-1-e' :'ui-icon-carat-2-e-w';
            divsorname.addClass(sortClass);
            divsorname.data('comp',0);divsorjobs.data('comp',1); 
            divsorname.data('control',divsorjobs);divsorjobs.data('control',divsorname); 
            divsorname.data('tag',sumtxt);divsorjobs.data('tag',sumtxt); 
            divsorname.click(sortClick); divsorjobs.click(sortClick); 
            sumtxttitle.append(divsorname);
            sumtxttitle.append("<span  style='display:inline;'>"+sdata.length+"</span>");
            sumtxttitle.append("<span title='The number of the jobs' style='display:inline'>:"+jcount+"</span>");
            sortClass = comp == 1 ? dsc ? 'ui-icon-triangle-1-w': 'ui-icon-triangle-1-e' :'ui-icon-carat-2-e-w';
            divsorjobs.addClass(sortClass);
            sumtxttitle.append(divsorjobs);
            sumtxttitle.append("<span  style='display:inline;'>)</span>");
         }
         sumtxttitle.append("<span style='display:inline'>:</span>"); 
         div.empty(); div.append(sumtxttitle);div.append(sumtxt);div.append(plotdiv);
         return div;
      }
      
   /* _________________________________________________________________________ */
   PandaMonitorViews.prototype.pilotTiming = function(val) {
      var timing = val.split('|');
      var pilotTimeObj = " --> ";
      for (var t in timing) {
         var tval = timing[t];
         pilotTimeObj += '&nbsp;&nbsp; ';
         switch (parseInt(t)) {
            case 0: pilotTimeObj += 'getJob:'+ tval+ ' sec'; break;
            case 1: pilotTimeObj += 'stagein:'+ (parseFloat(tval)/60).toFixed(1) + ' min'; break;
            case 2: pilotTimeObj += 'execute:'+ (parseFloat(tval)/60).toFixed(1) + ' min'; break;
            case 3: pilotTimeObj += 'stageout:'+ (parseFloat(tval)/60).toFixed(1) + ' min'; break;
            case 4: pilotTimeObj += 'setup:'+ tval+ ' sec';  break;
            default: pilotTimeObj += ' ' + t + '-->' + tval +' unrecognized code'; break;
         };
      }
      pilotTimeObj +=  " &nbsp;<a href='" +views().AtlasTwiki+"/" + views().PandaPilotTwiki + "#QaPilotTiming'"
                    +  " title='Q:Which are the timings in pilotTiming?'>"
                    + "<div class='ui-icon ui-icon-help' width='32px' style='display:inline-block'></div></a>";
      return pilotTimeObj;
   }
      
   /* _________________________________________________________________________ */
   PandaMonitorViews.prototype.renderJediSets = function(title,job) {
      function jdset(tg,mn)  {
         tg.empty();
         tg.append(views().pageSection("<a href='https://twiki.cern.ch/twiki/bin/viewauth/AtlasComputing/PandaJEDI#The_JEDI_Datasets_table'>The List of the Datasets</a>"));
         utils().renderTable(tg,mn.header,mn.data);
      }
      var jedids = $("<div>Checking the task datasets  . . . </div>");
      title.append(jedids);
      var aj = new AjaxRender();
      aj.cache(true);
      aj.download(jedids,jdset,'jedi/jdset',{JediTaskID:job.JediTaskID,dsparam:'DATASETNAME,type,status,creationTime,nFiles,nFilesUsed,nFilesFailed'}); 
      return jedids;
   }
      
   /* _________________________________________________________________________ */
   PandaMonitorViews.prototype.renderJediSetCont= function(title,job) {
      function jdcont(tg,mn)  {
         tg.empty();
         tg.append(views().pageSection("<a href='https://twiki.cern.ch/twiki/bin/viewauth/AtlasComputing/PandaJEDI#The_JEDI_Dataset_Contents_table'>The List of the Datasets Files</a>"));
         utils().renderTable(tg,mn.header,mn.data);
      }
      var jedilfn = $("<div>Checking the task files  . . . </div>");
      title.append(jedilfn);
      var aj1 = new AjaxRender();
      aj1.cache(true);
      aj1.download(jedilfn,jdcont,'jedi/jdscont',{JediTaskID:job.JediTaskID,dsparam:'lfn,fsize,type,status,creationDate,GUID'});
      return  jedilfn; 
   }

   /* _________________________________________________________________________ */
   PandaMonitorViews.prototype.formatTime = function(time) {
      if (time  != undefined && typeof time != "string" )  return new Date(time*1000).format("yyyy-mm-dd HH:MM");
      return time;
   }
   
   /* _________________________________________________________________________ */
   PandaMonitorViews.prototype.jobParamaters = function(job,colNames)  {
      var div = $("<div><p></div>");
      var title = $("<div></div>"); div.append(title);
      var names =  colNames;
      var tstart = views().formatTime(job.modificationTime);
      var settabs  = [];
      var taskId;
      if ( names  != undefined && names.length >0 ) {
         var table = "<table id='id_jobparameter_table' border=0 cellpadding=1 width=100%>";
         if (job.PandaID != undefined) {
            title.html("<b>Job #" +utils().linkJob(job.PandaID)+ " parameters:<b><br>"); 
            table += "<thead><tr><th><small>PanDA Job Parameter</small></th><th><small>Value</small></th></tr></thead></tbody>";
         } else if (job.JediTaskID  != undefined)  {
            title.empty();
            title.before("<b>Jedi Task </b>");
            title.before("<div class='ui-icon ui-icon-transferthick-e-w' style='display:inline;cursor:pointer;verticalAlign:center;'>"
                       +views().linkJobInfoPars('&nbsp;&nbsp;&nbsp;&nbsp;',{JediTaskID:job.JediTaskID,hours:'undefined',tstart:tstart},undefined,"Show the PanDA jobs for the Jedi task #" + job.JediTaskID ) + "</div>");
            title.before(" &nbsp;<b>#" +job.JediTaskID+ " parameters:</b>" );
            var ds = views().renderJediSets(title,job);
            var dcont = views().renderJediSetCont(title,job);
            settabs.push(ds);  settabs.push(dcont);
            table += "<thead><tr><th><small>JEDI Task Parameter</small></th><th><small>Value</small></th></tr></thead></tbody>";
         }  else {  
            taskId = job.ID;
            title.html("<b>Task parameters:<b><br>"); 
            table += "<thead><tr><th><small>Task Parameter</small></th><th><small>Value</small></th></tr></thead></tbody>";
         }
         for (var col in names) {
            var name = names[col];
            var val =  job[name];
            table += "<tr><td style='padding-right:2px;padding-left:4px;'><b>" +name+  "</b></td>";
            if ( val == undefined ) {
               val  = "--"; 
            } else {
               if ( name == 'transformation' || name =='transPath') {
                  val = views().makeLink(val);
                  var f = val.attr('href');
                  var h = val.html();
                  if ( f != undefined) {
                     val = "<a href="+f+ ">" +h+ "</a>";
                  }  else {
                      val = h; 
                  }
               } else if ( name.toLowerCase().indexOf('time') >=0  && name.toLowerCase().indexOf('consumption') <0  && name.toLowerCase().indexOf('wall') <0 ) {
                  val =  views().formatTime(val);
               } else if (name == 'parentID') {
                  val = views().linkJob(val,val,'Click to go to the parent job parameters');
               } else if ( name == 'PandaID') {
                  val = views().linkJob(val);
               } else if ( name == 'batchID') {
                  /* it shows itself . strange */ 
                  val = views().linkJobInfoPars(val,{batchID:val});
               } else if ( name == 'destinationDBlock') {
                  val = utils().linkDataset(val);
               } else if ( name == 'prodUserName') {
                  val = views().linkJobInfoPars(val,{prodUserName:val});
               } else if ( name.toUpperCase() == 'JOBMETRICS') {
                  if (val !== '--') { 
                        val += " &nbsp;<a href='" +views().AtlasTwiki+"/" + views().PandaPilotTwiki + "#QaJobMetrics'"
                            +  " title='Q:What are the jobMetrics?'>"
                            +  "<div class='ui-icon ui-icon-help' width='32px' style='display:inline-block'></div></a>";
                  }
               } else if ( name == 'pilotTiming') {
                  if (val !== '--') { val += views().pilotTiming (val); }
               } else if ( name == 'pilotID') {
                  if (val !== '--') {
                     var timing = val.split('|');
                     val = '';
                     for (var t in timing) {
                        var tval = timing[t];
                        val += '&nbsp;&nbsp; ';
                        switch (parseInt(t)) {
                           case 0: val += "<b>" + views().linkPilotLog(tval) + '&nbsp;&nbsp; '
                                                + views().linkPilotLog(tval,'err','err') + '&nbsp;&nbsp; '
                                                + views().linkPilotLog(tval,'log','log') +  "</b>";
                                   break;
                           case 1: val += 'BatchID:&nbsp;&nbsp; '+ views().linkJobInfoPars(tval,{batchID:tval}); break;
                           case 2: val += 'Batch system type:&nbsp;&nbsp; '+ tval; break;
                           case 3: val += 'Pilot type:&nbsp;&nbsp; ' + tval;  break;
                           case 4: val += 'Pilot version:&nbsp;&nbsp; '+ tval; break;
                           default: val += ' ' + t + '-->' + tval +' unrecognized code'; break;
                        };
                        val += '<br>';
                     }
                  }
               } else if ( name.toUpperCase() == 'REQ_JOBS' || name.toUpperCase() == 'DONE_JOBS') {               
                     var style = '';
                     if  ( names['REQ_JOBS'] != names['DONE_JOBS'] ) {
                        style ='color:red;font-weight:bold;';
                     } 
                     if (name.toUpperCase() == 'DONE_JOBS' ) {
                        val = views().linkJobInfoPars(val,{taskID:taskId,jobStatus:'finished,failed,cancelled',limit:200,hours:71},val,"Click to see the finished, failed, cancelled jobs for #"+ taskId+ " task");
                     } else {
                        val = views().linkJobInfoPars(val,{taskID:taskId,limit:200,hours:71},val,"Click to see the status of jobs for #"+ taskId+ " task");
                     }
               } else if ( name.toUpperCase() == 'INPUT') {
                   val = utils().linkDataset(val);
               } else if ( name.toUpperCase() == 'TASK_NAME') {                    
                    val = views().linkTaskListPars(val, {tidm:''+taskId+','+taskId,columns:'*'},"Show all parameters");
               } else if ( name.toUpperCase() == 'VPARAMS' || name.toUpperCase() == 'LPARAMS') {
                    val = "<textarea cols='70' readonly>" + val + "</textarea>";
                   ;
               } else if ( name == 'jobParameters') {
                    val = "<textarea rows='3' cols='70' readonly>" +val+ "</textarea>";
               }
            }
            table += "<td style='padding-right:2px;padding-left:4px;'>" +val+ "</td></tr>"; 
         }
         table += "</tbody></table>";
         if (settabs.length >0) {
           var li = $("<ul></ul>");
           li.append("<li href=#id_jobparameter_table>Parameters</li>");
           var labels = ["Datasets","Files"];
           for (var tb in settabs) {             
              li.append("<li href=#"+settabs[tb].uid()+">"+labels[tb]+"</li>");
           }
           title.append($(table));
           / * settabs[0].before(li);   VF disable for the time being */ 
           tabs = title.uid();
         } else {
           div.append($(table));
         }            
      }  else {
         title.html("<b>No - Job Parameters Available</b>"); 
      }         
      return div;
   }
   
   /*___________________________________________________________________________________________________ */
   PandaMonitorViews.prototype.makeLink = function (field) {
      var tlink;
      if (field.indexOf("http:")==0) { 
         tlink =  $("<a></a>"); tlink.attr("href",field); 
      } else {
         tlink =  $("<span></span>");
      }
      tlink.html(views().basename(field,""));
      return tlink;
   }

   /* _________________________________________________________________________ */
   PandaMonitorViews.prototype.renderPandaJob = function(tag,main) {
      var tabs = undefined;
      function makeLink(field) {
         var tlink;
         if (field.indexOf("http:")==0) { 
            tlink =  $("<a></a>"); tlink.attr("href",field); 
         } else {
            tlink =  $("<span></span>");
         }
         tlink.html(views().basename(field,""));
         return tlink;
      }

      function jobParamaters(job,colNames) {
         var div = $("<div><p></div>");
         var title = $("<div></div>"); div.append(title);
         var names =  colNames;
         var tstart = views().formatTime(job.modificationTime);
         var settabs  = [];
         if ( names  != undefined && names.length >0 ) {
            var table = "<table id='id_jobparameter_table' border=0 cellpadding=1 width=100%>";
            if (job.PandaID != undefined) {
               title.html("<b>Job #" +utils().linkJob(job.PandaID)+ " parameters:<b><br>"); 
               table += "<thead><tr><th><small>PanDA Job Parameter</small></th><th><small>Value</small></th></tr></thead></tbody>";
            } else if (job.JediTaskID  != undefined)  {
               title.empty();
               title.before("<b>Jedi Task </b>");
               title.before("<div class='ui-icon ui-icon-transferthick-e-w' style='display:inline;cursor:pointer;verticalAlign:center;'>"
                          +views().linkJobInfoPars('&nbsp;&nbsp;&nbsp;&nbsp;',{JediTaskID:job.JediTaskID,hours:'undefined',tstart:tstart},undefined,"Show the PanDA jobs for the Jedi task #" + job.JediTaskID ) + "</div>");
               title.before(" &nbsp;<b>#" +job.JediTaskID+ " parameters:</b>" );
               var ds = views().renderJediSets(title,job);
               var dcont = views().renderJediSetCont(title,job);
               settabs.push(ds);  settabs.push(dcont);
               table += "<thead><tr><th><small>JEDI Task Parameter</small></th><th><small>Value</small></th></tr></thead></tbody>";
         }
            for (var col in names) {
               var name = names[col];
               var val =  job[name];
               table += "<tr><td style='padding-right:2px;padding-left:4px;'><b>" +name+  "</b></td>";
               if ( val == undefined ) {
                  val  = "--"; 
               } else {
                  if ( name == 'transformation' || name =='transPath') {
                     val = views().makeLink(val);
                     var f = val.attr('href');
                     var h = val.html();
                     if ( f != undefined) {
                        val = "<a href="+f+ ">" +h+ "</a>";
                     }  else {
                         val = h; 
                     }
                  } else if ( name.toLowerCase().indexOf('time') >=0  && name.toLowerCase().indexOf('consumption') <0  && name.toLowerCase().indexOf('wall') <0 ) {
                     val =  views().formatTime(val);
                  } else if (name == 'parentID') {
                     val = views().linkJob(val,val,'Click to go to the parent job parameters');
                  } else if ( name == 'PandaID') {
                     val = views().linkJob(val);
                  } else if ( name == 'batchID') {
                     /* it shows itself . strange */ 
                     val = views().linkJobInfoPars(val,{batchID:val});
                  } else if ( name == 'destinationDBlock') {
                     val = utils().linkDataset(val);
                  } else if ( name == 'prodUserName') {
                     val = views().linkJobInfoPars(val,{prodUserName:val});
                  } else if ( name.toUpperCase() == 'JOBMETRICS') {
                     if (val !== '--') { 
                           val += " &nbsp;<a href='" +views().AtlasTwiki+"/" + views().PandaPilotTwiki + "#QaJobMetrics'"
                               +  " title='Q:What are the jobMetrics?'>"
                               +  "<div class='ui-icon ui-icon-help' width='32px' style='display:inline-block'></div></a>";
                     }
                  } else if ( name == 'pilotTiming') {
                     if (val !== '--') { val += views().pilotTiming (val); }
                  } else if ( name == 'pilotID') {
                     if (val !== '--') {
                        var timing = val.split('|');
                        val = '';
                        for (var t in timing) {
                           var tval = timing[t];
                           val += '&nbsp;&nbsp; ';
                           switch (parseInt(t)) {
                              case 0: val += "<b>" + views().linkPilotLog(tval) + '&nbsp;&nbsp; '
                                                   + views().linkPilotLog(tval,'err','err') + '&nbsp;&nbsp; '
                                                   + views().linkPilotLog(tval,'log','log') +  "</b>";
                                      break;
                              case 1: val += 'BatchID:&nbsp;&nbsp; '+ views().linkJobInfoPars(tval,{batchID:tval}); break;
                              case 2: val += 'Batch system type:&nbsp;&nbsp; '+ tval; break;
                              case 3: val += 'Pilot type:&nbsp;&nbsp; ' + tval;  break;
                              case 4: val += 'Pilot version:&nbsp;&nbsp; '+ tval; break;
                              default: val += ' ' + t + '-->' + tval +' unrecognized code'; break;
                           };
                           val += '<br>';
                        }
                     }
                  } else if ( name == 'jobParameters') {
                    val = "<textarea rows='3' cols='80' readonly>"+val+"</textarea>";
                  }
               }
               table += "<td style='padding-right:2px;padding-left:4px;'>" +val+ "</td></tr>"; 
            }
            table += "</tbody></table>";
            if (settabs.length >0) {
              var li = $("<ul></ul>");
              li.append("<li href=#id_jobparameter_table>Parameters</li>");
              var labels = ["Datasets","Files"];
              for (var tb in settabs) {             
                 li.append("<li href=#"+settabs[tb].uid()+">"+labels[tb]+"</li>");
              }
              title.append($(table));
              / * settabs[0].before(li);   VF disable for the time being */ 
              tabs = title.uid();
            } else {
              div.append($(table));
            }            
         }  else {
            title.html("<b>No - Job Parameters Available</b>"); 
         }         
         return div;
      }
     /* ------- entry renderPandaJob -------------- */
   
      var thisTag = views().jqTag(tag);
      var job = utils().zip(main.header,main.info[0]);
      if (main.jobset != undefined) {
         var jobsets = main.jobset.jobsets;
         var jbset;
         for ( var j in jobsets ) {jbset = jobsets[j].jobs;break;}
         for ( var j in jbset) {  var jb = jbset[j]; jbset= jb; break; }
         var jobsetsheader = main.jobset.header;
         $.extend(job, utils().zip(jobsetsheader,jbset));
      }
      var jobpardiv = $("<div></div>");
      var jobfilediv = $("<div><P>Checking the job file list  . . . </div>");
      var jobscriptdiv = undefined;

      jobpardiv.append(jobfilediv );
      var jobextradiv = $("<div><P>Checking the job log extract  . . . </div>");
      jobpardiv.append(jobextradiv );
      
      if (job.JediTaskID != undefined) {
           jobpardiv.append("<b>Show the associated JEDI task:&nbsp;  " + views().linkJobInfoPars(job.JediTaskID,{JediTaskID:job.JediTaskID,limit:2000},job.JediTaskID,"Click to see the status of jobs for #"+ job.JediTaskID+ " JEDI task") + "</b><br>"); 
           jobpardiv.append("<b>Show the associated DEFT task:&nbsp;  " 
                          +views().linkDefTaskListPars( job.JediTaskID, {taskID:job.JediTaskID },"Click to see "+ job.JediTaskID+" DEFT task status") + "</b><br>");
      }
      else if (job.jobsetID != undefined) {
         jobpardiv.append("<b>Show the associated jobset:&nbsp;  " + views().linkJobInfoPars(job.jobsetID,{jobsetID:job.jobsetID,limit:2000},job.jobsetID,"Click to see the status of jobs for #"+ job.taskID+ " jobset") + "</b><P>"); 
      }
      else if (job.taskID != undefined) {
            jobpardiv.append("<b>Show the associated task:&nbsp;  " + views().linkJobInfoPars(job.taskID,{taskID:job.taskID,limit:2000},job.taskID,"Click to see the status of jobs for #"+ job.taskID+ " task") + "</b><P>"); 
            jobscriptdiv = $("<div>Checking script to re-create job for offline debugging  . . . .</div>");
            jobpardiv.append(jobscriptdiv);
      }
      jobpardiv.append( views().jobParamaters(job,main.colNames));
      thisTag.append(jobpardiv);
      var pages = [ [ 35,50, 75, 100, 150, -1], [ 35, 50, 75, 100, 150,"ALL"] ];
      var defflt  = -1;
         $('#id_jobparameter_table').dataTable({"bProcessing": true,"bJQueryUI": true,"aaSorting":[]
                   , "iDisplayLength": defflt
                   , "aLengthMenu": pages
                   , "bStateSave": true});
      if (tabs !== undefined) {
         //  $('head').append("<script>$('#"+tabs+ "').tabs();</script>");
      }
      views().queryJobFiles(jobfilediv,job);
      views().queryJobExtract(jobextradiv,job);
      if (jobscriptdiv != undefined) { views().queryScriptOffline(jobscriptdiv,job); }
   }
   
    /* _________________________________________________________________________ */
   PandaMonitorViews.prototype.renderJobLogExtract = function(tag,content,animate) {
      var data = content.data;
      if ( animate!= undefined) { $(tag).html("<P>&nbsp;"); }
      if ( data != undefined) {
          /* Render the "content" */
          var header =  data.header;          
          var rows =  data.rows;
          var iId = utils().name2Indx(header,'pandaid');
          var iLog = utils().name2Indx(header,'log1');          
          if (rows.length > 0) {
             for (var r in rows) {
                var id =  rows[r][iId];
                var txt  = rows[r][iLog];
                var titlediv = $('<div></div>');
                var htmltitleicon = $("<div>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</div>").css({cursor:'pointer','vertical-align':'middle',display:'inline'});
                var htmltitle = $("<div><b>" +id+" log file extracts:</b></div>").css({ color:'blue',cursor:'pointer','text-decoration':'underline','vertical-align':'middle',display:'inline'});
                var htmlbody = "<div class='ui-widget ui-widget-content ui-corner-all' style='padding:7px;'>";
                htmlbody += "<pre><font color=brown>" +txt+"</font></pre></div></div>";
                htmlbody =  $(htmlbody);
                titlediv.append(htmltitleicon).append(htmltitle);
                if (animate) {
                  htmlbody.hide();
                  htmltitleicon.addClass('ui-icon ui-icon-circlesmall-plus');
                  var onclick = function ( ) { 
                     if ( htmlbody.is(':hidden') ) {
                        htmltitleicon.removeClass('ui-icon-circlesmall-plus').addClass('ui-icon-circlesmall-minus');
                     } else {
                        htmltitleicon.removeClass('ui-icon-circlesmall-minus').addClass('ui-icon-circlesmall-plus');
                     }
                     htmlbody.toggle('slow');
                  };                  
                  htmltitleicon.on('click', onclick);
                  htmltitle.on('click', onclick);
                  htmlbody.on('click', onclick);
                }
                $(tag).empty();
                $(tag).append("<P>");
                $(tag).append(titlediv);
                $(tag).append(htmlbody);
             }
          } else if (animate == undefined){
             views().renderAlert(tag, "No logfile extract was found");
          }
      } else if (animate == undefined) {
         views().renderAlert(tag, "No logfile extract was found");
      }
   }

    /* _________________________________________________________________________ */
   PandaMonitorViews.prototype.queryJobExtract = function(tag,job) {
      if (job.PandaID != undefined) {
         function rendJbEtxra(tg,data) { views().renderJobLogExtract(tg,data,true); }
         var lpars = { pandaid: job.PandaID};
         var aj = new AjaxRender();
         aj.download(tag,rendJbEtxra,"jobs/joblogs",lpars);
      } else {
         this.jqTag(tag).html("<P>");
      }
   }

    /* _________________________________________________________________________ */
   PandaMonitorViews.prototype.renderJobFileList = function(tag,main,dialog) {
      /*______________________________________________________________________________________________________ */
      function getSpaceToken(destToken, ddm, setoken) {
         var spaceToken = '?';
         if (utils().isFilled(destToken)) {
            var tokenName = destToken
            var ddmList = ddm.split(',')
            var setokenList = [];
            if (utils().isFilled(setoken)) {
               setokenList = setoken.split(',')
            }
            var i=0;
            for (var d in setokenList) {
               if (setokenList[d] == tokenName) {
                   spaceToken = ddmList[i];
                   break;
               }
               i += 1;
            }
         } else {
            spaceToken = ddm.split(',')[0];
         }
         return spaceToken;
      }

      var time = main.time;
      var job = this.jqTag(tag).data('job');
      var ddmsite,vo,linksite,linksite;
      if ( job != undefined) {
         ddmsite = job.ddm;
         vo = job.VO;
         linksite = job.ddmsite;
      }
      var sysrealtime = new Number(main._system.timing.real/1000.);
      var method  = main.buffer.method;
      var params  = main.buffer.params;
      var jobs =  main.buffer.jobs;
      var data = main.buffer.data;
      var header = data.header;
      var rows = data.rows;
      var d = $('<div></div>');
      var query = "<P>The server spent <b>" + sysrealtime.toFixed(3) + "</b> to access the CERN Oracle server";
      /* var fetch = " and <p><b>" + time.fetch + "</b> to execute the TaskBuffer."+ method + " query";  */
      d.html(query);
      var tdiv = $("<div></div>");
      /* var tline = '<p><b>' + method + '(' +params+ '): </b>'; */
      var tline = '';
      if ( jobs != undefined) { tline += '<br><b>Panda Job:&nbsp ' + views().linkJob(jobs)+'</b>'; }
      tdiv.append(tline);
      if ( rows != undefined && rows.length > 0) {
         var table = $('<table class="display"></table>'); 
         var tuid =  table.uid('JobLFNId');
         var iPandaId = utils().name2Indx(header,"pandaid");
         var iType = utils().name2Indx(header,"type");
         var iDs = utils().name2Indx(header,"dataset");
         var iGuid = utils().name2Indx(header,"guid");
         var iLfn = utils().name2Indx(header,"lfn");
         var iScope = utils().name2Indx(header,"scope");
         var iFsize = utils().name2Indx(header,"fsize");
         var tabheader = {lfn:'Filename',type:'Type',status:'Status',dataset:'Dataset',fsize: 'Size'};
         var uhdr = new Array(header.length);
         for (var h in header) { 
            var lbl = tabheader[header[h].toLowerCase()];
            if (lbl == undefined) { lbl = header[h]; }
            uhdr[h] =  {sTitle:lbl,  "bVisible": (h < iGuid) };  
         }
         tdiv.append(table);
         d.append(tdiv);
         $(tag).empty();
         $(tag).append(d);
         $('#'+tuid).dataTable( {
              "aaData"        : rows 
            , "aoColumns"     : uhdr
            , "bJQueryUI"     : true 
            , "aoColumnDefs"  : [  { "sWidth": "10%", "aTargets": [ 0 ] } ,{ "sWidth": "5%", "aTargets": [ 1 ] }]
            , "fnRowCallback" : function( nRow, aData, iDisplayIndex, iDisplayIndexFull ) 
               {  
                  if (iPandaId != undefined) {
                     $('td:eq('+iPandaId+')', nRow).html(views().linkJob(aData[iPandaId]));        
                  }
                  var lfn = aData[iLfn];
                  var guid = aData[iGuid];
                  var scope = aData[iScope];
                  if (vo != undefined && vo.toLowerCase() === 'cms') {lfn = "cms:"+ lfn; guid = ''; }
                  $('td:eq('+iLfn+')', nRow).html(utils().linkLfn(lfn,guid,scope,"Click to find the <" +lfn+ "> file origin"));
                  var sizeStyle = "text-align:right;padding:0px;"
                  var fsize = parseInt(aData[iFsize])/1048576.;
                  var tooltiptxt = '';
                  var fsizebig = 5120;  /* see: https://twiki.cern.ch/twiki/bin/viewauth/AtlasComputing/PandaRun */
                  if ( false && fsize > fsizebig  ) {
                     sizeStyle+= "background-color:red;color:white;";
                     tooltiptxt = " title='" + "The <" +aData[iLfn]+ "> file size is larger than " + fsizebig/1024 + " GB ."
                     tooltiptxt += "It must be less than 5 Gb to avoid overflowing the remote disk.'";                  
                   }
                  var sspan = "<span " + tooltiptxt+ " style='" + sizeStyle+ "'>"+ fsize.toFixed(2) + "&nbsp;M </span>";
                  $('td:eq(iFsize)', nRow).html(sspan);        
                  return nRow;       
               }
         });
      
         if ( job != undefined) {
            if ($.inArray(job.jobStatus,['finished', 'failed', 'holding', 'transferring', 'cancelled' ])>=0 ) {
               for (var r in rows) {
                  var lfn = rows[r];
                  if (lfn[iType].toLowerCase() === 'log' ) {
                     if ( utils().isFilled(lfn[iGuid]) ) {
                        var ddmse = job.ddmse;
                        var href = $("<a></a>"); href.attr("href", utils().oldPandaHost+ "?overview=viewlogfile&nocachemark=yes&guid=" +lfn[iGuid]+ "&lfn="+lfn[iLfn]+"&site=" +ddmse+"&scope="+lfn[iScope]);
                        href.html("<b>Find and view log files</b>");
                        $(tag).append(href);
                      } else {
                         $(tag).append("<b>Log files are not available; incomplete log file information (no guid)</b>");
                      }
                  }
               }
            } else {
                  $(tag).append("<div><font color=grey>Log files are not available until job is completed</font></div>");
            }
         }
      } else {
         $(tag).append(tdiv);
         $(tag).append("<div><font color=red><b>No files was found</b></font></div>");
      }
   }

    /* _________________________________________________________________________ */
   PandaMonitorViews.prototype.queryJobFiles = function(tag,job,dialog) {
      if (job.PandaID != undefined) {
         this.jqTag(tag).data('job', job);
         function rendJbFiles(tg,data) { views().renderJobFileList(tg,data,true); if (dialog != undefined) { views().jqTag(tg).dialog({ width: 800 });} }
         var lpars = { jobs: job.PandaID,type:'*',select:'lfn,type,fsize,status,dataset,guid,dispatchDBlock,destinationDBlock,destinationDBlockToken,scope,destinationse'};
         var aj = new AjaxRender();
         aj.download(tag,rendJbFiles,"joblfn",lpars);
      } else {
         this.jqTag(tag).html("<P>");
      }
   }
   /* _________________________________________________________________________ */
   PandaMonitorViews.prototype.queryScriptOffline = function(tag,job) {
      if (job.PandaID != undefined) {
         var scriptdiv = $("<div></div>");
         var theTag = views().jqTag(tag);
         function rendJbScript(tg,main) { 
            theTag.empty();
            if (main.buffer.type) {
               var data = main.buffer.data;
               if (data.indexOf("ERROR") == 0) { 
                 utils().renderAlert(scriptdiv,"No script has been fetched");
                 utils().renderAlert(scriptdiv,data);
               } else {
                 utils().renderText(scriptdiv,"\n  \n  \n"+data);
               }
               var link = $('<div><b>Show script to re-create job for offline debugging:&nbsp; '+ job.PandaID+ '</b><div>').addClass('pmLink');
               theTag.append(link);
               theTag.append(scriptdiv);
               link.on('click',function() { tg.toggle();} );
            }
         }
         var lpars = { method: 'getScriptOfflineRunning('+job.PandaID+')'};
         scriptdiv.css('display','none');
         var aj = new AjaxRender();
         aj.download(scriptdiv,rendJbScript,"taskBuffer",lpars);         
      } else {
         views().jqTag(tag).html("<P>");
      }
   }

   
    /* _________________________________________________________________________ */
   PandaMonitorViews.prototype.renderMCores = function(tag,main) {
      var d = $("<div></div>");
      var jobsumd = main.jobsumd;   var states  = main.states;  var params = main.params; 
      var jobtype = params['jobtype']; var cores = params['cores'];
      var mcores = (cores > 1);
      var hours = params['hours'];
      if (utils().len(jobsumd) >0 ) {
         var labels = ['Cloud'];
         if (mcores) { labels =['Cloud','Site']; } 
         labels = labels.concat(states);
         if (mcores) { labels = labels.concat(['cores']); }
         var hdr = utils().openTableHeader(labels);
         $(tag).empty();
         var table = [];
         for (var ir in jobsumd)  {
            var cloud  = ir;
            var sites = jobsumd[ir];
            var status = sites['status'];
            if ( status != 'online' && status != undefined ) {
               cloud += ' (' +status+ ')';
            }
            var r;
            if (mcores) {
                for ( var s in sites  ) {
                    if (s == 'status' || ( s == 'ALL' && cloud != 'ALL' ))  { continue; }
                    var site = sites[s]
                    r = [cloud,s];
                    r = r.concat(site);
                    table.push(r);
                 }
            } else {
                r = [cloud];
                r = r.concat(jobsumd[ir]['ALL']);
                table.push(r);
            }
         }
         var total = this.len(table);
         function tbFunc() {
            var options = {"aaSorting":[],"bStateSave" : false,"bUseRendered":false};
            if (total > 64) {
                 var displayTotal =  total;
                 if (total>300) displayTotal = 300; 
                 var half = displayTotal/2;
                 options= $.extend(options,{ "iDisplayLength": displayTotal
                          , "aLengthMenu": [ [displayTotal, -1,half], [displayTotal, "ALL" ,half] ]
                          });
            } else {
                options=$.extend(options,{   "bPaginate"    : false
                                           , "bLengthChange": false
                                           , "bInfo"        : false 
                                           , "sDom"         : '<"H"r>t<"F">'
                                           });
            }
            var dtHeader = utils().openTableHeader(labels);
            options["aaData"]    = table;
            options["aoColumns"] = dtHeader;
            options["fnRowCallback"]= function( nRow, aData, iDisplayIndex, iDisplayIndexFull ) 
            {
               var cloudvalue = aData[0];
               var sitevalue  = aData[1];
               var coreCount  = aData[15];
               var bf = undefined;
               var forceOldMon = true;
               if (cloudvalue == 'ALL' ) { 
                    bf = 'font-weight:bold'; 
                    $('td:eq(0)', nRow).html("<span style=" +bf+ ">"+cloudvalue+"</span>"); 
                    cloudvalue = undefined;
               }
               if (sitevalue == 'ALL' ) {  $('td:eq(1)', nRow).html('&nbsp;');sitevalue= undefined; }
               for (var i in aData) { 
                  if (i < 2) {
                     if  ( i == 0 && cloudvalue != undefined ) { $('td:eq('+i+ ')', nRow).html(utils().linkCloud(cloudvalue)); }
                     if  ( i == 1 && sitevalue != undefined ) { $('td:eq('+i+ ')', nRow).html(utils().linkSite(sitevalue)); }
                  }  else { 
                     var value =  aData[i];
                      if ( (( cloudvalue && cloudvalue != 'ALL' ) || sitevalue )&& value != 0)  {
                        var statusLabel = states[i-2];
                        pars = {
                            jobtype:jobtype
                           ,jobStatus:statusLabel
                           ,hours:hours
                           ,coreCount:coreCount
                        }
                        if (cloudvalue != 'ALL') { pars['cloud'] = cloudvalue;     }
                        if (sitevalue != 'ALL')  { pars['computingSite']=sitevalue;}
/*     this doesn't work from the http://panda.cern.ch pages !                   $('td:eq('+i+ ')', nRow).html(
                           views().linkJobInfoPars(value, pars,value,"Show the list of the " +statusLabel+ " " +coreCount+"-cores jobs for "+sitevalue+" site")); */
                        $('td:eq('+i+ ')', nRow).html(utils().linkJobs(cloudvalue,jobtype,statusLabel,hours,sitevalue,value, bf,undefined,undefined,undefined,undefined,undefined,undefined,undefined,undefined,true,coreCount,forceOldMon));
                     } else if ( value==0 ){
                         $('td:eq('+i+ ')', nRow).empty();
                     } else {
                         $('td:eq('+i+ ')', nRow).html("<span style=" +bf+ ">"+value+"</span>" );
                     }
                  }
               }
               return nRow;
            }
            return options;
         }     
         var tb = $('<table cellpadding="0" cellspacing="0" border="0" class="display" width=100%></table>');       
         d.append(tb);
         $(tag).append(d);
         utils().datatable(tb.uid(),tbFunc(), 25 );
      } else {
         d.html("<h3>There is no data to render</h3><br>"+ states + "<br>" + params);
         $(tag).append(d);
      }
   }


/* _____________________________________________________________________________*/
   PandaMonitorViews.prototype.ajax = function (refresh,tag,query,params,host,success,failure,delay) {
      /*  Execute the function 'success" with the dynamically loaded  the ajax data from 
                 http:<host>/<query>?params
          The  execution can be delayed if "delay"=true 
          and it can be refreshing  in 'refresh' sec
          The 'success' is the function to render its content with the "container" defined by "tag" parameter
      */
      if ( delay == undefined || !delay ) {
        this.download(tag,query,params,host,success,failure);
      }
      if  ( refresh && refresh > 0 ) {
         var download = function (t,q,p,h,s,f) { views().download(t,q,p,h,s,f); };
         setTimeout( function() { download(tag,query,params,host,success,failure);}, refresh*1000);
      }
   }

/* _____________________________________________________________________________*/
   PandaMonitorViews.prototype.download = function (tag,query,params,host,success,failure) {
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
PandaMonitorViews.prototype.pageSectionButton  = function(text,id) {
    /* JQuery UI '.ui-widget-header' button section separator */
    txt = "<p><table class='ui-corner-all ui-widget ui-widget-header' width='100%'><thead><tr><th align=left>"
    txt += "<button class='ui-button ui-widget ui-state-default ui-corner-all ui-button-text-only' "
    if (id !=undefined) {  txt +=  " id='" +id+ "'"; }
    txt += " width=100%>" +text+ "</button>";
    txt += "</th></tr></thead></table><p>";
    return $(txt);
}

//___________________________________________________________________________________________________
PandaMonitorViews.prototype.pageSection  = function(text) {
    /* JQuery UI '.ui-widget-header' page section separator */
    txt = $("<p><table class='ui-corner-all ui-widget ui-widget-header' width='100%'><thead><tr><th align=left>" +text+ "</th></tr></thead></table><p>");
    return txt;
}
//___________________________________________________________________________________________________
   PandaMonitorViews.prototype.renderHtml = function(tag,html) {
   var t = this.jqTag(tag);
   var alext = '<div class="ui-widget"><div class="ui-widget-content ui-corner-all" style="padding: 0 .7em;"><div>';
   alext +=  html;
   alext +=    '</div></div>'
   var alert = $(alext);
   t.append(alert);
}

//___________________________________________________________________________________________________
   PandaMonitorViews.prototype.renderScript = function(tag,html) {
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
   PandaMonitorViews.prototype.len =  function (object) {
   /* Calculate the number of the properties within the object */
      var count;
      if ( object != undefined ){  count = object.length; }
      if ( count == undefined) {
         count = 0;
         for (i in object) ++count;
      }
      return count;
   }
//___________________________________________________________________________________________________
   PandaMonitorViews.prototype.rebuidPlots =  function () {
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
   PandaMonitorViews.prototype.linkTable = function (table, column,showtxt,db) {
      /* Return link to  the Db table desciption   */
      if (showtxt == undefined)  {
         if ( table != undefined ) {  showtxt = table; 
         } else {  showtxt = column; }
      }
      return "<a href='" +$.param.querystring('describe', {table:table,column:column,db:db})+ "'>" +showtxt+ "</a>";
   }
   //___________________________________________________________________________________________________
   PandaMonitorViews.prototype.renderTblDescription =  function (header,table,db) {  
      var tableTable = "<table border=1 cellspacing=0 cellpadding=2><thead><tr>";
      var tableheaders = "<th>&nbsp;&nbsp;&nbsp;Table&nbsp;&nbsp;&nbsp;</th><th>Column&nbsp;</th><th>Size&nbsp;</th><th>Type&nbsp;&nbsp;</th>";
      tableTable += tableheaders+ "<td></td>" +tableheaders;
      tableTable += "<tbody>";
      var iTable = utils().name2Indx(header,'table_name');
      var itCol  = utils().name2Indx(header,'column_name');
      var itSiz  = utils().name2Indx(header,'data_length');
      var iType  = utils().name2Indx(header,'data_type');
      for ( var i in table ) {
         var row = table[i];
         if (! (i & 1))  {  tableTable+= "<tr>" } ;
         tableTable+= "<td align=left width=6em><b>" +this.linkTable(row[iTable],undefined,undefined,db)+ "</b></td>";
         tableTable+= "<td align=right width=6em>" +this.linkTable(undefined,row[itCol],undefined,db)+ "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</td>";
         tableTable+= "<td align=right width=5em>" +row[itSiz]+ "&nbsp;&nbsp;&nbsp;&nbsp;</td>";
         tableTable+= "<td align=right width=5em>" +row[iType]+ "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</td>";
         if ( i & 1)  { tableTable+=  "</tr>" ; }
         else { tableTable+= "<td></td>" ; }
      }
      tableTable += "</tbody></table>";
      return tableTable;
   }
   //___________________________________________________________________________________________________
   PandaMonitorViews.prototype.renderUsers=  function (tag,main) {  
      var dt = false;
      var sysrealtime = new Number(main._system.timing.real/1000.);
      var method  = main.buffer.method;
      var params  = main.buffer.params;
      var hours = params.hours;
      var data = main.buffer.data;
      var header = data.header;
      var users = data.rows;
      var totaljobs = main.buffer.totaljobs;
      var recent = main.buffer.recent;
      var iName = utils().name2Indx(header,'NAME');
      var iNJobs  = parseInt(utils().name2Indx(header,'NJOBSA'));
      var iLast  = utils().name2Indx(header,'LATESTJOB');
      var iCpua1  = utils().name2Indx(header,'CPUA1');
      var iCpua7  = utils().name2Indx(header,'CPUA7');
      var iCpup1  = utils().name2Indx(header,'CPUP1');
      var iCpup7  = utils().name2Indx(header,'CPUP7');
      var iCache  = utils().name2Indx(header,'SCRIPTCACHE');
      var headermap = {"NAME"       : "Users"
                      ,"NJOBSA"     : "<center># Jobs</center>"
                      ,"LATESTJOB"  : "<center>Latest</center>"
                      , "CPUA1"     : "<center>Personal<br>CPU-hours<br> 1 day</center>"
                      , "CPUA7"     : "<center>Personal<br>CPU-hours<br>7 days</center>"
                      , "CPUP1"     : "<center>Group<br>CPU-hours<br> 1 day</center>"
                      , "CPUP7"     : "<center>Group<br>CPU-hours<br>7 days</center>"
                      ,"SCRIPTCACHE": "Groups" };
      var d = $("<div id=renderUsersFrameId style='padding:0;margin:0'></div>");
      var sumtab = $("<table></table>");
      var tr = $("<tr></tr>"); sumtab.append(tr);
      var left = $("<td></td>");
      var wright=380; var hright=120;
      var right = $("<td></td>");
      right.css('width',wright); right.css('height',hright);
      left.css('height',hright);
      var tdiv = $("<div></div>");
      tr.append(left);tr.append(right);
      left.append(tdiv);
      var tline = "<p><p>Users in the last " ;
      var days2show = [3,7,30,90,180];
      var suffx = [" days " ,"","","",""];
      if (recent != undefined) {
         for (var h in days2show ) { var s = days2show[h]; tline += s+suffx[h] +":&nbsp; <b>" + recent['d'+s] +';</b> &nbsp;'; }
      }
      if (totaljobs!= undefined) { 
         tline += '<br>Usage in the last 7 days:  Job count:&nbsp; <b>';
         tline += totaljobs['anajobs'];
         
         tline += ';</b><br>Users with >1000 jobs: &nbsp;<b>' + totaljobs['n1000'];
         tline += ';</b> &nbsp; Users with >10k jobs: &nbsp;<b>'  + totaljobs['n10k']+ '</b>';
      }
      tdiv.html(tline);
      //var renderFunc =  function(t,m) { views().renderDebugInfo(t,m); }
      renderFunc = function success(tg,msg) {
         var timestamp = new Date();
         var elapsed = 0;
            var rows   = msg.info;
            var rhists;
            for (var el in rows) {
               if (rows[el][0] == "Histogram" ) {rhists = rows[el][1]; break; }
            }
            var d = $('<div></div>');
            d.attr('onclick','document.location="http://pandamon.cern.ch/useract?plot=True&width=880&file=useract365daysTotal";');
            d.css('cursor','pointer');
            var pl = new pmPlot(d);
            tg.append(d);
            pl.plotContainer(rhists, wright-20, hright-30);
       }
       //(tag,render,query,params,host,refresh,delay
      var aj = new AjaxRender();
      aj.download(right,renderFunc,'useract',{plot:'True',file:'useract365daysTotal'},'pandamon.cern.ch' );      
     /*  up('useract','plot=True&file=useract365daysTotal','atlascloud.org'); */
     /*    up('pyroot','block=pandsusers&file=useract365days','atlascloud.org'); */

      function tbFunc() {
         var total = utils().len(users);
         var options = {"aoColumnDefs": [  { "sWidth": "25%", "aTargets": [ iName ] }
                                         , { "sWidth": "5%",  "sClass" : "alignRight", "aTargets": [ iNJobs ]       } 
                                         , { "sWidth": "11%","bUseRendered": false ,  "aTargets": [iLast ]    }
                                         , { "sWidth": "7%" ,"bUseRendered": false,  "sClass" : "alignRight", "aTargets": [ iCpua1,iCpua7,iCpup1,iCpup7 ] }
                                        ]
                        };
         if (total > 64 ) {
              var displayTotal =  total;
              if (total>300) displayTotal = 300; 
              var half = displayTotal/2;
              $.extend(options,{ "iDisplayLength": displayTotal
                       , "aLengthMenu": [ [displayTotal, -1,half], [displayTotal, "ALL" ,half] ]
                       });
         } else {
             $.extend(options,{ "bPaginate": false,"bLengthChange": false, "bInfo": false });
             if (main.buffer.top != undefined) { options['aaSorting'] = []; }
         }
         var dtRows = users;
         options["aaData"]    = dtRows;        
         /* 
            var dtHeader = utils().openTableHeader(webHeader);  
            options["aoColumns"] = dtHeader; 
         */
         function tbclmn(i) {
            return 'td:eq('+i+')';
         }
         options["fnRowCallback"]= function( nRow, aData, iDisplayIndex, iDisplayIndexFull ) 
            {
               /* console.log(JSON.stringify(aData)); */
               var usrn = aData[iName]+"";
               var h = 71;
               if (aData[iCpua1] > 1 || aData[iCpup1] > 1  ) { h = 24; }
               /* else if ( aData[iCpua7] >=1  || aData[iCpup7] >=1  ) { h = 168; } */
               $(tbclmn(iName),nRow).html(utils().linkUser(usrn,usrn,h));
               $(tbclmn(iLast),nRow).html("<center>"+aData[iLast].slice(5,5+5)+' '+ aData[iLast].slice(11,11+5)+"</center>");
               function showHours(itm,u,h,d) {
                  var hours = h/3600.0;
                  if (hours>0) { 
                     itm.html(utils().linkUser(u,hours.toFixed(1),d*24));
                  } else { itm.html(''); }
               }
               showHours($(tbclmn(iCpua1),nRow),usrn,aData[iCpua1],1);
               showHours($(tbclmn(iCpua7),nRow),usrn,aData[iCpua7],7);
               showHours($(tbclmn(iCpup1),nRow),usrn,aData[iCpup1],1);
               showHours($(tbclmn(iCpup7),nRow),usrn,aData[iCpup7],7);
               return nRow;
            };
         return options;
      }

      d.append(sumtab);
      var top = main.buffer.top != undefined ? " Top " : "";
      d.append(utils().pageSection(''+utils().len(users)+ top+ ' Users in the Last ' +hours/24+ ' Days &nbsp; (CPU in CPU-hours)'));
      var table = $('<table border=1 cellspacing=0 cellpadding=3 class="display" width=100%></table>');
      var webHeader = "<thead>";
      var webFooter = "<tfoot>";
      var totaltop = main.buffer.totaltop;
      for (var h in header) {
         webHeader += "<th><small>"+headermap[header[h]]+"</small></th>";
         if (top != "" ) {
            if (h == iName)  {webFooter += "<th><small><b>Total " + utils().len(users)+ " users:</small></th>"; }
            else if  (h == iCpua1) {webFooter += "<th><b><small>" + (totaltop.cpua1/3600.0).toFixed(1)+ "&nbsp;<br>("+(totaltop.cpua1/3600.0/24).toFixed(0)+" days) &nbsp;</small></th>"; }
            else if  (h == iCpua7) {webFooter += "<th><b><small>" + (totaltop.cpua7/3600.0).toFixed(1)+ "&nbsp;<br>("+(totaltop.cpua7/3600.0/24).toFixed(0)+" days) &nbsp;</small></th>"; }
            else if  (h == iCpup1) {webFooter += "<th><b><small>" + (totaltop.cpup1/3600.0).toFixed(1)+ "&nbsp;<br>("+(totaltop.cpup1/3600.0/24).toFixed(0)+" days) &nbsp;</small></th>"; }
            else if  (h == iCpup7) {webFooter += "<th><b><small>" + (totaltop.cpup7/3600.0).toFixed(1)+ "&nbsp;<br>("+(totaltop.cpup7/3600.0/24).toFixed(0)+" days) &nbsp;</small></th>"; }
            else if  (h == iNJobs) {webFooter += "<th><b><small>" + totaltop.njobsa+ "&nbsp;&nbsp;</small></th>"; }
            else {webFooter += "<th></th>" } 
         }
       }
      webHeader += "</thead>";
      webFooter += "</tfoot>";
      table.append(webHeader);
      if (main.buffer.top != undefined ) {table.append(webFooter); }
      d.append(table);
      $(tag).empty();
      $(tag).append(d);
      utils().datatable(table.uid(),tbFunc(), 25 );
   }
   //___________________________________________________________________________________________________
   PandaMonitorViews.prototype.renderSiteSummary = function(tag,main,site) {
      var d = $("<div></div>");
      var jobsumd = main.jobsumd;   var states  = main.states;  var params = main.params;
      if (utils().len(jobsumd) >0 ) {
         var labels = ['Site'];
         labels = labels.concat(states);
         var hdr = utils().openTableHeader(labels);
         $(tag).empty();
         var table = []; 
         var htmlbody = ''
         var ir = site;
         var cloud  = site;
         for (var siteName in jobsumd[ir] ) {
            if (siteName == 'status' || siteName == 'ALL' ) { continue; } 
            var siteStat = [siteName];
            siteStat = siteStat.concat(jobsumd[ir][siteName].slice(0));
            r = [];
            for (var jbs in siteStat) {r.push(siteStat[jbs]); }
            table.push('<tr><td>'+r.join('</td><td>') + '</td></tr>');
         }
         htmlbody = '<tbody>' +table.join('')+ '</tbody>';         
         var dtb = '';/* '<table cellpadding="0" cellspacing="0" border="0" class="display" width=100%>'; */
         var htmlhdr = '<thead><th><small>'+labels.join('</small></th><th><small>') + '</small></th></thead>';
         dtb += htmlhdr;
         dtb += htmlbody;
         dtb += '</table>';
         return dtb;
      } else {
            d.html("<h3>There is no data to render</h3><br>"+ states + "<br>" + params);
            $(tag).append(d);
      }
   }
   
   //___________________________________________________________________________________________________
   PandaMonitorViews.prototype.PopUp = function(ref, site, type) {
      var newWin;
      var strFeatures="toolbar=no,status=no,menubar=no,location=no"
      strFeatures=strFeatures+",scrollbars=no,resizable=no,height=500,width=500"
      if (!newWin || newWin.closed) {newWin = window.open(ref,'TellObj',strFeatures);
      if (!newWin.opener) {newWin.opener = window; }
         newWin.document.write('<img src="http://gridinfo.triumf.ca/panglia/sites/day.php?'+ref+'" id="show_image"><p>');
         newWin.document.write('<input type=button onclick=document.getElementById("show_image").src="http://gridinfo.triumf.ca/panglia/sites/hour.php?'+ref+'"; value=Hour>');
         newWin.document.write('<input type=button onclick=document.getElementById("show_image").src="http://gridinfo.triumf.ca/panglia/sites/day.php?'+ref+'"; value=Day>');
         newWin.document.write('<input type=button onclick=document.getElementById("show_image").src="http://gridinfo.triumf.ca/panglia/sites/week.php?'+ref+'"; value=Week>');
         newWin.document.write('<input type=button onclick=document.getElementById("show_image").src="http://gridinfo.triumf.ca/panglia/sites/month.php?'+ref+'"; value=Month>');
         newWin.document.write('<input type=button onclick=document.getElementById("show_image").src="http://gridinfo.triumf.ca/panglia/sites/year.php?'+ref+'"; value=Year>');
         newWin.document.write('<p><input type=button value="Close" onclick="window.close();return false;">');
         newWin.document.close(); 
      }else { 
         if (window.focus) {newWin.focus()}; 
      } 
   }

   //___________________________________________________________________________________________________
   PandaMonitorViews.prototype.renderCloudSummary = function(tag,main) {
      var ALL =  ' ALL';
      var d = $("<div></div>");
      var jobsumd = main.jobsumd;   var states  = main.states;  var params = main.params;
      var jobtype = params['jobtype'];
      var vo = params['vo'];
      var hours = params['hours'];
      var region = params['region'];
      if (utils().len(jobsumd) >0 ) {
         var labels = (region != undefined)? ['Region'] : ['Cloud'];
         labels = labels.concat(states);
         var iPilots =  utils().name2Indx(labels,'Pilots');
         var iRatio  =  utils().name2Indx(labels,'%fail');
         var iFinished =  utils().name2Indx(labels,'finished');
         var iFailed =  utils().name2Indx(labels,'failed');
         var iLatest =  utils().name2Indx(labels,'latest');
         $(tag).empty();
         var table = [];
         for (var ir in jobsumd)  {
            var cloud  = ir;
            var status = jobsumd[ir]['status'];
            if ( status != 'online' && status != undefined ) {
               cloud += ' (' +status+ ')';
            }
            r = [cloud];
            r = r.concat(jobsumd[ir][ALL]);
            table.push(r);
         }
         var options={ 
               "bPaginate"   : false
              ,"bLengthChange": false
              ,"bInfo"       : false
              ,"aaSorting"   : []
              ,"bStateSave"  : true
              ,"bUseRendered": false
              ,"bJQueryUI"   : true
              ,"sDom"        : '<"H"r>t<"F">'
            };
/*
         var thisWindowSize = utils().windowSize();
         options['sScrollY']=Math.ceil(0.55*thisWindowSize[1]);
*/
         options["aaData"]    = table;
         options["aoColumns"] = utils().openTableHeader(labels);
         options["fnRowCallback"]= function( nRow, aData, iDisplayIndex, iDisplayIndexFull )
            {
               var cloudvalue = aData[0];
               var disabled =  cloudvalue.indexOf('(') >0 ;
               if (cloudvalue == ALL ) { cloudvalue = undefined; }
               for (var i in aData) {
                  var value =  aData[i];
                  var item =$('td:eq('+i+ ')', nRow);
                  if (disabled)  {  item.addClass("ui-state-disabled"); }
                  if (i == 0) {
                      if( value.toUpperCase() !== ALL) { item.html("<span style='cursor:pointer;display:inline;text-decoration:underline;' title='Click to toggle the site table'><b>"+value+"</b></span>"); 
                      } else {item.html("<span style='cursor:pointer;display:inline;text-decoration:underline;' title='Click to toggle all site tables'><b>"+value+"</b></span>") ; }
                      continue;
                  }
                  if ( i == iRatio)  {
                     if ( value > 50)  { 
                        item.html(''+parseInt(value));item.css('background-color',utils().colorMap['nfailed']).addClass('right').css('font-weight','bold');
                        var cells = [iFinished,iFailed];
                        for (var icell in cells) {
                            $('td:eq('+cells[icell]+ ')', nRow).css('background-color',utils().colorMap['nfailed']);
                        }
                     }else if (value < 1) { 
                       item.html("&lt;&nbsp;1%").css('font-weight','bold');
                     } else { 
                        item.html(''+parseInt(value));  
                     }
                     item.addClass('right');
                  } else if (i == iPilots)  {
                      if (value == 0) { value = '&nbsp;' ;}
                      item.html(''+value).addClass('right');
                  } else if (i == iLatest)  {
                      if (value == 0) { value = '&nbsp;' ;}
                        item.addClass('pmDate');
                        item.html(''+value);
                  } else if (value != 0)  {
                    var statusLabel = states[i-1];
                    var items = $.deparam.querystring();
                    $.extend(items, { jobtype:jobtype, jobStatus:statusLabel,hours:hours} );
                    if (items.region == undefined) {
                       items['cloud'] = cloudvalue;
                    } else {
                       items['region'] = cloudvalue;
                    }
                    if (items.jobtype == 'production') { items.jobtype += ",test";}
                    item.html(views().linkJobInfoPars(value,items)).css('text-align','right'); /*undefined,undefined,undefined,undefined,vo)); */
                  } else {
                    item.empty();
                  }
               }
               return nRow;
            };
          var dtb = $('<table cellpadding="0" cellspacing="0" border="0" class="display" width=100%></table>');
          d.append(dtb);
          var tdbui = dtb.uid();
          views().showSelection(tag,undefined,'cloudsummary');
          $(tag).append(d);
          var oTable = utils().datatable(tdbui,options, 25 );
          var selectall = $('#'+ tdbui + ' tbody tr');
          var alltr =  undefined;
          selectall.on('click',function () {
             if ( oTable.fnIsOpen(this) )  {
                oTable.fnClose(this);
             } else {
               var aPos = oTable.fnGetPosition( this ); 
               var aData = oTable.fnGetData( aPos );  
               var cloudName = aData[0];
               if (cloudName.toUpperCase() === ALL) {
                   /* open expand all other tables */
                   if (alltr == undefined) {
                      alltr = this;
                      selectall.click();
                      alltr =  undefined;
                  }
               } else {
                  var siteDiv = $('<div></div>');
                  var siteTag = siteDiv.uid();
                  var siteId = siteTag+'_site'; 
                  var siteTable = '<table id=' +siteId+' cellpadding="0" cellspacing="0" border="0" class="display" width=100%>' + views().renderSiteSummary('#'+siteTag,main,cloudName);
                  oTable.fnOpen(this,siteTable,'row-info');
                  var siteTableArray = []; 
                  for (var siteName in jobsumd[cloudName] ) {
                  /*  if (siteName == 'status') || siteName == 'ALL' ) { continue; }  */
                    if (siteName == 'status') { continue; } 
                    var siteStat = [siteName];
                    siteStat = siteStat.concat(jobsumd[cloudName][siteName].slice(0));
                    siteTableArray.push(siteStat);
                  }
                  var options={ 
                        "bPaginate"    : false
                       ,"bLengthChange": false
                       ,"bInfo"        : false
                       ,"aaSorting"    : []
                       ,"bStateSave"   : true
                       ,"bUseRendered" : false
                       ,"bJQueryUI"    : true
                       ,"sDom"         : 't<"F">'
                       ,"aaData"       : siteTableArray
                     };
                  options["fnRowCallback"]= function( nRow, aData, iDisplayIndex, iDisplayIndexFull )
                  {   
                     var items = { jobtype:jobtype, hours:hours};
                     if (region == undefined) {items['cloud'] = cloudName ; }
                     else { items['region'] = cloudName; } 
                     if ( aData[0] != 'Unknown' ) { items['computingSite']=aData[0];  }
                     else {items['computingSite']=undefined; }
                     for (var jbs in aData) {
                        var val = aData[jbs];
                        var row =   $('td:eq('+jbs+ ')', nRow);
                        var statusLabel = parseInt(jbs);
                        if (statusLabel == 0) {
                           items['jobStatus'] = undefined;
                           val = views().linkWnList(items.computingSite, jobtype,(parseFloat(hours)/24.).toFixed(2),undefined, val,undefined,"Show the site "+items.computingSite+" site load",'wn');
                           img = "<a style='cursor:help;' title= 'Show the site "+items.computingSite+" panglia plots' onclick='views().PopUp(\"SITE="+items.computingSite+"&SIZE=medium\", \"" +items.computingSite+"\", \"day\")'>"
                           img += "<img src='http://tjweb.org/tinychart.png' width=14 height=14 border=0/></a>";
                           val += " " + img;
                        } else if ( statusLabel == iRatio)  {
                           value = parseFloat(val).toPrecision(3);
                           row.addClass('right');
                           if ( value > 50)  { 
                              val = parseInt(value);
                              row.css('background-color',utils().colorMap['nfailed']).addClass('right').css('font-weight','bold');
                              var cells = [iFinished,iFailed];
                              for (var icell in cells) {
                                  $('td:eq('+cells[icell]+ ')', nRow).css('background-color',utils().colorMap['nfailed']);
                              }
                           }else if (value < 1) { 
                             val = "&lt;&nbsp 1%";
                           } else { 
                             val = ''+parseInt(value);  
                           }
                        } else if (statusLabel == iPilots)  {
                           row.addClass('right');
                           val = parseInt(val);
                           if ( items.computingSite != undefined ) {
                              val = utils().linkPilots(items.computingSite,val);
                           } else if (val==0) { val = '&nbsp;'; }
                        } else if ( statusLabel == iLatest)  {
                           row.addClass('pmDate');
                        } else {
                           row.addClass('right');
                           val = parseInt(val);
                           if (val != 0) { 
                              items['jobStatus'] = labels[statusLabel];
                              if  (val != undefined && val != 'undefined'  && val != '') {
                                 var itms = $.deparam.querystring();
                                 $.extend(itms,items );
                                 if (itms.jobtype == 'production') { itms.jobtype += ",test";}
                                 if (itms.computingSite != undefined && itms.computingSite.indexOf('ALL') >= 0) { itms.computingSite = undefined; } 
                                 val = views().linkJobInfoPars(val,itms); /* undefined,undefined,undefined,undefined,vo)); */
                              } else {
                                 val = '&nbsp;';
                              }
                           } else {
                              val = '&nbsp;';
                           }
                        }
                        row.html(val);
                     }
                  };
                  var dtab = $("#" + siteId).dataTable(options);
               }
             }
          });
      } else {
            d.html("<h3>There is no data to render</h3><br>"+ states + "<br>" + params);
            $(tag).append(d);
      }
   }
   //___________________________________________________________________________________________________
   PandaMonitorViews.prototype.renderPtimes=  function (tag,main)  {
      var d = $("<div></div>");
      var jtag = utils().jqTag(tag);
      jtag.empty(); /* jtag.uid(true); */
      var rows   = main.info;
      var layout = main.layout;
      var rhists;
      var rfile;   
      for (var el in rows) {
           if (rows[el][0] == "Histogram" ) {rhists = rows[el][1];}
           else if (rows[el][0] == "Root File" ) {rfile = rows[el][1].replace('.root',''); }
      }
      /* one can use http://www.orcca.on.ca/MathML/texmml/textomml.html to axis titles */
      
      var plottable= $('<table cellPadding="10" cellSpacing="4" border="4" class="display"></table>');
      plottable.uid();
      plottable.css("width",main.width+10);
      var maxHist = rhists.length;
      var div = new Array(maxHist);
      var plotHeaders = "<thead><tr class='ui-widget-header'>";
      for (var c=0; c<layout.columns; ++c) {
          var hname = rhists[c].attr.name;
          var hn= hname.split("_")[2]; /* to accommodate ppop application */
          if (hn == undefined) {hn=hname;}
          plotHeaders += "<th>" + hn+ "</th>";
      }
      plotHeaders += "</tr></thead><tbody>";  
      plottable.append(plotHeaders);
      var h = 0;   
      for (var r=0; r<layout.rows  && h < maxHist; ++r) { 
         var tr = $("<tr></tr>");
         for (var c=0; c<layout.columns  && h < maxHist; ++c,++h) { 
            var td = $("<td></td>");
            td.css('height',main.height+10);
            div[h] = $("<div></div>");
            td.append(div[h]);
            tr.append(td);
         }
         plottable.append(tr);
      }
      d.append(plottable);
      d.append("<P></P>");
      jtag.append(d);
      
      //$(document).ready(function() {
         for (var h in rhists) {
            var pl = new pmPlot(div[h]);
            pl.style = {title:true};
            pl.plotContainer([rhists[h]], main.width, main.height,main.log);
         }
       //utils().datatable(plottable.uid()); 
      //});
      var header = main.header;
      if (header != undefined && header.length >0 ) {
         var rtable = $('<table cellpadding="0" cellspacing="0" border="0" class="display"></table>');
         d.append(rtable );
         var hdr = [];
         var i = 0;
         for (var h in header)  {
            var hh = header[h];
            hdr.push( {"sTitle":hh } );
         }
         utils().datatable(rtable.uid(),{ 
                "aaData"       : rows
              , "aoColumns"    : hdr 
              , "fnRowCallback": function( nRow, aData, iDisplayIndex, iDisplayIndexFull ) 
                {
                  if (aData[0] == 'File') {
                     var cell = "Contains : "; 
                     if (aData[1] != undefined) { 
                        var dt = aData[1].data;
                        for (var o in dt) {
                           var rootObj = dt[o];
                           for (var  rootClass  in rootObj) {
                              if (rootClass.indexOf("TH1") >=0) {
                                 cell += " <b> " +rootClass+ "</b> : ";
                                 var qs = $.deparam.querystring();
                                 var name = rootObj[rootClass].split('_');
                                 qs.plots=name[1];
                                 qs.app=name[2];
                                 cell += "<a href=//atlascloud.org/" +$.param.querystring('ptimes',qs)+ ">" + rootObj[rootClass]+"</a>";
                              } else {   
                                 cell += " <span title='rendering the "+rootClass+ " ROOT object to be implemeneted yet'>" +rootClass+ ":";
                                 cell += rootObj[rootClass]+ " </span>";
                              }
                           }
                        }
                        $('td:eq(1)', nRow).html(cell); 
                     }
                  }
                  return nRow;
                }
         }, 25 );
      } else {
         d.html("<h3>There is no data to render</h3>");
         jtag.append(d);
      }
   }
   
   //___________________________________________________________________________________________________
   PandaMonitorViews.prototype.renderTaskTable=  function (tag,main,module) {  
      /* $Id: PandaMonitorViews.js 19632 2014-07-06 07:30:10Z jschovan $ */      
      $(tag).empty();
      if (module == undefined) {
         var loc = '' + location.pathname;
         if (loc.indexOf('tasks/listtasks1') ) {  
           module = 'tasks/listtasks1'; 
         } else if (loc.indexOf('tasks/listtasks') ) {  
           module = 'tasks/listtasks'; 
         }
      }
      views().showSelection(tag,undefined,module);
      var serialize = false;
      var _actionhdr='ACTION';
      var sysrealtime = new Number(main._system.timing.real/1000.);
      var method  = main.method;
      var hours = main.params.hours;
      var jobstatus = main.params.jobstatus;
      var action = main.action;
      var statushdr=jobstatus+'_JOBS';
      var iJobStatusIndx;
      if (action != undefined || jobstatus != undefined) {      
         var hd = main.tasks.header;
         if (action != undefined)  { hd = main.tasks.header = [_actionhdr].concat(hd); }
         if ( jobstatus != undefined ) {
             var hd2 =[];
             iJobStatusIndx  = 0;
             for (var h2 in hd ) {
                 if ( hd[h2].toLowerCase() == 'state' ) { hd2.push(statushdr); iJobStatusIndx = parseInt(h2);}
                 hd2.push(hd[h2]);
             }
             main.tasks.header = hd2;
         }
         var rows = main.tasks.rows;
         var idIndx = parseInt(utils().name2Indx(main.tasks.header,'ID'));
         var rowshash = {};
         for (var r in rows) {
            if (action != undefined) {
               rows[r] = [rows[r][0]].concat(rows[r]);
            }
            if (iJobStatusIndx != undefined) {
               rows[r] = rows[r].slice(0,iJobStatusIndx).concat([''],rows[r].slice(iJobStatusIndx));
//               rowshash[rows[r][idIndx] ] = rows[r];
               rowshash[ rows[r][idIndx] ] = r;
            }
         }
      }
      
      var d = $('<div></div>');
      var hh = '';
      if  (hours != undefined) {hh = '&hours='+hours; }
      d.append("<a href='http://panda.cern.ch?mode=listtaskAll'>ListTaskReqByID</a>&nbsp; &nbsp; <a title='Click to switch to the classic Panda view. Be patient. It may take time' href='http://panda.cern.ch?mode=listtaskStatus'>ListTaskReqByGrid</a>&nbsp; &nbsp;<a href='http://panda.cern.ch/?mode=listtask" + hh+ "&classic=true'>Classic List of the TaskReq</a>");
      var query = "<br> The server spent <b>" + sysrealtime.toFixed(3) + "</b> to access the CERN Oracle server";
      d.append(query);
      var tdiv = $("<div></div>");
      var tline = '<p><b>' + method + ': </b>';
      tdiv.html(tline);
      d.append(tdiv);
      $(tag).append(d);
      var taskTable;
      /* _________________________________________________________________________ */
      function countAttr(tag,main,attr) {                    
          var rows = main.tasks.rows;
          var header = main.tasks.header;
          var iStep =  utils().name2Indx(header,attr);
          var steps = {}
          var nsteps = 0;
          for (var r in rows) {
             var row = rows[r];
             var step = row[iStep];
             if  (steps[step] == undefined) { steps[step]  = 0; nsteps++;}
             steps[step]++;
          }
          if (nsteps >1) {
             var sta = $("<div class='ui-widget ui-widget-content ui-corner-all' style='padding:4px;'></div>");
             sta.append("<b>Task '"+attr+"' attributes: </b>");
             for (var s in steps) {
               var st = steps[s];
               if (st) {
                  sta.append("<b>"+s+":</b>");
                  var divstat = $("<div name='"+s+"' title='Click to see the <"+s+"> tasks' style='cursor:pointer; text-align:center; text-decoration:underline; color:blue; display:inline-block;'></div>");
                  divstat.click (function(){ if (taskTable != undefined) { var nm = $(this).attr('name'); taskTable.fnFilter(nm); } } ); 
                  divstat.append("("+st+ ")&nbsp; ");
                  sta.append(divstat);
               } 
             }
             var t = views().jqTag(tag);
             
             t.append(sta);
          }
      }
      
      /* _________________________________________________________________________ */
      function countSteps(tag,main) { 
          countAttr(tag,main,'STEP');
      }
      /* _________________________________________________________________________ */
      function countState(tag,main) {
          var jobsSubmitted = 0;
          var jobsRunning   = 0;
          var jobsDone      = 0;
          var jobsPending   = 0;
          var rows = main.tasks.rows;
          var header = main.tasks.header;
          var iState    =  utils().name2Indx(header,'state');
          var iReqJobs  =  utils().name2Indx(header,'Req_Jobs');
          var iDoneJobs =  utils().name2Indx(header,'Done_Jobs');
          var state= "total obsolete holding pending waiting submitting archived submitted running done finished failed aborted".split(' ');
          states = {total:rows.length };
          for (var r in rows) {
             var row = rows[r];
             var stat = row[iState];
             if  (states[stat] == undefined) { states[stat]  = 0; }
             states[stat]++;
             if (stat == 'pending' || stat == 'accepted') {
               jobsPending += row[iReqJobs];
             } else if (stat == 'submitted' || stat == 'submitting') {
               jobsSubmitted +=row[iReqJobs] - row[iDoneJobs];
               jobsDone    += row[iDoneJobs];
             } else if (stat == 'running' || stat == 'done' || stat == 'finished') { 
               jobsRunning += row[iReqJobs] - row[iDoneJobs];
               jobsDone    += row[iDoneJobs];
             }
          }
          var  jobsTotal = jobsPending + jobsSubmitted + jobsRunning + jobsDone;           

          var sta = $("<div class='ui-widget ui-widget-content ui-corner-all' style='padding:4px'></div>");
          var stab = $("<table></table>");
          var thead = $("<thead></thead>");
          var theadtr = $("<tr></tr>");
          var tbody  = $("<tbody></tbody>");
          var tbodytr = $("<tr></tr>");
          for (var s in state) {
            var st = state[s];
            theadtr.append("<th><small>"+st+"</small></th>");
            if (states[st]) {
               var divstat = $("<div name='"+st+"' title='Click to see the <"+st+"> tasks' style='cursor:pointer; text-align:center; text-decoration:underline; color:blue;'></div>");
               divstat.click (function(){ if (taskTable != undefined) { var nm = $(this).attr('name'); if (nm==state[0]){nm='';}; taskTable.fnFilter(nm,iState); } } ); 
               divstat.append(states[st]);
               var td = $("<td style='text-align:center;'></td>");
               td.append(divstat);
               tbodytr.append(td);
            } else {
               tbodytr.append("<td style='text-align:center;'>-</td>");
            } 
          }
          tbody.append(tbodytr);
          thead.append(theadtr);
          stab.append(thead); stab.append(tbody);
          sta.append("<b>Tasks:</b>");
          sta.append(stab);
          sta.append("<hr><b>Jobs:</b>" )
          sta.append(
                " &nbsp;&nbsp;&nbsp; Total: "    + jobsTotal
              + "; &nbsp;&nbsp;&nbsp; submitted:" + jobsSubmitted
              + "; &nbsp;&nbsp;&nbsp; running:"   + jobsRunning
              + "; &nbsp;&nbsp;&nbsp; done: "     + jobsDone
              );
          var jobsummary = $("<div id=jobsummaryid>Loading Job Summary . . . </div>");
          sta.append(jobsummary)
          jobsummary.data('jobsummaryid',{});
          var t = views().jqTag(tag);
          t.append(sta);
          t.append("<hr>");
      }
      /* _________________________________________________________________________ */
      function linkTasks(tid,jobStatus,txt) {
         var lpars = $.deparam.querystring();
         if (txt == undefined)  { txt = tid;}
         hourstxt = '';  if (lpars.hours != undefined)  { hourstxt = '&hours='+lpars.hours;}
         if (jobStatus == undefined)  { jobStatus = '';}
         else {jobStatus = '&jobStatus='+jobStatus; }
         if (module=='tasks/listtasks') { idname = "JediTaskID" ;} 
         else { idname = "taskID" ; } 
         title = 'Open the separate Window to show the Panda Jobs for this task';            
         return "<a target=panda_job title='" +title+"' href='http://pandamon.cern.ch/jobinfo?jobtype=production&"+idname+"=" +tid+jobStatus+hourstxt+ "'>" +txt+ "</a>";
       }
      
      /* _________________________________________________________________________ */
       function renderTasks(tag,main) {
          /* quick way to draw the Db table with the header generated by pmTaskBuffer */
         var header = main.tasks.header;
         var options = {};
         var hindx = utils().name2Indx(header);
         var lpars = $.deparam.querystring();
         var hours = 96;  if (lpars.hours != undefined) { hours= lpars.hours; }
         var actionIndx = parseInt(hindx[_actionhdr]);
         var idIndx=parseInt(hindx['ID']);   var tNameIndx =hindx['TASK_NAME'];var tInIndx = hindx["INPUT"];
         var rJobsIndx = hindx["REQ_JOBS"];  var nEvtIndx  =  hindx["EVENTS"]; var nPriIndx=hindx["PRI"]; 
         var dJobsIndx = hindx["DONE_JOBS"];
         var nGridIndx=hindx["GRID"];        var nStateIndx=hindx["STATE"];    var nPostIndx=hindx["POSTPROD"]; 
         var nTimeIndx=hindx["TIMESTAMP"];   var nProjectIndx=hindx["PROJECT"];var nDsnIndx=hindx["DSN"];
         var nPhysIndx=hindx["PHYS_REF"];    var nStepIndx=hindx["STEP"];      var nTagIndx=hindx["TAG"];
         /* create the hash */         
         var rows = main.tasks.rows;
         var t = views().jqTag(tag);
         var uid= undefined;
         var twidget = $("<div class='ui-widget ui-widget-content ui-corner-all'></div>");          
         var total = views().len(rows);
         if (total > 1) {
            if (total > 64) {
                 var displayTotal =  total;
                 if (total>300) displayTotal = 300; 
                 var half = parseInt(displayTotal/2)+1;
                 options= { "iDisplayLength": displayTotal
                          , "aLengthMenu": [ [displayTotal, -1,half], [displayTotal, "ALL" ,half] ]
                          };
             } else {
                options={ "bPaginate": false,"bLengthChange": false, "bInfo": false };
             }
             options['aaSorting']= [];
             options["aoColumnDefs"] = [ 
                      { "sWidth": "5em", "bUseRendered": false, "aTargets": [ idIndx ] } 
             ];
             if ( actionIndx != undefined ) {
                  options["aoColumnDefs"].push({"bSortable": false,"bUseRendered": false, "aTargets": [ actionIndx ] });
              }
              if (iJobStatusIndx != undefined) {
                   options["aoColumnDefs"].push( {  "bVisible": true , "bSortable": false, "aTargets": [ iJobStatusIndx ] }); 
              }
             options["bStateSave"] = true;
             function showTasks(tid,txt) {
               if (module !='tasks/listtasks') {
                  if (txt == undefined)  { txt = tid; } 
                  title = 'Open the separate Window to show the Task Request parameters';
                  return "<a target=panda_job title='" +title+"' href='http://panda.cern.ch?mode=showtask0&reqid=" +tid+ "'>" +txt+ "</a>";
               } else {
                  return txt;
               }
             }
             function thead(hdr) {
               hd = "<thead><tr>";
               for (var h in hdr) {
                  // if  (h==hdr.length-1) { break;}
                  if  (hdr[h] == _actionhdr) {  hd +="<td><center><span class='ui-icon ui-icon-gear'></span></center></td>" ; } 
                  else {
                    hd += "<th class='ui-state-default'><small>"+hdr[h].replace('_',' ')+ "</small></th>";
                  }
               }
               hd += "</tr></thead>";
               return hd;
            }
            function linkAction(id) {
               return  "<a class='ui-icon ui-icon-copy' title='Click to clone "+id+ " task' href='"+utils().version('tasks/clonetask')+"?tid="+id+"'>";
            }
            options["aaData"] = rows;
            options["fnRowCallback"]= function( nRow, aData, iDisplayIndex, iDisplayIndexFull ) 
            {  
               for (var i in aData) {
                 var item = $('td:eq('+i+')', nRow);
                 var val = aData[i];
                 var taskId;
                 if (i==idIndx) {
                     taskId = parseInt(val);
                     item.html(linkTasks(val));                  
                  } else if (i==tNameIndx)  {
                     item.html(showTasks(aData[idIndx],val));
                  } else if  (i==tInIndx) 
                     item.html("<center>"+ utils().linkDataset(val)+"</center>");
                  else if ( i ==  rJobsIndx ||  i== dJobsIndx  ) {
                     var style = '';
                     if  ( aData[rJobsIndx] != aData[dJobsIndx] ) {
                        item.css('color','red').css('font-weight','bold');
                     } 
                     if (i == rJobsIndx) {item.css('text-align','right'); }
                     if (i == dJobsIndx ) {
                        item.html(views().linkJobInfoPars(val,{taskID:taskId,jobStatus:'finished,failed,cancelled',limit:200,hours:hours},val,"Click to see the finished, failed, cancelled jobs for #"+ taskId+ " task"));
                     } else {
                        item.html(views().linkJobInfoPars(val,{taskID:taskId,limit:200,hours:hours},val,"Click to see the status of jobs for #"+ taskId+ " task"));
                     }
                  } else if (i == nPriIndx || i == nGridIndx || i== nEvtIndx )
                     item.css('text-align','right');
                  else if (i == actionIndx)
                     item.html(linkAction(val)); 
                  else if (i == nTimeIndx )
                     item.html((new Date(val*1000)).format("yyyy-mm-dd HH:MM"));
               }
               return nRow;
            };

            var table = $('<table cellpadding="0" cellspacing="0" border="0" class="display" width=100%></table>');
            table.append(thead(header));
            var tbody = $("<tbody></tbody>");
            table.append(tbody);
            twidget.append(table);
            uid = table.uid();
         } else if ( rows !== undefined && rows.length == 1) {
            var job = utils().zip(header,rows[0]);
            twidget.append(views().jobParamaters(job,header));
            uid = 'id_jobparameter_table';
            t.append(twidget);
            utils().datatable(uid,options,25);
            return undefined;
         } else {
            twidget.append("<div>no data to display</div>");
            t.append(twidget);
            return uid;
         }         
         t.append(twidget);
         return utils().datatable(uid,options,25);
      }
      views().jqTag(tag).append("<b>"+ new Date().format("yyyy-mm-dd HH:MM") +"</b><br>");
      countState(tag,main);
      countSteps(tag,main);
      countAttr(tag,main,'PROJECT');
      $(tag).append("<hr>");
      taskTable = renderTasks(tag,main);
      if (iJobStatusIndx != undefined) {
        /*  taskTable.fnSetColumnVis( iJobStatusIndx, false );*/
      }

      var rows = main.tasks.rows;
      var header = main.tasks.header;
      var total = views().len(rows);
      var iId = utils().name2Indx(header,'ID');
      var iJobsIndx = utils().name2Indx(header,"DONE_JOBS");
      var iFirst = 0;
      var iLast =  rows.length;
      /*_________________________________________*/
      function queryJobSummary() {
         taskIds = [];
         for (var ir=iFirst; ir < iLast; ++ir) {
            var rw = rows[ir];
            if ( rw[iJobsIndx] != 0) { taskIds.push(rw[iId]);}
            if (taskIds.length == 300 || ir == iLast-1 ) {
               if (taskIds.length != 0) {
                  var staskIds = taskIds.join(',');
                  aj = new AjaxRender();
                  var lpars = {  method : 'getTaskJobSummary(tasks=['+staskIds+']' };
                  if (hours != undefined ) { lpars['method'] += ',hours='+hours;}
                  if (jobstatus != undefined) {lpars['method'] += ",select='taskId,jobstatus'";}
                  lpars['method'] += ')';
                  iFirst = ir+1;
                  aj.download('jobsummaryid',showJobSummary, "taskBuffer",lpars);
                  if (serialize) {
                     break; 
                  } else { 
                     taskIds = [];
                  }
               }
            }
         }
      }
      /*_________________________________________*/
      function showJobSummary(tag,data) {
            if (iFirst == 0) {  
              $('#jobsummaryid').hide(); 
            } else {  
                var tg = $('#'+tag);
                var jobstates = tg.data(tag);
                var states =  data.buffer.data.rows;
                var header =  data.buffer.data.header;
                var hindx = utils().name2Indx(header);
                var  iStatus =  parseInt(hindx['JOBSTATUS']);
                var  iNJob =  parseInt(hindx['NJOBS']);
                var  iTaskID =  parseInt(hindx['TASKID']);
                var lStates = states.length-1;
                for (var st in states) {
                  var ss = states[st];
                  var njobs = ss[iNJob];
                  if (njobs == undefined) { continue;} 
                  var code = ss[iStatus];
                  if (jobstates[code] == undefined) { jobstates[code] = njobs;  }
                  else { jobstates[code] += njobs; }
                  if (iTaskID != undefined && iTaskID >=0 && code.toLowerCase() ==jobstatus) {
                     if  (rowshash[ss[iTaskID]] == undefined) {
                        /* console.log("ERROR. Unknown task status was fetched: " + ss[iTaskID]); */                     
                     } else {
                        rindx = rowshash[ss[iTaskID]];
                        var bDraw = (st == lStates);
                        var clr = views().colorMap[jobstatus];
                        var style = "font-weight:bold;text-align:right;"
                        if (clr != undefined )
                           style += "color:"+clr+";"
                        var statCell = "<div style='"+style+"'>"+linkTasks(ss[iTaskID],jobstatus,njobs)+"</div>";
                        if ( taskTable !== undefined )  {
                           var res = taskTable.fnUpdate(statCell,parseInt(rindx), parseInt(iJobStatusIndx), false,true);
                        }
                     }
                  }
                }       
                tg.empty();
                tg.append("<br><b>Summary of the Job States:</b>");
                outstat = '';
                var sttitle=['pending','defined','waiting','assigned','activated','sent','starting','running','holding','transferring','finished','failed','cancelled','unassigned'];
                for (var o in sttitle) { 
                  if (jobstates[sttitle[o]] != undefined && jobstates[sttitle[o]] != 0) {
                     outstat += ' &nbsp;&nbsp;<b>'+sttitle[o]+':</b>'+ jobstates[sttitle[o]];
                  }
                }
                tg.append(outstat);
                tg.show();
            }
            if (serialize) { queryJobSummary(); }
      }
      if (document.location.href.indexOf('panda.cern.ch') >=0 ){
         /* there is some issue with the nested ajax to be investigated later 17.01.2013 VF */
         $('#jobsummaryid').empty();
      } else {
         queryJobSummary();
      }      
   }

   //___________________________________________________________________________________________________
   PandaMonitorViews.prototype.renderPopularity=  function (tag,main) {  
      function hist2table(hist) {
         /* convert the histogram to table */
         var data = hist.data
         var bins = data.bins;
         var property = data.property;
         var total = property.Total;
         var xbound = property.xbound;
         var attr = hist.attr;
         var xlabels = attr.xaxis.labels;
         var xname = attr.xaxis.title
         var yname = attr.yaxis.title
         var ncolumn =4;
         var header = new Array(ncolumn);
         header[0]='#'; header[1]=xname;header[3]=yname;header[2]="%";
         var lrows = bins.length>xbound ? xbound : bins.length;
         var rows = new Array(lrows);
         for (var i=0;i<lrows;++i) {
            var row = new Array(ncolumn);
            row[0] = i+1;
            row[1]=xlabels[i];row[3]=bins[i];row[2]=(100*bins[i]/total).toFixed(1);
            rows[i]=row;
         }
         return {header: header, rows: rows, title:attr.title};
      }
      function linkPpop(months) {
         var div = $("<div class='ui-widget ui-widget-content ui-corner-all'></div>");
         div.append("<div class='ui-widget-header ui-corner-top' style='padding-left:5pt;padding-right:3px;'> The data are available for: </div>");
         var divdata = $("<div class='ui-widget ui-widget-content ui-corner-bottom' style='padding-left:5pt;padding-right:3px;'></div>");
         var qs = $.deparam.querystring();
         var frag =  $.deparam.fragment;
         var count = 0;
         for (var y  in months) {
            qs.year = y;
            var mm = months[y];
            for (var m in mm) {
               count++;
               qs.month = mm[m];
               cell = $("<a href=http://pandamon.atlascloud.org/" +$.param.querystring('ppop',qs)+ ">" +qs.year+"/"+qs.month +"</a>");
               divdata.append(cell); divdata.append("<span>&nbsp; </span>");
            }
         }
         // div.css({width: 6*count+'em'});
         div.append(divdata);
         return div;
      }  
      var d = $("<div></div>");
      $(tag).empty(); /* $(tag).uid(true); */
      /*
      $(tag).append("<b>TH1: </b>");
      var form = $("<form style='display:inline' id='formid'></form>");
      var input = $("<input type=text, id=jobid name='TH1', value='Enter the name'>");
      form.append(input);
      $(tag).append(form);   
      $(tag).delegate('form','submit', { tag : $(tag) } , function (event) { 
                  var t = event.data.tag;
                  var submit = 'pyroot?' + input.attr("name")+'='+ input.attr('value');
                  console.log('submit event'+ submit);
                  utils().submit(t,submit,event);
                  });               
   */
      var rows   = main.info;
      var layout = main.layout;
      var rhists;
      var rfile;   
      for (var el in rows) {
           if (rows[el][0] == "Histogram" ) {rhists = rows[el][1];}
           else if (rows[el][0] == "Root File" ) {rfile = rows[el][1].replace('.root',''); }
      }
      /* one can use http://www.orcca.on.ca/MathML/texmml/textomml.html to axis titles */
     
      var plottable= $('<table cellPadding="2" cellSpacing="2" border="3"></table>');
      // plottable.uid();
      plottable.css("width",main.width+10);
      var maxHist = rhists.length;
      var div = new Array(maxHist);
      var tab = new Array(maxHist);
      var plotHeaders = "<thead>";
      plotHeaders += "<tr><td id='datadirId' colspan=" + layout.columns+ "></td></tr>" 
      plotHeaders += "<tr class='ui-widget-header'>";
      
      for (var c=0; c<layout.columns; ++c) {
          var hname = rhists[c].attr.name;
          var hn= hname.split("_")[2]; /* to accomodate ppop application */
          if (hn == undefined) {hn=hname;}
          plotHeaders += "<th>" + hn+ "</th>";
      }
      plotHeaders += "</tr></thead><tbody>";  
      plottable.append(plotHeaders);
      var h = 0;
      for (var r=0; r<layout.rows  && h < maxHist; ++r) { 
         var tr = $("<tr></tr>");
         var trtab = $("<tr></tr>");
         for (var c=0; c<layout.columns  && h < maxHist; ++c,++h) { 
            var td = $("<td></td>");
            td.css('height',main.height+10);
            div[h] = $("<div></div>");
            td.append(div[h]);
            tr.append(td);
            td = $("<td></td>");
            tab[h] = $("<div></div>");
            td.append(tab[h]);
            trtab.append(td);
         }
         plottable.append(tr);
         plottable.append(trtab);
      }
      var center = $("<center></center>");
      center.append(plottable);
      d.append(center);
      d.append("<P></P>");
      $(tag).append(d);
      if (main.months) {
         var dtid = $('#datadirId');
         dtid.attr('id',"");
         dtid.append(linkPpop(main.months));
      }
      
      //$(document).ready(function() {
         for (var h in rhists) {
            var pl = new pmPlot(div[h]);
            pl.style = {title:true};
            pl.plotContainer([rhists[h]], main.width, main.height,main.log);
            
            var table =  hist2table(rhists[h]);
            var datatb= $('<table cellpadding="0" cellspacing="0" border="0"  class="display" width="100%"></table>');
            tab[h].append(datatb);
            var hdr = "<thead><tr><th class='ui-widget-header' colspan="+ table.header.length+ "><b>"+ table.title+ "</b></th></tr><tr>";
            for  (var h in table.header) {
              hdr += "<th"
              if (h==0) { hdr += " width=4em"; }
              /* else if (h == 1)  { hdr += " width=35em"; } */
              else if (h == 2)  { hdr += " width=15em"; }
              hdr += ">";
              hdr += table.header[h] + "</th>";
           }
           hdr += "</td></thead>";
           datatb.append(hdr);
           var lTable = table.rows.length;
           var optTable = {  "aaData"       : table.rows
/*                           , "bAutoWidth"   : false */
                           , "aoColumnDefs": [  { "aTargets": [ 0 ], "sClass": "alignRight"    } 
                                              , { "aTargets": [ 2 ], "sClass": "alignRight"    } 
                                              , { "aTargets": [ 3 ], "sClass": "alignRight"    } 
                                             ]
                           , "fnRowCallback": function( nRow, aData, iDisplayIndex, iDisplayIndexFull ) 
                              {
                                 var iRatio = 2;
                                 var ratio = parseFloat(aData[iRatio]);
                                 if (ratio < 0.1) {
                                   $('td:eq('+iRatio+')', nRow).html("&lt;0.1%");
                                 }               
                                 return nRow;
                              }
                          };
           if (lTable <= 25) {
              optTable['bPaginate']=false;
              optTable['bLengthChange']=false;
              optTable['bInfo']=false;
           }
           utils().datatable(datatb.uid('datatb'),optTable,25 );

         }
       //utils().datatable(plottable.uid()); 
      //});   
      var header = main.header;
      var tbrows = [];
      for (var row in rows) {
         if (rows[row][0].indexOf('Histo') >=0) {continue;}
         tbrows.push(rows[row]);
      }
      if (header != undefined && header.length >0 ) {      
         d.append('<table cellpadding="0" cellspacing="0" border="0" id="example" class="display"></table>' );
         var hdr = [];
         var i = 0;
         for (var h in header)  {
            var hh = header[h];
            hdr.push( {"sTitle":hh } );
         }
         var ex = $('#example'); ex.attr('id',ex.guid("example"));
         utils().datatable(ex.uid(),{ 
                "aaData"       : tbrows
              , "aoColumns"    : hdr 
              , "bPaginate"    :false
              , "bLengthChange":false
              , "bInfo"        :false
              , "fnRowCallback": function( nRow, aData, iDisplayIndex, iDisplayIndexFull ) 
                {
                  if (aData[0] == 'File') {
                     var cell = "Contains : "; 
                     if (aData[1] != undefined) { 
                        var dt = aData[1].data;                     
                        for (var o in dt) {
                           var rootObj = dt[o];
                           for (var  rootClass  in rootObj) {
                              if (rootClass.indexOf("TH1") >=0) {
                                 cell += " <b> " +rootClass+ "</b> : ";
                                 var qs = $.deparam.querystring();
                                 var name = rootObj[rootClass];
                                 qs.plots=name;
                                 cell += "<a href=//atlascloud.org/" +$.param.querystring('ppop',qs)+ ">" + rootObj[rootClass]+"</a>";
                              } else {   
                                 cell += " <span title='rendering the "+rootClass+ " ROOT object to be implemeneted yet'>" +rootClass+ ":";
                                 cell += rootObj[rootClass]+ " </span>";
                              }
                           }
                        }
                        $('td:eq(1)', nRow).html(cell);
                     }
                  } else if (aData[0].indexOf('Root') >=0 ){
                     $('td:eq(0)', nRow).html("Download the "+ aData[0]);
                     var filename = aData[1];
                     var anchor = $("<a title='Download the ROOT file' href='http://atlascloud.org/static/root/ppop/"+filename+"'>"+filename+"</a>")
                     anchor.click(function(event) { 
                          event.preventDefault();
                           event.stopPropagation(); 
                           window.location=$(this).attr('href'); 
                     });
                     var row = $('td:eq(1)', nRow);
                     row.html("");
                     var bytton = $('<span style="cursor: pointer; display: inline-block;" title="Download the ROOT file" class="ui-icon ui-icon-disk"> </span>');
                     row.append(bytton);
                     bytton.click(function(event) { 
                          event.preventDefault();
                          event.stopPropagation(); 
                          window.location=anchor.attr('href'); 
                     });
                     row.append("&nbsp;&nbsp; ");
                     row.append(anchor);
                  }
                  return nRow;
                }
         }, 25 );
      } else { 
         d.html("<h3>There is no data to render</h3>");
         $(tag).append(d);
      }
   }

   //___________________________________________________________________________________________________
   PandaMonitorViews.prototype.renderMCShares =  function (header,mcshare) {  
      var mcshareTable = "<table border=1 cellspacing=0 cellpadding=2><thead><tr>";
      mcshareTable += "<th colspan=5>";
      mcshareTable += "<a href='https://twiki.cern.ch/twiki/bin/viewauth/AtlasComputing/BambooServer#Task_brokerage'>";
      mcshareTable += "MC share used in the task brokerage</a></th><tr>"
      var mcshareheaders = "<th>&nbsp;&nbsp;&nbsp;Cloud&nbsp;&nbsp;&nbsp;</th><th>MC Share&nbsp;&nbsp;</th>";
      mcshareTable += mcshareheaders+ "<td></td>" +mcshareheaders;
      mcshareTable += "<tbody>";
      var imcshares = utils().name2Indx(header,'mcshare');
      for ( var i in mcshare ) {
         var share = mcshare[i];
         if (! (i & 1))  {  mcshareTable+= "<tr>" } ;
         mcshareTable+= "<td align=center width=5em><b>" +utils().linkCloud(share[0])+ "</b></td><td align=right width=10em>" + share[imcshares]+ "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</td>";
         if ( i & 1)  { mcshareTable+=  "</tr>" ; }
         else { mcshareTable+= "<td></td>" ; }
      }
      mcshareTable += "</tbody></table>";
      return mcshareTable;
   }
