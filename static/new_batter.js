$(document).ready(function(){
	$('#avg2014').click(function(){
		ensure_enabled();
		set_mlbavg();
	})
	$('#half_and_half').click(function () {
		ensure_enabled();
		half_and_half();
	})
})

function ensure_enabled() {
	var greyed = $('input:disabled');
	if (greyed.length > 0) {
		for (var i = 0; i < greyed.length; i++) {
			greyed[i].removeAttribute('disabled');
		};
	}
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

function set_mlbavg () {
	$('input').each(function(){
		var name = this.name;
		// console.log(name);
		stat = Math.round(mlb_avg_2014[name]);
		// console.log(stat);
		$(this).val(stat);
	})
}

mlb_avg_2014 = {'SF': 3.5171288189190566, 'GIDP': 9.95372243662762, 'AB': 456.1360784780428, 
	'PA': 506.57671840731734, 'G': 162.0, 'HR': 11.529131743144221, 'Season': '2014', 
	'BB': 38.614053282102724, 'SH': 3.6989068158248184, 'HBP': 4.549958346792703, 
	'CS': 2.8506094969312636, '1B': 78.28296978867373, 'SO': 103.12045427497917, 
	'2B': 22.411023648820958, 'H': 114.56145123174484, 'RBI': 51.627705333310665, 
	'3B': 2.338326051105935, 'R': 54.42598480082967, 'AVG" ': '.251', 'IBB': 2.7128988932147777, 
	'SB': 7.612642173447355}