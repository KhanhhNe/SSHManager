const socket = io('/check-ssh');

socket.on('live', function (ssh) {
    vm.$data.ssh_live_list.push(ssh)
})
socket.on('die', function (ssh) {
    vm.$data.ssh_die_list.push(ssh)
})
function check_ssh() {
    vm.$data.ssh_live_list = []
    vm.$data.ssh_die_list = []
    socket.emit('check_ssh')
}