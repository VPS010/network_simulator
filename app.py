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

    def send_data(self, data, source_mac=None, dest_mac=None, visited=None):
        if visited is None:
            visited = set()
        visited.add(self.device_id)
        print(f"Device {self.device_id} sending data: {data}")
        for device in self.connected_devices:
            if device.device_id not in visited:
                if isinstance(device, Switch):
                    device.receive_data(data, source_mac, dest_mac, visited)
                else:
                    device.receive_data(data, visited)

    def receive_data(self, data, visited=None):
        if visited is None:
            visited = set()
        visited.add(self.device_id)
        print(f"Device {self.device_id} received data: {data}")
        self.send_data(data, visited=visited)

    def generate_mac_address(self):
        if not hasattr(self, 'mac_address'):
            self.mac_address = ':'.join(''.join(random.choices(string.hexdigits.lower(), k=2)) for _ in range(6))
        return self.mac_address

class Hub(Device):
    def __init__(self, hub_id):
        super().__init__(hub_id)

    def broadcast(self, data, source_mac=None, dest_mac=None, visited=None):
        if visited is None:
            visited = set()
        visited.add(self.device_id)
        print(f"Hub {self.device_id} broadcasting data: {data}")
        for device in self.connected_devices:
            if device.device_id not in visited:
                if isinstance(device, Switch):
                    device.receive_data(data, source_mac, dest_mac, visited)
                else:
                    device.receive_data(data, visited)

    def receive_data(self, data, visited=None):
        if visited is None:
            visited = set()
        visited.add(self.device_id)
        print(f"Hub {self.device_id} received data: {data}")
        self.broadcast(data, visited=visited)

class Switch(Device):
    def __init__(self, switch_id):
        super().__init__(switch_id)
        self.mac_table = {}

    def receive_data(self, data, source_mac, dest_mac, visited=None):
        if visited is None:
            visited = set()
        visited.add(self.device_id)
        print(f"Switch {self.device_id} received data: {data} from {source_mac} to {dest_mac}")
        self.mac_table[source_mac] = source_mac
        if dest_mac in self.mac_table:
            for device in self.connected_devices:
                if device.generate_mac_address() == dest_mac:
                    device.receive_data(data, visited)
                    break
        else:
            for device in self.connected_devices:
                if device.generate_mac_address() != source_mac:
                    device.receive_data(data, visited)

class Repeater(Device):
    def __init__(self, repeater_id):
        super().__init__(repeater_id)

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
            elif isinstance(sender, Switch):
                sender.send_data(message, sender.generate_mac_address(), receiver.generate_mac_address())
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

    def create_network_with_switch(self, num_topologies, devices_per_topology):
        hubs = []
        for i in range(num_topologies):
            devices = [Device(f"Device{i+1}_{j+1}") for j in range(devices_per_topology[i])]
            hub = Hub(f"Hub{i+1}")
            hubs.append(hub)
            self.topology.create_star_topology(devices, hub)

        switch = Switch("Switch1")
        self.topology.add_device(switch)
        for hub in hubs:
            self.topology.create_connection(hub, switch)

    def run_simulation_with_switch(self, num_topologies, devices_per_topology, sender_id, receiver_id, message):
        self.create_network_with_switch(num_topologies, devices_per_topology)
        print("Devices in the network with switch:", [device.device_id for device in self.topology.devices])

        path = self.check_message_path(sender_id, receiver_id)
        if path:
            self.topology.plot_topology()
            self.send_message(path, message, receiver_id)
            
            # Calculate broadcast domains
            broadcast_domains = 1  # Single switch creates one broadcast domain

            # Calculate collision domains
            collision_domains = 0
            hubs = [device for device in self.topology.devices if isinstance(device, Hub)]
            switches = [device for device in self.topology.devices if isinstance(device, Switch)]
            
            for switch in switches:
                collision_domains += len(hubs)  # Each hub connected to a switch is a separate collision domain
            
            return True, path, broadcast_domains, collision_domains
        else:
            return False, None, 0, 0

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        use_switch = request.form.get('use_switch') == 'yes'
        if not use_switch:
            num_devices = int(request.form['num_devices'])
            topology_type = request.form['topology_type']
            sender_id = request.form['sender_id']
            receiver_id = request.form['receiver_id']
            message = request.form['message']

            simulation = Simulation()
            success, path = simulation.run_simulation(num_devices, topology_type, sender_id, receiver_id, message)
            if success:
                mac_addresses = {device.device_id: device.generate_mac_address() for device in simulation.topology.devices}
                return render_template('index.html', plot_available=True, path=path, message=message, mac_addresses=mac_addresses)
            else:
                return render_template('index.html', plot_available=False, error_message="No path found between the sender and receiver.")
        else:
            num_topologies = int(request.form['num_topologies'])
            devices_per_topology = [int(request.form[f'num_devices_topology{i+1}']) for i in range(num_topologies)]
            sender_id = request.form['sender_id']
            receiver_id = request.form['receiver_id']
            message = request.form['message']

            simulation = Simulation()
            success, path, broadcast_domains, collision_domains = simulation.run_simulation_with_switch(num_topologies, devices_per_topology, sender_id, receiver_id, message)
            if success:
                mac_addresses = {device.device_id: device.generate_mac_address() for device in simulation.topology.devices}
                return render_template('index.html', plot_available=True, path=path, message=message, mac_addresses=mac_addresses, broadcast_domains=broadcast_domains, collision_domains=collision_domains)
            else:
                return render_template('index.html', plot_available=False, error_message="No path found between the sender and receiver.")
    return render_template('index.html', plot_available=False)

if __name__ == "__main__":
    app.run(debug=True)
