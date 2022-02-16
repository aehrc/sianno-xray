//CODE adapted from https://gist.github.com/RiseupDev/b07f7ccc1c499efc24e9

$(document).ready(function(){

    $(".annotation_button").click(
        function(){

            last_key_pressed = $(this).attr("data-key-pressed-id");
            //add spinner to the the current button
            $(this).append('<div class="spinner-grow spinner-grow-sm    " role="status"><span class="sr-only">Loading...</span></div>');
            //disable all annotation buttons
            $(".annotation_button").prop("disabled", true);     
        }
    );
    
    $("#btn_delete_selected").click(function(){

        d3.selectAll('g.active').remove();
        d3.selectAll('circle.active').remove();
        d3.selectAll('polygon.active').remove();
    });

    $("#id_btn_save_next").click(function(){           
        updatePolygonInfo(false, "NO_MODAL");      
    });

    $("#id_btn_save_wrist_xray").click(function(){

        updatePolygonInfo(true,'#wxModal') 
    });
})

//---------------------------------  Variables  -----------------------------------//

var last_key_pressed = "-1";
var dragging, drawing = false;
var startPoint;
var global_data = [];
var points = [], g;


if(type == "PANAROMIC"){
    if(width > 1200 && scale == 1.0){
      scale = width/1200;
    };
} else {
    if(width > 1000 && scale == 1.0){
      scale = width/1000;
    };
};

//instantiate svg and group elements 
//DOM is:
//<div id="imageBody-WX" class="container-fluid">
//  <svg width="" height="">
//    <g id="g_all_elements">
//      <image href="/media/document_tray/<user>/<image name>" width="" height="" x="" y=""></image>
//      <g class="polygon">
//        <polygon class="wfPoly" points="676, 232.1, 232.2, 122.45" style=blah>
//        <circle class="polygonCircle" cx="676" cy="232.1" r=4 etc></circle>
//        <circle class="polygonCircle"></circle>
//        <circle class="polygonCircle"></circle>
//      </g>
//    </g>
//  </svg>
//</div>
var svg = d3.select("#imageBody-WX").append("svg")
            .attr("width", width/scale)
            .attr("height", height/scale);
var text = svg.selectAll("text");
var g_wrist = svg.append("g")
                 .attr("id", "g_all_elements")  
                 .attr("draggable", false)               
                 .on("focus", function(){});

var img = g_wrist.append("svg:image")
	.attr("xlink:href", url)
	.attr("width", width/scale) //is this neccessary?
	.attr("height", height/scale)
	.attr("x", 0)
	.attr("y", 0)
    /*
	.on("mousedown", mousedown)
	.on("mouseup", mouseup);*/

//zoom functionality
var zoom = d3.behavior.zoom()
.scaleExtent([1, 10])
.on("zoom", zoom_wrist);


//TODO - enabling zoom causes image (as part of <g class="g_all_elements">) to drag along with
//polygon points.
function zoom_wrist() {
    //g_wrist.attr("transform", "translate(" + d3.event.transform.x + "," + d3.event.transform.y + ") scale(" + d3.event.transform.k + ")");
}

g_wrist.call(zoom);
//disable zoom on double-click
g_wrist.on("dblclick.zoom", null);


//fetch the locally saved json polygon data and draw them onto the image
d3.json("/media/" + document_id + "/polygon_new.json", function(error,data){    
    circle_points = data["circle"];
    polygon_points = data["polygon"];
    fracture_info = data["fracture_info"]
    if(circle_points.length !=0) {
        for(var i=0; i < circle_points.length; i++) {
            //for each polygon draw it, circles on the points, and the fracture info
            DrawPolygon(circle_points[i], polygon_points[i], fracture_info[i]) 
        }
    }
});//thanks, json

//--------------------------------------  Functions  -----------------------------------------------//

//Get the set of x,y coordinate where y is the lowest (ie closest to the top of the screen) value
function FindLowestCoordinatePairY(arr){
    var x = arr[0][0];
    var minY = arr[0][1];
    for(var i=1; i < arr.length; i++) {
        if(arr[i][1] < minY){
            x = arr[i][0];
            minY = arr[i][1];
        }
    }
    var coords = [];
    coords[0] = x;
    coords[1] = minY;

    return coords
}

