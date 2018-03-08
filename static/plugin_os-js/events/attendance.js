/**

	Created by Edwin van de Ven (edwin@openstudioproject.com)
	License: GPLv2 or v3

**/

$(document).ready(function() {
	/* 
		This function adds an handler to the checkboxes. When they are clicked
		the data is serialized and sent to "attendance_change_info.json".
		After the data is sent, a message is shown with the message returned by
		web2py.
	*/
	
	$('input[type="checkbox"]').change(function() {
		var $form = $(this).closest('form');
		var data = $form.serializeArray();
		// put the checkbox in a variable so we can use it to change the checkbox status.
		var $checkbox = $(this);
		// post attendance info
		var url = '/workshops/product_customer_update_info.json';
		var post = $.post(url, data, function(json) {
			console.log("Posted attendance info to " + url + 
						", data: " + JSON.stringify(data)); 
		}, "json");

		// Success
		post.done(function(json) {
			$('div.flash').html(json.message + '<span id="closeflash"> × </span>');
			$('div.flash').show();
			setTimeout(function() {
				$('div.flash').fadeOut();	
			}, 2500 );
			if (json.status == 'fail') {
				revert_checkbox_state();
			}
			console.log("Attendance update info done, result: " + JSON.stringify(json));
		});
		
		// fail
		post.fail(function(data) {
			var msg = "Uh oh... something went wrong when updating the attendance info..."
			$('div.flash').html(msg + '<span id="closeflash"> × </span>');
			$('div.flash').show();
			setTimeout(function() {
				$('div.flash').fadeOut();	
			}, 2500 );
			console.log("Failed update attendance info. Status: " + data.status + " " +
					 	"Status Text: " + data.statusText);
			/* revert checkbox status to the status it had before the click that 
				initiated the failed post. */
			revert_checkbox_state();
		});
		
		function revert_checkbox_state() {
			checked = $checkbox.prop('checked');
			$checkbox.prop('checked', !checked);
		}
	});
}); // end document ready


