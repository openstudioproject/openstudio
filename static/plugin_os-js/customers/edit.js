/**

    Created by Edwin van de Ven (edwin@openstudioproject.com)
    License: GPLv2 or v3

**/

$(document).ready(function() {
    $("#all_bo_notes, #all_te_notes").click(function(e){  
        console.log('clicked');
        iconHandlers();
    });
    
    $("button.close").click(function() {
        reloadNotes();
    });
    
    $("button.btn-modal-close").click(function() {
        reloadNotes();
    });
});

$(document).keyup(function(e) {
    if (e.keyCode == 27) reloadNotes();
});

function reloadNotes() {
    $('#os-bonote_latest').get(0).reload();
    $('#os-tenote_latest').get(0).reload();
}

function iconHandlers() {
    // remove and edit links
    $('.modal-body .btn .fa-times').each(function() {
        $(this).parent().unbind();
        $(this).parent().click(function(event) {
            event.preventDefault(); // prevent jumping to top of page after confirmation
            $li = $(this).closest('li'); // save the table row in a variable to fade it out when removing
            if(confirm("Really delete this note?")) {
                var $id = $(this).closest('li').attr('id');
                var data = {};
                data['id'] = $id.split('_')[1];
                var url = '/customers/note_delete.json';
            
                var post = $.post(url, data, function(json) {
                    console.log("Note delete posted to " + url + 
                                ", data: " + JSON.stringify(data));
                }, "json");
            
                // success
                post.done(function(json) {
                    $('div.flash').html(json.message + '<span id="closeflash"> × </span>');
                    $('div.flash').show();
                    setTimeout(function() {
                        $('div.flash').fadeOut();
                    }, 2500 ); 
                    if (json.status == 'success') { // fade out row in table
                        $li.fadeOut().slideUp();
                    }
                    console.log("Note delete done, result: " + JSON.stringify(json));
                });
            
                // fail
                post.fail(function(data) {
                    var msg = "Uh oh... something went wrong while removing the customer from the list..."
                    $('div.flash').html(msg + '<span id="closeflash"> × </span>');
                    $('div.flash').show();
                    setTimeout(function() {
                        $('div.flash').fadeOut();    
                    }, 2500 );
                    console.log("Note delete failed. Status: " + data.status + " " +
                                 "Status Text: " + data.statusText);
                });
            } // close if for confirmation
        }); // close click event
    }); // close span loop
}

