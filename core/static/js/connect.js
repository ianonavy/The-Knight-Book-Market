function connect(id) {
    // Get the message textarea.
    textarea = document.getElementById('message');
    
    // If the textarea is missing (i.e., the user is at the home page),
    if (textarea == null) {
        // send a prompt dialogue asking them for a message.
        message = prompt('Add a personalized message (or leave blank):');
    } else {
        // Otherwise, grab the message
        message = textarea.value
    }
    
    // If the user hit the Cancel button,
    if (message == null) {
        // Refresh the page and exit the function.
        window.location = window.location;
        return;
    }
    
    // Set the URL to /connect/id/
    url = "/connect/" + id + "/";
    
    // If there was a non-blank message,
    if (message != "") {
        // add it to the URL.
        url += message + "/";
    }
    
    // Connect the team and the mentor for the first time, potentially uniting
    // these people for many years.
    window.location = url
}