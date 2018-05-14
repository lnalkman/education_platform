// CHANGE COURSE FORM

$("form.update-course").find("input, textarea").focus(function () {
    $("form.update-course .status").hide();
});

$("form.update-course").submit(function (e) {
    $(this).find('.status').hide();
    $(this).find('button[type=submit]').button('loading');
    var formData = new FormData(this);
    $.ajax({
        url: $(this).attr('action'),
        data: formData,
        method: 'post',
        dataType: 'json',
        context: this,
        timeout: 5000,
        success: function (data) {
            if (data.success) {
                $(this).find('.status.label-success').show();
                $(this).find('button[type=submit]').button('reset');
            }
        },
        error: function (jqXHR, textStatus) {
            $(this).find('.status.label-danger').show();
            $(this).find('button[type=submit]').button('reset');
        },
        cache: false,
        contentType: false,
        processData: false
    });
    return false;
});


// ADD MODULE FORM
$('button.submit-modal').click(function (e) {
    var form = $('form.add-module');
    var btn = $(this);
    btn.button('loading');
    $.ajax({
        url: $(form).attr('action'),
        data: $(form).serialize(),
        method: 'post',
        dataType: 'json',
        context: form,
        timeout: 5000,
        success: function (data) {
            if (data.success) {
                location.reload();
            }
            else {
                for (var field in data.errors) {
                    var input = form.find('[name=' + field + ']');
                    input.parents('.form-group').addClass('has-error');
                    input.next('.help-block').text(data.errors[field]);
                }
                btn.button('reset');
            }
        },
        error: function (jqXHR, textStatus) {
            $(this).find('button.submit-modal').button('reset');
        }

    });
    return false;
});


// SEARCH AND ADD GROUPS

var ajaxTimerId = 0;
$("input.search-group").on('input', function () {
    clearTimeout(ajaxTimerId);
    ajaxTimerId = setTimeout(function () {
        $.ajax({
            url: $("input.search-group").attr('data-url'),
            type: 'get',
            data: {q: $("input.search-group").val()},
            context: $("input.search-group"),
            success: function (data) {
                var name;
                $('.search-results').html('');
                for (var i in data) {
                    name = data[i]['fields']['name'];
                    $('.search-results').append(
                        $('<a href="#" class="list-group-item"></a>').text(name)
                    )
                }
                $(".search-results .list-group-item:not(.disabled)").click(function (e) {
                    e.preventDefault();
                    $("input.search-group").val($(this).text())
                    $('.search-results').html('');
                });
            }
        })
    }, 500)
});

$(".onhighlight-checkboxes").click(function (e) {
    e.preventDefault();
    $(".access-control ul.list-group input[type=checkbox]").prop('checked', true);
});
$(".offhighlight-checkboxes").click(function (e) {
    e.preventDefault();
    $(".access-control ul.list-group input[type=checkbox]").prop('checked', false);
});

function loadGroupList() {
    var container = $('.access-control ul.styled-input-container');
    container.empty();
    $.ajax({
        url: $(".reload-groups:first").data('url'),
        type: 'get',
        context: container,
        dataType: 'json',
        success: function (data) {
            var group_name,
                pk;
            var groups = data['groups'];
            if (groups.length) {
                for (var i in groups) {
                    group_name = groups[i]['fields']['name'];
                    pk = groups[i]['pk'];
                    this.append(
                        '<li class="list-group-item">\n' +
                        '<a href="#">' + group_name + '</a>\n' +
                        '<div class="styled-input-single pull-right">\n' +
                        '<input type="checkbox" id="inp-' + i + '" data-pk="' + pk + '"/>\n' +
                        '<label for="inp-' + i + '"></label>\n' +
                        '</div>\n' +
                        '</li>'
                    )
                }
            }
            else {
                this.append(
                    '<p class="text-center">Список груп пустий</p>'
                )
            }
        },
        error: function () {
            this.append(
                '<p class="text-center">Не вдалось завантажити список груп. Спробуйте оновити.</p>'
            )
        }
    })
};

$(".add-group-btn").click(function () {
    var group_name = $("input.search-group").val();
    var url = $(this).data("add-group-url");
    var csrf = $("input[name=csrfmiddlewaretoken]:first").val();
    $(this).button('loading');
    $.ajax({
        url: url,
        type: 'post',
        data: {group_name: group_name, csrfmiddlewaretoken: csrf},
        context: this,
        success: function (data) {
            loadGroupList();
            $(this).button('reset');
        }
    })
});

$(".reload-groups").click(function (e) {
    e.preventDefault();
    loadGroupList();
});

$(".groups-remove").click(function (e) {
    e.preventDefault();
    var pks = [];
    $(".access-control .list-group input[type=checkbox]:checked").each(function () {
        pks.push($(this).data('pk'));
    });
    var url = $(this).data('url');
    var csrf = $("input[name=csrfmiddlewaretoken]:first").val();
    console.log($.param({csrfmiddlewaretoken: csrf, pk_list: pks}))
    $.ajax({
        url: url,
        type: 'post',
        data: $.param({csrfmiddlewaretoken: csrf, pk_list: pks}),
        success: function (data) {
            loadGroupList();
        }
    });
});


$('.image-preview-clear').click(function(){
		$('.image-preview-filename').val("");
		$('.image-preview-clear').hide();
		$('.image-preview-input input:file').val("");
		$(".image-preview-input-title").text("Обрати");
	});
	// Create the preview image
	$(".image-preview-input input:file").change(function (){
		var file = this.files[0];
		var reader = new FileReader();
		// Set preview image into the popover data-content
		reader.onload = function (e) {
			$(".image-preview-input-title").text("Змінити");
			$(".image-preview-clear").show();
			$(".image-preview-filename").val(file.name);
			$('#course-image-preview').attr('src', e.target.result);
		};
		reader.readAsDataURL(file);
	});


loadGroupList();

