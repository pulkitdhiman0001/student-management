//remove disable form
function hideDisable(){
var inputs = document.getElementsByClassName('form_disabled');

document.getElementById('edit_button').style.visibility='hidden';
document.getElementById('update_button').hidden = false;
document.getElementById('discard_button').hidden = false;
for(var i = 0; i < inputs.length; i++) {
    inputs[i].disabled = false;
}

}
