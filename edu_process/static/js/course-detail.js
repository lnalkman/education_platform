$(function () {
    $window = $(window);
    $('div[data-type="background"]').each(function () {
        var $bgobj = $(this);
        $(window).scroll(function () {
            var yPos = -($window.scrollTop() / $bgobj.data('speed'));
            var coords = '50% ' + yPos + 'px';
            $bgobj.css({backgroundPosition: coords});
        });
    });
    $('#carouselExampleIndicators').carousel();

    $('.section-right').click(function () {
        var section = $(this).parents('.section');
        if (section.hasClass('active')) {
            section.find('.section-inner').slideUp();
            section.removeClass('active');
        }
        else {
            section.find('.section-inner').slideDown();
            section.addClass('active');
        }
    });

    $('button[data-loading-text]').click(function () {
       $(this).button('loading');
    })
});


Vue.options.delimiters = ['((', '))'];
var __EMPTY__ = Object.freeze({});

var app = new Vue({
    el: '.content',
    data: {
        active_lesson: __EMPTY__
    },
    methods: {
        show_lesson: function (event) {
            var target = $(event.currentTarget),
                vm = this;

            if (this.active_lesson.id !== target.data('lesson-id')) {
                this.active_lesson = __EMPTY__;
                $.ajax({
                    url: '/lesson/' + target.data('lesson-id') + '/json/',
                    method: 'get',
                    success: function (data) {
                        vm.active_lesson = data;
                    }
                });
            }
        },
        format_datetime: function (datetimeString) {
            var dt = new Date(datetimeString),
                fillZeroLeft = function (s) {
                    return s < 10 ? '0' + s : s
                };

            return fillZeroLeft(dt.getDate()) + '.' + fillZeroLeft(dt.getMonth()) + '.' + dt.getFullYear() + ', '
                + fillZeroLeft(dt.getHours()) + ':' + fillZeroLeft(dt.getMinutes());
        },
        is_empty: function (val) {
            return val === __EMPTY__;
        }

    }
});