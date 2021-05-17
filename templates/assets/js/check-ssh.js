const socket = io('/check-ssh');

socket.on('live', function (ssh) {
    vm.$data.ssh_live_list.push(ssh)
    console.log(`LIVE ${Object.values(ssh).join('|')}`)
})
socket.on('die', function (ssh) {
    vm.$data.ssh_die_list.push(ssh)
    console.log(`DIE ${Object.values(ssh).join('|')}`)
})