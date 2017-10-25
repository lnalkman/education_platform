$("#user-add form").submit(function () {
    $.post(
        $(this).attr('action'),
        $(this).serialize(),
        function (data, textStatus, jqXHR) {
            if (textStatus == 'success') {
                if (data['status'] == '200') {
                    $('.alert-block').append('<div class="alert alert-info alert-dismissible fade in" role="alert"><button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>' + data['text'] + '</div>')
                    $('#user-add form')[0].reset();
                } else {
                    $('.alert-block').append('<div class="alert alert-error alert-dismissible fade in" role="alert"><button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>' + data['text'] + '</div>')
                }
            }
            return true
        },
        'json'
    );
    return false
});