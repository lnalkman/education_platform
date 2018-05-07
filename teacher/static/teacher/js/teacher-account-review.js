$(function () {
    $('.events-opener').click(function () {
        $('.related-courses').toggleClass('related-courses-opened');
        $('.events-opener span').toggleClass('glyphicon-calendar');
        $('.events-opener span').toggleClass('glyphicon-remove');
    });

    $('.navbar-opener').click(function () {
        $(this).toggleClass('light');
    });
});