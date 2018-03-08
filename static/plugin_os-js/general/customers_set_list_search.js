/**

    Created by Edwin van de Ven (edwin@openstudioproject.com)
    License: GPLv2 or v3

**/

function customers_set_list_search($input, $target) {
    /*
        $input is expected to be a jquery variable of the input that provides the search string.
        $target is expected to be the target div into which the customers list is loaded. 
        On success $target will be reloaded.
    */
    var data = {};
    data['name'] = $input.val();
    
    var url = '/customers/load_list_set_search.json';

    var post = $.post(url, data, function(json) {
        console.log("Search name posted to " + url + 
                    ", data: " + JSON.stringify(data));
    }, "json");

    // success
    post.done(function(json) {
        if (json.status == 'success') { // fade out row in table
            $target.get(0).reload();
        } 
        console.log("Set search name, result: " + JSON.stringify(json));
    });

    // fail
    post.fail(function(data) {
        var msg = "Uh oh... something went wrong while submitting the search..."
        $('div.flash').html(msg + '<span id="closeflash"> × </span>');
        $('div.flash').show();
        setTimeout(function() {
            $('div.flash').fadeOut();    
        }, 2500 );
        console.log("Setting search name failed. Status: " + data.status + " " +
                     "Status Text: " + data.statusText);
    });
}
