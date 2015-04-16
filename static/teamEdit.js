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
	} else {
		$('#team_form .AB input').each(function () {
			$(this).attr('disabled', "");
		})

	}
}

// index() and get()

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