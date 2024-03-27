import io
from flask import Flask, render_template, request, send_file
from network_simulation import *
import matplotlib.pyplot as plt
import networkx as nx

app = Flask(__name__)

# Function to generate and save the network diagram
def generate_network_diagram(devices, hub, topology_name):
    G = nx.Graph()

    # Add devices to the graph
    for device in devices:
        G.add_node(device.name)

    # Add connections between devices and hub
    for device in devices:
        G.add_edge(hub.name, device.name)

    # Generate the network diagram
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, node_size=700, node_color='lightblue', font_size=10, font_weight='bold')
    plt.title(f"Network Topology: {topology_name}")
    plt.tight_layout()

    # Save the diagram to a BytesIO object
    img_bytes = io.BytesIO()
    plt.savefig(img_bytes, format='png')
    img_bytes.seek(0)
    plt.close()

    return img_bytes

# Function to create a star topology with one hub at the center
def create_star_topology(devices, hub_name):
    hub = Hub(hub_name)
    for device in devices:
        hub.connect_device(device)
    return hub

# Function to create a point-to-point topology
def create_point_to_point_topology(devices):
    # Connect devices in a line (point-to-point)
    for i in range(len(devices) - 1):
        devices[i].connect_to(devices[i+1])



@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        num_devices = int(request.form['num_devices'])
        devices = []
        for i in range(num_devices):
            name = request.form[f'name{i+1}']
            device_type = request.form[f'type{i+1}']
            if device_type == 'EndDevice':
                devices.append(EndDevice(name))
            elif device_type == 'Hub':
                devices.append(Hub(name))

        topology_choice = int(request.form['topology_choice'])
        topology_name = request.form['topology_name']
        hub = None  # Initialize hub variable

        if topology_choice == 1:
            hub = create_star_topology(devices, topology_name)
        elif topology_choice == 2:
            create_point_to_point_topology(devices)
            hub = devices[0]  # Set the hub to the first device in point-to-point topology
        elif topology_choice == 3:
            hub = create_bus_topology(devices)
        elif topology_choice == 4:
            create_ring_topology(devices)
        elif topology_choice == 5:
            create_mesh_topology(devices)

        if hub:
            # Generate and save the network diagram
            diagram_bytes = generate_network_diagram(devices, hub, hub.name)
            # Send the diagram file as a response
            return send_file(diagram_bytes, mimetype='image/png')

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
