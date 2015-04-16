$(document).ready(function () {
	scale_ab();
	orig_data = make_orig_array()
})

$('#ab_scale').on('click', function(){
	scale_ab();
})

function scale_ab () {
	if ($('#team_form .AB :enabled').length == 0) {
		// console.log('HERERERERERE');
		$('#team_form .AB input').each(function () {
			$(this).removeAttr('disabled');
		})
		$('.AB input').change(function () {
			var row_num = ($('.AB input').index($(this)));
			new_abs = parseFloat($(this).val());
			old_abs = parseFloat(orig_data[row_num][1]);
			ratio = parseFloat(new_abs / old_abs);
			// set target row
			target_row = $('.y2015').get(row_num);
			targets = $(target_row).find('td :disabled');
			$(targets).each(function(){
				old_val = $(this).val();
				new_val = Math.round(parseFloat(old_val * ratio));
				$(this).val(new_val);
			})

			// loop though target
		})
	} else {
		$('#team_form .AB input').each(function () {
			$(this).attr('disabled', "");
		})

	}
}

// index() and get()
// d = $('.AB input').get(3) // or use this
// $('.AB input').index(d) // returns 3

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