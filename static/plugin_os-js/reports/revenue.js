/**

	Created by Edwin van de Ven (edwin@openstudioproject.com)
	License: GPLv2 or v3

**/

$(document).ready(function() {

	var chart_opts = { 
		  scaleFontSize: 11,
	};

	$.getJSON("revenue_get_data.json", function(json) {
		// totls chart
		var data = json.json_data.total;
		var ctx = $("#total-chart-area").get(0).getContext("2d");
		var totalBar = new Chart(ctx).Bar(data, chart_opts);
		// subscriptions chart
		var data = json.json_data.subscriptions;
		var ctx = $("#subscriptions-chart-area").get(0).getContext("2d");
		var subscriptionsBar = new Chart(ctx).Bar(data, chart_opts);
		// classcards chart
		var data = json.json_data.classcards;
		var ctx = $("#classcards-chart-area").get(0).getContext("2d");
		var classcardsBar = new Chart(ctx).Bar(data, chart_opts);
		// workshops chart
		var data = json.json_data.workshops;
		var ctx = $("#workshops-chart-area").get(0).getContext("2d");
		var workshopsBar = new Chart(ctx).Bar(data, chart_opts);
		// dropin chart
		var data = json.json_data.dropin;
		console.log(data);
		var ctx = $("#dropin-chart-area").get(0).getContext("2d");
		var dropinBar = new Chart(ctx).Bar(data, chart_opts);
		// trialclasses chart
		var data = json.json_data.trialclasses;
		var ctx = $("#trialclasses-chart-area").get(0).getContext("2d");
		var trialclassesBar = new Chart(ctx).Bar(data, chart_opts);
	});
	

    $('#reports_revenue_tabs a').click(function (e) {
	  e.preventDefault()
      console.log('clicked');
      $(this).tab('show')
    });

});
	
