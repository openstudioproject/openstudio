/**

	Created by Edwin van de Ven (edwin@openstudioproject.com)
	License: GPLv2 or v3

**/

$(document).ready(function() {
	$.getJSON("discovery_get_data.json", function(json) {
		if (json.json_data.length > 0) {
			var data = json.json_data;
			var ctx = $("#chart-area").get(0).getContext("2d");
			var myPie = new Chart(ctx).Doughnut(data);
		} else {
			alert("No data found");
		}
	});
});
	




