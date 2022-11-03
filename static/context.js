let country = document.getElementById('country');
let state = document.getElementById('state');
let city = document.getElementById('city');
let fname = document.getElementById('fname');


country.value = '{{request.form["country"]}}'
state.value = '{{request.form["state"]}}'
city.value = '{{request.form["city"]}}'
fname = {{request.form["fname"]}}