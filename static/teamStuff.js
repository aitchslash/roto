$(document).ready(function(){
	add_wOBA();
})

function test_woba(){
	rows = $('tr');
	for (var i = 0; i < rows.length; i++) {
		var games = parseFloat($(rows[i]).find('.G').text())
		console.log(games)
	};
}


function add_wOBA () {
	// $('#wOBA_add').slideUp(); // better at the bottom, but...
	if (($('#2015 .wOBA').text()).length == 0) {
		rows = $('tr');
		head = $('<th class="wOBA">wOBA</th>');
		head.appendTo(rows[0]);
		for (var i = 1; i < rows.length; i++) {
			var bb = parseFloat($(rows[i]).find('.BB').text());
			var ibb = parseFloat($(rows[i]).find('.IBB').text());
			var hbp = parseFloat($(rows[i]).find('.HBP').text());
			var h = parseFloat($(rows[i]).find('.H').text());
			var h2b = parseFloat($(rows[i]).find('.2B').text());
			var h3b = parseFloat($(rows[i]).find('.3B').text());
			var hr = parseFloat($(rows[i]).find('.HR').text());
			var ab = parseFloat($(rows[i]).find('.AB').text());
			var sf = parseFloat($(rows[i]).find('.SF').text());
			/*bb = getStat(rows[i].id, "BB");
			ibb = getStat(rows[i].id, "IBB");
			hbp = getStat(rows[i].id, "HBP");
			h = getStat(rows[i].id, "H");
			h2b = getStat(rows[i].id, "2B");
			h3b = getStat(rows[i].id, "3B");
			hr = getStat(rows[i].id, "HR");
			ab = getStat(rows[i].id, "AB");
			sf = getStat(rows[i].id, "SF");*/
			woba = parseFloat((.689*(bb - ibb) + .722*hbp + .892*(h - h2b - h3b - hr)
				+ 1.283*h2b + 1.635*h3b + 2.135*hr) / (ab + bb - ibb + sf + hbp)).toFixed(3);
			woba_str = "<td class=wOBA>" + woba + "</td>";
			woba_q = $(woba_str);
			woba_q.appendTo(rows[i]);
		}
	console.log("got here"); // if this works can move top line down here
	
	};
}

function getStat (row_id, stat) {
	selector = "#" + row_id + " ." + stat;
	//console.log(selector);
	stat_floated = parseFloat($(selector).text());
	//console.log(stat_floated);
	return stat_floated
}