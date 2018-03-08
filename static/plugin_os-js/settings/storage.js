/**

	Created by Edwin van de Ven (edwin@openstudioproject.com)
	License: GPLv2 or v3

**/

$(document).ready(function() {
	$.getJSON("system_storage.json", function(json) {
		if (json.json_data.length > 0) {
			var data = json.json_data;
			var ctx = $("#chart-area").get(0).getContext("2d");
			var myPie = new Chart(ctx).Doughnut(data);
		} else {
			alert("Error generating chart: No data retrieved.");
		}
	});
});
	




