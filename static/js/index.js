$(document).ready(function(){


$(".clickable-row").click(function(){

    window.location = $(this).attr("data-href");
});

var table_draft = new Tabulator("#id_table_worklist_draft", {
    rowClick:function(e, row){
        // alert("Row " + row.getIndex() + " Clicked!!!!");
        window.location = "/sianno/detail/?d="+row.getIndex();
    
    },
    height:"311px",

//     groupBy:"status",
// groupValues:[["Draft", "Reviewed"]],
layout:"fitDataStretch",

    columns:[
    {title:"ID", field:"id"},
    {title:"Status", field:"status"},
    {title:"User", field:"user"},
    {title:"Purpose", field:"purpose"},
    {title:"Type", field:"type"}, 

    {
        title:"Date Modified", 
        field:"date_modified", 
        hozAlign:"center", 
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
    height:"311px",

//     groupBy:"status",
// groupValues:[["Draft", "Reviewed"]],
layout:"fitDataStretch",

    columns:[
    {title:"ID", field:"id"},
    {title:"Status", field:"status"},
    {title:"User", field:"user"},
    {title:"Purpose", field:"purpose"},
    {title:"Type", field:"type"}, 

    {
        title:"Date Modified", 
        field:"date_modified", 
        hozAlign:"center", 
        formatter:"datetime",
        formatterParams: {outputFormat:"DD/MM/YY HH:mm", inputFormat:'DD/MM/YY HH:mm Z ZZ', timezone:"Australia/Perth"},

    },],
});

table_reviewed.setData("/sianno/index_json/?status=Reviewed");

$("#uploadDiv").load("/sianno/new_files");

$("#btn_upload").click(function(){
    $("#uploadModal").modal();

});


});