/**

	Created by Edwin van de Ven (edwin@openstudioproject.com)
	License: GPLv2 or v3

**/
var menu_selector = 'ul#os-menu-settings-permissions li';
var active_class = 'active';


$(document).ready(function() {
	hideAllTables();
	showTable('pinboard');

	$(menu_selector).click(function() {
		clearActive();
		$(this).addClass(active_class);
		$id = $(this).attr('id');
		var id_name = $id.split('-')[1];
		console.log(id_name);
		
		hideAllTables();
		showTable(id_name);
	});
	
	$('td.level_0, td.level_1, td.level_2, td.level_3, td.level_4').click(function() {
		$checkbox = $(this).next().find('input');
		$checked = $checkbox.is(':checked');
		$checkbox.prop('checked', !$checked);
	});
});

function clearActive() {
	// clear all active tabs
	$(menu_selector).each( function( index ) {
		$( this ).removeClass(active_class);
	});
}

function showTable(table_id) {
	$('table#' + table_id).show();
	//$('div#' + table_id + ' ').each(function() {
	//	$(this).show();
	//});
}

function hideAllTables() {
	$('div#os-permissions table').each(function() {
		$(this).hide();
	});
	
}
