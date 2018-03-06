var GlobalBus = new Vue();

// USER
Vue.component('user', {
    props: ['id', 'first_name', 'last_name', 'message', 'image', 'sended', 'new_msg_amount'],
    template:
    '  <a @click="chooseUser" :class="[\'user\', \'list-group-item\', {\'active\': choosen}]">\n' +
    '    <template v-if="image">' +
    '       <img :src="\'/Media/\' + image" :alt="first_name" class="img-circle pull-left">' +
    '    </template>' +
    '    <template v-else>' +
    '       <img src="/Static/img/logo.png" :alt="first_name" class="img-circle pull-left">' +
    '    </template>' +
    '    <h4 class="list-group-item-heading">{{ short_name }} <small class="pull-right text-muted">{{ message_datetime }}</small></h4>\n' +
    '    <p class="list-group-item-text">{{ short_message }} <span v-if="new_msg_amount" class="badge pull-right">{{ new_msg_amount }}</span></p>\n' +
    '  </a>\n',
    data: function () {
        return {
            choosen: false
        }
    },
    computed: {
        short_name: function () {
            var short_name = this.first_name + ' ' + this.last_name[0].toUpperCase();

            if (short_name.length > 15) {
                return short_name.slice(0, 15) + "..."
            }
            return short_name
        },
        short_message: function () {
            if (this.message.length > 30) {
                return this.message.slice(0, 30) + "..."
            }
            return this.message
        },
        message_datetime: function () {
            var datetime = new Date(this.sended);
            return datetime.toLocaleString();
        }
    },
    methods: {
        chooseUser: function () {
            this.$emit('choose', this);
        }
    }
});

// USERS BAR
Vue.component('users-bar', {
    created: function () {
        GlobalBus.$on('users-reload', this.reloadUsers);
    },
    template:
    '<div class="users-bar">' +
    '   <user v-for="u in users" :key="u.id" v-bind="u" @choose="setActiveUser"></user>' +
    '</div>',
    data: function () {
        return {
            activeUser: undefined,
            users: []
        }
    },
    methods: {
        setActiveUser: function (u) {
            if (this.activeUser) {
                this.activeUser.choosen = false;
            }
            u.choosen = true;
            this.activeUser = u;
            GlobalBus.$emit('messages-reload', u);
        },
        reloadUsers: function () {
            var vm = this;
            axios.get('/api/messages/users/').then(
                function (response) {
                    vm.users = response.data;
                }
            )
        }
    }
});

// MESSAGE WINDOW
Vue.component('message-window', {
    created: function () {
        GlobalBus.$on('message-window-scroll-bottom', this.scrollBottom);
    },
    // updated: function () {
    //     this.$nextTick(function () {
    //         if (this.autoScrolling) {
    //             this.$el.scrollTop = this.$el.scrollHeight - this.$el.clientHeight;
    //         }
    //     })
    // },
    props: ['messages'],
    template:
    '<div class="message-window" v-on:scroll="processScroll">' +
    '   <div v-for="msg in messages" :class="[fromto(msg.fields) ? \'from\' : \'to\', \'message\']">' +
    '       {{ msg.fields.text }}' +
    '       <br><small class="text-muted pull-right">{{ message_datetime(msg.fields) }}</small>' +
    '   </div>' +
    '</div>',
    // data: function () {
    //   return {
    //       autoScrolling: true      // Автоматичний скролінг вниз, якщо змінюються messages
    //   }
    // },
    methods: {
        fromto: function (msg) {
            if (+$("#app").data('self-id') == msg.sender) {
                return true
            }
            return false
        },
        message_datetime: function (msg) {
            var datetime = new Date(msg.sended);
            if (datetime != 'Invalid Date')
                return datetime.toLocaleString();

            return msg.sended;
        },
        processScroll: function (event) {
            console.log(event.target.scrollTop);
            if (event.target.scrollTop < 150) {
                GlobalBus.$emit('load-more-messages');
            }
        },
        scrollBottom: function (offset) {
            this.$nextTick(function () {
                if (!offset) {
                    this.$el.scrollTop = this.$el.scrollHeight - this.$el.clientHeight;
                }
                else {
                    this.$el.scrollTop = offset
                }
            })
        }
    }
});

