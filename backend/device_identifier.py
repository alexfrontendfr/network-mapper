from typing import Dict, List, Tuple
import re
import socket

class DeviceIdentifier:
    def __init__(self):
        self.vendor_patterns = {
            r'Apple|iPhone|iPad|Mac|AirPort|iMac|MacBook': 'Apple Device',
            r'Android|Samsung|Huawei|Xiaomi|OPPO|OnePlus|Realme|Vivo|Galaxy': 'Android Device',
            r'Intel|Dell|HP|Lenovo|ASUS|Acer|MSI|Gigabyte|ASRock': 'Computer',
            r'Cisco|Juniper|NETGEAR|D-Link|TP-Link|ASUS|Ubiquiti|Linksys|Belkin|Mikrotik|UniFi|EdgeRouter': 'Network Equipment',
            r'Raspberry|RPi|Pi Foundation': 'Raspberry Pi',
            r'ESP|Arduino|Particle|NodeMCU|Teensy': 'IoT Device',
            r'Microsoft|Xbox|Surface|Windows': 'Windows Device',
            r'Sony|PlayStation|PS\d': 'Gaming Console',
            r'Amazon|Kindle|Echo|Ring|Alexa': 'Smart Home Device',
            r'Google|Nest|Chromecast|Home': 'Smart Home Device',
            r'Canon|Epson|Brother|HP|Xerox': 'Printer',
            r'Roku|FireTV|Apple TV|Shield|Mi Box': 'Media Device',
            r'Ring|Arlo|Nest Cam|Wyze|Hikvision|Dahua': 'Security Camera',
            r'VMware|VirtualBox|Hyper-V': 'Virtual Machine',
            r'Sonos|Bose|Denon|Yamaha|Pioneer': 'Audio Device',
            r'NAS|Synology|QNAP|Western Digital|Seagate': 'Storage Device'
        }
        
        self.port_signatures = [
            ((80, 443), 'Web Server'),
            ((22,), 'SSH Server'),
            ((21,), 'FTP Server'),
            ((53,), 'DNS Server'),
            ((3389,), 'Windows Device'),
            ((445, 139), 'Windows Device'),
            ((8080,), 'Web Server'),
            ((25, 587), 'Mail Server'),
            ((123,), 'Time Server'),
            ((161,), 'SNMP Device'),
            ((548, 5009), 'Apple Device'),
            ((1714, 1764), 'Audio Device'),
            ((8009,), 'Chromecast'),
            ((32400,), 'Plex Server'),
            ((5353,), 'mDNS Device'),
            ((1900,), 'UPNP Device'),
            ((2869,), 'UPNP Device'),
            ((5357,), 'Windows Network Device'),
            ((62078,), 'Apple Device'),
            ((8200,), 'GoToMeeting'),
            ((3478,), 'STUN Server'),
            ((1701,), 'L2TP VPN'),
            ((1194,), 'OpenVPN'),
            ((500,), 'IPsec VPN'),
            ((1723,), 'PPTP VPN'),
            ((1883,), 'MQTT Broker'),
            ((8883,), 'MQTT SSL Broker'),
            ((5938,), 'TeamViewer'),
            ((3283,), 'Apple Remote Desktop'),
            ((548,), 'AFP Server')
        ]

    def _check_hostname_patterns(self, hostname: str) -> str:
        """Identify device type based on hostname patterns"""
        hostname = hostname.lower()
        patterns = {
            r'printer|print': 'Printer',
            r'camera|cam|ipcam': 'Security Camera',
            r'xbox': 'Gaming Console',
            r'playstation|ps\d': 'Gaming Console',
            r'android|phone': 'Mobile Device',
            r'ipad|iphone|macbook|imac': 'Apple Device',
            r'desktop|laptop': 'Computer',
            r'nas|storage': 'Storage Device',
            r'router|gateway|ap|access-point': 'Network Equipment',
            r'switch|managed': 'Network Equipment',
            r'raspberry|pi': 'Raspberry Pi',
            r'chromebook': 'Computer',
            r'virtual|vm': 'Virtual Machine'
        }
        
        for pattern, device_type in patterns.items():
            if re.search(pattern, hostname):
                return device_type
        return None

    def _check_ports(self, ports: List[int]) -> str:
        """Identify device type based on open ports"""
        if not ports:
            return None
            
        ports_set = set(ports)
        for signature_ports, device_type in self.port_signatures:
            if all(port in ports_set for port in signature_ports):
                return device_type
        return None

    def _analyze_mac_prefix(self, mac: str) -> str:
        """Analyze MAC address prefix for virtual machines and special devices"""
        if not mac:
            return None
            
        mac = mac.lower()
        if mac.startswith(('00:00:00', 'ff:ff:ff')):
            return 'Virtual Interface'
        if mac.startswith('01:00:5e'):
            return 'Multicast Device'
            
        vm_prefixes = ['00:05:69', '00:0c:29', '00:1c:14', '00:50:56', '00:1c:42']
        if any(mac.startswith(prefix) for prefix in vm_prefixes):
            return 'Virtual Machine'
            
        return None

    def identify_device(self, device_info: Dict) -> str:
        """Identify device type using multiple methods"""
        ip = device_info.get('ip', '')
        mac = device_info.get('mac', '').lower()
        vendor = device_info.get('vendor', '').lower()
        ports = device_info.get('ports', [])
        hostname = device_info.get('hostname', '').lower()
        
        # Special handling for router detection
        if (ip.endswith('.1') or ip.endswith('.254')) and any(port in ports for port in [53, 80, 443]):
            return 'Router'
        
        # Check hostname first
        hostname_type = self._check_hostname_patterns(hostname)
        if hostname_type:
            return hostname_type
        
        # Vendor-based identification
        for pattern, device_type in self.vendor_patterns.items():
            if re.search(pattern.lower(), vendor):
                return device_type
        
        # Port-based identification
        port_type = self._check_ports(ports)
        if port_type:
            return port_type
            
        # MAC address pattern matching
        mac_type = self._analyze_mac_prefix(mac)
        if mac_type:
            return mac_type
            
        # Additional heuristics
        if ports:
            if 80 in ports or 443 in ports:
                return 'Web Server'
            if 22 in ports:
                return 'Network Device'
            if set([139, 445]).intersection(ports):
                return 'Windows Device'
            
        # If device has many open ports, likely a server
        if len(ports) > 5:
            return 'Server'
            
        return 'Unknown Device'