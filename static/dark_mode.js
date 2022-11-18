
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
