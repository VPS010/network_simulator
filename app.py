from flask import Flask, render_template, request, redirect, url_for
import matplotlib.pyplot as plt
import networkx as nx
import os

app = Flask(__name__)

class Device:
    def __init__(self, device_id):
        self.device_id = device_id
        self.connected_devices = []
    
    def connect(self, other_device):
        if other_device not in self.connected_devices:
            self.connected_devices.append(other_device)
            other_device.connected_devices.append(self)
            print(f"Devices {self.device_id} and {other_device.device_id} connected.")
    
    def send_data(self, data):
        print(f"Device {self.device_id} sending data: {data}")
        for device in self.connected_devices:
            device.receive_data(data)
    
    def receive_data(self, data):
        print(f"Device {self.device_id} received data: {data}")


class Hub(Device):
    def __init__(self, hub_id):
        super().__init__(hub_id)
    
    def connect_to_hub(self, device):
        self.connect(device)
    
    def broadcast(self, data):
        print(f"Hub {self.device_id} broadcasting data: {data}")
        for device in self.connected_devices:
            device.receive_data(data)
    
    def receive_data(self, data):
        print(f"Hub {self.device_id} received data: {data}")
        self.broadcast(data)


class Switch(Device):  # Switch is also a Device
    def __init__(self, switch_id):
        super().__init__(switch_id)
    
    def connect_to_switch(self, device):
        self.connect(device)

    def send_data(self, data, receiver_id):
        for device in self.connected_devices:
            if device.device_id == receiver_id:
                device.receive_data(data)
                print(f"Switch {self.device_id} forwarded data to {device.device_id}")
                return
        print(f"Receiver device {receiver_id} not connected to switch {self.device_id}")


class Topology:
    def __init__(self):
        self.devices = []
        self.graph = nx.Graph()
    
    def add_device(self, device):
        self.devices.append(device)
        self.graph.add_node(device.device_id)
    
    def create_connection(self, device1, device2):
        device1.connect(device2)
        self.graph.add_edge(device1.device_id, device2.device_id)
    
    def create_star_topology(self, devices, hub):
        self.add_device(hub)
        for device in devices:
            self.add_device(device)
            self.create_connection(device, hub)
    
    def create_bus_topology(self, devices, switches):
        self.add_device(switches[0])  # Connect the first switch to the hub
        self.create_connection(switches[0], devices[0])
        self.add_device(devices[0])
        for i in range(1, len(switches)):
            self.add_device(switches[i])
            self.create_connection(switches[i], switches[i-1])  # Connect switches in a line
            self.create_connection(switches[i], devices[i])
            self.add_device(devices[i])
    
    def create_ring_topology(self, devices, switches):
        for device, switch in zip(devices, switches):
            self.add_device(switch)
            self.add_device(device)
            self.create_connection(device, switch)
        for i in range(len(switches)):
            self.create_connection(switches[i], switches[(i + 1) % len(switches)])  # Circular connection
    
    def create_mesh_topology(self, devices, switches):
        for device, switch in zip(devices, switches):
            self.add_device(switch)
            self.add_device(device)
            self.create_connection(device, switch)
            for other_switch in switches:
                if other_switch != switch:
                    self.create_connection(switch, other_switch)
    
    def plot_topology(self):
        pos = nx.spring_layout(self.graph)  # Layout for graph visualization
        nx.draw(self.graph, pos, with_labels=True, node_size=800, node_color='skyblue', font_size=10, font_weight='bold')
        plt.title('Network Topology')
        plt.savefig('static/topology.png')  # Save the plot image
        plt.close()


class Simulation:
    def __init__(self):
        self.topology = Topology()
    
    def create_network(self, num_devices, topology_type):
        if topology_type.lower() == 'star':
            devices = [Device(f"Device{i+1}") for i in range(num_devices)]
            hub = Hub("Hub1")
            self.topology.create_star_topology(devices, hub)
        elif topology_type.lower() == 'bus':
            num_switches = num_devices
            switches = [Switch(f"Switch{i+1}") for i in range(num_switches)]
            devices = [Device(f"Device{i+1}") for i in range(num_devices)]
            self.topology.create_bus_topology(devices, switches)
        elif topology_type.lower() == 'ring':
            num_switches = num_devices
            switches = [Switch(f"Switch{i+1}") for i in range(num_switches)]
            devices = [Device(f"Device{i+1}") for i in range(num_devices)]
            self.topology.create_ring_topology(devices, switches)
        elif topology_type.lower() == 'mesh':
            num_switches = num_devices
            switches = [Switch(f"Switch{i+1}") for i in range(num_switches)]
            devices = [Device(f"Device{i+1}") for i in range(num_devices)]
            self.topology.create_mesh_topology(devices, switches)
        else:
            print("Invalid topology type.")
    
    def check_message_path(self, sender_id, receiver_id):
        if sender_id not in self.topology.graph.nodes or receiver_id not in self.topology.graph.nodes:
            print("Invalid sender or receiver device ID.")
            return False
        
        try:
            path = nx.shortest_path(self.topology.graph, source=sender_id, target=receiver_id)
            print("Path found:", " -> ".join(path))
            return path
        except nx.NetworkXNoPath:
            print("No path found between the sender and receiver.")
            return False
    
    def send_message(self, path, message, receiver_id):
        for i in range(len(path)-1):
            sender = next(device for device in self.topology.devices if device.device_id == path[i])
            receiver = next(device for device in self.topology.devices if device.device_id == path[i+1])
            if isinstance(sender, Switch):
                sender.send_data(message, receiver_id)
            else:
                sender.send_data(message)
            print(f"Message sent from {sender.device_id} to {receiver.device_id}")
    
    def run_simulation(self, num_devices, topology_type, sender_id, receiver_id, message):
        self.create_network(num_devices, topology_type)
        print("Devices in the network:", [device.device_id for device in self.topology.devices])
        
        path = self.check_message_path(sender_id, receiver_id)
        if path:
            self.topology.plot_topology()  # Plot the network graph
            self.send_message(path, message, receiver_id)
            return True, path
        else:
            return False, None


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        num_devices = int(request.form['num_devices'])
        topology_type = request.form['topology_type']
        sender_id = request.form['sender_id']
        receiver_id = request.form['receiver_id']
        message = request.form['message']
        
        simulation = Simulation()
        success, path = simulation.run_simulation(num_devices, topology_type, sender_id, receiver_id, message)
        if success:
            return render_template('index.html', plot_available=True, path=path, message=message)
        else:
            return render_template('index.html', plot_available=False, error_message="No path found between the sender and receiver.")
    return render_template('index.html', plot_available=False)


if __name__ == "__main__":
    app.run(debug=True)
