Vue.options.delimiters = ['((', '))'];

Vue.filter('short', function (item, count) {
    if (item.length > count) {
        item = item.slice(0, count) + "...";
    }
    return item;
});


//Підсвічування тексту

jQuery.fn.highlight = function (pat) {
    function innerHighlight(node, pat) {
        var skip = 0;
        if (node.nodeType == 3) {
            var pos = node.data.toUpperCase().indexOf(pat);
            if (pos >= 0) {
                var spannode = document.createElement('span');
                spannode.className = 'highlight';
                var middlebit = node.splitText(pos);
                var endbit = middlebit.splitText(pat.length);
                var middleclone = middlebit.cloneNode(true);
                spannode.appendChild(middleclone);
                middlebit.parentNode.replaceChild(spannode, middlebit);
                skip = 1;
            }
        }
        else if (node.nodeType == 1 && node.childNodes && !/(script|style)/i.test(node.tagName)) {
            for (var i = 0; i < node.childNodes.length; ++i) {
                i += innerHighlight(node.childNodes[i], pat);
            }
        }
        return skip;
    }

    return this.each(function () {
        innerHighlight(this, pat.toUpperCase());
    });
};

//Видалення підсвітки

jQuery.fn.removeHighlight = function () {
    function newNormalize(node) {
        for (var i = 0, children = node.childNodes, nodeCount = children.length; i < nodeCount; i++) {
            var child = children[i];
            if (child.nodeType == 1) {
                newNormalize(child);
                continue;
            }
            if (child.nodeType != 3) {
                continue;
            }
            var next = child.nextSibling;
            if (next == null || next.nodeType != 3) {
                continue;
            }
            var combined_text = child.nodeValue + next.nodeValue;
            new_node = node.ownerDocument.createTextNode(combined_text);
            node.insertBefore(new_node, child);
            node.removeChild(child);
            node.removeChild(next);
            i--;
            nodeCount--;
        }
    }

    return this.find("span.highlight").each(function () {
        var thisParent = this.parentNode;
        thisParent.replaceChild(this.firstChild, this);
        newNormalize(thisParent);
    }).end();
};


