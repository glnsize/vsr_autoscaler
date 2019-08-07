#!/usr/bin/env python

"""
* *******************************************************
* Copyright (c) VMware, Inc. 2019. All Rights Reserved.
* SPDX-License-Identifier: MIT
* *******************************************************
*
* DISCLAIMER. THIS PROGRAM IS PROVIDED TO YOU "AS IS" WITHOUT
* WARRANTIES OR CONDITIONS OF ANY KIND, WHETHER ORAL OR WRITTEN,
* EXPRESS OR IMPLIED. THE AUTHOR SPECIFICALLY DISCLAIMS ANY IMPLIED
* WARRANTIES OR CONDITIONS OF MERCHANTABILITY, SATISFACTORY QUALITY,
* NON-INFRINGEMENT AND FITNESS FOR A PARTICULAR PURPOSE.
"""

__author__ = 'VMware, Inc.'

import argparse
import atexit
import requests
import socket
import ipaddress

from com.vmware.vmc.model_client import EsxConfig, ErrorResponse
from com.vmware.vapi.std.errors_client import InvalidRequest
from vmware.vapi.vmc.client import create_vmc_client

class vsr_watcher(object):
    """
    Demostrates how to automate SDDC scale as part of a VSR/SRM failover.

    adapted from add_remove_hosts sample in the phython sdk.  
    """

    def __init__(self):
        self.dr_network = None
        self.sddc_id = None
        self.sddc = None
        self.org_id = None
        self.cluster_name = None
        self.cluster_size = None
        self.vmc_client = None
        self.refresh_token = None
        self.interval_sec = None

    def options(self):
        parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        
        parser.add_argument('-r', '--refresh-token',
                            required=True,
                            help='VMware Cloud API refresh token')

        parser.add_argument('-o', '--org-id',
                            required=True,
                            help='Organization identifier.')

        parser.add_argument('-s', '--sddc-id',
                            required=True,
                            help='Sddc Identifier.')

        parser.add_argument('-c', '--cluster-name',
                            required=True,
                            help='Name of the target cluster.')

        parser.add_argument('-S', '--cluster-size',
                            required=True,
                            help='Desired cluster size.')

        parser.add_argument('-n', '--dr-network',
                            required=True,
                            help='network address of the DR subnet with CIDR example "192.168.5.0/24"')

        parser.add_argument('-i', '--interval-sec',
                            default=60,
                            help='Task pulling interval in sec')

        args = parser.parse_args()

        self.refresh_token = args.refresh_token
        self.org_id = args.org_id
        self.sddc_id = args.sddc_id
        self.cluster_name = args.cluster_name
        self.cluster_size = int(args.cluster_size)
        self.dr_network = args.dr_network
        self.interval_sec = int(args.interval_sec)

    def check_running_in_dr_network(self):
         # return the current ipaddress of the system that is able to reach vmc.vmware.com.
        def get_ip():
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            try:
                s.connect(('vmc.vmware.com', 1))
                IP = s.getsockname()[0]
            except:
                IP = '127.0.0.1'
            finally:
                s.close()
            return IP
        host_ip = get_ip()
        host_address = ipaddress.ip_address(host_ip)
        dr_network = ipaddress.ip_network(self.dr_network)
        if host_address in dr_network: 
            print("we in the cloud")
            return True
        else: 
            print(host_ip)
            print('we on the ground')
            return False

    def setup(self):
        # Login to VMware Cloud on AWS
        session = requests.Session()
        self.vmc_client = create_vmc_client(self.refresh_token, session)
        atexit.register(session.close)

        # Check if the organization exists
        orgs = self.vmc_client.Orgs.list()
        if self.org_id not in [org.id for org in orgs]:
            raise ValueError("Org with ID {} doesn't exist".format(self.org_id))

        # Check if the SDDC exists
        sddcs = self.vmc_client.orgs.Sddcs.list(self.org_id)
        if self.sddc_id not in [sddc.id for sddc in sddcs]:
            raise ValueError("SDDC with ID {} doesn't exist in org {}".
                             format(self.sddc_id, self.org_id))
        self.sddc = self.vmc_client.orgs.Sddcs.get(self.org_id,self.sddc_id)

        # Check if the cluster exists
        if self.cluster_name not in [cluster.cluster_name for cluster in self.sddc.resource_config.clusters]:
            raise ValueError("Specified Cluster {} doesn't exist in SDDC {}".
                             format(self.cluster_name, self.sddc.name))
    
    def fix_cluster_size(self,host_count):
        if self.sddc.sddc_state != self.sddc.SDDC_STATE_READY:
            raise ValueError("Specified Cluster {} in SDDC {} not ready current status {}".
                             format(self.cluster_name, self.sddc.name,self.sddc.sddc_state))
        print('SCALE UP {} in {} SDDC by adding {} hosts'.
            format(self.cluster_name,self.sddc.name,host_count))
        esx_config = EsxConfig(num_hosts=host_count)
        try:
            task = self.vmc_client.orgs.sddcs.Esxs.create(org=self.org_id,
                                                          sddc=self.sddc_id,
                                                          esx_config=esx_config)
        except InvalidRequest as e:
            # Convert InvalidRequest to ErrorResponse to get error message
            error_response = e.data.convert_to(ErrorResponse)
            raise Exception(error_response.error_messages)

        print('Host Add initiated, Task ID: {} Status: {}'.format(task.id,task.status))
        
    
    def get_cluster_size(self):
        for cluster in self.sddc.resource_config.clusters:
            if (cluster.cluster_name == self.cluster_name):
                return len(cluster.esx_host_list)
    
    def check_cluster_size(self,current_cluster_size):
        if self.cluster_size > current_cluster_size:
            return self.cluster_size - current_cluster_size
            


def main():
    monitor = vsr_watcher()
    monitor.options()
    if monitor.check_running_in_dr_network():
        monitor.setup()
        host_count = monitor.check_cluster_size(monitor.get_cluster_size())
        if host_count >= 1:
            monitor.fix_cluster_size(host_count)
        elif host_count >= -1:
            print('we too big scale down...')
            print('... relevant comment found: TODO: Implement scale down')
        
if __name__ == '__main__':
    main()
    

