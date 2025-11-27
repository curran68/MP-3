$(document).ready(function() {
    $('.sidenav').sidenav({ edge: "right" });
    $('.collapsible').collapsible();
    $('.modal').modal();

    // FIX: re-initialise selects properly
    $('select').formSelect();

    // Some browsers need delayed init for Materialize
    setTimeout(function() {
        $('select').formSelect();
    }, 200);
});
