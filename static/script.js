let country_select = document.getElementById('country');
let state_select = document.getElementById('state');
let city_select = document.getElementById('city');

country_select.onchange = function(){
 country = country_select.value;
 console.log(country)
 <!-- alert(country); -->
 fetch('/get_state_list/' + country).then(function(response){

  response.json().then(function(data) {
  console.log(data)
   optionHTML = '<option value="">Select State</option>';
   for (let state of data.state_list) {
    optionHTML += '<option value="' + state.id +'">' + state.name + '</option>'
   }
   state_select.innerHTML = optionHTML;

  });
 });
}


state_select.onchange = function(){
 state = state_select.value;
 fetch('/get_city_list/' + state).then(function(response){
  response.json().then(function(data) {
   optionHTML ='<option value="">Select City</option>';

   for (city of data.city_list) {

    optionHTML += '<option value="' + city.id +'">' + city.name + '</option>'
   }
   city_select.innerHTML = optionHTML;
  });
 });
}



window.onload = function () {
    country = country_select.value;

    state = state_select.value;
    console.log(state)
    fetch('/get_state_list/' + country).then(function (response) {
        response.json().then(function (data) {
            console.log(data)
            optionHTML = '';
            for (let state of data.state_list) {
                optionHTML += '<option value="' + state.id + '">' + state.name + '</option>'
            }
            state_select.innerHTML = optionHTML;
        });
    });

    fetch('/get_city_list/' + state).then(function (response) {
        response.json().then(function (data) {
            optionHTML = '';
            for (city of data.city_list) {
                optionHTML += '<option value="' + city.id + '">' + city.name + '</option>'
            }
            city_select.innerHTML = optionHTML;
        });
    });
}
