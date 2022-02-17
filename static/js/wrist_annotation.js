//------------------------Global scope variables----------------------------//
//constants
var HANDLE_R = 5;
var HANDLE_R_ACTIVE = 7;

var MAP_HEIGHT = 2500;
var MAP_WIDTH = MAP_HEIGHT * Math.sqrt(2);

var MAX_TRANSLATE_X = MAP_WIDTH / 2;
var MIN_TRANSLATE_X = -MAX_TRANSLATE_X;

var MAX_TRANSLATE_Y = MAP_HEIGHT / 2;
var MIN_TRANSLATE_Y = -MAX_TRANSLATE_Y;

var MIN_RECT_WIDTH = 10;
var MIN_RECT_HEIGHT = 10;

//d3.json fetches the rectangles for that document id that are stored as /rect.json'. 
//Update then puts the rectangles onto the image
var global_data = []
d3.json('/media/' + document_id + '/rect.json', function(error, data){
	data.forEach(function(rect){
		global_data.push(rect);
	});	
	update();
});//end of json


//Not used
var
  inpX = document.getElementById("x"),
  inpY = document.getElementById("y"),
  inpWidth = document.getElementById("width"),
  inpHeight = document.getElementById("height");

//null, null, null, null
console.log("inpX = " + inpX + ", inpY = " + inpY + ", width = " + inpWidth + ", height = " + inpHeight);

//Get image scale
if(type == "PANAROMIC"){
  if(width > 1200 && scale == 1.0){
    scale = width/1200;
  };
}else{
  if(width > 1000 && scale == 1.0){
    scale = width/1000;
  };
}

//select div container with id of imageBody-wx, add it to SVG with width and height adjusted
var svg = d3.select("#imageBody-WX").append("svg")
  .attr("width", width/scale)
  .attr("height", height/scale);
//get text annotation
var text = svg.selectAll("text");
//add svg to group
var g_wrist = svg.append("g"); //group

//Still unsure of this one
g_wrist.on("keydown", function(){
	if(d3.event.key == "Backspace" || d3.event.key == "Delete"){
    console.log("keydown; backspace or delete");
    //need to remove from global_data too
    g_wrist.selectAll(".active").each(function(){
      width = d3.select(this).attr("width");
      height = d3.select(this).attr("height");
      x = d3.select(this).attr("x");
      y = d3.select(this).attr("y");

      filtered_array = global_data.filter(function(elems, i){
        if(elems.width == width && elems.height == height){
            //then that value exist in newEndPointDict
            console.log(global_data.splice(i, 1));                    
        };//end if
      });//end of filter
    })
        update();
        //g_wrist.selectAll(".active").remove();        
  }
}).on("focus",function(){});

// get the image using the url provided in detail.html, append it to svg
var img = g_wrist.append("svg:image")
	.attr("xlink:href", url)
	.attr("width", width/scale)
	.attr("height", height/scale)
	.attr("x", 0)
	.attr("y", 0)
	.on("mousedown", mousedown)
	.on("mouseup", mouseup);


//--------------------------- Functions -----------------------------//

//draw a rectangle on the image when clicked
function mousedown() {
  event.stopPropagation();
  var m = d3.mouse(this);
  rect = g_wrist.append("g").classed("rectangle", true).
    append("rect")
    .attr("x", m[0])
    .attr("y", m[1])
    .attr("height", 0)
    .attr("width", 0)
    .attr("class", "rectangle")
    .classed("new", true)
    .on("mousedown", mousedown)
    .on("mouseup", mouseup)
    // .on("click", toggle_active);
    // .on("dblclick", open_modal);
    .on("dblclick", function(d){
      d["active"] = true;
        open_modal(d);
    });
    g_wrist.on("mousemove", mousemove);
}

//not used
function keydown(){
	if(d3.event.key == "delete"){
    console.log('delete')
		d3.selectAll(".active").remove();
	}
};

function mousemove(d) {
  console.log("mousemove");
	var m = d3.mouse(this);

	rect.attr("width", Math.max(0, m[0] - +rect.attr("x")))
		.attr("height", Math.max(0, m[1] - +rect.attr("y")))
		.style("opacity", 0.4);
};

