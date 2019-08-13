DISCLAIMER. THIS PROGRAM IS PROVIDED TO YOU "AS IS" WITHOUT 
WARRANTIES OR CONDITIONS OF ANY KIND, WHETHER ORAL OR WRITTEN,
EXPRESS OR IMPLIED. THE AUTHOR SPECIFICALLY DISCLAIMS ANY IMPLIED
WARRANTIES OR CONDITIONS OF MERCHANTABILITY, SATISFACTORY QUALITY,
NON-INFRINGEMENT AND FITNESS FOR A PARTICULAR PURPOSE.

# VSR_Autoscaler.py
Example implementation of the VMware Cloud on AWS API, which integrates SDDC scale-up into VSR failover.  Sample uses local IP information to detect locality.  When it detects that it is running in the designated DR Subnet it checks the SDDC size triggering a scale-up if required. 

## Requires
VMware Python SDK

## Setup from PhotonOS
1. tdnf install docker, python3, git
1. tdnf install python3-pip
1. pip3 install --upgrade pip
1. pip3 install --upgrade requests
1. pip3 install --upgrade git+https://github.com/vmware/vsphere-automation-sdk-python.git
1. mkdir /app && cd /app
1. git clone git@github.com:glnsize/vsr_autoscaller.git .

## Run one time
1. `python3 /app/vsr_autoscaller.py --refresh-token '11670dd3-ba77-48e8-8086-b33e58b0e0cc' --org-id '194734cc-fbc1-4b72-9090-2523d8522148' --sddc-id 'abd3761a-8730-400a-95cb-f86820169f7c' --cluster-name 'Cluster-1' --cluster-size 5 -dr-network '10.72.30.0/24'`

## Setup to run with secured APIKEY
1. create secretes file to secure api key.
`echo '11670dd3-ba77-48e8-8086-b33e58b0e0cc' > /app/refresh.token
chmod u=r /app/refresh.token`
2. Run cmd
`python3 /app/vsr_autoscaller.py --refresh-token $(cat /app/refresh.token) --org-id '194734cc-fbc1-4b72-9090-2523d8522148' --sddc-id 'abd3761a-8730-400a-95cb-f86820169f7c' --cluster-name 'Cluster-1' --cluster-size 5 -dr-network '10.72.30.0/24'`
 
 



