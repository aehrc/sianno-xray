var svg = d3.select("#svg_screening_image");
var zoom_all = d3.zoom()
  .scaleExtent([1, 10])
  .on("zoom", zoom_function);


function zoom_function() {
    g_all_elements.attr('transform', 'translate(' + d3.event.transform.x + ',' + d3.event.transform.y + ') scale(' + d3.event.transform.k + ')');

}

var g_all_elements = d3.select("#g_all_elements");
g_all_elements.call(zoom_all);
