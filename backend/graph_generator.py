import networkx as nx
import matplotlib.pyplot as plt
from typing import List, Dict
import io
import threading

class NetworkGraphGenerator:
    def __init__(self):
        self.G = nx.Graph()
        self.colors = {
            'Router': '#FF6B6B',
            'Computer': '#4ECDC4',
            'Network Equipment': '#45B7D1',
            'Apple Device': '#96CEB4',
            'Android Device': '#A8E6CF',
            'IoT Device': '#FFD93D',
            'Unknown Device': '#6C757D',
            'Printer': '#FF9F1C',
            'Media Device': '#2196F3',
            'Security Camera': '#9C27B0',
            'Windows Device': '#00BCD4',
            'Smart Home Device': '#FF9800',
            'Virtual Machine': '#9C27B0',
            'Server': '#F44336',
            'Gaming Console': '#E91E63'
        }
        
    def create_graph(self, devices: List[Dict]) -> bytes:
        """Generate network graph visualization"""
        # Create a new figure to ensure clean state
        plt.close('all')
        fig = plt.figure(figsize=(15, 10))
        
        # Clear the graph
        self.G.clear()
        
        try:
            # Add router node (assumed to be first device or device ending in .1)
            router_found = False
            for device in devices:
                if device['type'] == 'Router' or device['ip'].endswith('.1'):
                    self.G.add_node(device['ip'], 
                                  type='Router',
                                  label=f"Router\n{device['ip']}\n{device.get('vendor', 'Unknown')}")
                    router_found = True
                    break
                    
            if not router_found and devices:
                self.G.add_node(devices[0]['ip'], 
                              type='Router',
                              label=f"Router\n{devices[0]['ip']}\n{devices[0].get('vendor', 'Unknown')}")
            
            # Add other devices
            for device in devices:
                if device['type'] != 'Router' and not device['ip'].endswith('.1'):
                    label = f"{device['type']}\n{device['ip']}"
                    if device.get('vendor') and device['vendor'] != 'Unknown':
                        label += f"\n{device['vendor']}"
                    if device.get('hostname'):
                        label += f"\n{device['hostname']}"
                    self.G.add_node(device['ip'], 
                                  type=device['type'],
                                  label=label)
                    # Connect to router
                    try:
                        router_node = next(n for n in self.G.nodes if self.G.nodes[n]['type'] == 'Router')
                        self.G.add_edge(router_node, device['ip'])
                    except StopIteration:
                        # If no router found, connect to first device
                        if len(self.G.nodes) > 0:
                            first_node = list(self.G.nodes)[0]
                            self.G.add_edge(first_node, device['ip'])
            
            # Create layout
            pos = nx.spring_layout(self.G, k=1, iterations=50)
            
            # Draw nodes for each device type
            for device_type, color in self.colors.items():
                node_list = [n for n in self.G.nodes if self.G.nodes[n]['type'] == device_type]
                if node_list:
                    nx.draw_networkx_nodes(self.G, pos,
                                         nodelist=node_list,
                                         node_color=color,
                                         node_size=3000,
                                         alpha=0.7)
            
            # Draw edges
            nx.draw_networkx_edges(self.G, pos, 
                                 edge_color='#2f3640',
                                 width=2,
                                 alpha=0.5)
            
            # Add labels
            labels = nx.get_node_attributes(self.G, 'label')
            nx.draw_networkx_labels(self.G, pos,
                                  labels,
                                  font_size=8,
                                  font_weight='bold')
            
            plt.title("Network Device Map", fontsize=16, pad=20)
            
            # Add legend
            legend_elements = []
            for device_type, color in self.colors.items():
                if any(self.G.nodes[n]['type'] == device_type for n in self.G.nodes):
                    legend_elements.append(plt.Line2D([0], [0], marker='o', color='w', 
                                        markerfacecolor=color, 
                                        markersize=10, 
                                        label=device_type))
            
            if legend_elements:
                plt.legend(handles=legend_elements, 
                          loc='center left',
                          bbox_to_anchor=(1, 0.5))
            
            plt.tight_layout()
            
            # Save to bytes buffer
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight', dpi=300)
            plt.close(fig)
            
            return buf.getvalue()

        except Exception as e:
            print(f"Error generating graph: {str(e)}")
            plt.close(fig)
            raise