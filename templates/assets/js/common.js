socket.on('ssh', function (ssh_list) { vm.$data.ssh_list = ssh_list })


function export_csv(export_data, filename) {
    if (!export_data) return;
    const headers = [Object.keys(export_data[0]).join('|')]
    const body = export_data.map(info => Object.values(info).join('|'))
    const blob = new Blob([headers.concat(body).join('\n')], {type: "text/plain;charset=utf-8"})
    saveAs(blob, filename)
}


function import_ssh_text(ssh_text) {
    vm.$data.ssh_list = ssh_text.split('\n').map(line => {
        const splitted = line.split('|')
        return {
            'ip': splitted[0],
            'username': splitted[1],
            'password': splitted[2]
        }
    })
    socket.emit('ssh', vm.$data.ssh_lis)
}