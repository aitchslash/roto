
$(document).ready(function(){
	$('#wOBA_add').click(function(){
		add_wOBA();
		$('#wOBA_formula').removeClass();
	})
})

$(document).ready(function(){
	set_form_2015()
})

$('#reset_form').on('click', function(){
	// alert('Clicked!!!');
	document.getElementById('form2').reset()
	//	set_form_2015();
	/*stat_list = $('#custom2 th'); // [1:] use innerText
	target = $('#custom2 input');
	for (var i = 1; i < stat_list.length; i++) {
		target[i - 1].setAttribute("value", getStat('2015', stat_list[i].innerText))
	};*/
});

$('#submit').on('click', function(){
	document.getElementById('form2').submit();
})

$('#game_scale').on('click', function(){
	var origG = parseInt($('input').val())
	var inputs = $('input');
	if ($('input:disabled').length == 0) {
		for (var i = 1; i < inputs.length; i++) {
			inputs[i].setAttribute('disabled', true);
		};
		$('#Ginput').change(function(){
			var games = parseInt($(this).val());
			if (games >= 0 && games <= 162) {
				for (var i = 1; i < inputs.length; i++) {
					inputs[i].value = Math.round((games / origG) * inputs[i].defaultValue)
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


function build_year (year_name) {
	var row_name;
	if (year_name == "2015") {row_name = "full2015"};
	if (year_name == "career") {row_name = '162avg'};
	var new_row_str = "<tr id = " + row_name + "><td class='Year'>" + row_name + "</td></tr>";
	new_row = $(new_row_str);
	selector = "#" + year_name + " td";
	g_selector = "#" + year_name + " .G";
	games = parseFloat($(g_selector).text());
	old_row = $(selector);
	for (var i = 1; i < old_row.length; i++) {
		new_class = old_row[i].getAttribute('class');
		new_number = parseFloat(parseFloat(old_row[i].innerText) * 162 / games).toFixed(0);
		$('<td></td>').text(new_number).addClass(new_class).appendTo(new_row);
	};
	//$('table').append(new_row)
	t_select = "table #" + year_name;
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
	for (var i = 1; i < stat_list.length; i++) {
		target[i - 1].setAttribute("value", getStat('2015', stat_list[i].innerText))
	};
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