var demo = new Vue({
    el: '#my-courses',
    data: function () {
        return {
            searchString: "",
            limit: 2,
            showMore: true,
            dateDisplayOptions: {
                year: 'numeric',
                month: 'numeric',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'

            },
            filteredCourses: undefined,
            activeCategoryId: null,
            searchResultCount: 0,
            _searchInputTimer: undefined,
            courses: [],
            loading: true
        }
    },

    mounted: function () {
        var vm = this;
        this.loading = true;

        function download_courses(offset) {
            $.ajax({
                url: '/api/course/',
                data: {student_id: 'self', offset: offset},
                type: 'get',
                success: function (data) {
                    var queryset = data['queryset'];
                    if (queryset.length) {
                        for (var i = 0; i < queryset.length; i++) {
                            queryset[i]['pub_date'] = new Date(queryset[i]['pub_date']);
                        }
                        vm.courses = vm.courses.concat(data['queryset']);

                        // Ініціалізуємо список відфільтрованих курсів
                        vm.filteredCourses = vm.get_courses();

                        if (vm.courses.length < data['result_count']) {
                            download_courses(vm.courses.length);
                        }
                        else {
                            vm.loading = false;
                        }
                    }
                }
            })
        }

        download_courses(0);
    },
    methods: {

        locale_pub_date: function (date) {
            if (typeof(date) === "object") {
                return date.toLocaleDateString("uk", this.dateDisplayOptions)
            }
            return "";
        },
        set_active_category: function (event) {
            console.log('set_active_cateogry ' + $(event.target).data('category-id'));
            if ($(event.target).text() === "Всі") {
                this.activeCategoryId = null;
            }
            else {
                this.activeCategoryId = +$(event.target).data('category-id');
            }
            $(".categories .active").removeClass("active");
            $(event.target).addClass("active");
        },

        get_courses: function () {
            var courses_array = this.courses,
                searchString = this.searchString,
                vm = this;


            vm.limit = 2;
            courses_array = courses_array.filter(function (item) {
                for (var i = 0; i < item.categories.length; i++) {
                    console.log(vm.activeCategoryId + ' ' + item.categories[i].id);
                    if (+vm.activeCategoryId === +item.categories[i].id || vm.activeCategoryId === null) {
                        return true;
                    }
                }
            });


            if (!searchString) {
                $(".item").removeHighlight();
            }
            else {
                searchString = searchString.trim().toLowerCase();
                courses_array = courses_array.filter(function (item) {
                    if ((item.name.toLowerCase().indexOf(searchString) !== -1
                            || item.description.toLowerCase().indexOf(searchString) !== -1)) {
                        return item;
                    }
                })
            }
            console.log(courses_array);
            vm.searchResultCount = courses_array.length;

            // Повертає відфільтровані розділи

            return courses_array;
        },
        category_is_active: function (categoryId) {
            return this.activeCategoryId === +categoryId || categoryId === "Всі"
        }
    },
    watch: {
        searchString: function () {
            var vm = this,
                delay = 750;

            if (this._searchInputTimer) {
                clearTimeout(this._searchInputTimer);
                this._searchInputTimer = undefined;
            }

            this._searchInputTimer = setTimeout(function () {
                    vm.filteredCourses = vm.get_courses();
                },
                delay
            )
        },
        activeCategoryId: function () {
            this.filteredCourses = this.get_courses();
        },
        filteredCourses: function () {
            if (this.searchString) {
                this.$nextTick(function () {
                    $(".item ").removeHighlight();
                    $(".item .name").highlight(this.searchString);
                    $(".item .description").highlight(this.searchString);
                })
            }
        }
    }
});

    
var search_courses = new Vue({
    el: '#all-courses',
    data: function () {
        return {
            searchString: "",
            limit: 2,
            showMore: true,
            dateDisplayOptions: {
                year: 'numeric',
                month: 'numeric',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'

            },
            filteredCourses: undefined,
            activeCategoryId: undefined,
            _searchInputTimer: undefined,
            _result_count: 0,
            courses: [],
            order: '',      // student_count || pub_date,
            loading: true,
            loading_more: false,
        }
    },
    mounted: function () {
        this.download_courses();
    },
    methods: {
        locale_pub_date: function (date) {
            if (typeof(date) === "object") {
                return date.toLocaleDateString("uk", this.dateDisplayOptions)
            }
            return "";
        },

        set_active_category: function (event) {
            console.log('set_active_cateogry ' + $(event.target).data('category-id'));
            if ($(event.target).text() === "Всі") {
                this.activeCategoryId = null;
            }
            else {
                this.activeCategoryId = +$(event.target).data('category-id');
            }
            $(".categories .active").removeClass("active");
            $(".categories").addClass("active");

            this.download_courses();
        },

        get_courses: function (change_limit) {
            if (change_limit) {
                this.limit = 4;
            }

            return this.courses;
        },

        category_is_active: function (categoryId) {
            return this.activeCategoryId === categoryId || categoryId === null
        },

        download_courses: function (offset) {
            var vm = this;
            if (offset === undefined) {
                offset = 0;
            }

            if (!offset) {
                this.loading = true;
            }
            else {
                this.loading_more = true;
            }

            $.ajax({
                url: '/api/course/',
                data: {offset: offset, q: vm.searchString, order: vm.order, category_id: vm.activeCategoryId},
                type: 'get',
                success: function (data) {
                    var queryset = data['queryset'];
                    vm._result_count = +data['result_count'];

                    vm.loading = false;
                    vm.loading_more = false;

                    if (queryset.length) {
                        for (var i = 0; i < queryset.length; i++) {
                            queryset[i]['pub_date'] = new Date(queryset[i]['pub_date']);
                        }

                        // Ініціалізуємо список відфільтрованих курсів
                        if (data['offset'] !== 0) {
                            vm.courses = vm.courses.concat(data['queryset']);
                            vm.filteredCourses = vm.get_courses();
                        }
                        else {
                            vm.courses = data['queryset'];
                            vm.filteredCourses = vm.get_courses(true);
                        }
                    }
                    else {
                        if (offset === 0) {
                            vm.courses = [];
                            vm.filteredCourses = vm.get_courses();
                        }

                    }
                }
            })
        },
        set_order: function (event) {
            event.preventDefault();
            var target = $(event.srcElement);

            $('[data-order]').removeClass('active');
            target.addClass('active');

            this.order = target.data('order');
        },
        show_more_courses: function () {
            this.limit += 4;
            if (this.limit >= this.courses.length && this.courses.length < this._result_count) {
                this.loading_more = true;
                this.download_courses(this.courses.length);
            }
        }
    },
    watch: {
        searchString: function () {
            var vm = this,
                delay = 1000;
            this.loading = true;

            if (this._searchInputTimer) {
                clearTimeout(this._searchInputTimer);
                this._searchInputTimer = undefined;
            }

            this._searchInputTimer = setTimeout(function () {
                    vm.download_courses();
                },
                delay
            )
        },
        activeCategoryId: function () {
            this.download_courses();
        },
        order: function () {
            this.download_courses();
        }
    },
    computed: {
        searchResultCount: {
            get: function () {
                return this.courses.length;
            },
            set: function(val) {

            }
        }
    }
});


