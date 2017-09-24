function _hellodb_(tag,data) {
/* $Id: hellodb.js 10933 2012-03-06 22:46:22Z fine $ */
/* Display DB status and stats */
    $(tag).empty();
    var thisTag =  $("<div></div>");
    thisTag.append("<p>Total size: " + data.size + "  MB"); 
    thisTag.append("<p>Total items: " + (data.items/(1024*1024)).toFixed() + "  MB");
    thisTag.append("<p>Average item size: " + data.itemsize + "  bytes"); 
    thisTag.append("<p>Number of domains: " + data.ndomains); 
    thisTag.append("<p>Domain info:");
    var table = $('<table cellpadding="2" cellspacing="2" border="1" class="display" id="dbstat_table"></table>');
    thisTag.append(table);
    var h = $("<thead></thead>");
    table.append(h);
    var hr = $("<tr></tr>");
    hr.css( {"text-decoration":"underline", "color":"blue", "cursor":"pointer"});
    h.append(hr);
    $.each(data.header, function(i,header) { hr.append($("<th>" +header + "</th>")); } );
    h = $("<tbody></tbody>");
    table.append(h);
    $.each(data.info, function(i,r) {
      var tr = $('<tr></tr>');
      tr.css("font-size","0.6em");
      h.append(tr);
      $.each(r, function(d,v) {
         if (d == 1)      v = (v/100000).toFixed(2);
         else if (d == 5) v = (v/100000).toFixed(1); 
         var td = $("<td>" + v  + "</td>");
         tr.append(td);
         if ( d!=0) { td.css("text-align","right") ;}
      } );
    } );
    var h = $("<tfoot></tfoot>");
    table.append(h);
    var hr = $("<tr></tr>");
    h.append(hr);
    $.each( data.header , function(i,h) { hr.append($("<th>" + h + "</th>")); } );
    $(tag).append(thisTag);
    $('#dbstat_table').dataTable({"bProcessing": true ,"bJQueryUI": true});
}

