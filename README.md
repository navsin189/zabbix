# ZABBIX

Zabbix is an enterprise-class open source distributed monitoring solution.

Zabbix is software that monitors numerous parameters of a network and the health and integrity of servers. Zabbix uses a flexible notification mechanism that allows users to configure e-mail based alerts for virtually any event. This allows a fast reaction to server problems. Zabbix offers excellent reporting and data visualisation features based on the stored data. This makes Zabbix ideal for capacity planning.

For more information and related downloads for Zabbix components, please visit https://hub.docker.com/u/zabbix/ and https://zabbix.com

- It is an open source tool.
- [Zabbix Architecture](https://www.zabbix.com/documentation/current/en/manual/introduction/overview)
- Zabbix by default uses a "pull" model when a server connects to agents on each monitoring machine, and agents periodically gather the information and send it to a server. The alternative is "active checks" mode when agents establish a connection with a server and send data to it when it need.
- **Passive and active checks**

  - Zabbix agents can perform passive and active checks.
  - In a passive check the agent responds to a data request. Zabbix server (or proxy) asks for data, for example, CPU load, and Zabbix agent sends back the result.
  - Active checks require more complex processing. The agent must first retrieve a list of items from Zabbix server for independent processing. Then it will periodically send new values to the server.

### Architecture

![Zabbix Architecture](https://static.packt-cdn.com/products/9781785289262/graphics/4239_01_02.jpg)

### SETUP

- Initially I'm going to setup docker containers to have less load and better understanding.
- Zabbix-6.4.2 requires MySQL >= 8 as database. Other RDMS can be used in place of MySQL.
- I'm not setting proxies.

```
sudo docker compose up -d
# wait for some minutes as zabbix database takes time to create
```

**OR**

```
sudo docker run --network zabbix --name zabbix_mysql -e MYSQL_ROOT_PASSWORD=admin -e MYSQL_DATABASE=naveen -e MYSQL_USER=zabbix_admin -e MYSQL_PASSWORD=password -d mysql:8.0

# After the server launched wait for some minutes as the Zabbix database Schema is getting created.
sudo docker run --network zabbix --name zabbix_server_mysql -p 10051:10051 -e DB_SERVER_HOST=zabbix_mysql -e MYSQL_USER=root -e MYSQL_PASSWORD=admin -d zabbix/zabbix-server-mysql:alpine-trunk

sudo docker logs -f zabbix_server_mysql

sudo docker run --network zabbix --name zabbix_web_apache_mysql -p 80:8080 -e DB_SERVER_HOST=zabbix_mysql -e MYSQL_USER=root -e MYSQL_PASSWORD=admin -e ZBX_SERVER_HOST=zabbix_server_mysql -e PHP_TZ="Asia/Kolkata" -d zabbix/zabbix-web-apache-mysql:ubuntu-latest
```

### Zabbix UI

- [QuickStart](https://www.zabbix.com/documentation/current/en/manual/quickstart/login)
- access the UI on port 80
- Enter **Admin** as username and **zabbix** as password.
- The Dashboard will appear after successful login.
- From left panel go to

  - Data Collection then
    - [Hosts](https://www.zabbix.com/documentation/current/en/manual/quickstart/host)
      - Add new host. Remember Hostname should be unique.
      - Add [templates](https://www.zabbix.com/documentation/current/en/manual/quickstart/template) named(as a starter)
        - Linux by Zabbix agent
        - Zabbix server health
      - Add interface and update the IP or DNS of the target machine.
      - other than this go with by default config.

### Zabbix Agent

- [QuickStart](https://www.zabbix.com/documentation/current/en/manual/concepts/agent)
- Download [zabbix agent](https://repo.zabbix.com/zabbix/6.4/) for your OS.
- I install zabbix-agent on my Rocky 9 machine

```
sudo dnf install https://repo.zabbix.com/zabbix/6.4/rhel/9/x86_64/zabbix-agent-6.4.0-release1.el9.x86_64.rpm
```

- Updated `/etc/zabbix/zabbix_agentd.conf`

```
EnableRemoteCommands=1
PidFile=/run/zabbix/zabbix_agentd.pid
LogFile=/var/log/zabbix/zabbix_agentd.log
LogFileSize=0
# this is my zabbix_server_mysql container IP
Server=172.19.0.3
ServerActive=172.19.0.3
# hostname will used to check whether the same host is available on UI or not
Hostname=localhost.localdomain
Include=/etc/zabbix/zabbix_agentd.d/*.conf
```

- By default the agent runs on port 10050 and the mentioned server will try to connect to the agent.
- I did try to change the server to `192.168.1.6` that is my host IP but it didn't work and throws an error
- Because, the server is trying to connect to the agent not the vice versa hence server connects from its own IP(container's IP) not from the proxy I passed.
- server runs on port 10051.

```
4086:20230517:073337.130 failed to accept an incoming connection: connection from "172.19.0.3" rejected, allowed hosts: "192.168.1.6"
```

### API

- [QuickStart](https://www.zabbix.com/documentation/current/en/manual/api)
- Let's convert this curl call into python script.
- **Note -** I'm using password not token.

```
curl --request POST \
         --url 'http://localhost/api_jsonrpc.php' \
         --header 'Content-Type: application/json-rpc' \
         --data '{"jsonrpc":"2.0","method":"user.login","params":{"username":"Admin","password":"zabbix"},"id":1}'

curl --request POST \
         --url 'http://localhost/api_jsonrpc.php' \
         --header 'Content-Type: application/json-rpc' \
         --data '{"jsonrpc":"2.0","method":"host.get","params":{"output":["hostid"]},"auth":"0424bd59b807674191e7d77572075f33","id":1}'
```

- Using Python script to call Zabbix API

```
# https://github.com/erigones/zabbix-api/blob/master/zabbix_api.py
# check line 193 and 259

pip install zabbix-api
```

- zabbix.py (Demo)

```
zapi = ZabbixAPI(server="http://localhost/")
zapi.login("Admin", "zabbix")
detail = zapi.host.get({'filter': {'host': 'localhost.localdomain'}})
print(detail)
```

- output

```
[{'hostid': '10568', 'proxy_hostid': '0', 'host': 'localhost.localdomain', 'status': '0', 'ipmi_authtype': '-1', 'ipmi_privilege': '2', 'ipmi_username': '', 'ipmi_password': '', 'maintenanceid': '0', 'maintenance_status': '0', 'maintenance_type': '0', 'maintenance_from': '0', 'name': 'localhost.localdomain', 'flags': '0', 'templateid': '0', 'description': '', 'tls_connect': '1', 'tls_accept': '1', 'tls_issuer': '', 'tls_subject': '', 'proxy_address': '', 'auto_compress': '1', 'custom_interfaces': '0', 'uuid': '', 'vendor_name': '', 'vendor_version': '', 'inventory_mode': '1', 'active_available': '1'}]
```

- Methods

```
Python 3.9.10 (main, Feb  9 2022, 00:00:00)
[GCC 11.2.1 20220127 (Red Hat 11.2.1-9)] on linux
Type "help", "copyright", "credits" or "license" for more information.

>>> from zabbix_api import ZabbixAPI, ZabbixAPIException
>>> zapi = ZabbixAPI(server="http://localhost/")
>>> dir(zapi)
['__checkauth__', '__class__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattr__', '__getattribute__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__password__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__tokenauth__', '__username__', '__weakref__', '_setuplogging', 'api_version', 'auth', 'debug', 'do_request', 'httppasswd', 'httpuser', 'id', 'json_obj', 'kwargs', 'logged_in', 'logger', 'login', 'logout', 'method', 'params', 'proto', 'r_query', 'recent_query', 'server', 'set_log_level', 'test_login', 'timeout', 'url', 'validate_certs']
```

### How Zabbix API call works?

```
zapi.login(username, password) --> json_obj('user.login', params={'username': user, 'password': password}, auth=False) --> zapi.do_request --> fulfill requests.
```

- Every call gets converted in json object and then passed as argument to do_request.
