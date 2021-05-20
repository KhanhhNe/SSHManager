const socket = io('/connect-ssh');


const range = (start, stop) => Array.from(Array(stop - start + 1).keys())
    .map(offset => offset + start)


function connect_ssh() {
    $('#connect-ssh-input').addClass('was-validated')
    if (!$('#port-input').get(0).checkValidity()) {
        return
    }

    vm.$data.proxy_list = []
    const portStr = $('#port-input').val()
    const portList = portStr.split(',').map(portOrRange => {
        if (portOrRange.includes('-')) {
            return range(...portOrRange.split('-').map(i => parseInt(i)))
        } else {
            return parseInt(portOrRange)
        }
    }).reduce((a,b) => a.concat(b), [])
    socket.emit('connect_ssh', portList)
}


socket.on('port_proxy', port_data => {
    let found = false
    for (let proxy of vm.$data.proxy_list) {
        if (proxy.port == port_data.port) {
            proxy.ip = port_data.ip
            found = true
            break
        }
    }
    if (!found) {
        vm.$data.proxy_list.push(port_data)
        vm.$data.proxy_list.sort((p1, p2) => p1.port > p2.port ? 1 : -1)
    }
})


socket.on('out_of_ssh', function () {
    $('#out-of-ssh-toast').toast({autohide: false})
    $('#out-of-ssh-toast').toast('show')
})