$(document).ready(function(){
	add_wOBA();
	$('.Year').hide();
	$('#teamtable').dataTable({
		"paging": false,
		"info": false,
		"searching": false,
		"order": [[20, "desc"]] // this i.e. [20] is wOBA
	});
});

function add_wOBA () {
	// $('#wOBA_add').slideUp(); // better at the bottom, but...
	if (($('#2015 .wOBA').text()).length == 0) {
		var rows = $('tr');
		var head = $('<th class="wOBA">wOBA</th>');
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
			
			woba = parseFloat((.689*(bb - ibb) + .722*hbp + .892*(h - h2b - h3b - hr)
				+ 1.283*h2b + 1.635*h3b + 2.135*hr) / (ab + bb - ibb + sf + hbp)).toFixed(3);
			woba_str = "<td class=wOBA>" + woba + "</td>";
			woba_q = $(woba_str);
			woba_q.appendTo(rows[i]);
		}
	// console.log("got here"); // if this works can move top line down here
	
	};
}

function calc162avg() {
	$('.fullname:visible').each(function(){
		//console.log($('.y162').find(".fullname").text($(this)));
		//console.log($(this).text());
		var name = $(this).text();
		if (name != "Name") {
			var career = ($(".y162:contains('" + name + "')")); // working
			var games = parseFloat($(career).find('.G').text());
			var pos = $(career).find('.POS').text();
			var wOBA = $(career).find('.wOBA').text();
			var avg162 = $("<tr id = 162avg><td class='fullname'>" + name + "</td><td class='POS'>" + pos + "<td class='Year'>162avg</td></tr>");
			var stuff = career.children()
			for (var i = 3; i < stuff.length - 1; i++) {
				new_class = career.children()[i].getAttribute('class');
				new_number = parseFloat(parseFloat(stuff[i].innerText) * 162 / games).toFixed(0);
				$('<td></td>').text(new_number).addClass(new_class).appendTo(avg162);
			};
			$('<td></td>').text(wOBA).addClass('wOBA').appendTo(avg162);
			var target = $("tr:visible:contains('" + name +"')");
			$(target).after($(career));
			$('.Year').show();
			// $(career).show();
			$(target).after($(avg162));
		};
	})
}

function make162avg() {
	// wrap this is a each()
	var new_row_str = "<tr id = 162avg><td class='Year'>162avg</td></tr>";
	var new_row = $(new_row_str);
	var old_row = $('#.y162');
	for (var i = 1; i < old_row.length - 1; i++) {
		new_class = old_row[i].getAttribute('class');
		new_number = parseFloat(parseFloat(old_row[i].innerText) * 162 / games).toFixed(0);
		$('<td></td>').text(new_number).addClass(new_class).appendTo(new_row);
	};
	$('table .y162')
}
