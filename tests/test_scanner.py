import pytest
from backend.network_scanner import NetworkScanner

def test_network_scanner():
    scanner = NetworkScanner('192.168.1.0/24')
    devices = scanner.scan_network()
    
    assert isinstance(devices, list)
    for device in devices:
        assert 'ip' in device
        assert 'mac' in device
        assert 'status' in device