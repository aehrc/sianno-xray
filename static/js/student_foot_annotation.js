



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


var global_data_foot_student = []; //global variable to store the rectanglel data

//select div container with id of imageBody-wx, add it to SVG with width and height adjusted
var svg_student = d3.select("#imageBody-FX").append("svg")
  .attr("width", width/scale)
  .attr("height", height/scale);

  //get text annotation
var text_student = svg_student.selectAll("text");
//add svg to group
var g_foot_student = svg_student.append("g"); //group

var rects_student ;//Global rectangle variable

//Load the data from the server and store the data in the global variable
d3.json('/media/' + document_id + '/rect.json', function(error, data){
	data.forEach(function(rect){
		global_data_foot_student.push(rect);
    });






//call the update function once the data is received
	update_student();

});//end of get json




//Get image scale
if(type == "PANAROMIC"){
  if(width > 1200 && scale == 1.0){
    scale = width/1200;
  };
}else{
  if(height > 1000 && scale == 1.0){
    scale = height/1000;
  };
}




//Key Down Event for the whole G element
g_foot_student.on("keydown", function(){
	if(d3.event.key == "Backspace" || d3.event.key == "Delete"){
    //console.log("keydown; backspace or delete");
    //need to remove from global_data too
    g_foot_student.selectAll(".active").each(function(){
      width = d3.select(this).attr("width");
      height = d3.select(this).attr("height");
      x = d3.select(this).attr("x");
      y = d3.select(this).attr("y");

      filtered_array = global_data_foot_student.filter(function(elems, i){
        if(elems.width == width && elems.height == height){
            //then that value exist in newEndPointDict
            console.log(global_data_foot_student.splice(i, 1));                    
        };//end if
      });//end of filter
    })
   
        update_student();
        // update_info(true, "NO____MODAL"); 
        //g_wrist.selectAll(".active").remove();        
  }

  if(d3.event.key == "h" || d3.event.key == "H"){
    console.log("he was pressed!!!");
    g_foot_student.selectAll(".rectangle").classed("visible",  g_foot_student.selectAll(".rectangle").classed("visible")? false : true);
    g_foot_student.selectAll(".rectangle").each(function(d){
        if(d3.select(this).classed("visible") == true){
            console.log("it is visible");
            d3.select(this).style("opacity", 0.4);


        }else{
            console.log("it is not visible");
            d3.select(this).style("opacity", 0);
        }
    });

}
}).on("focus",function(){});

// get the image using the url provided in detail.html, append it to svg
var img_student = g_foot_student.append("svg:image")
	.attr("xlink:href", url)
	.attr("width", width/scale)
	.attr("height", height/scale)
	.attr("x", 0)
	.attr("y", 0)
	.on("mousedown", mousedown_student)
	.on("mouseup", mouseup_student);



//draw a rectangle on the image when clicked
function mousedown_student() {
//create rectangles only using the middle mouse button (which enables the mouse drag on primary click)
if (d3.event.button === 1)
{
  d3.event.stopPropagation();
  
  
  var m = d3.mouse(this);
  rect = g_foot_student.append("g").classed("rectangle", true).
    append("rect")
    .attr("x", m[0])
    .attr("y", m[1])
    .attr("height", 0)
    .attr("width", 0)
    .attr("class", "rectangle")
    .classed("new", true)
    .on("mousedown", mousedown_student)
    .on("mouseup", mouseup_student)
    // .on("click", toggle_active);
    // .on("dblclick", open_modal);
    .on("dblclick", function(d){
      d["active"] = true;
      open_diabetic_foot_modal_student(d);
    });
    g_foot_student.on("mousemove", mousemove_student);


  }
  else{

    //propagate the event for dragging...
    
  }
}


//on mouse move
function mousemove_student(d) {
  // console.log("mousemove");
	var m = d3.mouse(this);

	rect.attr("width", Math.max(0, m[0] - +rect.attr("x")))
		.attr("height", Math.max(0, m[1] - +rect.attr("y")))
		.style("opacity", 0.4);
};


function toggle_active(d){
  // console.log("toggle_active");
  d3.selectAll(".active").classed("active", false);
	if(d3.select(this).classed("active")){
		d3.select(this).classed("active", false);
	}else{
		d3.select(this).classed("active", true);
	}
};

function mouseup_student() {
  // console.log("mouseup");
	g_foot_student.on("mousemove", null);
	redraw_new_rect_student();	
}