function toggle_active(d){
  console.log("toggle_active");
  d3.selectAll(".active").classed("active", false);
	if(d3.select(this).classed("active")){
		d3.select(this).classed("active", false);
	}else{
		d3.select(this).classed("active", true);
	}
};

function mouseup() {
  console.log("mouseup");
	// event.stopPropagation();
	g_wrist.on("mousemove", null);
	redraw_new_rect();	
}

function redraw_new_rect(){

  console.log("redraw_new_rect");
  d3.selectAll(".active").classed("active", false);
  //JV fix for removing active data . Modify the data to disable all selection
  for (i = 0 ; i < global_data.length ; i++)
  { global_data[i].active = false;}

	g_wrist.selectAll("rect.new").each(function(d){
		x = d3.select(this).attr("x");
		y = d3.select(this).attr("y");
		width = d3.select(this).attr("width");
		height = d3.select(this).attr("height");
		active = d3.select(this).classed("active");

		if(width < 10 || height < 10){
			d3.select(this).remove();
		}else{
			global_data.push({"x": x, "y": y, "width": width, "height": height,
       "bone_number":"unknown",		 
       "fracture_on_current_view":"unknown",
       "fracture_on_other_view":"unknown",
       "view_type":"unknown",


			 "active": active});
			d3.select(this).remove();
		}
	});
	update();
}

var zoom_d = d3.zoom()
  .scaleExtent([1, 10])
  .on("zoom", zoom_wrist);


function zoom_wrist() {
  console.log("zoom wrist")
   g_wrist.attr('transform', 'translate(' + d3.event.transform.x + ',' + d3.event.transform.y + ') scale(' + d3.event.transform.k + ')');
  //  text.attr("transform","scale(" + d3.event.transform.scale().x + " " + d3.event.transform.scae().y + ")");
}

g_wrist.call(zoom_d);

// DISABLE double click for zoom
g_wrist.on("dblclick.zoom", null);
 
update();


function resizerHover() {
  console.log("resizeHover");
  var el = d3.select(this), isEntering = d3.event.type === "mouseenter";
  el
    .classed("hovering", isEntering)
    .attr(
      "r",
      isEntering || el.classed("resizing") ?
        HANDLE_R_ACTIVE : HANDLE_R
    );
}

  function rectResizeStartEnd() {
    console.log("rectResizeStartEnd");
    var el = d3.select(this), isStarting = d3.event.type === "start";
    d3.select(this)
      .classed("resizing", isStarting)
      .attr(
        "r",
        isStarting || el.classed("hovering") ?
          HANDLE_R_ACTIVE : HANDLE_R
      );
  }

  function rectResizing(d) {
    console.log("rectResizing");
    var dragX = Math.max(
      Math.min(d3.event.x, MAX_TRANSLATE_X),
      MIN_TRANSLATE_X
    );


    var dragY = Math.max(
      Math.min(d3.event.y, MAX_TRANSLATE_Y),
      MIN_TRANSLATE_Y
    );


    if (d3.select(this).classed("topleft")) {
      console.log("topleft");
      var newWidth = Math.max(parseInt(d.width) + parseInt(d.x) - parseInt(dragX), MIN_RECT_WIDTH);

      d.x  = parseInt(d.x) + parseInt(d.width) - parseInt(newWidth);
      d.width = newWidth;

      var newHeight = Math.max(parseInt(d.height) + parseInt(d.y) - parseInt(dragY), MIN_RECT_HEIGHT);

      d.y = parseInt(d.y) +  parseInt(d.height) - parseInt(newHeight);
      d.height = newHeight;

    } else {
      d.width = Math.max(dragX - parseInt(d.x), MIN_RECT_WIDTH);
      d.height = Math.max(dragY - parseInt(d.y), MIN_RECT_HEIGHT);
    }

    update();
  }

  function rectMoveStartEnd(d) {
    console.log("rectMoveStartEnd");
    d3.select(this).classed("moving", d3.event.type === "start");
  }

  function rectMoving(d) {

    var dragX = Math.max(
      Math.min(d3.event.x, MAX_TRANSLATE_X - d.width),
      MIN_TRANSLATE_X
    );

    var dragY = Math.max(
      Math.min(d3.event.y, MAX_TRANSLATE_Y - d.height),
      MIN_TRANSLATE_Y
    );

    d.x = dragX;
    d.y = dragY;

    update();
}

