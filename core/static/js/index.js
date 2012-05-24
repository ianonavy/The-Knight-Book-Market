$('#sold tr, #bought tr').mouseenter(function() {
    $(this).find('a').css({"visibility":"visible"});
})

$('#sold tr, #bought tr').mouseleave(function() {
    $(this).find('a').css({"visibility":"hidden"});
})

$('.flash').click(function() {
    $(this).hide();
})