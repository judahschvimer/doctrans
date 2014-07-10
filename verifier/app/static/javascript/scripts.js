$(document).ready(function(){
    $(".edit").on('click',edit);
    $(".approve").on('click',approve);
});


function edit(){
    $(this).parent().children(".approve").attr("disabled",true);
    $(this).parent().children(".edit").html("Save");
    $(this).parent().children(".target_sentence").attr("readOnly",false);
    $(this).parent().children(".target_sentence").css("backgroundColor", "#FFFFFF");
    $(this).parent().children(".edit").off('click').on('click',save);
    
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
    $(this).parent().children(".edit").attr("disabled",true);
    $(this).parent().children(".approve").html("Unapprove");
    $(this).parent().children(".approve").off('click').on('click', unapprove);
    
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

function unapprove(){
    $(this).parent().children(".edit").attr("disabled",false); 
    $(this).parent().children(".approve").html("Approve");
    $(this).parent().children(".edit").off('click').on('click', edit);
    $(this).parent().children(".approve").off('click').on('click', approve);

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
