$(document).ready(function(){
    $(".edit").on('click',edit);
    $(".approve").on('click',approve);
    $(".unapprove").on('click',unapprove);
    $(".language").on('click',language);
    
    $(".target").each(check_approval);   
    $(".target").each(check_editor);   
});

function check_approval(){
    var approvers= $(this).data('sentence').approvers;
    for(var i=0; i< approvers.length; i++){
        if(approvers[i].$oid == $('#navigation').data('userid')){
            approve_html($(this).children('.approve'));
        }
    }
}

function check_editor(){
    if($('#navigation').data('userid') == $(this).data('sentence').userID.$oid){
        edit_html($(this).children('.edit'));
    }
}

function edit(e){
    edit_html($(this));
}

function edit_html(e){
    e.parent().children(".approve").attr("disabled",true);
    e.parent().children(".edit").html("Save");
    e.parent().children(".target_sentence").attr("readOnly",false);
    e.parent().children(".target_sentence").css("backgroundColor", "#FFFFFF");
    e.parent().children(".edit").off('click').on('click',save);

}
function save(){
    var new_content={"editor": $("#username").val(), "new_target_sentence": $(this).parent().children(".target_sentence").val()};
    var j={"old": $(this).parent().data("sentence"), "new": new_content};
    $.ajax({
          type: "POST",
          contentType: "application/json; charset=utf-8",
          url: "/add",
          data: JSON.stringify(j),
          dataType: "json"
    }).done().fail();
}

function approve(){
    approve_html($(this));   

    var new_content={"approver": $("#username").val()}
    var j={"old": $(this).parent().data("sentence"), "new": new_content};
    $.ajax({
          type: "POST",
          contentType: "application/json; charset=utf-8",
          url: "/approve",
          data: JSON.stringify(j),
          dataType: "json"
    }).done().fail();
}

function approve_html(e){
    console.log(e);
    e.parent().children(".edit").attr("disabled",true);
    e.parent().children(".approve").html("Unapprove");
    e.parent().children(".approve").off('click').on('click', unapprove);
    e.parent().children(".approve").addClass('unapprove').removeClass('approve');

}
function unapprove(){
    unapprove_html($(this))

    var new_content={"unapprover": $("#username").val()}
    var j={"old": $(this).parent().data("sentence"), "new": new_content};
    $.ajax({
          type: "POST",
          contentType: "application/json; charset=utf-8",
          url: "/unapprove",
          data: JSON.stringify(j),
          dataType: "json"
    }).done().fail();
}  

function unapprove_html(e){
    e.parent().children(".edit").attr("disabled",false); 
    e.parent().children(".unapprove").html("Approve");
    e.parent().children(".edit").off('click').on('click', edit);
    e.parent().children(".unapprove").off('click').on('click', approve);
    e.parent().children(".unapprove").addClass('approve').removeClass('unapprove');

}

function language(){
    window.location.href = 'file/'+$('#username').val()+'/'+$(this).html();
}
