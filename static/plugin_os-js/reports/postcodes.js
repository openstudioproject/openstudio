/**

	Created by Edwin van de Ven (edwin@openstudioproject.com)
	License: GPLv2 or v3

**/

$(document).ready(function() {

	var chart_opts = { 
		  scaleFontSize: 11,
	};

	$.getJSON("postcodes_get_data.json", function(json) {
		// postcodes chart
		/*
		var data = json.data;
		var ctx = $("#chart-area").get(0).getContext("2d");
		var postcodesBar = new Chart(ctx).Bar(data, chart_opts); */
		if (json.data.length > 0) {
			var ctx = $("#chart-area").get(0).getContext("2d");
			var myPie = new Chart(ctx).Doughnut(json.data);
		} else {
			alert("No data found");
		}
		
	});
});
	