function redraw_new_rect_student(){

  // console.log("redraw_new_rect");
  d3.selectAll(".active").classed("active", false);
  //JV fix for removing active data . Modify the data to disable all selection
  for (i = 0 ; i < global_data_foot_student.length ; i++)
  { global_data_foot_student[i].active = false;}

	g_foot_student.selectAll("rect.new").each(function(d){
		x = d3.select(this).attr("x");
		y = d3.select(this).attr("y");
		width = d3.select(this).attr("width");
		height = d3.select(this).attr("height");
		active = d3.select(this).classed("active");

		if(width < 10 || height < 10){
			d3.select(this).remove();
		}else{
			global_data_foot_student.push({"x": x, "y": y, "width": width, "height": height,
       "toe_number":"unknown",
			 "active": active});
			d3.select(this).remove();
		}
	});
	update_student();
}

var zoom_d = d3.zoom()
// .filter(function(){
//   return (d3.event.button === 0 ||
//           d3.event.button === 1);
// })
  .scaleExtent([1, 10])
  .on("zoom", zoom_foot_student);


function zoom_foot_student() {
  // console.log("zoom foot")
  g_foot_student.attr('transform', 'translate(' + d3.event.transform.x + ',' + d3.event.transform.y + ') scale(' + d3.event.transform.k + ')');
  //  text.attr("transform","scale(" + d3.event.transform.scale().x + " " + d3.event.transform.scae().y + ")");
}

g_foot_student.call(zoom_d);

// DISABLE double click for zoom
g_foot_student.on("dblclick.zoom", null);
 
// update();


