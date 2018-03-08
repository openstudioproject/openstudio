/**

	Created by Edwin van de Ven (edwin@openstudioproject.com)
	License: GPLv2 or v3

**/

$(document).ready(function() {
	// Class list begin
	var tools_selector = 'div.os-schedule_links';
	var filler_selector = 'td.os-schedule_filler';
	
	$(tools_selector).each(function() {
		$(this).hide(); // hide the customer tools
	});
	
	$('tr.os-schedule_class').each(function(index) {
		$(this).hover(function() {
				$(this).next().find(tools_selector).show();
				$(this).next().find(filler_selector).hide();
				$(this).next().css("background-color", "#F5F5F5");
				$(this).css("background-color", "#F5F5F5");
			}, // end handlerIn
			function() {
				$(this).next().find(tools_selector).hide();
				$(this).next().find(filler_selector).show();
				$(this).next().css("background-color", "#FFF");
				$(this).css("background-color", "#FFF");
			} // end handlerOut
		);
	}); // end setup hover handler for class table rows
	
	$('tr.os-schedule_links').each(function(index) {
		$(this).hover(function() {
			$(this).find(tools_selector).show();
			$(this).find(filler_selector).hide();
			$(this).prev().css("background-color", "#F5F5F5");
			$(this).css("background-color", "#F5F5F5");
		}, // end handlerIn
		function() {
			$(this).prev().css("background-color", "#FFF");
			$(this).css("background-color", "#FFF");
			$(this).find(tools_selector).hide();
			$(this).find(filler_selector).show();
		}); // end handlerOut & end hover function
	}); // end setup hover handler for tools table rows
});