function DrawPolygon(circle_points, polygon_points, fracture_info){
    //only draws one polygon at a time
    var g = g_wrist.append("g")
                .attr("class","wfPoly")
                .on("mousedown", function(d){ //set polygon to active on click
                    console.log("DrawPolygon; clicked on polygon");
                    //if already active, make elements not active
                    //if the clicked polygon is already active , then we make all elements not active
                    if (d3.select(this).classed("active")){
                        d3.select(this).classed("active", false );
                        d3.select(this).select("polygon").classed("active", false);
                        d3.select(this).selectAll("circle").classed("active", false);
                    }
                    else {//if clicked polygon is not active then only make the current one active                        
                        d3.select(this).classed("active", true);
                        d3.select(this).select("polygon").classed("active", true);
                        d3.select(this).selectAll("circle").classed("active", true);
                    }                    
                });
    g.append("polygon")
     .attr("points", polygon_points)
     .style("fill", "blue")
     .style("fill-opacity", "0.4");    
    
    for(var i = 0; i < circle_points.length; i++) {
        g.selectAll("circles")
            .data([circle_points[i]])
            .enter()
            .append("circle")          
            .attr("cx", circle_points[i]["x"])
            .attr("cy", circle_points[i]["y"])
            .attr("r", 2)
            .attr("fill", "#FDBC07")
            .attr("stroke", "#000")
            .attr("is-handle", "true")
            .style({cursor: "move"})
            .call(dragger)        
    }; 
    //need to convert the polygon points to numbers for FindLowestCoordinatePair() to work
    var int_polygon_points = [];
    for(var i = 0; i < polygon_points.length; i++){
        int_polygon_points[i] = [parseFloat(polygon_points[i][0]),parseFloat(polygon_points[i][1])]
        
    }
    var text_coords = FindLowestCoordinatePairY(int_polygon_points);

    g.append("text")
     .classed("bone_number", true)
     .attr("x", text_coords[0])
     .attr("y", text_coords[1])
     .style("font-size", function(){
        if(type == "PANAROMIC"){
          return "1.0em"
        }else{
          return "1.5em"
        }
      })
     .style("fill", "orange")
     .text(fracture_info["bone_number"])
     .attr("bone_number", fracture_info["bone_number"])
     .attr("fracture_on_current_view", fracture_info["fracture_on_current_view"])
     .attr("fracture_on_other_view", fracture_info["fracture_on_other_view"])
     .attr("view_type", fracture_info["view_type"])

    return;
}

var dragger = d3.behavior.drag()
    .on("drag", handleDrag)
    .on("dragend", function(d){
        dragging = false;
        var newPoints = [], circle;        
        var circles = d3.select(this.parentNode).selectAll("circle");
        var text = d3.select(this.parentNode).select("text");
        for (var i = 0; i < circles[0].length; i++) {
            circle = d3.select(circles[0][i]);
            newPoints.push([circle.attr("cx"), circle.attr("cy")]);
        }        
        //these come as strings, so convert them        

        var intNewPoints = [];
        for(var i = 0; i < newPoints.length; i++){
            intNewPoints[i] = [parseFloat(newPoints[i][0]),parseFloat(newPoints[i][1])]        
        }
        var text_coords = FindLowestCoordinatePairY(intNewPoints);
        text.attr("x",text_coords[0])
            .attr("y",text_coords[1])
            
    });
//drag the polygon using its points
function handleDrag() {
    console.log("handle drag");
    if(drawing) return;
    var dragCircle = d3.select(this), newPoints = [], circle;
    dragging = true;
    var poly = d3.select(this.parentNode).select("polygon");
    var circles = d3.select(this.parentNode).selectAll("circle");
    dragCircle.attr("cx", d3.event.x).attr("cy", d3.event.y);
    for (var i = 0; i < circles[0].length; i++) {
        circle = d3.select(circles[0][i]);
        newPoints.push([circle.attr("cx"), circle.attr("cy")]);
    }
    poly.attr("points", newPoints);
}

