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
    data: function() {
        return {
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
            filteredCourses: undefined,
            activeCategory: "",
            searchResultCount: 0,
            _searchInputTimer: undefined,
            courses: []
        }
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
                vm.courses = data['queryset:'];

                // Ініціалізуємо список відфільтрованих курсів
                vm.filteredCourses = vm.get_courses();
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
            if ($(event.target).text() == "Всі") {
                this.activeCategory = "";
            }
            else { this.activeCategory = $(event.target).text(); }
            $(".categories .active").removeClass("active");
            $(".categories").find("div:contains(" + $(event.target).text() + ")").addClass("active");
            $(event.target).addClass("active"); 

        },
        
        get_courses: function(){
            var courses_array = this.courses,
                searchString = this.searchString,
                vm = this;
                      
            if (vm.activeCategory.length) {
                vm.limit = 2;
                courses_array = courses_array.filter(function(item) {
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
                        || item.description.toLowerCase().indexOf(searchString) !== -1)){
                        $(".item ").removeHighlight();    
                        $(".item .name").highlight(searchString);
                        $(".item .description").highlight(searchString);
                        console.log(item.name);
                        return item;
                    }
                })
            }
            
            vm.searchResultCount = courses_array.length;
            
            // Повертає відфільтровані розділи
            
            return courses_array;
        },
        category_is_active: function (categoryName) {
            if (this.activeCategory === categoryName || categoryName == "Всі") {
                return true;
            }
            return false;
        }
    },
    watch: {
        searchString: function() {
            var vm = this,
                delay = 750;

            if (this._searchInputTimer) {
                clearTimeout(this._searchInputTimer);
                this._searchInputTimer = undefined;
            }

            this._searchInputTimer = setTimeout(function () {
                     console.log(vm.searchString);
                    vm.filteredCourses = vm.get_courses();
                },
                delay
            )
        },
        activeCategory: function () {
            this.filteredCourses = this.get_courses();
        }
    },
});

    
