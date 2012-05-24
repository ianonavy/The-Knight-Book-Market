$('#toggle_details').click(function() {
    details = $('#instructions_details')
    if (details.css('display') == 'none')
        details.fadeIn('slow')
    else
        details.fadeOut('slow')
})

$('#toggle_expires').click(function() {
    details = $('#expires_details')
    if (details.css('display') == 'none')
        details.fadeIn('slow')
    else
        details.fadeOut('slow')
})