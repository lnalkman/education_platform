function random_password() {
    return Math.random().toString(36).slice(-8);
}

$("#user-add form").submit(function () {
    $('.err-list').empty();
    $.ajax({
        url: $(this).attr('action'),
        data: $(this).serialize(),
        context: this,
        method: 'post',
        beforeSend: function (jqXHR, settings) {
            $('.alert-block').empty();
            return true;
        },
        success: function (data, textStatus, jqXHR) {
            if (textStatus == 'success') {
                if (data['status'] == '200') {
                    $('.alert-block').append('<div class="alert alert-info alert-dismissible fade in" role="alert"><button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>' + data['text'] + '</div>')
                    $('#user-add form')[0].reset();
                    $('#user-add [name=password]').attr('value', random_password());
                } else {
                    $('.alert-block').append('<div class="alert alert-danger alert-dismissible fade in" role="alert"><button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>' + data['text'] + '</div>')
                    data['errors'] = JSON.parse(data['errors']);
                    console.log(data['errors']);
                    for(var subject in data['errors']) {
                        var selector = '[name=' + subject + '] + .err-list';
                        console.log($(selector));
                        $(selector).append('<li class="text-danger">' + data['errors'][subject][0]['message'] + '</li>')
                    }
                }
            }
            return true
        },
        dataType: 'json'
    });
    return false
});

$('[name=password]').attr('value', random_password());