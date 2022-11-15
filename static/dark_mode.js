//
//$('.form-check-input').change(function () {
//    if ($(this).is("checked")) {
//        $(this).closest('tr').addClass('bglight');
//        return;
//    }
//    $(this).closest('tr').removeClass('bglight');
//});

if(localStorage.getItem('theme')==='dark'){
    document.body.classList.toggle('dark');
}

$(document).ready(function(){
    $("#theme-toggle").click(function(){
       if (localStorage.getItem('theme') === 'dark'){
         localStorage.setItem('theme','light')
        document.body.classList.toggle('dark');

        $('.dark').removeClass('dark').addClass('bglight');

       }else{
            document.body.classList.toggle('dark');
          localStorage.setItem('theme','dark')
            $('.bglight').removeClass('bglight').addClass('dark');
       }
    });
    $("[name='check-box']").change(function() {
        if (localStorage.getItem('theme') === 'dark'){
            $(this).closest('tr').toggleClass('dark');
        }
        else{
            $(this).closest('tr').toggleClass('bglight');
        }


    })
})


//
//
//
//$("[name='check-box']").change(function() {
//if (localStorage.getItem('theme') === 'dark'){
//
////    $(this).closest('tr').removeClass('bglight');
//    $(this).closest('tr').toggleClass('dark');
//}
//
//else if(localStorage.getItem('theme') === 'light'){
//$("#theme-toggle").click(function(){
//        //$(".form-check-input").prop("checked", false);
//        //$('tr').removeClass('dark');
//    });
//
////    $(this).closest('tr').removeClass('dark');
//    $(this).closest('tr').toggleClass('bglight');
//
//}
//
//});
//
//function remove_class(){
//$('tr').removeClass('bglight');
//$('tr').removeClass('dark');
//}
//
//
////var check = $('#table-hover');
////
//
//
////$('.form-check-input').on('change', function() {
////   $(this).closest('tr').addClass('bglight');
////});
////
////$('#theme-toggle').on('click', function() {
////$(this).closest('tr').removeClass('bglight');
////   $(this).closest('tr').addClass('bgdark');
////});
//
//
//
//
//
//
//var darkMode = false;
//
//if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
//	darkMode = true;
//
//}
//if (localStorage.getItem('theme') === 'dark') {
//	darkMode = true;
//
//
//} else if (localStorage.getItem('theme') === 'light') {
//	darkMode = false
//
//}
//
//if (darkMode) {
//	document.body.classList.toggle('dark');
//
//}
//
//document.addEventListener('DOMContentLoaded', () => {
//
//    document.getElementById('theme-toggle').addEventListener('click', () => {
//		document.body.classList.toggle('dark');
//    	localStorage.setItem('theme', document.body.classList.contains('dark') ? 'dark' : 'light');
//	});
//
//});
//
//