function update(){
  console.log("update");
	var rects = g_wrist
      .selectAll("g.rectangle")
      .data(global_data, function (d) {
        return d;
     });

    rects.exit().remove();
    
    var newRects =
      rects.enter()
        .append("g")
        .classed("rectangle", true);

    newRects
      .append("rect")
      .classed("bg", true)
      .style("opacity", 0.4)
      .attr("stroke", "blue")
      .attr("stroke-width", 3)
      .call(d3.drag()
        .container(g_wrist.node())
        .on("start end", rectMoveStartEnd)
        .on("drag", rectMoving)
      )
      .on("click", function(d){
      	console.log("update; on click; clicked");
        d3.selectAll(".active").classed("active", false);
            //JV fix for removing active data . Modify the data to disable all selection
        for (i = 0 ; i < global_data.length ; i++)
        { global_data[i].active = false;}
  
      	d3.select(this).classed("active", true);
      	d["active"] = true;

      })
      // .on("dblclick", open_modal); 
      .on("dblclick", function(d){
        console.log("what is d: " + d.bone_number)
        d["active"] = true;
        open_modal(d);
      })
    newRects
      .append("g")
      .classed("circles", true)
      .each(function (d) {
        console.log("what is this: " + this)
        var circleG = d3.select(this);

        circleG
          .append("circle")
          .classed("topleft", true)
          .style("fill", "yellow")
          .attr("r", HANDLE_R)
          .on("mouseenter mouseleave", resizerHover)
          .call(d3.drag()
            .container(g_wrist.node())
            .subject(function () {
              return {x: d3.event.x, y: d3.event.y};
            })
            .on("start end", rectResizeStartEnd)
            .on("drag", rectResizing)
          );

        circleG
          .append("circle")
          .classed("bottomright", true)
          .style("fill", "yellow")
          .attr("r", HANDLE_R)
          .on("mouseenter mouseleave", resizerHover)
          .call(d3.drag()
            .container(g_wrist.node())
            .subject(function () {
              return {x: d3.event.x, y: d3.event.y};
            })
            .on("start end", rectResizeStartEnd)
            .on("drag", rectResizing)
          );
        circleG
        .append("text")
        .classed("toothN", true)
        .style("font-size", function(){
          if(type == "PANAROMIC"){
            return "1.0em"
          }else{
            return "1.5em"
          }
        })
        .style("fill", "orange")
        
        // .attr("dy", ".35em")
        // .text(d.tooth + " " + d.site + " " + d.depth)
        .text(d.bone_number)        
        .attr("bone_number", d.bone_number)
        .attr("fracture_on_current_view", d.fracture_on_current_view)
        .attr("fracture_on_other_view", d.fracture_on_other_view)
        .attr("view_type", d.view_type)        
      });

      var allRects = newRects.merge(rects);

    allRects
      .attr("transform", function (d) {
        return "translate(" + d.x + "," + d.y + ")";
      });

    allRects
      .select("rect.bg")
      .attr("height", function (d) {
        return d.height;
      })
      .attr("width", function (d) {
        return d.width;
      })
      .classed("active", function(d){
      	return d.active;
      });

    allRects
      .select("circle.bottomright")
      .attr("cx", function (d) {
        return d.width;
      })
      .attr("cy", function (d) {
        return d.height;
      });

    allRects
      .select("text.toothN")
      .attr("x", function (d) {
        // return 200;
        console.log(JSON.stringify(d))
        try{
          return x(d.x);
        }
        catch(error){
          console.log("An error occured: " + error)
        }
      })
      .attr("y", function (d) {
        try{
          return y(d.y);
        }
        catch(error){
          console.log("An error occurred" + error)
        }
        // return 200;
      });      
};

