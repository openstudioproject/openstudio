/**

	Created by Edwin van de Ven (edwin@openstudioproject.com)
	License: GPLv2 or v3

**/

$(document).ready(function() {

	var chart_opts = { 
		  scaleFontSize: 11,
	};

	$.getJSON("geography_get_data.json", function(json) {
		// city chart
		var data = json.json_data.city;
		var ctx = $("#city-chart-area").get(0).getContext("2d");
		var cityBar = new Chart(ctx).Bar(data, chart_opts);
		// country chart
		var data = json.json_data.country;
		var ctx = $("#country-chart-area").get(0).getContext("2d");
		var cityBar = new Chart(ctx).Bar(data, chart_opts);
	});
});
	