g_wrist.on("keydown", function() {
    // last_key_pressed = d3.event.key;
    if(d3.event.key == 'Escape'){
        g_elm.select('g.drawPoly').empty();
        g_elm.select('g.drawPoly').remove();
        points = [];
        startPoint = "";
    };
})

g_wrist.on("mouseup", function(){
    if(last_key_pressed == "1"){

        if(dragging) return;
        drawing = true;
        startPoint = [d3.mouse(this)[0], d3.mouse(this)[1]];

        if(g_wrist.select("g.drawPoly").empty()){
            g = g_wrist.append("g")
                    .attr("class","drawPoly");            
        }

        if(d3.event.shiftKey){
            closePolygon();
            return;
        }

        points.push(d3.mouse(this));
        g.select("polyline").remove();

        g.append("polyline")
            .attr("points", points)
            .style("fill","none")
            .attr("stroke","#000");

        for(var i =0; i < points.length; i++){
            g.append("circle")
            .attr("cx", points[i][0])
            .attr("cy", points[i][1])
            .attr("r", 4)
            .attr("fill", "#FDBC07")
            .attr("stroke", "#000")
            .attr("is-handle", "true")
            .style({cursor: "pointer"})
            .on("click",function(d){
                d3.select(this).classed("active", !d3.select(this).classed("active"));
                d3.select(this.parentNode).select("polygon")
                                        .classed("active",d3.select(this).classed("active"));
                d3.select(this.parentNode).select("polygon")
                                        .classed("active",d3.select(this).classed("active"));
                
            })
        }
    }
});

//closes polygon and adds the same on click functionality as DrawPolygon()
function closePolygon() {
    console.log("closePolygon");
    g_wrist.select("g.drawPoly").remove();
    var g = g_wrist.append("g")
    g.attr("class","wfPoly") 
     .on("click", function(d){ 
        //console.log("closePolygon - clicked on polygon");              
        //if the clicked polygon is active, make it not active
        if (d3.select(this).classed("active")){
            d3.select(this).classed("active", false );
            d3.select(this).select("polygon").classed("active", false);
            d3.select(this).selectAll("circle").classed("active", false);
        }
        else//if clicked polygon is not active then only make the current one active
        {
            d3.select(this).classed("active", true);
            d3.select(this).select("polygon").classed("active", true);
            d3.select(this).selectAll("circle").classed("active", true);
        }         
    })
    //on double click
    .on("dblclick", function(d){
        var text_element = d3.select(this).select("text");
        console.log("Bone number: " + text_element.attr("bone_number"));
        open_modal(text_element)
    });

    g.append("polygon")
    .attr("points", points)
    .style("fill", "blue")
    .style("fill-opacity", "0.4");
    
    for(var i = 0; i < points.length; i++) {
        g.selectAll("circles")
         .data([points[i]])
         .enter()
         .append("circle")
         .classed("circle" + i, true)
         .attr("cx", points[i][0])
         .attr("cy", points[i][1])
         .attr("r", 2)
         .attr("fill", "#FDBC07")
         .attr("stroke", "#000")
         .attr("is-handle", "true")
         .style({cursor: "move"})
         .call(dragger);
    }
    
    var text_coords = FindLowestCoordinatePairY(points);

    g.append("text")
     .classed("bone_number", true)
     .attr("x", text_coords[0])
     .attr("y", text_coords[1])
     .style("font-size", function(){
        if(type == "PANAROMIC"){
          return "1.0em"
        }else{
          return "1.5em"
        }
      })
     .style("fill", "orange")
     .text("unknown")
     .attr("bone_number", "unknown")
     .attr("fracture_on_current_view", "unknown")
     .attr("fracture_on_other_view", "unknown")
     .attr("view_type", "unknown")


    points.splice(0);
    drawing = false;

    //reset the annotation button
    $(".annotation_button").prop("disabled", false);
    $(".spinner-grow").remove();
    //reset the last_key_pressed
    last_key_pressed = "-1";

    return;
}

