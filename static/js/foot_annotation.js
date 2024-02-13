



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


var global_data_foot = []; //global variable to store the rectanglel data
var draw_rectangle_toggle = false;//global variable which toggles the rectangle draw function



//select div container with id of imageBody-wx, add it to SVG with width and height adjusted
var svg = d3.select("#imageBody-FX").append("svg")
  .attr("width", width/scale)
  .attr("height", height/scale);
  // .attr("width",600)
  // .attr("height", 600);

  //get text annotation
var text = svg.selectAll("text");
//add svg to group
var g_foot = svg.append("g"); //group

var rects ;//Global rectangle variable

//Load the data from the server and store the data in the global variable
d3.json('/media/' + document_id + '/rect.json', function(error, data){
	data.forEach(function(rect){
		global_data_foot.push(rect);
    });






//call the update function once the data is received
	update();

});//end of get json




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




//Key Down Event for the whole G element
g_foot.on("keydown", function(){
	if(d3.event.key == "Backspace" || d3.event.key == "Delete"){
    //console.log("keydown; backspace or delete");
    //need to remove from global_data too
    g_foot.selectAll(".active").each(function(){
      width = d3.select(this).attr("width");
      height = d3.select(this).attr("height");
      x = d3.select(this).attr("x");
      y = d3.select(this).attr("y");

      filtered_array = global_data_foot.filter(function(elems, i){
        if(elems.width == width && elems.height == height){
            //then that value exist in newEndPointDict
            console.log(global_data_foot.splice(i, 1));                    
        };//end if
      });//end of filter
    })
        update();
        // update_info(true, "NO____MODAL"); 
        //g_wrist.selectAll(".active").remove();        
  }
}).on("focus",function(){});

// get the image using the url provided in detail.html, append it to svg
var img = g_foot.append("svg:image")
	.attr("xlink:href", url)
	.attr("width", width/scale)
	.attr("height", height/scale)
	.attr("x", 0)
	.attr("y", 0)
	.on("mousedown", mousedown)
	.on("mouseup", mouseup);



//draw a rectangle on the image when clicked
function mousedown() {
//create rectangles only using the rectangle toggle (by pressing r key)
if (draw_rectangle_toggle == true)
{
  d3.event.stopPropagation();
  
  
  var m = d3.mouse(this);
  rect = g_foot.append("g").classed("rectangle", true).
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
        open_foot_xray_modal(d);
    });
    g_foot.on("mousemove", mousemove);


  }
  else{

    //propagate the event for dragging...
    
  }
}


