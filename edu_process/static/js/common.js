$(function () {

    $('.navbar-opener').click(function () {
        var header = $('.header');
        header.toggleClass('responsive');
        header.removeClass('mobile-scrollable');
        $('.navbar-opener span').toggleClass('glyphicon-menu-up');
    });

    $('.header').on('transitionend', function () {
       var navbar = $(this);
       if (navbar.hasClass('responsive')) {
           navbar.addClass('mobile-scrollable');
       }
    });


});
