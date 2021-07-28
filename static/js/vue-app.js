const vm = new Vue({
    el: '#main-app',
    data() {
        return {
            ssh_list: [],
            ssh_live_list: [],
            ssh_die_list: [],
            proxy_list: [],
            settings: {
                process_count: 20
            },
            temp_settings: {
                process_count: 20
            },
            ssh_text: ''
        }
    }
})