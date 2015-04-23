$(document).ready(function(){
	$('#avg2014').click(function(){
		ensure_enabled();
		set_mlbavg();
	})
	$('#half_and_half').click(function () {
		ensure_enabled();
		half_and_half();
	})
})

function ensure_enabled() {
	var greyed = $('input:disabled');
	if (greyed.length > 0) {
		for (var i = 0; i < greyed.length; i++) {
			greyed[i].removeAttribute('disabled');
		};
	}
}

function half_and_half () {
	$('#datums input').each(function(){
		var name = this.name;
		// console.log(name);
		stat = Math.round(mlb_avg_2014[name]);
		// console.log(stat);
		stat2 = Math.round($('#full2015 .' + name).text());
		//console.log(stat2);
		combo = Math.round((stat2 + stat) * 0.5)
		$(this).val(combo);
	})
}

function set_mlbavg () {
	$('#datums input').each(function(){
		var name = this.name;
		// console.log(name);
		stat = Math.round(mlb_avg_2014[name]);
		// console.log(stat);
		$(this).val(stat);
	})
}

function add_ten(x) {
	var plus = ["H", "R", "2B", "3B", "HR", "RBI", "SB", "BB", "IBB", "HBP", "SF", "SH"]
	var minus = ["CS", "SO", "GIDP"]
	if (x === true) {
		var multiplier = 1.10;
	} else {
		var multiplier = 0.90
	}
	$('#datums input').each(function(){
		var current_value = $(this).val();
		if (plus.indexOf(this.name) >= 0) {
			$(this).val(Math.round(current_value * multiplier));
		}
		if (minus.indexOf(this.name) >= 0) {
			$(this).val(Math.round(current_value *(1 / multiplier)));
		}
	})
}

$('#plus_10').on('click', function() {
	add_ten(true);
})

$('#minus_10').on('click', function() {
	add_ten(false);
} )

$('#all_fields').on('click', function(){
	$('.extra').toggle();
})

$('#game_scale').on('click', function(){
	var origG = parseInt($('#datums input').val());
	orig_data = [];
	a = $('#datums input');
	for (i=0; i < a.length; i++) {orig_data.push(a[i].value)}
	// var origG = parseInt(document.getElementById('Ginput').defaultValue) // worrks for 2015
	// console.log(orig_data);
	var inputs = $('#datums input');
	if ($('#datums input:disabled').length == 0) {
		for (var i = 1; i < inputs.length; i++) {
			inputs[i].setAttribute('disabled', true);
		};
		$('#Ginput').change(function(event){
			var games = parseInt($(this).val());
			// console.log(event.type);
			if (games >= 0 && games <= 162) {
				for (var i = 1; i < inputs.length; i++) {
					//inputs[i].value = Math.round((games / origG) * inputs[i].defaultValue)
					// var gamez = parseInt($('input').val());
					inputs[i].value = Math.round(parseFloat(games / parseInt(orig_data[0])) * parseInt(orig_data[i]));
				};
			} else {
				console.log('Not!!!') //
			};
			
		})
		.change();
	} else {
		// console.log('here');
		for (var i = 1; i < inputs.length; i++) {
			inputs[i].removeAttribute('disabled');
		}
	}
})

/*  date = $('#dob input').val
prop valueAsDate
age
target = $('#dob')
make age element
age element after target
*/

function calculateAge(birthday) { // birthday is a date
    var ageDifMs = Date.now() - birthday.getTime();
    var ageDate = new Date(ageDifMs); // miliseconds from epoch
    return Math.abs(ageDate.getUTCFullYear() - 1970);
}

mlb_avg_2014 = {'SF': 3.5171288189190566, 'GIDP': 9.95372243662762, 'AB': 456.1360784780428, 
	'PA': 506.57671840731734, 'G': 162.0, 'HR': 11.529131743144221, 'Season': '2014', 
	'BB': 38.614053282102724, 'SH': 3.6989068158248184, 'HBP': 4.549958346792703, 
	'CS': 2.8506094969312636, '1B': 78.28296978867373, 'SO': 103.12045427497917, 
	'2B': 22.411023648820958, 'H': 114.56145123174484, 'RBI': 51.627705333310665, 
	'3B': 2.338326051105935, 'R': 54.42598480082967, 'AVG" ': '.251', 'IBB': 2.7128988932147777, 
	'SB': 7.612642173447355}