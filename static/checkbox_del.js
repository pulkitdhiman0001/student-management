
var values=[];

textbox = document.getElementById("stu_ids")

$(".form-check-input").click(function(){
    values=[];
    $(".form-check-input").each(function(){
        if($(this).is(":checked")){
        values.push($(this).val());
        }


        });
        console.log(values);
        textbox.value = values

    });


var class_id = [];
textbox2 = document.getElementById("class_ids")

$(".form-check-input").click(function(){
    class_id=[];
    $(".form-check-input").each(function(){
        if($(this).is(":checked")){
        class_id.push($(this).val());
        }


        });
        console.log(class_id);
        textbox2.value = class_id

    });





$(document).ready(function() {

    var $submit = $("#stu_ids_submit").hide(),
        $cbs = $('input[name="check-box"]').click(function() {
            $submit.toggle( $cbs.is(":checked") );
        });

});

$(document).ready(function() {

    var $submit = $("#class_ids_submit").hide(),
        $cbs = $('input[name="check-box"]').click(function() {
            $submit.toggle( $cbs.is(":checked") );
        });

});