//on mouse move
function mousemove(d) {
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

function mouseup() {
  // console.log("mouseup");
	g_foot.on("mousemove", null);
	redraw_new_rect();	
}

function redraw_new_rect(){

  // console.log("redraw_new_rect");
  d3.selectAll(".active").classed("active", false);
  //JV fix for removing active data . Modify the data to disable all selection
  for (i = 0 ; i < global_data_foot.length ; i++)
  { global_data_foot[i].active = false;}

	g_foot.selectAll("rect.new").each(function(d){
		x = d3.select(this).attr("x");
		y = d3.select(this).attr("y");
		width = d3.select(this).attr("width");
		height = d3.select(this).attr("height");
		active = d3.select(this).classed("active");

		if(width < 10 || height < 10){
			d3.select(this).remove();
		}else{
			global_data_foot.push({"x": x, "y": y, "width": width, "height": height,
       "annotation_type":"unknown",
			 "active": active,
       "toe_number" : "" //Set an empty toe number
      });
			d3.select(this).remove();
		}
	});
	update();
}

var zoom_d = d3.zoom()
// .filter(function(){
//   return (d3.event.button === 0 ||
//           d3.event.button === 1);
// })
  .scaleExtent([0.5, 10])
  .on("zoom", zoom_foot)
  .filter(function(){
    return (event.button === 0 ||
            event.button === 1);
  })
  ;


function zoom_foot() {
  // console.log("zoom foot")
  // g_foot.attr('transform', 'translate(' + d3.event.transform.x + ',' + d3.event.transform.y + ') scale(' + d3.event.transform.k + ')');
  
  //  text.attr("transform","scale(" + d3.event.transform.scale().x + " " + d3.event.transform.scae().y + ")");

  g_foot.attr("transform", d3.event.transform);
  // gX.call(xAxis.scale(d3.event.transform.rescaleX(x)));
  // gY.call(yAxis.scale(d3.event.transform.rescaleY(y)));

}


svg.call(zoom_d);//zoom needs to be called on SVG and not the G element. otherwise it flickers. 

// DISABLE double click for zoom
svg.on("dblclick.zoom", null);
 
// update();


function resizerHover() {
  // console.log("resizeHover");
  var el = d3.select(this), isEntering = d3.event.type === "mouseenter";
  el.classed("hovering", isEntering)
    .attr(
      "r",
      isEntering || el.classed("resizing") ?
        HANDLE_R_ACTIVE : HANDLE_R
    );
}

  function rectResizeStartEnd() {
    // console.log("rectResizeStartEnd");
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

    update();
  }

  function rectMoveStartEnd(d) {
    // console.log("rectMoveStartEnd");
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



  // console.log("update");
  g_foot
  .selectAll("g.rectangle").remove();



  rects = g_foot
.selectAll("g.rectangle")
.data(global_data_foot, function (d) {
  return d;
});


    
    var newRects =
      rects.enter()
        .append("g")
        .attr("visibility", function(d){

          //first check if the osteomyelitis_present_score_visualisation_enabled is true, if yes, then check for further keyboard togge. If not then display everything
          if (osteomyelitis_present_score_visualisation_feature_enabled == true)
          {
            // console.log(d.osteomyelitis_present_score)

            if (osteomyelitis_present_score_visualisation == true && "osteomyelitis_present_score" in d)
            {
                //if the toggle is on, then show only the ones with the score.
                if (parseInt(d.osteomyelitis_present_score) >= 50 ){
                  return "visible"; 
                }
                else
                {
                  return "hidden";
                } 
            }
            else//if toggle is off, then show everything. 
            {
              return "visible";
            }

          }
          else//if the feature is disabled then show everything
          {
            return "visible";
          }
  
      
         } )
  
        .classed("rectangle", true);
        
      
      
    

    newRects
      .append("rect")
      .classed("bg", true)
      .style("opacity", 0.4)
      .attr("stroke", "blue")
      .attr("stroke-width", 3)
      // show rectangles which has above the osteo percentage 50%

      
      // .attr('fill', function(d){
      //   if (d.osteomyelitis_present_score){
      //     return osteomyelitis_present_score_visualisation ?  'rgb(' + Math.floor((d.osteomyelitis_present_score * 255)/100)  + ',0,0)' : null 

      //   }
      //   else
      //   {
      //     return null;

      //   }

      // } )

      .call(d3.drag()
        .container(g_foot.node())
        .on("start end", rectMoveStartEnd)
        .on("drag", rectMoving)
      )
      .on("click", function(d){
      	// console.log("update; on click; clicked");
        d3.selectAll(".active").classed("active", false);
            //JV fix for removing active data . Modify the data to disable all selection
        for (i = 0 ; i < global_data_foot.length ; i++)
        { global_data_foot[i].active = false;}
  
      	d3.select(this).classed("active", true);
      	d["active"] = true;

      })
      // .on("dblclick", open_modal); 
      .on("dblclick", function(d){
        // console.log("what is d: " + d.annotation_type)
        d["active"] = true;
        open_diabetic_foot_modal(d);
      });
    newRects
      .append("g")
      .classed("circles", true)
      .each(function (d) {
        // console.log("what is this: " + this)
        var circleG = d3.select(this);
        // console.log("test for Jana-------------");

        circleG
          .append("circle")
          .classed("topleft", true)
          .style("fill", "yellow")
          .attr("r", HANDLE_R)
          .on("mouseenter mouseleave", resizerHover)
          .call(d3.drag()
            .container(g_foot.node())
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
            .container(g_foot.node())
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
              return "1.5em"
            }else{
              return "1.5em"
            }
          })
          .style("fill", "orange")
          .attr("dy", "1.0em")
          // .text(d.tooth + " " + d.site + " " + d.depth)
          .text(
            
            function(d){
            //If Ostemyletitis, then return the toe number
            if (d.annotation_type == "Osteomyelitis")
            {
              if (d.osteomyelitis_present_score){
                return d.toe_number.toString() + " - DF:" + d.osteomyelitis_present_score.toString() + "%";
              }
              else
              {
                return d.toe_number.toString();
              }

            
            }
            else
            {
              return d.annotation_type ;
            }
          }
            
            )        
          .attr("annotation_type", d.annotation_type)
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

    var allRects = newRects.merge(rects);

    allRects
      .attr("transform", function (d) {
        return "translate(" + d.x + "," + d.y + ")";
      });

    allRects
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

    allRects
      .selectAll("circle.bottomright")
      .attr("cx", function (d) {
        return d.width;
      })
      .attr("cy", function (d) {
        return d.height;
      });

    allRects
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
      
      rects.exit().remove();

      



};//Update

function get_foot_rects(){
  // console.log("get_foot_rects");
	foot_rects = [];
  toe_number = "";

	g_foot.selectAll("g.rectangle").each(function(d){
    if(d.annotation_type != "Osteomyelitis"){
      toe_number = "";
     }else{
      toe_number = d.toe_number;
     }
		// console.log("get foot rects: " + d.x, d.y, d.width, d.height);
		foot_rects.push({"x": d.x, "y": d.y, "width": d.width, "height": d.height,       
      "annotation_type":d.annotation_type,
      "toe_number": toe_number,
  });
});
  


	return foot_rects;
};


function update_info(do_reload, modal_id){
  // console.log("update_info");
	var foot_rects = get_foot_rects();

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

function open_diabetic_foot_modal(id){
	// console.log("double clicked, open diabetic foot modal");
	
	if(type == "FOOT-XRAY"){

    d3.selectAll(".btn.btn-primary.annotation_type").classed("active", false);
    d3.select("#__" + id["annotation_type"]).classed("active", true);
    $("#__" + id["annotation_type"]+">input").prop("checked", true);
    d3.select("#__" + id["toe_number"]).classed("active", true);
    $("#__" + id["toe_number"]+">input").prop("checked", true);

    if(id["annotation_type"] == "Osteomyelitis"){
      //select the div element and show
      $("#id_bone_form").show();
      //otherwise hidehide
    }else{
      // $("#id_bone_form").find("input[type='radio']").prop("checked", false);
      // $("#id_bone_form").find("input[type='label']").prop("active", false);
      $("#id_bone_form").hide();
  
  
    }

    // d3.selectAll(".btn.btn-primary.fracture_on_current_view").classed("active", false);
    // d3.select("#__fracture_on_current_view_" + id["fracture_on_current_view"]).classed("active", true);

    // d3.selectAll(".btn.btn-primary.fracture_on_other_view").classed("active", false);
    // d3.select("#__fracture_on_other_view_" + id["fracture_on_other_view"]).classed("active", true);


    d3.selectAll(".btn.btn-primary.view_type").classed("active", false);
    d3.select("#__view_type_" + id["view_type"]).classed("active", true);
		$("#fxModal").modal();
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
            update();
            
};

function btn_clicked_foot_bone(key, value){
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
  filtered_array = global_data_foot.filter(function(elems, i){
    if(elems.width == width && elems.height == height){
        //then that value exist in newEndPointDict

        global_data_foot[i][key] = value;

        // update();
    
     };//end if
});//end of filter
update();




};

$(document).ready(function(){

  $("#id_btn_save_next_foot").click(function(){
      //call update without reloading the page
      update_info(false, "NO_MODAL"); 
  }); 

  $("#id_btn_save_foot_xray").click(function(){

    // update_info(true,'#fxModal') 
    $("#fxModal").modal('hide');

  });


 //When the Ostemyelitis detection algorithm is clicked, 
 $("#id_btn_run_osteomyelitis_detection").click(function () {

  //call osteomylitiis code in the server side and reload the page
  var json_dict = { "foot_xray_run_osteomylitis_detection": true, };
  //send in a HTTP POST to start the osteo detection process
  $.ajax({
    type: "POST",
    url: "/sianno/detail/?d=" + document_id,
    data: json_dict,
    // contentType: "application/json; charset=utf-8",
    dataType: "json",
    success: function (data) {
      if (data.result == "OK") {
        alert("Run Osteo Succeeded");
        window.location.reload(true);
      }
      else {
        alert("Run Osteo Data returned is NOT OK: " + data.result);
      }
    },
    error: function (req, textStatus, errorThrown) {
      alert("Osteo Run failed" + errorThrown);
      // console.log("why it is failing?");
      //  window.location.reload(true);
      console.log(JSON.stringify(errorThrown));
    }
  });//end of ajax post



});//end of run osteo button click function




// //Key Down Event for the SVG
// document.on("keydown", function(event){
//   alert(event);
// 	// if(d3.event.key == "d" ){
//   //   // alert("d pressed");
//   //   osteomyelitis_present_score_visualisation = !osteomyelitis_present_score_visualisation;
//   //   update();
//   // }
  document.addEventListener("keydown", (event) => {
    if(event.key == "d" ){
          
          osteomyelitis_present_score_visualisation = !osteomyelitis_present_score_visualisation;
          check_info_label_status();
          

          update();
        }  
      
        if(event.key == "r" ){
          draw_rectangle_toggle = !draw_rectangle_toggle;
          check_info_label_status();

        }
      
      });
      
//function to update the text of the label at the top which provides user hints
      function check_info_label_status(){


        if (osteomyelitis_present_score_visualisation_feature_enabled)
        {
          if (osteomyelitis_present_score_visualisation && draw_rectangle_toggle ){
            $("#id-label-ui-info").html("Drawing new Bones and Displaying All Bones, Press d key again to show only osteo bones, Press r key to end bone drawing");
          }
          else if (osteomyelitis_present_score_visualisation && !draw_rectangle_toggle )
          {
            $("#id-label-ui-info").html("Displaying All Bones, Press d key again to show only osteo bones, Press r key to draw new bones");

          }
          else if (!osteomyelitis_present_score_visualisation && draw_rectangle_toggle )
          {
            $("#id-label-ui-info").html("Drawing new Bones and Displaying Osteo Bones, Press d key again to show all bones, Press r key to end bone drawing");

          }
          else if (!osteomyelitis_present_score_visualisation && !draw_rectangle_toggle )
          {
            $("#id-label-ui-info").html("Displaying Osteo Bones, Press d key to show all bones, Press r key to draw new bone");

          }
          
        }
        else
        {
          if (draw_rectangle_toggle ){
            $("#id-label-ui-info").html("Displaying All Bones. Press r key to end bone drawing");
        }
        else
        {
          $("#id-label-ui-info").html("Displaying All Bones. Press r key to draw new bones");
          

        }

      }
    }//end of function check_info_label_status
      
      check_info_label_status();

});//end of document ready