// MESSAGE BAR
Vue.component('message-bar', {
    created: function () {
        GlobalBus.$on('messages-reload', this.reloadMessages);
        GlobalBus.$on('load-more-messages', this.loadMoreMessages);
    },
    template:
    '<div class="message-bar">' +
    '   <div class="row">' +
    '       <div class="message-bar-header bg-info">\n' +
    '           <a href="#" class="receiver">{{ first_name }} {{ last_name }}</a>\n' +
    '       </div>' +
    '           <message-window v-show="!loadBannerShoved" :messages="messages"></message-window>' +
    '           <div v-show="loadBannerShoved" class="load-banner">Завантаження</div>' +
    '       <div class="col-md-10 col-md-offset-1">' +
    '           <form @submit.prevent="sendMessage">' +
    '               <div class="col-md-10">\n' +
    '                   <textarea v-model="inputMessage" class="col-md-4 form-control" rows="3" style="resize: none"></textarea>\n' +
    '               </div>\n' +
    '               <button class="btn btn-link send-message"><span class="glyphicon glyphicon-send"></span></button>\n' +
    '           </form>' +
    '       </div>' +
    '   </div>' +
    '</div>',
    data: function () {
        return {
            messages: [],
            activeUser: undefined,
            loadBannerShoved: false,
            inputMessage: '',
            loadingMoreMessages: false
        }
    },
    methods: {
        reloadMessages: function (user) {
            this.activeUser = user;
            this.loadBannerShoved = true;

            var vm = this;
            axios.get('/api/messages/list/', {
                params: {
                    id: user.id
                }
            }).then(
                function (response) {
                    vm.loadBannerShoved = false;
                    response.data = response.data.reverse();
                    vm.messages = response.data;
                    GlobalBus.$emit('message-window-scroll-bottom');
                }
            );
        },
        loadMoreMessages: function () {
            if (!this.loadingMoreMessages) {
                this.loadingMoreMessages = true;
                console.log('load messages');
                var vm = this;
                axios.get('/api/messages/list/', {
                    params: {
                        id: vm.activeUser.id,
                        last_message_pk: vm.messages[0].pk
                    }
                }).then(
                    function (response) {
                        vm.messages = response.data.reverse().concat(vm.messages);
                        vm.loadingMoreMessages = false;
                        if (response.data.length) {
                            GlobalBus.$emit('message-window-scroll-bottom', 150)
                        }
                    }
                ).catch(
                    function (error) {
                        vm.loadingMoreMessages = false;
                });
            }
        },
        sendMessage: function () {
            if (this.activeUser && this.inputMessage) {
                var msg = {
                    pk: null,
                    fields: {
                        text: this.inputMessage,
                        sended: 'Очікується',
                        sender: +$("#app").data('self-id')
                    }
                };
                this.messages.push(msg);
                $.ajax({
                    url: '/api/messages/list/',
                    type: 'post',
                    data: {
                        'csrfmiddlewaretoken': $('[name=csrfmiddlewaretoken]').val(),
                        'receiver_pk': this.activeUser.id,
                        'message': this.inputMessage
                    },
                    context: this,
                    success: function (data) {
                        msg.fields.sended = data;
                    }
                })
            }
            this.inputMessage = '';
            GlobalBus.$emit('message-window-scroll-bottom');
        }
    },
    computed: {
        first_name: function () {
            if (this.activeUser) {
                return this.activeUser.first_name
            }
            return "Виберіть"
        },
        last_name: function () {
            if (this.activeUser) {
                return this.activeUser.last_name
            }
            return "користувача"
        }
    }

});


var app = new Vue({
    el: '#app',
    data: function () {
        return {}
    }
});

GlobalBus.$emit('users-reload');