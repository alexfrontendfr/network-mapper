from flask import Flask, jsonify, send_file, make_response
from flask_cors import CORS
from flask_socketio import SocketIO
import io
from network_scanner import NetworkScanner
from device_identifier import DeviceIdentifier
from graph_generator import NetworkGraphGenerator
import traceback
import threading
import queue
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*")

# Queue for scan results
scan_queue = queue.Queue()
last_scan_results = []  # Cache for last scan results

# Initialize components with error handling
try:
    scanner = NetworkScanner()  # Let it auto-detect network range
    identifier = DeviceIdentifier()
    graph_gen = NetworkGraphGenerator()
except Exception as e:
    print(f"Initialization error: {str(e)}")
    traceback.print_exc()
    raise

def background_scan():
    """Perform network scan in background"""
    global last_scan_results
    try:
        devices = scanner.scan_network()
        if devices:
            for device in devices:
                device['type'] = identifier.identify_device(device)
            last_scan_results = devices
        scan_queue.put(devices)
    except Exception as e:
        scan_queue.put({'error': str(e)})

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

@app.route('/api/scan', methods=['GET'])
def scan_network():
    try:
        # Start background scan
        scan_thread = threading.Thread(target=background_scan)
        scan_thread.start()
        
        # Wait for results with timeout
        try:
            result = scan_queue.get(timeout=45)  # Extended timeout
            if isinstance(result, dict) and 'error' in result:
                return jsonify({'error': result['error']}), 500
            if result:
                return jsonify(result)
            return jsonify({'error': 'No devices found'}), 404
        except queue.Empty:
            return jsonify({'error': 'Scan timeout'}), 504
            
    except Exception as e:
        print(f"Scan error: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/graph', methods=['GET'])
def get_graph():
    try:
        devices = last_scan_results if last_scan_results else scanner.scan_network()
        if not devices:
            return jsonify({'error': 'No devices found'}), 404
            
        for device in devices:
            if 'type' not in device:
                device['type'] = identifier.identify_device(device)
            
        graph_image = graph_gen.create_graph(devices)
        response = make_response(send_file(
            io.BytesIO(graph_image),
            mimetype='image/png',
            download_name='network_map.png'
        ))
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    except Exception as e:
        print(f"Graph error: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000, host='0.0.0.0')