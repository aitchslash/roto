// var career_g = parseInt($('#career td').first().next().text())
// var proj_g = parseFloat($('#2015 td').first().next().text()).toFixed(3)


/*
function career_avg() {
	var career_array = $('#career td');
	for (i = 1; i < career_array.length; i++){
		
		//console.log(career_array[i].innerText);
	return career_array
	}
}
*/

//h = career_avg()

// h = $('#career td');
/*
var c162 = $('<tr id = c162><td>162avg</td></tr>')

for (i = 1; i < $('#career td').length; i++){
	var datum = parseFloat($('#career td')[i].innerText).toFixed(1);
	//var stat_class = $('#2015 td')[i].attr('class');
	datum = (datum * 162 / career_g).toFixed(1);
	$('<td></td>').text(datum).appendTo(c162);
}

$('table #career').after(c162)
*/
/*
var proj162 = $('<tr id = proj162><td>proj162</td></tr>')

for (i = 1; i < $('#2015 td').length; i++){
	var datum = parseFloat($('#2015 td')[i].innerText).toFixed(1);
	var stat_class = $('#2015 td')[i].attr('class');
	datum = (datum * 162 / proj_g).toFixed(1);
	$('<td></td>').text(datum).addClass(stat_class).appendTo(proj162);
}

$('table #c162').after(proj162)
*/
function build_year (year_name) {
	var row_name;
	if (year_name == "2015") {row_name = "full2015"};
	if (year_name == "career") {row_name = '162avg'};
	var new_row_str = "<tr id = " + row_name + "><td>" + row_name + "</td></tr>";
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
	stat_floated = parseFloat($(selector).text());
	return stat_floated
}

function add_wOBA () {
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
	};
}
