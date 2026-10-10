import ipaddress

def cidr_contains(cidr, ip):
    net = ipaddress.ip_network(cidr, strict=False)
    addr = ipaddress.ip_address(ip)
    if net.version != 4 or addr.version != 4:
        raise ValueError("ipv4 only")
    return addr in net
