/*
    Created by Edwin van de Ven (edwin@openstudioproject.com)
    License: GPLv2 or v3
    
    Javascript tests for customers/edit.js
*/
var lb_teachers = "#os-lb_teachers";
var lb_teachers_content = "#os-lb_teachers-content";
var lb_backoffice = "#os-lb_backoffice";
var lb_backoffice_content = "#os-lb_backoffice-content";

QUnit.test("Teacher Notes lightbox", function( assert ) {
//    var fixture = $( "div.span9" );
    // Check teachers lightbox
    assert.deepEqual($(lb_teachers).css("display"), "none", "#os-lb_teachers (Teachers notes lightbox) should be hidden");
    $("#all_te_notes").click();
    assert.deepEqual($(lb_teachers).css("display"), "block", "#os-lb_teachers (Teachers notes lightbox) should be shown");
    assert.deepEqual($(lb_teachers_content).css("display"), "block", "#os-lb_teachers-content (Teachers notes lightbox) should be shown");
    
    $("#os-lb_teachers_close").click();
    var done = assert.async();
    setTimeout(function() {
        assert.deepEqual($(lb_teachers).css("display"), "none", "#os-lb_teachers (Teachers notes lightbox) should be hidden");
        assert.deepEqual($(lb_teachers_content).css("display"), "none", "#os-lb_teachers-content (Teachers notes lightbox) should be hidden");
        done();
    }, 1000); // use a timeout to allow for the fadeOut animation to complete
});

QUnit.test("Backoffice Notes lightbox", function( assert ) {
    // Check teachers lightbox
    assert.deepEqual($(lb_backoffice).css("display"), "none", "#os-lb_backoffice (Backoffice notes lightbox) should be hidden");
    $("#all_bo_notes").click();
    assert.deepEqual($(lb_backoffice).css("display"), "block", "#os-lb_backoffice (Backoffice notes lightbox) should be shown");
    assert.deepEqual($(lb_backoffice_content).css("display"), "block", "#os-lb_backoffice (Backoffice notes lightbox) should be shown");
    $("#os-lb_backoffice_close").click();
    var done = assert.async();
    setTimeout(function() {
        assert.deepEqual($(lb_backoffice).css("display"), "none", "#os-lb_backoffice (Backoffice notes lightbox) should be hidden");
        assert.deepEqual($(lb_backoffice_content).css("display"), "none", "#os-lb_backoffice-content (Backoffice notes lightbox) should be hidden");
        done();
    }, 1000); // use a timeout to allow for the fadeOut animation to complete
});


