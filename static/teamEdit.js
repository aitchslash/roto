$(document).ready(function () {
	scale_ab();
})

function scale_ab () {
	if ($('#team_form .AB :enabled').length == 0) {
		console.log('HERERERERERE');
		$('#team_form .AB input').each(function () {
			$(this).removeAttr('disabled');
			// console.log($(this).val());
			// console.log(this)
		})
	} else {
		$('#team_form .AB input').each(function () {
			$(this).attr('disabled', "");
			// console.log($(this).val());
			// console.log(this)
		})

	}
}