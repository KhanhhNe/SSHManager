const socket = io('/check-ssh');

socket.on('live', function (ssh) {
    vm.$data.ssh_live_list.push(ssh)
})
socket.on('die', function (ssh) {
    vm.$data.ssh_die_list.push(ssh)
})
socket.on('clear_live', function () {
    vm.$data.ssh_live_list = []
})
socket.on('clear_die', function () {
    vm.$data.ssh_die_list = []
})
function check_ssh() {
    socket.emit('check_ssh')
}