function resizerHover() {
  // console.log("resizeHover");
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
    // console.log("rectResizeStartEnd");
    d3.select(this).classed("moving", false);
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
    // console.log("rectResizing");
    var dragX = Math.max(
      Math.min(d3.event.x, MAX_TRANSLATE_X),
      MIN_TRANSLATE_X
    );


    var dragY = Math.max(
      Math.min(d3.event.y, MAX_TRANSLATE_Y),
      MIN_TRANSLATE_Y
    );

    d3.select(this).classed("moving", true);
    
    if (d3.select(this).classed("topleft")) {
      // console.log("topleft");
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

    update_student();
  }

  function rectMoveStartEnd(d) {
    // console.log("rectMoveStartEnd");
    d3.select(this).classed("moving", d3.event.type === "start");
    // d3.select(this).classed("moving", true);
    // if(d3.event.type != "start"){
    //     // d3.selectAll(".rectangle").style("opacity", 1);
    // d3.selectAll("rect.bg.active").style("opacity", 1);
    // d3.selectAll("rect.bg.active.moving").style("opacity", 1);
    // }else{
    //     d3.selectAll(".rectangle").style("opacity", 0);
    //     // d3.selectAll(".rectangle.moving").style("opacity", 0);
    // }

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
    
    update_student();
}

function update_student(){



  // console.log("update");
  g_foot_student
  .selectAll("g.rectangle").remove();



  rects_student = g_foot_student
.selectAll("g.rectangle")
.data(global_data_foot_student, function (d) {
  return d;
});


    
    var newRects_student =
      rects_student.enter()
        .append("g")
        .classed("rectangle", true);
      
      
    

    newRects_student
      .append("rect")
      .classed("bg", true)
      .style("opacity", 0.4)
      .attr("stroke", "blue")
      .attr("stroke-width", 3)
      .call(d3.drag()
        .container(g_foot_student.node())
        .on("start end", rectMoveStartEnd)
        .on("drag", rectMoving)
      )
      .on("click", function(d){
      	// console.log("update; on click; clicked");
        d3.selectAll(".active").classed("active", false);
            //JV fix for removing active data . Modify the data to disable all selection
        for (i = 0 ; i < global_data_foot_student.length ; i++)
        { global_data_foot_student[i].active = false;}
  
      	d3.select(this).classed("active", true);

        // g_foot_student.selectAll("rect").each(function(d){
        //     if(d3.select(this).classed("active")){
        //         d3.select(this).style("opacity", 0.5);
                
        //     }else{
        //         d3.select(this).style("opacity", 0);
        //         d3.select(this.parentElement).selectAll("circle").style("opacity", 0.1);
        //         d3.select(this.parentElement).selectAll(".toothN").style("opacity", 0.1);
        //     }
        // });
        
      	d["active"] = true;
        //   d3.selectAll("rect:not(.active))").style("opacity", 0);


      })
      // .on("dblclick", open_modal); 
      .on("dblclick", function(d){
        // console.log("what is d: " + d.annotation_type)
        d["active"] = true;
        open_diabetic_foot_modal_student(d);
      });
    newRects_student
      .append("g")
      .classed("circles", true)
      .each(function (d) {
        // console.log("what is this: " + this)
        var circleG_student = d3.select(this);
        // console.log("test for Jana-------------");

        circleG_student
          .append("circle")
          .classed("topleft", true)
          .style("fill", "yellow")
          .attr("r", HANDLE_R)
          .on("mouseenter mouseleave", resizerHover)
          .call(d3.drag()
            .container(g_foot_student.node())
            .subject(function () {
              return {x: d3.event.x, y: d3.event.y};
            })
            .on("start end", rectResizeStartEnd)
            .on("drag", rectResizing)
          );

        circleG_student
          .append("circle")
          .classed("bottomright", true)
          .style("fill", "yellow")
          .attr("r", HANDLE_R)
          .on("mouseenter mouseleave", resizerHover)
          .call(d3.drag()
            .container(g_foot_student.node())
            .subject(function () {

                
              return {x: d3.event.x, y: d3.event.y};
            })
            .on("start end", rectResizeStartEnd)
            .on("drag", rectResizing)
          );


          circleG_student
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
          .text(d.toe_number)        
        //   .attr("annotation_bone", d.toe_number)
          .attr("toe_number", function(i,d){
            // var toe_name = d.toe_number[i];
            // var test = "1 Hlx"
            // var find_string = "input[name='" +  test.toString() + "']"
            // $("#id_bone_form").find(find_string).prop("checked", true);
            return d.toe_number;
            
          })
          // .attr("fracture_on_current_view", d.fracture_on_current_view)
          // .attr("fracture_on_other_view", d.fracture_on_other_view)
          // .attr("view_type", d.view_type)   
           
      });

    var allRects_student = newRects_student.merge(rects_student);

    allRects_student
      .attr("transform", function (d) {
        return "translate(" + d.x + "," + d.y + ")";
      });

      allRects_student
      .selectAll("rect.bg")
      .attr("height", function (d) {
        return d.height.toString();
      })
      .attr("width", function (d) {
        return d.width.toString();
      })
      .classed("active", function(d){
      	return d.active;
      });

      allRects_student
      .selectAll("circle.bottomright")
      .attr("cx", function (d) {
        return d.width;
      })
      .attr("cy", function (d) {
        return d.height;
      });

      allRects_student
      .selectAll("text.toothN")
      .attr("x", function (d) {
        // return 200;
        // console.log(JSON.stringify(d))
        try{
          
          // return x(d.x);
          return 0;
        }
        catch(error){
          console.log("An error occured: " + error)
        }
      })
      .attr("y", function (d) {
        try{
          // return y(d.y);
          return 0;
        }
        catch(error){
          console.log("An error occurred" + error)
        }
        // return 200;

      }); 
      
      rects_student.exit().remove();

      



};//Update

function get_foot_rects_student(){
  // console.log("get_foot_rects");
	foot_rects = [];
  toe_number = "";

	g_foot_student.selectAll("g.rectangle").each(function(d){
    // if(d.annotation_type != "Osteomyelitis"){
    //   toe_number = "";
    //  }else{
      toe_number = d.toe_number;
    //  }
		// console.log("get foot rects: " + d.x, d.y, d.width, d.height);
		foot_rects.push({"x": d.x, "y": d.y, "width": d.width, "height": d.height,       
    //   "annotation_bone":d.annotation_bone,
      "toe_number": toe_number,
  });
});
  


	return foot_rects;
};


function update_info_student(do_reload, modal_id){
  // console.log("update_info");
	var foot_rects = get_foot_rects_student();

	var foot_rects_strings = JSON.stringify(foot_rects);
	var json_dict = {
		"foot_xray": true,
    "scale": scale,
		"foot_xray_rects": foot_rects_strings,

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
            // console.log("success in ajax post");
            if (do_reload == true){

              window.location.reload(true);
            }
            else
            {
              //check if modal is is passed
              if (modal_id == "NO_MODAL")
              {
                // alert ("boxes saved");
                $("#form-next-foot-grading").submit();
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
            console.log(JSON.stringify(errorThrown));
        }
    });
};

// function open_modal(id){
// 	//double-click on rectangle
// 	console.log("double clicked, open foot fracture modal");
// 	// toggle_active();
//   //if already labelled then these will be logged, otherwise they will all be "unknown"
// 	console.log(JSON.stringify(id["bone_number"]));
// 	console.log(JSON.stringify(id["fracture_on_current_view"]));
// 	console.log(JSON.stringify(id["view_type"]));
// 	// console.log(JSON.stringify(id["active"]));

	
// 	if(type == "WRIST-XRAY"){

//     d3.selectAll(".btn.btn-primary.bone_number").classed("active", false);
//     d3.select("#__bone_" + id["bone_number"]).classed("active", true);

//     d3.selectAll(".btn.btn-primary.fracture_on_current_view").classed("active", false);
//     d3.select("#__fracture_on_current_view_" + id["fracture_on_current_view"]).classed("active", true);

//     d3.selectAll(".btn.btn-primary.fracture_on_other_view").classed("active", false);
//     d3.select("#__fracture_on_other_view_" + id["fracture_on_other_view"]).classed("active", true);

//     d3.selectAll(".btn.btn-primary.view_type").classed("active", false);
//     d3.select("#__view_type_" + id["view_type"]).classed("active", true);

// 		$("#wxModal").modal();
//   }
// };
	//double-click on rectangle

function open_diabetic_foot_modal_student(id){
	// console.log("double clicked, open diabetic foot modal");
	
	if(type == "FOOT-XRAY"){
        console.log("TYPE IS FOOT XRAY");

    // d3.selectAll(".btn.btn-primary.annotation_type").classed("active", false);
    // d3.select("#___" + id["annotation_type"]).classed("active", true);
    // $("#___" + id["annotation_type"]+">input").prop("checked", true);
    d3.select("#___" + id["toe_number"]).classed("active", true);
    $("#___" + id["toe_number"]+">input").prop("checked", true);

    // if(id["annotation_type"] == "Osteomyelitis"){
      //select the div element and show
      $("#fxStudentModal").modal();
      //otherwise hidehide
    // }else{
    //   // $("#id_bone_form").find("input[type='radio']").prop("checked", false);
    //   // $("#id_bone_form").find("input[type='label']").prop("active", false);
    //   $("#id_bone_form").hide();
  
  
    // }

    // d3.selectAll(".btn.btn-primary.fracture_on_current_view").classed("active", false);
    // d3.select("#__fracture_on_current_view_" + id["fracture_on_current_view"]).classed("active", true);

    // d3.selectAll(".btn.btn-primary.fracture_on_other_view").classed("active", false);
    // d3.select("#__fracture_on_other_view_" + id["fracture_on_other_view"]).classed("active", true);


    // d3.selectAll(".btn.btn-primary.view_type").classed("active", false);
    // d3.select("#__view_type_" + id["view_type"]).classed("active", true);
	// 	$("#fxModal").modal();
  }
};


function btn_clicked_foot(key,value){
	
	if(value == "Osteomyelitis"){
    //select the div element and show
    $("#id_bone_form").show();
    //otherwise hidehide
  }else{
    $("#id_bone_form").find("input[type='radio']").prop("checked", false);
    // $("#id_bone_form").find("input[type='label']").prop("active", false);
    $("#id_bone_form").hide();


  }

	console.log("btn_clicked; " + key + value);

  //Deactivates all of the bone_number buttons
	d3.selectAll(".btn.btn-primary.annotation_button").classed("active", false);
  //Activates only the button with the corresponding value
  d3.select("#__" + value).classed("active", true);
  
	width = d3.select("rect.active").attr("width").toString();
	height = d3.select("rect.active").attr("height").toString();

	filtered_array = global_data_foot.filter(function(elems, i){
                        if(elems.width == width && elems.height == height){
                            //then that value exist in newEndPointDict
                            global_data_foot[i][key] = value;
                            if(value != "Osteomyelitis"){
                              global_data_foot[i]["bone_number"] = "";
                            }
                            
                            // update();
                        
                         };//end if
            });//end of filter
            update_student();
            
};

function btn_clicked_foot_bone_student(key, value){
  // var bone_array = [];
  // $("#id_bone_form").find("input[type='radio']").each(function(index, obj){
  //   if($(obj).prop("checked")==true){
  //     bone_array.push($(obj).attr("name"));
  //   } 
    
  // });
  //Deactivates all of the bone_number buttons
	d3.selectAll(".btn.btn-primary.annotation_button").classed("active", false);
  //Activates only the button with the corresponding value
  // d3.select("#__" + value).classed("active", true);


  width = d3.select("rect.active").attr("width");
	height = d3.select("rect.active").attr("height");
  filtered_array = global_data_foot_student.filter(function(elems, i){
    if(elems.width == width && elems.height == height){
        //then that value exist in newEndPointDict

        global_data_foot_student[i][key] = value;

        // update();
    
     };//end if
});//end of filter
update_student();




};

$(document).ready(function(){

  $("#id_btn_save_next_foot").click(function(){
      //call update without reloading the page
      update_info_student(false, "NO_MODAL"); 
  }); 

  $("#id_btn_save_foot_xray_student").click(function(){

    // update_info(true,'#fxModal') 
    $("#fxStudentModal").modal('hide');

  });









});


