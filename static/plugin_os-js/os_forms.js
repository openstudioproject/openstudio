/**

	Created by Edwin van de Ven (edwin@openstudioproject.com)
	License: GPLv2 or v3

**/
var selector = 'input[type="text"], input[type="email"], input[type="password"], input[type="number"], select, textarea';
var selector_submit = 'input[type="submit"]'

$(document).ready(function() {
    set_form_classes();
    activate_tooltips();
    //activate_datemask();
    //activate_timemask();
    //activate_popovers();
}); // close document.ready

function set_form_classes() {
    $(selector).addClass('form-control');
    $(selector_submit).addClass('btn btn-primary');
    $(selector_submit).removeClass('btn-default');
    $('.date').removeClass('date').addClass('datepicker').attr('autocomplete', 'off');
}

function activate_tooltips() {
    $('[data-toggle="tooltip"]').tooltip()
}

function activate_popovers() {
    $('[data-toggle="popover"]').popover()
}

        //Timepicker
        //$('.timepicker').timepicker({
          //showInputs: false,
          //showSeconds: false,
          //showMeridian: false,
          //defaultTime: false,
          //minuteStep: 5,
        //})

