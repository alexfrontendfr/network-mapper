import pytest
from backend.device_identifier import DeviceIdentifier

def test_device_identifier():
    identifier = DeviceIdentifier()
    
    test_cases = [
        ({'vendor': 'Apple Inc.'}, 'Apple Device'),
        ({'vendor': 'Samsung Electronics'}, 'Android Device'),
        ({'vendor': 'Unknown'}, 'Unknown Device')
    ]
    
    for test_input, expected in test_cases:
        assert identifier.identify_device(test_input) == expected