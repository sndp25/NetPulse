import socket
import argparse
import threading
import os
from tabulate import tabulate

def ping_host(ip):
    response = os.system("ping -c 1 -W 1 " + ip + " > /dev/null 2>&1")
    return response == 0

def scan_port(ip, port, results):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    result = sock.connect_ex((ip, port))
    if result == 0:
        try:
            service = socket.getservbyport(port)
        except socket.error:
            service = "unknown"
        results.append((ip, port, service))
    sock.close()

def scan_ip(ip, all_ports, results):
    if ping_host(ip):
        if all_ports:
            ports_to_scan = range(1, 65536)
        else:
            ports_to_scan = range(1, 1001)

        print(f"Scanning IP address {ip}...")
        threads = []
        for port in ports_to_scan:
            thread = threading.Thread(target=scan_port, args=(ip, port, results))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()

def scan_subnet(subnet, all_ports, results):
    ip_prefix = '.'.join(subnet.split('.')[:-1])

    if all_ports:
        ports_to_scan = range(1, 65536)
    else:
        ports_to_scan = range(1, 1001)
    
    print(f"Scanning subnet {subnet} for open ports...")
    threads = []
    for i in range(1, 255):
        ip = f"{ip_prefix}.{i}"
        if ping_host(ip):
            print(f"Host {ip} is reachable.")
            for port in ports_to_scan:
                thread = threading.Thread(target=scan_port, args=(ip, port, results))
                threads.append(thread)
                thread.start()
    
    for thread in threads:
        thread.join()

def main():
    parser = argparse.ArgumentParser(description="Simple Port Scanner with Ping and Timeout")
    parser.add_argument("target", help="IP address or subnet to scan")
    parser.add_argument("--all-ports", action="store_true", help="Scan all 65,535 ports")
    args = parser.parse_args()

    target = args.target
    all_ports = args.all_ports

    results = []

    if '/' in target:
        scan_subnet(target, all_ports, results)
    else:
        scan_ip(target, all_ports, results)

    if results:
        headers = ["IP Address", "Port", "Service"]
        print(tabulate(results, headers=headers, tablefmt="grid"))
    else:
        print("No open ports found.")

if __name__ == "__main__":
    main()
