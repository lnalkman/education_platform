$(function() {
	// Clear event
	$('.image-preview-clear').click(function(){
		$('.image-preview-filename').val("");
		$('.image-preview-clear').hide();
		$('.image-preview-input input:file').val("");
		$(".image-preview-input-title").text("Обрати");
	});
	// Create the preview image
	$(".image-preview-input input:file").change(function (){
		var img = $('<img/>', {
			id: 'dynamic',
			width:250,
			height:200
		});
		var file = this.files[0];
		var reader = new FileReader();
		// Set preview image into the popover data-content
		reader.onload = function (e) {
			$(".image-preview-input-title").text("Змінити");
			$(".image-preview-clear").show();
			$(".image-preview-filename").val(file.name);
			img.attr('src', e.target.result);
		};
		reader.readAsDataURL(file);
	});

	// При відкритті вкладки попереднього перегляду публікації
	// генеруємо публікацію
    $('a[href="#view"]').on('shown.bs.tab', function (e) {
        $('#preview_title').text($('.title-input input').val());
        $('#preview_content').html(
            markdown.toHTML(
                $('.content-input textarea').val()
            )
        );

		// Якщо немає фотографії ігноруємо помилку
        try {
            var photoURI = window.URL.createObjectURL($('.image-input .image-preview-input input')[0].files[0]);
            $('#preview_image').attr('src', photoURI);
        } catch (e) {}

    });

	// Збереження публікації з вкладки попереднього перегляду
    $('#save_post_from_view').click(function () {
        $('a[href="#add"]').tab('show');
        $('form.update-course').submit();
    });
});