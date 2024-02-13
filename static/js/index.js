$(document).ready(function(){


$(".clickable-row").click(function(){

    window.location = $(this).attr("data-href");
});

var table_draft = new Tabulator("#id_table_worklist_draft", {
    rowClick:function(e, row){
        // alert("Row " + row.getIndex() + " Clicked!!!!");
        window.location = "/sianno/detail/?d="+row.getIndex();
    
    },
    height:"600px",

//     groupBy:"status",
// groupValues:[["Draft", "Reviewed"]],
layout:"fitDataStretch",

    columns:[
    {title:"Accesstion No", field:"accession_no"},

    // {title:"ID", field:"id"},
    {title:"Anatomy", field:"anatomy"},
    {title:"View", field:"view_position"},


    // {title:"Status", field:"status"},
    // {title:"User", field:"user"},
    // {title:"Purpose", field:"purpose"},
    // {title:"Type", field:"type"}, 

    {
        title:"Date Modified", 
        field:"date_modified", 
        hozAlign:"right", 
        formatter:"datetime",
        formatterParams: {outputFormat:"DD/MM/YY HH:mm", inputFormat:'DD/MM/YY HH:mm Z ZZ', timezone:"Australia/Perth"},
},
    ],

});

table_draft.setData("/sianno/index_json/?status=Draft");


var table_reviewed = new Tabulator("#id_table_worklist_reviewed", {
    rowClick:function(e, row){
        // alert("Row " + row.getIndex() + " Clicked!!!!");
        window.location = "/sianno/detail/?d="+row.getIndex();
    
    },
    height:"600px",

//     groupBy:"status",
// groupValues:[["Draft", "Reviewed"]],
// layout:"fitColumns",

    columns:[
    {title:"Accession No", field:"accession_no"},
    {title:"Anatomy", field:"anatomy"},
    {title:"View", field:"view_position"},
    // {title:"ID", field:"id"},
    // {title:"Status", field:"status"},
    // {title:"User", field:"user"},
    // {title:"Purpose", field:"purpose"},
    // {title:"Type", field:"type"}, 

    {
        title:"Date Modified", 
        field:"date_modified", 
        hozAlign:"right", 
        formatter:"datetime",
        formatterParams: {outputFormat:"DD/MM/YY HH:mm", inputFormat:'DD/MM/YY HH:mm Z ZZ', timezone:"Australia/Perth"},

    },],
});

table_reviewed.setData("/sianno/index_json/?status=Reviewed");

// Data Table for Bone detection


var table_draft_bone_detected = new Tabulator("#id_table_draft_bone_detected", {
    rowClick:function(e, row){
        window.location = "/sianno/detail/?d="+row.getIndex();
    
    },
    height:"600px",

//     groupBy:"status",
// groupValues:[["Draft", "Reviewed"]],
// layout:"fitColumns",

    columns:[
    {title:"Accession No", field:"accession_no"},
    {title:"Anatomy", field:"anatomy"},
    {title:"View", field:"view_position"},
    // {title:"ID", field:"id"},
    // {title:"Status", field:"status"},
    // {title:"User", field:"user"},
    // {title:"Purpose", field:"purpose"},
    // {title:"Type", field:"type"}, 

    {
        title:"Date Modified", 
        field:"date_modified", 
        hozAlign:"right", 
        formatter:"datetime",
        formatterParams: {outputFormat:"DD/MM/YY HH:mm", inputFormat:'DD/MM/YY HH:mm Z ZZ', timezone:"Australia/Perth"},

    },],
});

table_draft_bone_detected.setData("/sianno/index_json/?status=Draft_Bone_Detected");

// Data Table for Osteo detection


var table_draft_osteo_detected = new Tabulator("#id_table_draft_osteo_detected", {
    rowClick:function(e, row){
        window.location = "/sianno/detail/?d="+row.getIndex();
    
    },
    height:"600px",

//     groupBy:"status",
// groupValues:[["Draft", "Reviewed"]],
// layout:"fitColumns",

    columns:[
    {title:"Accession No", field:"accession_no"},
    {title:"Anatomy", field:"anatomy"},
    {title:"View", field:"view_position"},
    // {title:"ID", field:"id"},
    // {title:"Status", field:"status"},
    // {title:"User", field:"user"},
    // {title:"Purpose", field:"purpose"},
    // {title:"Type", field:"type"}, 

    {
        title:"Date Modified", 
        field:"date_modified", 
        hozAlign:"right", 
        formatter:"datetime",
        formatterParams: {outputFormat:"DD/MM/YY HH:mm", inputFormat:'DD/MM/YY HH:mm Z ZZ', timezone:"Australia/Perth"},

    },],
});

table_draft_osteo_detected.setData("/sianno/index_json/?status=Draft_Osteo_Detected");



$("#uploadDiv").load("/sianno/new_files");

$("#btn_upload").click(function(){
    $("#uploadModal").modal();

});
//when the bone detection function is called, send an HTTP request to run the YOLOv7 function
$("#btn_detect_bones").click(function(){
    
    $.ajax({
        url: "/sianno/detect_bones",
        success: function(data){
            if (data.result == "OK"){
                alert("Detection successful");
            }
            else{
                alert(JSON.stringify(data));

            }
        },
        error:function(error){
            alert(JSON.stringify(error));


        }
    
    });

}); //end of button click detect bones

//when the osteo detection function is called, send an HTTP request to run the osteo function
$("#btn_detect_osteo").click(function(){
    
    $.ajax({
        url: "/sianno/detect_osteo",
        success: function(data){
            if (data.result == "OK"){
                alert("Detection successful");
            }
            else{
                alert(JSON.stringify(data));

            }
        },
        error:function(error){
            alert(JSON.stringify(error));


        }
    
    });

}); //end of button click detect bones



});