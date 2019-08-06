import socket
import ipaddress

dr_subnet = '10.72.30.0/24'
def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('vmc.vmware.com', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

host_ip = get_ip()
print(host_ip)

host_address = ipaddress.ip_address(host_ip)
dr_network = ipaddress.ip_network(dr_subnet)

print(dr_network)

if host_address in dr_network: 
    print("we in the cloud")
else: 
    print('we on the ground')