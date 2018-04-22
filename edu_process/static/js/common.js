$(function () {

    $('.navbar-opener').click(function () {
        var header = $('.header');
        header.toggleClass('responsive');
        $('.navbar-opener span').toggleClass('glyphicon-menu-up');
    });

    $('.errorlist .exit').click(function () {
        $(this).parent().remove();
    });
});
