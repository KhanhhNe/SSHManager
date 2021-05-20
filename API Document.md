# SSHManager API Document

**Check SSH Endpoint**
----
Get app data (ssh list, live list, die list) from SSH checking in JSON format.

* **URL**
	- /check-ssh/ssh (Imported SSH list)
	- /check-ssh/live (Live SSH)
	- /check-ssh/die (Die SSH)

* **Method:** `GET`

* **Success Response:**

  * **Code:** 200 <br />
    **Content:** `[{"ip": "14.160.52.26", "username": "admin", "password": "admin"}]`

* **Sample Call:**

  ```javascript
    $.ajax({
      url: "/check-ssh/ssh",
      dataType: "json",
      type : "GET",
      success : function(ssh_list) {
        console.log(ssh_list);
      }
    });
  ```

**Connect SSH Endpoint**
----
  Get SSH list and port connection status from /connect-ssh in JSON format.

* **URL**
	- /connect-ssh/ssh (Imported SSH list) (same as above)
	- /connect-ssh/port-info (SSH IPs connected with ports)

* **Method:**  `GET`

* **Success Response:**

  * **Code:** 200 <br />
    **Content:** `{"8000": "14.160.52.26", "8001": ""}`

* **Sample Call:**

  ```javascript
    $.ajax({
      url: "/connect-ssh/port-info",
      dataType: "json",
      type : "GET",
      success : function(port_info) {
        console.log(port_info);
      }
    });
  ```

**Emit Endpoint**
----
Emit a signal to both server and connected clients. Use for action triggering/data importing.

* **URL**

  /emit
  
* **Method:** `POST`

* **JSON body**

   **Required:**
	`event=event_name` **Required**
	`namespace=/namespace/path` (defaults to default namespace)
	`data=<data>` **Required**

* **Success Response:**

  * **Code:** 200 <br />
    **Content:** `1`
 
* **Error Response:**

  * **Code:** 400 BAD REQUEST <br />
    **Content:** `0`

* **Sample Call:**

  ```javascript
    $.ajax({
      url: "/emit",
      type : "POST",
      success : function(r) {
        console.log(r);
      }
    });
  ```

SocketIO events Documentation
----
Check SSH namespace
----

### Import SSH

Import SSH list, saved to server file.

* **Namespace:** /check-ssh or /connect-ssh

* **Event name:** `ssh`
  
*  **Params**

   `ssh: SSH list`
   Example: `[{"ip": "14.160.52.26", "username": "admin", "password": "admin"}]`
 
 * **Usage**

	If `ssh` is present, SSH list will be set to `ssh`, otherwise this event will be ommitted.

### Check SSH

Start checking SSH, generating live & die SSH lists.

* **Namespace:** /check-ssh

* **Event name:** `check_ssh`
  
*  **Params:** None

### Clear live/die

Clear previously generated live/die SSH list.

* **Namespace:** /check-ssh

* **Event name:** `clear_live`/`clear_die`
  
*  **Params:** None

Connect SSH namespace
----

### Connect SSH

Perform port forwarding to specified ports, with auto reconnecting when needed.

* **Namespace:** /connect-ssh

* **Event name:** `connect_ssh`
  
*  **Params**

   `port_list: port list`
   Example: `[8000, 8005]`

### Out of SSH

Returns if SSH list is used up or not.

* **Namespace:** /connect-ssh

* **Event name:** `out_of_ssh`
  
*  **Params:** None
  
*  **Returns**

   `1` if SSH is used up, or the SSH connection hasn't started. `0` if everything is fine. 

### Reset port

Reset port forwarding to specified port, reconnecting to a new one if possible.

* **Namespace:** /connect-ssh

* **Event name:** `reset_port`
  
*  **Params:** None

### Disconnect all ports

Stop all port forwarding to all ports.

* **Namespace:** /connect-ssh

* **Event name:** `disconnect_all_ssh`
  
*  **Params:** None

> Written with [StackEdit](https://stackedit.io/).
