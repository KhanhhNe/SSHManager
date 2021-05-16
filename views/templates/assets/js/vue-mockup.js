const vm = new Vue({
    el: '#main-app',
    data() {
        return {
            ssh_list: [{ip: '0.0.0.0', username: 'ssh', password: 'ssh'}],
            ssh_live_list: [{ip: '0.0.0.0', username: 'live', password: 'live'}],
            ssh_die_list: [{ip: '0.0.0.0', username: 'die', password: 'die'}],
            proxy_list: [{port: 8888, ip: '0.0.0.0'}],
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