$(document).ready(function(){
	$('#wOBA_add').click(function(){
		add_wOBA();
		// $('#wOBA_formula').removeClass();
	})
})

$(document).ready(function(){
	set_form_2015();
	set_team();
})

$(document).ready(function(){
	if (parseInt($('#2015 .AB').text()) < 300) {
		// console.log("in f(x)")
		add_2014_buttons();
		$('#avg2014').click(function(){
			ensure_enabled();
			set_mlbavg();
		})
		$('#half_and_half').click(function () {
			ensure_enabled();
			half_and_half();
			
		})
	};
})

function set_team() {
	var urlString = window.location.href;
	//var splitter = urlString.indexOf("new/");
	var teamID = $('#team_id').text()
	// find if url has user_id
	var url_array = urlString.split('/')
	// if user_id in url it'll be second last
	var user_int = parseInt(url_array[url_array.length - 2])
	console.log(user_int)
	// if NaN user_int == user_int will return false
	if (user_int !== user_int) {
		$('#team_sel select').val('/team/' + teamID);
	} else {  // there is a user_id
		$('#team_sel select').val('/team/' + teamID + user_int);
		console.log('/team/' + teamID + user_int)
	}
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

function add_2014_buttons() {
	var $avg2014 = $('<div class="button" id="avg2014">Use MLB avg</div>');
	$('body').append($avg2014);
	var $half_and_half = $('<div class="button" id="half_and_half">0.5*MLB avg, 0.5*2015</div>');
	$('body').append($half_and_half);
}

$('#reset_form').on('click', function(){
	ensure_enabled();
	reset_form();
});

$('#submit').on('click', function(){
	ensure_enabled();
	document.getElementById('form2').submit();
})



$('#game_scale').on('click', function(){
	var origG = parseInt($('input').val());
	var orig_data = [];
	a = $('input');
	for (i=0; i < a.length; i++) {orig_data.push(a[i].value)}
	// var origG = parseInt(document.getElementById('Ginput').defaultValue) // worrks for 2015
	// console.log(orig_data);
	var inputs = $('input');
	if ($('input:disabled').length == 0) {
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


function ensure_enabled() {
	var greyed = $('input:disabled');
	if (greyed.length > 0) {
		for (var i = 0; i < greyed.length; i++) {
			greyed[i].removeAttribute('disabled');
		};
	}
}

function build_year (year_name) {
	var row_name;
	if (year_name == "2015") {row_name = "full2015"};
	if (year_name == "career") {row_name = '162avg'};
	var new_row_str = "<tr id = " + row_name + "><td class='Year'>" + row_name + "</td></tr>";
	var new_row = $(new_row_str);
	var selector = "#" + year_name + " td";
	var g_selector = "#" + year_name + " .G";
	var games = parseFloat($(g_selector).text());
	var old_row = $(selector);
	for (var i = 1; i < old_row.length; i++) {
		new_class = old_row[i].getAttribute('class');
		new_number = parseFloat(parseFloat(old_row[i].innerText) * 162 / games).toFixed(0);
		$('<td></td>').text(new_number).addClass(new_class).appendTo(new_row);
	};
	//$('table').append(new_row)
	var t_select = "table #" + year_name;
	$(t_select).after(new_row);
}


build_year('career')
build_year('2015')

// build new heading: head = $('<th>AVG</th>')
// find target: $('tr')[0]
// add it: head.appendTo(target)

function add_avg () {
	rows = $('tr');
	// first row is headings
	head = $('<th class="AVG">AVG</th>');
	head.appendTo(rows[0]);
	// calc and add AVG to each row
	for (var i = 1; i < rows.length; i++) {
		hit_selector = "#" + rows[i].id + " .H";
		ab_selector = "#" + rows[i].id + " .AB";
		hits = parseFloat($(hit_selector).text());
		abs = parseFloat($(ab_selector).text());
		avg = parseFloat(hits / abs).toFixed(3);
		avg_str = "<td class = AVG>" + avg + "</td>";
		average = $(avg_str);
		average.appendTo(rows[i]);
	};
}

function getStat (row_id, stat) {
	selector = "#" + row_id + " ." + stat;
	//console.log(selector);
	stat_floated = parseFloat($(selector).text());
	return stat_floated
}

// get target(s)
// get content
// loop through content and set text/val to target(s)
function set_form_2015 () {
	stat_list = $('#custom2 th'); // [1:] use innerText
	target = $('#custom2 input');
	// console.log('set 2015');
	for (var i = 1; i < stat_list.length; i++) {
		//target[i - 1].setAttribute("value", getStat('2015', stat_list[i].innerText))
		target[i - 1].setAttribute("value", getStat('2015', stat_list[i].innerText))
		// console.log(stat_list[i].innerText)  // tester
	};
}

function reset_form () {
	$('input').each(function(){
		var dv = $(this).prop("defaultValue");
		// console.log(dv)
		$(this).val(dv);
	})
}

function set_mlbavg () {
	$('input').each(function(){
		var name = this.name;
		// console.log(name);
		stat = Math.round(mlb_avg_2014[name]);
		// console.log(stat);
		$(this).val(stat);
	})
}

function half_and_half () {
	$('input').each(function(){
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

function add_wOBA () {
	$('#wOBA_add').slideUp(); // better at the bottom, but...
	if (($('#2015 .wOBA').text()).length == 0) {
		rows = $('tr');
		head = $('<th class="wOBA">wOBA</th>');
		head.appendTo(rows[0]);
		for (var i = 1; i < rows.length; i++) {
			bb = getStat(rows[i].id, "BB");
			ibb = getStat(rows[i].id, "IBB");
			hbp = getStat(rows[i].id, "HBP");
			h = getStat(rows[i].id, "H");
			h2b = getStat(rows[i].id, "2B");
			h3b = getStat(rows[i].id, "3B");
			hr = getStat(rows[i].id, "HR");
			ab = getStat(rows[i].id, "AB");
			sf = getStat(rows[i].id, "SF");
			woba = parseFloat((.689*(bb - ibb) + .722*hbp + .892*(h - h2b - h3b - hr)
				+ 1.283*h2b + 1.635*h3b + 2.135*hr) / (ab + bb - ibb + sf + hbp)).toFixed(3);
			woba_str = "<td class=wOBA>" + woba + "</td>";
			woba_q = $(woba_str);
			woba_q.appendTo(rows[i]);
		}
	console.log("got here"); // if this works can move top line down here
	
	};
}



mlb_avg_2014 = {'SF': 3.5171288189190566, 'GIDP': 9.95372243662762, 'AB': 456.1360784780428, 
	'PA': 506.57671840731734, 'G': 162.0, 'HR': 11.529131743144221, 'Season': '2014', 
	'BB': 38.614053282102724, 'SH': 3.6989068158248184, 'HBP': 4.549958346792703, 
	'CS': 2.8506094969312636, '1B': 78.28296978867373, 'SO': 103.12045427497917, 
	'2B': 22.411023648820958, 'H': 114.56145123174484, 'RBI': 51.627705333310665, 
	'3B': 2.338326051105935, 'R': 54.42598480082967, 'AVG" ': '.251', 'IBB': 2.7128988932147777, 
	'SB': 7.612642173447355}
