function PhotoManager(input) {
    // input => string or jquery to input[type=file]
    MODAL_SELECTOR = "#change-photo-modal"
    DISMISS_BTN_SELECTOR = "#change-photo-modal[data-dismiss=modal]"
    this.PHOTO_WRAP = "photo-wrap"

    this.STATE = {
        NOT_LOADED: 0,
        LOADED: 1
    };

    // Modal body jQuery object
    this._modal = $(MODAL_SELECTOR + ' .modal-body')
    this.dismiss = $(DISMISS_BTN_SELECTOR)

    this._photoURI = '';
    this._state = this.STATE.NOT_LOADED;
    this._photo = undefined; // Photo jQuery object

    if (!this._modal.length) {
        throw 'Modal not found'
    }
    else if (this._modal.length > 1) {
        throw 'Multiple modals found'
    }

    try {
        this.input = $(input);
    } catch (e) {
    }
}

PhotoManager.prototype.loadFromInput = function (input) {
    if (typeof(input) != 'object') {
        input = $(input);
    }
    this._photoURI = window.URL.createObjectURL(input[0].files[0]);
    if (this._photoURI) {
        this._state = this.STATE.LOADED;
        return true;
    }
    return false;
};

// Дадає завантажену фотографію (якщо не завантажено, то намагається завантажити)
// у блок this._modal. Фотографія додається в початок блоку.
PhotoManager.prototype.showImage = function () {
    if (this._state == this.STATE.NOT_LOADED
        && (!this.input || !this.loadFromInput(this.input))) {
        throw 'No image to show.';
    }


    this._modal.prepend(
        '<div id="' + this.PHOTO_WRAP + '">' +
        '<img src="' + this._photoURI + '">' +
        '</div>'
    );
    this._photo = $('#' + this.PHOTO_WRAP + ':first-of-type img');
};

PhotoManager.prototype.removeImage = function () {
    this._modal.find('#' + this.PHOTO_WRAP).remove();
};


function ResizedPhotoManager(input) {
    PhotoManager.apply(this, [input]);

    this.RESIZE_SELECTOR = 'resize-block';
    this._resize_block = undefined;
}

ResizedPhotoManager.prototype = Object.create(PhotoManager.prototype);
ResizedPhotoManager.prototype.constructor = PhotoManager;

// Додає та ініціалізує область виділення на фотографії.
ResizedPhotoManager.prototype._initResizeArea = function () {
    $('#' + this.PHOTO_WRAP).append(
        '<div id="' + this.RESIZE_SELECTOR + '"></div>'
    );
    $('#' + this.RESIZE_SELECTOR).resizable({
        aspectRatio: 1,
        handles: "all",
        containment: 'parent'
    });
    $('#' + this.RESIZE_SELECTOR).draggable({
        containment: 'parent'
    });
};

ResizedPhotoManager.prototype.showImage = function () {
    PhotoManager.prototype.showImage.apply(this);
    this._initResizeArea();
};

// Повертає ширину (а так як зона квадратна, то й ширину) зони
// виділення зображення
ResizedPhotoManager.prototype.getResizeAreaLength = function () {
    return $('#' + this.RESIZE_SELECTOR).width();
};

// Повертає відступи зони виділення зображення
ResizedPhotoManager.prototype.getResizeAreaOffsets = function () {
    var rBlock = $('#' + this.RESIZE_SELECTOR);
    return {
        offsetTop: rBlock.position().top,
        offsetLeft: rBlock.position().left
    }
};

// Повертає оригінальні розміри завантаженого фото.
ResizedPhotoManager.prototype.getRealPhotoSize = function () {
    var photo = this._photo[0];
    if (this._state == this.STATE.NOT_LOADED) {
        throw "Photo have not loaded yet"
    }
    else if (!photo) {
        throw 'No photo';
    }


    return {
        height: photo.naturalHeight,
        width: photo.naturalWidth
    }
};

// Повертає розмір фото, що відображається на сторінці (розмір img об'єкта)
ResizedPhotoManager.prototype.getPhotoSize = function () {
    var photo = this._photo;
    if (this._state == this.STATE.NOT_LOADED) {
        throw "Photo have not loaded yet"
    }
    else if (!photo) {
        throw 'No photo';
    }


    return {
        height: photo.height(),
        width: photo.width()
    }
};

// Повертає відношення реального розміру(оригіналу фото) до того, що відображається
// на сторінці.
ResizedPhotoManager.prototype.getScale = function () {
    var rSize = this.getRealPhotoSize(),
        size = this.getPhotoSize();
    return rSize.width / size.width;
};

// Повертає массив з 2 кординатами:
// перші два числа кординати першої точки прямокутника
// другі два числа відповідно другої точки
// По суті знаходяться реальні розміри виділеної області на фотографії
// з урахуванням зменшення/збільшення фотографії.
// !!!
// Але ніде не перевіряється чи така область можлива, якщо так станеться,
// що область вийде за межі фотографії, метод всеодно обрахує прямокутник
// відповідно до розмірів фотографії та області виділення.
// !!!
ResizedPhotoManager.prototype.getRealPhotoArea = function () {
    var offset = this.getResizeAreaOffsets(),
        areaSide = this.getResizeAreaLength(),
        scale = this.getScale();

    return [
        offset.offsetTop * scale,
        offset.offsetLeft * scale,
        (offset.offsetTop + areaSide) * scale,
        (offset.offsetLeft + areaSide) * scale
    ]
}

$(function () {

    $('.events-opener').click(function () {
        $('.events').toggleClass('events-opened');
        $('.events-opener span').toggleClass('glyphicon-calendar');
        $('.events-opener span').toggleClass('glyphicon-remove');
    });

    $('.events').on('transitionend', function () {
        if ($(this).hasClass('events-opened')) {
            $('body').addClass('lock');
        }
        else {
            $('body').removeClass('lock');
        }
    });

    $('.navbar-opener').click(function () {
        $(this).toggleClass('light');
    });


    a = new ResizedPhotoManager("input[name=photo]");
    $("input[name=photo]").on('change', function () {
        $('.save-photo').removeAttr('disabled');
        $(".upload-btn-wrapper .btn").text('Обрати іншу фотографію');
        a.removeImage();
        a.loadFromInput($(this));
        a.showImage();
    });

    $('.delete-photo').click(function () {
        a.removeImage();
        $('.save-photo').attr('disabled', 'disabled');
        $(".upload-btn-wrapper .btn").text('Обрати фотографію');
    });

    $('.save-photo').click(function () {
        alert(a.getRealPhotoArea());
    });

});