function get_wrist_rects(){
  console.log("get_wrist_rects");
	rects = [];

	g_wrist.selectAll("g.rectangle").each(function(d){

		console.log("get wrist rects: " + d.x, d.y, d.width, d.height);
		rects.push({"x": d.x, "y": d.y, "width": d.width, "height": d.height,       
      "bone_number":d.bone_number,
      "fracture_on_current_view":d.fracture_on_current_view,
      "fracture_on_other_view":d.fracture_on_other_view,
      "view_type":d.view_type
    })
	});
	// g_wrist.selectAll("rect").each(function(d){

	// 	// var test = d3.select(this.parentNode)._groups[0][0].__data__

	// 	// if(test.x !== null){
	// 	// 	rects.push({"x": test.x, "y": test.y, "width": test.width, "height": test.height})
	// 	// }

	// 	rects.push({"x": d3.select(this).attr("x"),
	// 	 "y": d3.select(this).attr("y"),
	// 	 "width": d3.select(this).attr("width"),
	// 	 "height": d3.select(this).attr("height")})
	// });

	return rects;
};


function update_info(do_reload, modal_id){
  console.log("update_info");
	var wrist_rects = get_wrist_rects();

	var wrist_rects_strings = JSON.stringify(wrist_rects);
	var json_dict = {
		"wrist_xray": true,
    "scale": scale,
		"wrist_xray_rects": wrist_rects_strings,
	};

	 $.ajax({
        type: "POST",
        url: "/sianno/detail/?d=" + document_id,
        data : json_dict,
        // contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function(data) {
          if (data.result == "OK")
          {
            // alert("success in saving");
            console.log("success in ajax post");
            if (do_reload == true){

              window.location.reload(true);
            }
            else
            {
              //check if modal is is passed
              if (modal_id == "NO_MODAL")
              {
                // alert ("boxes saved");
                $("#form-wrist-xray-grading").submit();
              }
              else
              {
                $(modal_id).modal('hide');
              }                 
            }              
          }
        },
        
        error: function(  req, textStatus, errorThrown){
          alert("Update rectangles failed" + errorThrown);
            // console.log("why it is failing?");
            //  window.location.reload(true);
            console.log(JSON.stringify(error));
        }
    });
};

function open_modal(id){
	//double-click on rectangle
	console.log("double clicked, open wrist fracture modal");
	// toggle_active();
  //if already labelled then these will be logged, otherwise they will all be "unknown"
	console.log(JSON.stringify(id["bone_number"]));
	console.log(JSON.stringify(id["fracture_on_current_view"]));
	console.log(JSON.stringify(id["view_type"]));
	// console.log(JSON.stringify(id["active"]));

	
	if(type == "WRIST-XRAY"){

    d3.selectAll(".btn.btn-primary.bone_number").classed("active", false);
    d3.select("#__bone_" + id["bone_number"]).classed("active", true);

    d3.selectAll(".btn.btn-primary.fracture_on_current_view").classed("active", false);
    d3.select("#__fracture_on_current_view_" + id["fracture_on_current_view"]).classed("active", true);

    d3.selectAll(".btn.btn-primary.fracture_on_other_view").classed("active", false);
    d3.select("#__fracture_on_other_view_" + id["fracture_on_other_view"]).classed("active", true);

    d3.selectAll(".btn.btn-primary.view_type").classed("active", false);
    d3.select("#__view_type_" + id["view_type"]).classed("active", true);

		$("#wxModal").modal();
  }
};


function btn_clicked(key,value){
	
	
	console.log("btn_clicked; " + key + value);
  //Deactivates all of the bone_number buttons
	d3.selectAll(".btn.btn-primary.bone_number").classed("active", false);
  //Activates only the button with the corresponding value
  d3.select("#__bone_" + value).classed("active", true);
  
	width = d3.select("rect.active").attr("width");
	height = d3.select("rect.active").attr("height");

	filtered_array = global_data.filter(function(elems, i){
                        if(elems.width == width && elems.height == height){
                            //then that value exist in newEndPointDict
                            global_data[i][key] = value;
                            update();
                        
                         };//end if
            });//end of filter
};

$(document).ready(function(){

    $("#id_btn_save_next").click(function(){
        //call update without reloading the page
        update_info(false, "NO_MODAL"); 
    }); 

    $("#id_btn_save_wrist_xray").click(function(){

      update_info(true,'#wxModal') 
    });
});
