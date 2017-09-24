function _hellooraplot_(tag,data) {
/* $Id: hellodb.js 10144 2011-12-29 19:29:20Z fine $ */
/* Display DB status and stats */
    $(tag).empty();
    var thisTag =  $("<div></div>");
    thisTag.append("<p>Total size: " + data.size + "  MB"); 
    thisTag.append("<p>Total items: " + (data.items/(1024*1024)).toFixed() + "  MB");
    thisTag.append("<p>Average item size: " + data.itemsize + "  bytes"); 
    thisTag.append("<p>Number of domains: " + data.ndomains); 
    thisTag.append("<p>Domain info:");
    $(tag).append(thisTag);
}

