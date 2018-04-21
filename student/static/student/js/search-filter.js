Vue.options.delimiters = ['((', '))'];

 Vue.filter('short', function (item,count) {
  if (item.length>count)
        {
           item =  item.slice(0,count)+"...";
        }
        return item;
})


 //Підсвічування тексту 

 jQuery.fn.highlight = function(pat) {
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
 return this.each(function() {
  innerHighlight(this, pat.toUpperCase());
 });
};

//Видалення підсвітки

jQuery.fn.removeHighlight = function() {
 function newNormalize(node) {
    for (var i = 0, children = node.childNodes, nodeCount = children.length; i < nodeCount; i++) {
        var child = children[i];
        if (child.nodeType == 1) {
            newNormalize(child);
            continue;
        }
        if (child.nodeType != 3) { continue; }
        var next = child.nextSibling;
        if (next == null || next.nodeType != 3) { continue; }
        var combined_text = child.nodeValue + next.nodeValue;
        new_node = node.ownerDocument.createTextNode(combined_text);
        node.insertBefore(new_node, child);
        node.removeChild(child);
        node.removeChild(next);
        i--;
        nodeCount--;
    }
 }

 return this.find("span.highlight").each(function() {
    var thisParent = this.parentNode;
    thisParent.replaceChild(this.firstChild, this);
    newNormalize(thisParent);
 }).end();
};

 
 var demo = new Vue({
    el: '#my-courses',
    data: {
        searchString: "",
        limit:2,
        showMore: true,
        dateDisplayOptions: { 
            year: 'numeric', 
            month: 'numeric', 
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'

        },
        activeCategory: "",
        searchResultCount: 0,
        // Модель даних, які повинні передаватися ajax'ом

        courses: [
            {
                "image": "https://www.chiefcourses.com/wp-content/themes/olam332/index/img/our-history/freelance.jpg",
                "name": "27 блакабуль с задачками для оттачивания навыков программирования",
                "url_course": "#",
                "url_author": "#",
                "categories":[
                        "Програмування",
                        "Математика",
                        "Алгоритмізація",
                        "Фізика"
                ],
                "pub_date": "23.02.2018",
                "description": " curapatka Lorem ipsum dolor sit amet, consectetur adipisicing elit.curapatka Lorem ipsum dolor sit amet, consectetur adipisicing elit. curapatka Lorem ipsum dolor sit amet, consectetur adipisicing elit.  Velit sed sapiente aliquid alias dignissimos. Ipsa debitis nisi totam excepturi enim esse cum nam quaerat voluptatibus! Vitae eum, neque reiciendis harum."
            },
            {
                "image": "https://www.chiefcourses.com/wp-content/themes/olam332/index/img/our-history/freelance.jpg",
                "name": "forbi diam magna, varius a",
                "url_course": "#",
                "url_author": "#",
                "categories":[
                        "Програмування",
                        "Математика",
                        "Алгоритмізація",
                        "Фізика"
                ],
                "date_-register": "23.02.2018",
                "description": "Lorem ipsum dolor sit amet, consectetur adipisicing elit. Velit sed sapiente aliquid alias dignissimos. Ipsa debitis nisi totam excepturi enim esse cum nam quaerat voluptatibus! Vitae eum, neque reiciendis harum."
            },
            {
                "image": "https://www.chiefcourses.com/wp-content/themes/olam332/index/img/our-history/freelance.jpg",
                "name": "forbi diam magna, varius a",
                "url_course": "#",
                "url_author": "#",
                "categories":[
                        "Системна адміністрація"
                ],
                "date_-register": "23.02.2018",
                "description": "Lorem ipsum dolor sit amet, consectetur adipisicing elit. Velit sed sapiente aliquid alias dignissimos. Ipsa debitis nisi totam excepturi enim esse cum nam quaerat voluptatibus! Vitae eum, neque reiciendis harum."
            },
            {
                "image": "https://www.chiefcourses.com/wp-content/themes/olam332/index/img/our-history/freelance.jpg",
                "name": "Maecenas justo lorem",
                "url_course": "#",
                "url_author": "#",
                "categories":[
                        "Програмування",
                        "Математика",
                        "Алгоритмізація",
                        "Фізика"
                ],
                "pub_date": "23.02.2018",
                "description": "Lorem ipsum dolor sit amet, consectetur adipisicing elit. Velit sed sapiente aliquid alias dignissimos. Ipsa debitis nisi totam excepturi enim esse cum nam quaerat voluptatibus! Vitae eum, neque reiciendis harum."
            },
            {
                "image": "https://www.chiefcourses.com/wp-content/themes/olam332/index/img/our-history/freelance.jpg",
                "name": "Donec consectetur diam et ",
                "url_course": "#",
                "url_author": "#",
                "categories":[
                        "Програмування",
                        "Математика",
                        "Українська мова",
                        "Фізика"
                ],
                "pub_date": "23.02.2018",
                "description": "Lorem ipsum dolor sit amet, consectetur adipisicing elit. Velit sed sapiente aliquid alias dignissimos. Ipsa debitis nisi totam excepturi enim esse cum nam quaerat voluptatibus! Vitae eum, neque reiciendis harum."
            },
            {
                "image": "https://www.chiefcourses.com/wp-content/themes/olam332/index/img/our-history/freelance.jpg",
                "name": "Сгенерировано 5 абзацей",
                "url_course": "#",
                "url_author": "#",
                "categories":[
                        "Програмування",
                        "Математика",
                        "Алгоритмізація",
                        "Фізика"
                ],
                "pub_date": "23.02.2018",
                "description": "curapatka Lorem ipsum dolor sit amet, consectetur adipisicing elit. Velit sed sapiente aliquid alias dignissimos. Ipsa debitis nisi totam excepturi enim esse cum nam quaerat voluptatibus! Vitae eum, neque reiciendis harum."
            }
        ]

    },
    mounted: function () {
        var vm = this;
        $.ajax({
            url: '/api/course/',
            data: '',
            type: 'get',
            success: function (data) {
                var queryset = data['queryset:']
                for (var i = 0; i < queryset.length; i++) {
                    queryset[i]['pub_date'] = new Date(queryset[i]['pub_date']);
                }
                console.log(queryset);
                vm.courses = data['queryset:'];
            },
            complete: function (xhr, textStatus) {
                console.log(textStatus);
            }
        })
    },
    methods: {
        locale_pub_date: function (date) {
            if (typeof(date) === "object") {
                return date.toLocaleDateString("en-US", this.dateDisplayOptions)
            }
            return "";
        },
        set_active_category: function (event) {
            this.activeCategory = $(event.target).text();
        }
    },
    computed: {
        //Розрахункова властивість, яка містить розділи, що відповідають searchString
        filteredCourses: function () {
            var courses_array = this.courses,
                searchString = this.searchString,
                vm = this;

            if (vm.activeCategory.length) {
                courses_array = courses_array.filter(function(item) {
                    console.log(item.categories.includes(vm.activeCategory))
                    if (item.categories.includes(vm.activeCategory)) {
                        return true;
                    }
                })
            }

            if(!searchString) {
                $(".item").removeHighlight();
            }
            else {
                searchString = searchString.trim().toLowerCase();
                courses_array = courses_array.filter(function(item){
                    if ((item.name.toLowerCase().indexOf(searchString) !== -1 
                        || item.description.toLowerCase().indexOf(searchString) !== -1)
                        ) {
                        $(".item .name").removeHighlight();    
                        if ( searchString ) {
                             $(".item .name").highlight(searchString);
                        }
                         $(".item .description").removeHighlight();    
                        if ( searchString ) {
                             $(".item .description").highlight(searchString);
                        }
                        return item;
                    }
                })
            }
            
            this.searchResultCount = courses_array.length;
            // Повертає відфільтровані розділи
            return courses_array;
        },
    }
});

 $(document).ready(function(){
    

    $(".categories").find("div").click(function(){
        $(".categories .active").removeClass("active");
        $(".tags .active").removeClass("active");
        $(this).addClass("active");
        $(".tags").find('div:contains('+this.innerHTML+')').addClass("active");
    });

    $(".tags").find("div").click(function(){
        $(".tags .active").removeClass("active");
        $(".categories .active").removeClass("active");
        $(".categories").find('div:contains('+this.innerHTML+')').addClass("active");
        $(".tags").find('div:contains('+this.innerHTML+')').addClass("active");
        $(this).addClass("active");
    });
 })