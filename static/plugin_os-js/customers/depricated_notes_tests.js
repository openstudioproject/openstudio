/*
    Created by Edwin van de Ven (edwin@openstudioproject.com)
    License: GPLv2 or v3
    
    Javascript tests for customers/notes
*/

var list_item = 'ul#os-customers_notes li';

function createTestData() {
    /* 
        When no list items exist, add one using the form so we have something
        to test the delete action with.
    */
    nr_of_items = $(list_item).length
    if (nr_of_items < 1) {
        $('textarea').val('test');
        $('input[type=submit').click();
    }
}

$(document).ready(function() {
    createTestData();
    
    window.confirm = function(msg) {
        // This will get executed instead of showing a browser prompt message
        return true;
    }
    
    // click delete button
    $(list_item).find('span.icon-remove').click();
    // Define the test
    QUnit.test("Backoffice Notes lightbox", function( assert ) {
        var done = assert.async();
        setTimeout(function() {
            assert.deepEqual($(list_item).css("display"), "none", "List item is be hidden after successful delete.");
            done();
        }, 1000); // use a timeout to allow for the fadeOut animation to complete
    });
});


