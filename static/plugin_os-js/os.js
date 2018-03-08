/**

	Created by Edwin van de Ven (edwin@openstudioproject.com)
	License: GPLv2 or v3

**/

/* Function to slowly scroll to top after scrolling down */
$(document).ready(function() {
    $('#to_top').fadeOut();
});

$(window).scroll(function() {
    if ($(window).scrollTop() > 100) {
        $('#to_top').fadeIn();
    }
    else {
        // <= 100px from top - hide div
        $('#to_top').fadeOut();
    }
});

$('#to_top').click(function() {
    $('html,body').animate({ scrollTop: 0 }, 'slow');
});
