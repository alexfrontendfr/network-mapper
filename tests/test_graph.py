import pytest
from backend.graph_generator import NetworkGraphGenerator
import matplotlib.pyplot as plt
import io

@pytest.fixture
def graph_generator():
    return NetworkGraphGenerator()

@pytest.fixture
def sample_devices():
    return [
        {
            'ip': '192.168.1.1',
            'mac': '00:11:22:33:44:55',
            'vendor': 'Test Router',
            'type': 'router'
        },
        {
            'ip': '192.168.1.2',
            'mac': '00:11:22:33:44:66',
            'vendor': 'Test PC',
            'type': 'computer'
        },
        {
            'ip': '192.168.1.3',
            'mac': '00:11:22:33:44:77',
            'vendor': 'Test Phone',
            'type': 'mobile'
        }
    ]

def test_create_graph(graph_generator, sample_devices):
    # Generate graph
    graph_bytes = graph_generator.create_graph(sample_devices)
    
    # Check if output is bytes
    assert isinstance(graph_bytes, bytes)
    
    # Check if bytes contain valid image data
    try:
        plt.imread(io.BytesIO(graph_bytes))
    except Exception as e:
        pytest.fail(f"Failed to read generated graph image: {e}")

def test_empty_devices(graph_generator):
    # Test with empty device list
    graph_bytes = graph_generator.create_graph([])
    assert isinstance(graph_bytes, bytes)

def test_single_device(graph_generator):
    # Test with single device
    devices = [{
        'ip': '192.168.1.1',
        'mac': '00:11:22:33:44:55',
        'vendor': 'Test Device',
        'type': 'computer'
    }]
    graph_bytes = graph_generator.create_graph(devices)
    assert isinstance(graph_bytes, bytes)

def test_graph_properties(graph_generator, sample_devices):
    # Create graph and verify basic properties
    graph_generator.create_graph(sample_devices)
    
    # Check if graph has correct number of nodes
    assert len(graph_generator.G.nodes) == len(sample_devices) + 1  # +1 for router
    
    # Check if all devices are connected to router
    router_connections = list(graph_generator.G.edges('Router'))
    assert len(router_connections) == len(sample_devices)