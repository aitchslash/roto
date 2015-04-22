$(document).ready(function () {
	scale_ab();
	orig_data = make_orig_array()
}) // likely want to put other functions in here properly

	$('#ab_scale').on('click', function(){
		scale_ab();

})
	$('#g_scale').on('click', function () {
		scale_g();
	})

$('#reset').on('click', function(){
	reset();
});

$('#submit').on('click', function(){
	enable_column("*");
	document.getElementById('team_form').submit();
})

function reset () {
	var target_rows = document.getElementsByClassName('y2015');
	$(target_rows).each(function(){
		var i = $(this).index()
		var tds = $(this).find('input')
		$(tds).each(function(index){
			$(this).val(orig_data[i][index])
		})
	})	
}


function scale_g() {
	// set all col's to disabled, enable col "G"
	disable_all();
	enable_column("G");
	$('.G input').change(function () {
			var row_num = ($('.G input').index($(this)));
			new_g = parseFloat($(this).val());
			if (new_g >= 0 && new_g <= 162) {
			old_g = parseFloat(orig_data[row_num][0]);
			ratio = parseFloat(new_g / old_g);
			// set target row
			target_row = $('.y2015').get(row_num);
			targets = $(target_row).find('td:not(.id) :disabled');
			$(targets).each(function(index){
				old_val = orig_data[row_num][index + 1]
				new_val = Math.round(parseFloat(old_val * ratio));
				$(this).val(new_val);
			})
		} else {
			// message flash
			console.log("G must be >0 and < 162");
		}
	})
}


// may want to refactor w/ scale_g as scale to column
function scale_ab () {
	disable_all();
	enable_column("AB");
	
	$('.AB input').change(function () {
		var row_num = ($('.AB input').index($(this)));
		new_abs = parseFloat($(this).val());
		old_abs = parseFloat(orig_data[row_num][1]);
		ratio = parseFloat(new_abs / old_abs);
		var new_games = Math.round(parseFloat(orig_data[row_num][0] * ratio))
		// set target row
		target_row = $('.y2015').get(row_num);
		// targets = $(target_row).find('td :disabled');  // old line
		targets = $(target_row).find('td:not(.id) :disabled');
		$(targets).each(function(index){
			//old_val = $(this).val();
			if (index == 0) {
				var dex = index;
				
			} else {
				var dex = index + 1;
			};
			old_val = orig_data[row_num][dex]
			new_val = Math.round(parseFloat(old_val * ratio));
			if (new_games >= 0 && new_games <=162) {
				$(this).val(new_val);
			} else {
				// reset to either 0 or 162
				// message flash
				// might want to call scale_g and autofix to 162g
				console.log("more/less than a season of games");
			}
			
		})
	})
}


function make_orig_array () {
	orig_data = []
	// grab the table rows	
	$('.y2015').each(function (index) {
		// console.log(index);
		row_data=[];
		$(this).find('input').each(function () {
			row_data.push($(this).val());
		})
	orig_data.push(row_data);
	})
	return orig_data;
}


// use "column_name" to enable one col or "*"" for all
function enable_column(column_name) {
	if (column_name === 'undefined' || column_name == "*") {
		var greyed = $('input:disabled');
	} else {
		var greyed = $("." + column_name + ' input:disabled');
	};
	if (greyed.length > 0) {
		for (var i = 0; i < greyed.length; i++) {
			greyed[i].removeAttribute('disabled');
		};
	}
}

function disable_all() {
	var not_disabled = $('input:enabled');
	// console.log(not_disabled)
	if (not_disabled.length > 0) {
		for (var i = 0; i < not_disabled.length; i++) {
			not_disabled[i].setAttribute("disabled", true);
		};
	}
}