$(document).ready(function () {
	scale_ab();
})

$('#ab_scale').on('click', function(){
	scale_ab();
})

function scale_ab () {
	if ($('#team_form .AB :enabled').length == 0) {
		console.log('HERERERERERE');
		$('#team_form .AB input').each(function () {
			$(this).removeAttr('disabled');
		})
	} else {
		$('#team_form .AB input').each(function () {
			$(this).attr('disabled', "");
		})

	}
}