from scapy.all import ARP, Ether, srp, conf, get_if_addr, get_if_list, ICMP, IP, sr1
import nmap
import os
import sys
from typing import List, Dict, Set
import socket
import ipaddress
import subprocess
import platform
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import netifaces
import psutil

class NetworkScanner:
    def __init__(self, network_range: str = None):
        """Initialize scanner with optional network range"""
        self.clear_arp_cache()  # Clear ARP cache on start
        if network_range is None:
            self.network_ranges = self._get_all_network_ranges()
        else:
            self.network_ranges = [network_range]

        print(f"Detected network ranges: {self.network_ranges}")
        
        try:
            self.nm = nmap.PortScanner()
        except nmap.PortScannerError:
            self._setup_nmap()

    def clear_arp_cache(self):
        """Clear ARP cache to ensure fresh results"""
        try:
            if platform.system() == "Windows":
                subprocess.run(["arp", "-d", "*"], capture_output=True)
            else:
                subprocess.run(["ip", "neigh", "flush", "all"], capture_output=True)
        except Exception as e:
            print(f"Failed to clear ARP cache: {e}")

    def _get_active_interfaces(self) -> List[Dict]:
        """Get all active network interfaces"""
        active_interfaces = []
        
        def is_valid_ip(ip):
            try:
                return not (ip.startswith('127.') or ip.startswith('169.254.') or ip.startswith('0.'))
            except:
                return False

        # Get all network interfaces using psutil
        net_if_stats = psutil.net_if_stats()
        net_if_addrs = psutil.net_if_addrs()

        for interface, stats in net_if_stats.items():
            # Skip interfaces that are down or loopback
            if not stats.isup:
                continue

            addrs = net_if_addrs.get(interface, [])
            for addr in addrs:
                if addr.family == socket.AF_INET and is_valid_ip(addr.address):
                    active_interfaces.append({
                        'name': interface,
                        'ip': addr.address,
                        'netmask': addr.netmask
                    })
                    break  # Only take first valid IPv4 address

        return active_interfaces

    def _get_all_network_ranges(self) -> List[str]:
        """Get all possible network ranges from all interfaces"""
        network_ranges = set()

        # Get active interfaces
        interfaces = self._get_active_interfaces()
        for interface in interfaces:
            try:
                ip = interface['ip']
                netmask = interface['netmask']
                if ip and netmask and not ip.startswith('127.'):
                    network = ipaddress.IPv4Network(f'{ip}/{netmask}', strict=False)
                    network_ranges.add(str(network))
                    print(f"Found network range on {interface['name']}: {network}")
            except Exception as e:
                print(f"Error processing interface {interface['name']}: {e}")

        # If no ranges found, try alternative methods
        if not network_ranges:
            try:
                # Try getting default gateway
                if platform.system() == "Windows":
                    output = subprocess.check_output("ipconfig", universal_newlines=True)
                    for line in output.split('\n'):
                        if "Default Gateway" in line:
                            gateway = line.split(": ")[-1].strip()
                            if gateway and gateway != "":
                                network = ipaddress.IPv4Network(f'{gateway}/24', strict=False)
                                network_ranges.add(str(network))
                else:
                    output = subprocess.check_output(["ip", "route", "show", "default"], universal_newlines=True)
                    if output:
                        gateway = output.split()[2]
                        network = ipaddress.IPv4Network(f'{gateway}/24', strict=False)
                        network_ranges.add(str(network))
            except Exception as e:
                print(f"Error getting default gateway: {e}")

        # If still no ranges found, add common private networks
        if not network_ranges:
            network_ranges.update([
                "192.168.1.0/24",
                "192.168.0.0/24",
                "10.0.0.0/24",
                "172.16.0.0/24"
            ])

        return list(network_ranges)

    def _scan_ip_range_arp(self, ip_range: str) -> Set[str]:
        """Perform ARP scan on IP range"""
        active_ips = set()
        try:
            # Create ARP request packet
            arp = ARP(pdst=ip_range)
            ether = Ether(dst="ff:ff:ff:ff:ff:ff")
            packet = ether/arp

            # Send packet and get response
            ans, _ = srp(packet, timeout=3, retry=2, verbose=0)
            
            # Process responses
            for sent, received in ans:
                active_ips.add(received.psrc)
                print(f"Found device via ARP: {received.psrc} - {received.hwsrc}")

        except Exception as e:
            print(f"ARP scan error for {ip_range}: {str(e)}")
        
        return active_ips

    def _scan_ip(self, ip: str) -> Dict:
        """Scan a single IP address"""
        try:
            result = {
                'ip': ip,
                'mac': '',
                'vendor': 'Unknown',
                'status': 'active',
                'ports': [],
                'hostname': ''
            }

            # First try simple TCP connection to common ports
            common_ports = [80, 443, 22, 445]
            open_ports = []
            for port in common_ports:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(1)
                    if sock.connect_ex((ip, port)) == 0:
                        open_ports.append(port)
                    sock.close()
                except:
                    continue

            if open_ports:
                result['ports'] = open_ports

            # Try to get hostname
            try:
                hostname = socket.gethostbyaddr(ip)[0]
                result['hostname'] = hostname
            except:
                pass

            # Use nmap for more detailed scan
            try:
                self.nm.scan(ip, arguments='-sn -sP -T4')
                if ip in self.nm.all_hosts():
                    host = self.nm[ip]
                    if 'addresses' in host:
                        addrs = host['addresses']
                        if 'mac' in addrs:
                            result['mac'] = addrs['mac']
                            if 'vendor' in host and addrs['mac'] in host['vendor']:
                                result['vendor'] = host['vendor'][addrs['mac']]

                # Additional port scan if initial connection was successful
                if open_ports:
                    self.nm.scan(ip, arguments='-sS -p 20-1024 -T4 --host-timeout 10')
                    if ip in self.nm.all_hosts() and 'tcp' in self.nm[ip]:
                        result['ports'].extend([
                            port for port, data in self.nm[ip]['tcp'].items()
                            if data['state'] == 'open' and port not in result['ports']
                        ])
            except Exception as e:
                print(f"Nmap scan error for {ip}: {e}")

            return result if (result['mac'] or result['ports']) else None

        except Exception as e:
            print(f"Error scanning {ip}: {str(e)}")
            return None

    def scan_network(self) -> List[Dict]:
        """Scan network using multiple methods"""
        all_devices = []
        
        try:
            for network_range in self.network_ranges:
                print(f"\nScanning range: {network_range}")
                active_ips = set()
                
                # ARP scan for initial device discovery
                arp_ips = self._scan_ip_range_arp(network_range)
                active_ips.update(arp_ips)
                print(f"ARP scan found {len(arp_ips)} devices")

                # Scan discovered IPs in parallel
                with ThreadPoolExecutor(max_workers=10) as executor:
                    future_to_ip = {executor.submit(self._scan_ip, ip): ip for ip in active_ips}
                    for future in as_completed(future_to_ip):
                        try:
                            result = future.result()
                            if result:
                                all_devices.append(result)
                                print(f"Added device: {result['ip']} ({result.get('vendor', 'Unknown')})")
                        except Exception as e:
                            print(f"Error processing scan result: {str(e)}")

            print(f"\nTotal devices found: {len(all_devices)}")
            return all_devices

        except Exception as e:
            print(f"Scan error: {str(e)}")
            traceback.print_exc()
            return []