from zabbix_api import ZabbixAPI, ZabbixAPIException


def get_hostname_detail(hostname):
    """
    Output:
    [{'hostid': '10568', 'proxy_hostid': '0', 'host': 'localhost.localdomain',
      'status': '0', 'ipmi_authtype': '-1', 'ipmi_privilege': '2', 'ipmi_username': '', 
      'ipmi_password': '', 'maintenanceid': '0', 'maintenance_status': '0', 'maintenance_type': '0', 
      'maintenance_from': '0', 'name': 'localhost.localdomain', 'flags': '0', 'templateid': '0', 
      'description': '', 'tls_connect': '1', 'tls_accept': '1', 'tls_issuer': '', 'tls_subject': '', 
      'proxy_address': '', 'auto_compress': '1', 'custom_interfaces': '0', 'uuid': '', 'vendor_name': '', 
      'vendor_version': '', 'inventory_mode': '1', 'active_available': '1'}]
    """

    host_details = zapi.host.get({'filter': {'host': hostname}})
    if len(host_details) > 0:
        return host_details[0]['hostid']
    else:
        return None


if __name__ == '__main__':
    """
    Entry Point
    """
    zapi = ZabbixAPI(server="http://localhost/")
    zapi.login("Admin", "zabbix")
    host_id = get_hostname_detail('localhost.localdomain')
    print(host_id)