g_wrist.on("mousemove", function(){
    if(!drawing) return;
    var g = d3.select("g.drawPoly");

    g.select("line").remove();
    g.append("line")
        .attr("x1", startPoint[0])
        .attr("y1", startPoint[1])
        .attr("x2", d3.mouse(this)[0] + 2)
        .attr("y2", d3.mouse(this)[1])
        .attr("stroke", "#53DBF3")
        .attr("stroke-width", 1);
})

function getPolygonInfo(){
    polygon_info = [];
    polygon_point_list = [];     
    d3.selectAll("g.wfPoly").each(function(d,i){
        polygon_points = d3.select(this).select("polygon")[0][0].points;        
        var text_element = d3.select(this).select("text")        
        polygon_point_list = [];        
        for(i=0; i<polygon_points.length; i++){
            polygon_point_list.push({"x" : polygon_points.getItem(i)["x"], "y" : polygon_points.getItem(i)["y"], "idx" : i});
        };        
        polygon_info.push({polygon_point_list,
        "bone_number":text_element.attr("bone_number"),
        "fracture_on_current_view":text_element.attr("fracture_on_current_view"),
        "fracture_on_other_view":text_element.attr("fracture_on_other_view"),
        "view_type":text_element.attr("view_type")
        });       
    });
    //console.log("Stringify: " + JSON.stringify(polygon_info));
    return polygon_info;
};

//use ajax to post - gets a JSONResponse back (from view.py) with success or failure
function updatePolygonInfo(do_reload, modal_id){
    
    var polygon_info = JSON.stringify(getPolygonInfo());    
    //console.log("polygon_strings: ", polygon_strings)
    var json_dict = {
        "polygons" : polygon_info,
    };   
    
    $.ajax({
        type: "POST",
        url: "",
        data : json_dict,        
        dataType: "json",
        success: function(data){
            console.log("success in ajax post")
            if (data.result == "OK"){  
                if(do_reload == true){
                    window.location.reload(true);
                }
                else{
                    if(modal_id == "NO_MODAL"){                        
                        window.location.href = data.redirect_url;
                    } else {
                        $(modal_id).modal('hide')
                    }
                }                 
            }
            else {                   
                alert("Error in saving: " + data.result);   
            }        
        },
        error: function(data){
            alert("HTTP Error in saving: " + data.status + " result: " + data.result
            + " data: " + data.polygons);
        }
    });    
};

// modal functions

//function argument is the text element of the clicked polygon
function open_modal(text_element){
	//double-click on rectangle
	console.log("double clicked, open wrist fracture modal");
    var info = getPolygonInfo();    
	//make the text element that has been passed active
    text_element.classed("active", true)
    //if these attributes have been assigned, make the corresponding buttons active
    d3.selectAll(".btn.btn-primary.bone_number").classed("active", false);
    d3.select("#__bone_" + text_element.attr("bone_number")).classed("active", true);

    d3.selectAll(".btn.btn-primary.fracture_on_current_view").classed("active", false);
    d3.select("#__fracture_on_current_view_" + text_element.attr("fracture_on_current_view")).classed("active", true);

    d3.selectAll(".btn.btn-primary.fracture_on_other_view").classed("active", false);
    d3.select("#__fracture_on_other_view_" + text_element.attr("fracture_on_other_view")).classed("active", true);

    d3.selectAll(".btn.btn-primary.view_type").classed("active", false);
    d3.select("#__view_type_" + text_element.attr("view_type")).classed("active", true);
    
	$("#wxModal").modal();
  
};

//asigned to the buttons inline in wrist_xray_modal.html
function btn_clicked(key,value){
    console.log("btn_clicked; " + key + value);
    //Deactivates all of the bone_number buttons
    d3.selectAll(".btn.btn-primary.bone_number").classed("active", false);
    //Activates only the button with the corresponding value
    d3.select("#__bone_" + value).classed("active", true);

    text_element = d3.select("text.bone_number.active")//.attr("class", "bone_number active");    
    text_element.attr(key, value)
    console.log(JSON.stringify(getPolygonInfo()))
}


