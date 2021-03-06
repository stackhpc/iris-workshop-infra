#!/usr/bin/env python
#
# Copyright (c) 2018 StackHPC Ltd.
# Apache 2 Licence

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: os_server_interface
short_description: Create, update and delete server interface.
author: bharat@stackhpc.com
version_added: "1.0"
description:
    -  Create, update and delete server interface using Openstack Nova API.
notes:
    - This module returns C(network_interface) fact, which
      contains information about server network interfaces.
requirements:
    - "python >= 2.6"
    - "openstacksdk"
    - "python-novaclient"
options:
   cloud:
     description:
       - Cloud name inside cloud.yaml file.
     type: str
   state:
     description:
       - Must be `present` or `absent`.
     type: str
   server_id:
     description:
        - Server name or uuid.
     type: str
   interfaces:
     description:
        - List of network interface names.
     type: list of str
   security_groups:
     description:
        - List of security group names.
     type: list of str
extends_documentation_fragment: openstack
'''

EXAMPLES = '''
# Attach interfaces to <server_id>:
- os_server_interface:
    cloud: mycloud
    state: present
    server_id: xxxxx-xxxxx-xxxx-xxxx
    interfaces:
    - p3-lln
    - p3-bdn
  register: result
- debug:
    var: result
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.openstack import (
    openstack_cloud_from_module, openstack_full_argument_spec)
from novaclient.client import Client
from novaclient.exceptions import NotFound
import openstack.exceptions
import time

class OpenStackAuthConfig(Exception):
    pass

class ServerInterface(object):
    def __init__(self, sdk, cloud, **kwargs):
        self.sdk = sdk
        self.cloud = cloud
        self.server_id = kwargs['server_id']
        self.state = kwargs['state']

        self.client = Client('2', session=self.cloud.session)
        self.interfaces = []
        for interface in kwargs['interfaces']:
            network = self.cloud.network.find_network(interface)
            if not network:
                raise Exception("Unable to find network '%s'" % interface)
            self.interfaces.append(network)
        self.security_groups = []
        for sg in kwargs['security_groups']:
            sg = cloud.get_security_group(sg)
            self.security_groups.append(sg.id)

    def get_server(self):
        try:
            server = self.client.servers.find(id=self.server_id)
        except NotFound:
            server = self.client.servers.find(name=self.server_id)
        return server

    def apply(self):
        changed = False
        server = self.get_server()
        attached_interfaces = server.interface_list()
        for interface in self.interfaces:
            interface_exists = False
            for attached_interface in attached_interfaces:
                if interface.id == attached_interface.net_id:
                    if self.state == 'absent':
                        server.interface_detach(port_id=attached_interface.port_id)
                        try:
                            self.cloud.delete_port(attached_interface.port_id)
                        except openstack.exceptions.NotFoundException:
                            pass
                        changed = True
                    elif self.state == 'present':
                        interface_exists = True
            if interface_exists == False and self.state == 'present':
                kwargs = {}
                if self.security_groups:
                    kwargs['security_groups'] = self.security_groups
                port = self.cloud.create_port(interface.id, **kwargs)
                try:
                    server.interface_attach(port_id=port.id, net_id=None, fixed_ip=None)
                except:
                    cloud.delete_port(port.id)
                    raise
                changed = True
        if changed:
            self.server = self.get_server()
        else:
            self.server = server
        return changed


def main():
    argument_spec = openstack_full_argument_spec(
        state=dict(default='present', choices=['present', 'absent']),
        server_id=dict(required=True, type='str'),
        interfaces=dict(default=[], type='list'),
        security_groups=dict(default=[], type='list'),
    )
    module = AnsibleModule(argument_spec, supports_check_mode=False)
    sdk, cloud = openstack_cloud_from_module(module)

    try:
        server_interface = ServerInterface(sdk, cloud, **module.params)
        changed = server_interface.apply()
    except Exception as e:
        module.fail_json(msg=repr(e))

    server = server_interface.server

    module.exit_json(
        changed=changed,
        server_name=server.name,
        server_networks=server.networks,
    )


if __name__ == '__main__':
    main()
