// Отримує список файлів уроку з серверу у форматі json
function getFileList(pk, callback) {
    $.ajax({
        url: '/teacher/lesson/' + pk + '/files/',
        type: 'get',
        dataType: 'json',
        success: callback
    });
}

// Отримує опис уроку для генерації форми у форматі json
function getLessonFormData(pk, callback) {
    $.ajax({
        url: '/teacher/lesson/' + pk + '/json/',
        type: 'get',
        dataType: 'json',
        success: callback
    });
}

function delete_file () {
    var lesson_pk = $('#edit-lesson-modal').data('pk');
    console.log($(this));
    var csrf = $('input[name=csrfmiddlewaretoken]:first').val();
    $.ajax({
        url: '/teacher/lesson/' + lesson_pk + '/file/delete/',
        type: 'post',
        data: {
            'pk': $(this).data('pk'),
            'csrfmiddlewaretoken': csrf
        },
        success: function () {reloadFileList(lesson_pk, true    )}
    });
};

// Перезавантажує список файлів
// при outside == true, перезавантажується список файлів на всі сторінці, для заданого pk
function reloadFileList(pk, outside) {
    getFileList(pk, function (json) {
        $("#edit-lesson-modal .file-list li").remove();
        if (outside) {
            console.log(".lesson[data-pk=" + pk + "] .list-group");
            $(".lesson[data-pk=" + pk + "] .list-group").empty();
        }
        ;
        if (json) {
            var filename, url;
            for (var i in json) {
                // Отримали повний шлях до файлу
                filename = json[i].fields.file;
                url = $('body').data('media-url') + filename;
                // Забераємо лише назву файлу з шляху
                filename = filename.slice(filename.lastIndexOf('/') + 1);
                $("#edit-lesson-modal .file-list").append(
                    "<li class=\"list-group-item\"><a href=" + url + ">" + filename +
                    "</a><button class=\"btn btn-xs btn-link pull-right btn-remove\" data-pk='" + json[i].pk + "'><span class=\"glyphicon glyphicon-remove\"></span></button></li>"
                );
                if (outside) {
                    $(".lesson[data-pk=" + pk + "] .list-group").append(
                        '<li class="list-group-item"><span class="glyphicon glyphicon-duplicate type-icon"></span><a href="'
                        + url + '">' + filename +
                        '</a></li>'
                    )
                }
            }
            $("#edit-lesson-modal .file-list .btn-remove").click(delete_file);
        }
    });
}

function setLesson(data, textStatus, xhr, inPage) {
    console.log(data);
    var MODAL_LESSON_FORM_SELECTOR = "#edit-lesson-modal form:last";
    var form = $(MODAL_LESSON_FORM_SELECTOR);
    var fields = data[0]['fields'];

    for (var input_name in fields) {
        form.find('[name=' + input_name + ']').val(
            fields[input_name]
        )
    }

    if (inPage) {
        var lesson_block = $('.lesson[data-pk=' + data[0].fields.pk + ']');
        lesson_block.find('.panel-heading span:first').text(fields['name']);
        lesson_block.find('.panel-body p:first').text(fields['short_description']);

    }
    form.attr('action', '/teacher/lesson/' + data[0].pk + '/update/');
}

function reloadLesson(pk, outside) {
    getLessonFormData(pk, setLesson);
}

$('#edit-lesson-modal').on('show.bs.modal', function (event) {
    var button = $(event.relatedTarget);
    reloadFileList(button.data('pk'));
    reloadLesson(button.data('pk'));
    $('#edit-lesson-modal .file-upload-form').attr(
        'action',
        '/teacher/lesson/' + button.data('pk') + '/file/upload/'
    );
    $(this).data('pk', button.data('pk'))
});

$(".file-upload-form input").on('change', function () {
    var bar = $(".progress-bar");
    var form = $(".file-upload-form");

    form.ajaxForm({
        beforeSend: function () {
            $('.progress').show();
            bar.css({width: '0'});
        },
        uploadProgress: function (event, position, total, percentComplete) {
            var percentVal = percentComplete + '%';
            bar.css({width: percentVal});
        },
        complete: function (xhr) {
            console.log(xhr);
            setTimeout(function () {
                $('.progress').hide();
                bar.css({width: '0'});
                reloadFileList($('#edit-lesson-modal').data('pk'), true);
            }, 1000);
        }
    });
    form.submit();
});

$("#add-lesson-modal .btn-submit").click(function () {
    var form = $("#add-lesson-modal form");
    $.ajax({
        url: form.attr('action'),
        type: 'post',
        data: form.serialize(),
        dataType: 'json',
        success: function (data) {
            if (data.status) {
                window.location.reload();
            }
            else {
                console.log(data);
            }
        }
    })
});

$("#edit-modal .btn-submit").click(function () {
    $("#edit-modal form").submit();
});

// Форма редагування уроку
$('.edit-lesson-form').submit(function (e) {
    e.preventDefault();
    $.ajax({
        url: $(this).attr('action'),
        data: $(this).serialize(),
        type: 'post',
        context: this,
        beforeSend: function () {
            $(this).find('button[type=submit]').button('loading');
        },
        success: function (data) {
            var formData = {};
            if (data.success) {
                var inputs = $(this).find('input, textarea');
                for (var inp in $.makeArray(inputs)) {
                    formData[$(inputs[inp]).attr('name')] = $(inputs[inp]).val();
                }
                formData['pk'] = $('#edit-lesson-modal').data('pk');
                setLesson([{fields: formData}], null, null, true);
            }
        },
        complete: function () {
            $(this).find('button[type=submit]').button('reset');
        }

    })
});

$('#delete-lesson-modal').on('show.bs.modal', function (e) {
    var button = $(e.relatedTarget);
    $('#delete-lesson-modal').find('form').attr('action', button.data('url'));
});