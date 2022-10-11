document.body.style.backgroundColor= sessionStorage.getItem('bg')
document.body.style.color = sessionStorage.getItem('cc');


function dark_mode(){
    document.body.classList.toggle('dark-mode');
    document.getElementById('tb').classList.toggle('table-dark');
}



$('.form-check-input').click(function () {
     var backgroundColor = $(this).is(":checked") ? "lightcyan;" : "";
     $(this).closest('tr').attr('style', 'background-color: '+ backgroundColor +'');
});