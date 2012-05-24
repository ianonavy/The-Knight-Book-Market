window.myobj = {
    markerMoved: function() { 
        $('#id_latitude')[0].value = this.getPosition().lat() + '';
        $('#id_longitude')[0].value = this.getPosition().lng() + '';
    }
};

$('#id_location').change(function() { codeAddress() });

function codeAddress() {
    console.log('codeAddress ' + $('#id_location')[0].value)
    address = $('#id_location')[0].value;
    var geocoder = new google.maps.Geocoder();
    var latlng = new google.maps.LatLng(0, 0);
    var myOptions = {
      zoom: 16,
      center: latlng,
      mapTypeId: google.maps.MapTypeId.HYBRID
    }
    var map = new google.maps.Map(document.getElementById("id_google_map"),
        myOptions);
    
    geocoder.geocode({'address': address}, function(results, status) {
      if (status == google.maps.GeocoderStatus.OK) {
        map.setCenter(results[0].geometry.location);
        var marker = new google.maps.Marker({
            map: map,
            position: results[0].geometry.location,
            draggable: true
        });
        google.maps.event.addListener(marker, 'position_changed', function() {
            $('#id_latitude')[0].value = marker.getPosition().lat() + '';
            $('#id_longitude')[0].value = marker.getPosition().lng() + '';
        });
      } else {
        console.log("Error: " + status);
      }
    });
}

$('#id_contact_email').change(function() {
    if ($('#contact_email_for_user')[0].checked) {
        $('#id_email')[0].value = $('#id_contact_email')[0].value;
    }
});

$('#id_confirm_contact_email').change(function() {
    if ($('#contact_email_for_user')[0].checked) {
        $('#id_confirm_email')[0].value = $('#id_confirm_contact_email')[0].value;
    }
});

$('#contact_email_for_user').click(function() {
    if ($('#contact_email_for_user')[0].value) {
        $('#id_email')[0].value = $('#id_contact_email')[0].value;
        $('#id_confirm_email')[0].value = $('#id_confirm_contact_email')[0].value;
    }
});


/*
$(document).ready(function(){

    var thumb = $('img#avatar_preview');    

    new AjaxUpload('id_image', {
        action: $('form#signup').attr('action'),
        name: 'image',
        onSubmit: function(file, extension) { console.log('onSubmit')
            $('div.preview').addClass('loading');
        },
        onComplete: function(file, response) { console.log('onComplete')
            thumb.load(function(){
                $('div.preview').removeClass('loading');
                thumb.unbind();
            });
            thumb.attr('src', response);
        }
    });
});*/