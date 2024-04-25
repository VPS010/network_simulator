from flask import Flask, render_template, request
import matplotlib.pyplot as plt
import networkx as nx
import random
import string

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
    
    def generate_mac_address(self):
        if not hasattr(self, 'mac_address'):
            self.mac_address = ':'.join(''.join(random.choices(string.hexdigits.lower(), k=2)) for _ in range(6))
        return self.mac_address


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


class Repeater(Device):
    def __init__(self, repeater_id):
        super().__init__(repeater_id)
    
    def connect_to_repeater(self, device):
        self.connect(device)

    def send_data(self, data, receiver_id):
        for device in self.connected_devices:
            if device.device_id == receiver_id:
                device.receive_data(data)
                print(f"Repeater {self.device_id} forwarded data to {device.device_id}")
                return
        print(f"Receiver device {receiver_id} not connected to repeater {self.device_id}")


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
    
    def create_bus_topology(self, devices, repeaters):
        self.add_device(repeaters[0])
        self.create_connection(repeaters[0], devices[0])
        self.add_device(devices[0])
        for i in range(1, len(repeaters)):
            self.add_device(repeaters[i])
            self.create_connection(repeaters[i], repeaters[i-1])
            self.create_connection(repeaters[i], devices[i])
            self.add_device(devices[i])
    
    def create_ring_topology(self, devices, repeaters):
        for device, repeater in zip(devices, repeaters):
            self.add_device(repeater)
            self.add_device(device)
            self.create_connection(device, repeater)
        for i in range(len(repeaters)):
            self.create_connection(repeaters[i], repeaters[(i + 1) % len(repeaters)])
    
    def create_mesh_topology(self, devices, repeaters):
        for device, repeater in zip(devices, repeaters):
            self.add_device(repeater)
            self.add_device(device)
            self.create_connection(device, repeater)
            for other_repeater in repeaters:
                if other_repeater != repeater:
                    self.create_connection(repeater, other_repeater)
    
    def plot_topology(self):
        pos = nx.spring_layout(self.graph)
        nx.draw(self.graph, pos, with_labels=True, node_size=800, node_color='skyblue', font_size=10, font_weight='bold')
        plt.title('Network Topology')
        plt.savefig('static/topology.png')
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
            num_repeaters = num_devices
            repeaters = [Repeater(f"Repeater{i+1}") for i in range(num_repeaters)]
            devices = [Device(f"Device{i+1}") for i in range(num_devices)]
            self.topology.create_bus_topology(devices, repeaters)
        elif topology_type.lower() == 'ring':
            num_repeaters = num_devices
            repeaters = [Repeater(f"Repeater{i+1}") for i in range(num_repeaters)]
            devices = [Device(f"Device{i+1}") for i in range(num_devices)]
            self.topology.create_ring_topology(devices, repeaters)
        elif topology_type.lower() == 'mesh':
            num_repeaters = num_devices
            repeaters = [Repeater(f"Repeater{i+1}") for i in range(num_repeaters)]
            devices = [Device(f"Device{i+1}") for i in range(num_devices)]
            self.topology.create_mesh_topology(devices, repeaters)
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
            if isinstance(sender, Repeater):
                sender.send_data(message, receiver_id)
            else:
                sender.send_data(message)
            print(f"Message sent from {sender.device_id} to {receiver.device_id}")
    
    def run_simulation(self, num_devices, topology_type, sender_id, receiver_id, message):
        self.create_network(num_devices, topology_type)
        print("Devices in the network:", [device.device_id for device in self.topology.devices])
        
        path = self.check_message_path(sender_id, receiver_id)
        if path:
            self.topology.plot_topology()
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
            # Generate MAC addresses
            mac_addresses = {}
            for device in simulation.topology.devices:
                mac_addresses[device.device_id] = device.generate_mac_address()

            return render_template('index.html', plot_available=True, path=path, message=message, mac_addresses=mac_addresses)
        else:
            return render_template('index.html', plot_available=False, error_message="No path found between the sender and receiver.")
    return render_template('index.html', plot_available=False)


if __name__ == "__main__":
    app.run(debug=True)
