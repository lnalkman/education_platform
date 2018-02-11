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

});