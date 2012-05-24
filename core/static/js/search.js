fields = ['name', 'page', 'per', 'distance', 'mentors', 'teams', 'exp']

for (field in fields) {
    $('#' + fields[field]).change(function() {$('#submit').click()})
}