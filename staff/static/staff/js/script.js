function random_password() {
    return Math.random().toString(36).slice(-8);
}


// Завантаження нової таблиці неактивних користувача та заміна
// старої таблиці на нову
function reloadInactiveUsers(search) {
    $.ajax({
        url: '/staff/teachers/ajax',
        data: {is_active: '', q: search}, // Only inactive
        method: 'get',
        success: function (data, textStatus, jqXHR) {
            $('#disabled-users table').html(data);
            // Вмикаємо pop-up на доданих елементах
            $('[data-toggle="popover"]').popover();

            // Вмикаємо можливість обирати всі чекбокси
            $('#disabled-users table thead input[type="checkbox"]').click(function () {
                var checked = this.checked;
                $('#disabled-users input[name="user_pk"]').prop('checked', checked)
            });
        },
        dataType: 'html'
    })
}


// Ajax відправка форми на додавання нового викладача в БД
$("#user-add form").submit(function () {
    $('.err-list').empty();
    $.ajax({
        url: $(this).attr('action'),
        data: $(this).serialize(),
        context: this,
        method: 'post',
        beforeSend: function (jqXHR, settings) {
            $('.alert-block').empty();
            $('.err-list').empty();
            return true;
        },
        success: function (data, textStatus, jqXHR) {
            if (textStatus == 'success') {
                if (data['status'] == '200') {
                    // Показуємо повідомлення про успішне додання викладача
                    $('.alert-block').append('<div class="alert alert-info alert-dismissible fade in" role="alert"><button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>' + data['text'] + '</div>')

                    // Очищуємо форму
                    $('#user-add form')[0].reset();
                    // В поле паролю додаємо новий згенерований пароль
                    $('#user-add [name=password]').attr('value', random_password());
                } else {
                    // Показуємо повідомлення про неуспішність операції
                    $('.alert-block').append('<div class="alert alert-danger alert-dismissible fade in" role="alert"><button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>' + data['text'] + '</div>')

                    // Парсимо помилки
                    data['errors'] = JSON.parse(data['errors']);
                    // Перебираємо помилки по input
                    for (var subject in data['errors']) {
                        // У селектор .err-list під помилковим input'ом записуємо помилку
                        var selector = '[name=' + subject + '] + .err-list';
                        $(selector).append('<li class="text-danger">' + data['errors'][subject][0]['message'] + '</li>')
                    }
                }
            }
            return true
        },
        error: function (textStatus) {
            // Показуємо повідомлення про неуспішність операції
            $('.alert-block').append(
                '<div class="alert alert-danger alert-dismissible fade in" role="alert">' +
                '<button type="button" class="close" data-dismiss="alert" aria-label="Close">' +
                '<span aria-hidden="true">&times;</span></button><strong>Помилка!</strong><br>Не вдалось створити користувача.<br> Текст помилки:' + textStatus + '</div>');
        },
        dataType: 'json'
    });
    return false
});

$('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
    if ($(e.target).attr('aria-controls') == '#disabled-users') {
        reloadInactiveUsers();
    }
});

$("#disabled-users .search").submit(function (e) {
    reloadInactiveUsers($(this).children('input[type="text"]').val());
    return false;
});

$('.action').click(function () {
    var data = $('input[name=user_pk]').serializeArray();
    data = data.concat([
        {name: 'csrfmiddlewaretoken', value: $('input[name=csrfmiddlewaretoken]').val()},
        {name: 'action', value: 'delete'}
    ]);
    console.log(data);
    console.log($.param(data));
    $.ajax({
        url: '/staff/teachers/ajax',
        data: data,
        method: 'post',
        success: reloadInactiveUsers
    })
});


$('[name=password]').attr('value', random_password());
$('[data-toggle="popover"]').popover();