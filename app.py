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
        self.mac_address = None
        self.ipv4_address = None
        self.routing_table = {}  # Initialize routing table

    def connect(self, other_device):
        if other_device not in self.connected_devices:
            self.connected_devices.append(other_device)
            other_device.connected_devices.append(self)
            print(f"Devices {self.device_id} and {other_device.device_id} connected.")

    def send_data(self, data, visited=None):
        if visited is None:
            visited = set()
        visited.add(self.device_id)
        print(f"Device {self.device_id} sending data: {data}")
        for device in self.connected_devices:
            if device.device_id not in visited:
                device.receive_data(data, visited=visited)

    def receive_data(self, data, visited=None):
        if visited is None:
            visited = set()
        visited.add(self.device_id)
        print(f"Device {self.device_id} received data: {data}")
        self.send_data(data, visited=visited)

    def generate_mac_address(self):
        if not self.mac_address:
            self.mac_address = ':'.join(''.join(random.choices(string.hexdigits.lower(), k=2)) for _ in range(6))
        return self.mac_address

    def assign_ipv4_address(self):
        if not self.ipv4_address:
            self.ipv4_address = '.'.join(str(random.randint(0, 255)) for _ in range(4))
        return self.ipv4_address

    def add_routing_entry(self, destination, next_hop):
        self.routing_table[destination] = next_hop

class Hub(Device):
    def __init__(self, hub_id):
        super().__init__(hub_id)

    def broadcast(self, data, visited=None):
        if visited is None:
            visited = set()
        visited.add(self.device_id)
        print(f"Hub {self.device_id} broadcasting data: {data}")
        for device in self.connected_devices:
            if device.device_id not in visited:
                device.receive_data(data, visited=visited)

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

    def receive_data(self, data, visited=None):
        if visited is None:
            visited = set()
        visited.add(self.device_id)
        print(f"Switch {self.device_id} received data: {data}")
        self.mac_table[data['source_mac']] = data['source_mac']
        dest_mac = data['dest_mac']
        if dest_mac in self.mac_table:
            for device in self.connected_devices:
                if device.generate_mac_address() == dest_mac:
                    device.receive_data(data, visited)
                    break
        else:
            for device in self.connected_devices:
                if device.generate_mac_address() != data['source_mac']:
                    device.receive_data(data, visited)

class Repeater(Device):
    def __init__(self, repeater_id):
        super().__init__(repeater_id)

    def send_data(self, data, receiver_mac):
        for device in self.connected_devices:
            if device.mac_address == receiver_mac:
                device.receive_data(data)
                print(f"Repeater {self.device_id} forwarded data to {device.mac_address}")
                return
        print(f"Receiver device with MAC address {receiver_mac} not connected to repeater {self.device_id}")

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

    def assign_ipv4_addresses(self):
        for device in self.devices:
            device.assign_ipv4_address()

    def calculate_broadcast_domains(self):
        broadcast_domains = 1  # Single switch creates one broadcast domain
        return broadcast_domains

    def calculate_collision_domains(self):
        return len([device for device in self.devices if isinstance(device, Hub)])

    def generate_routing_tables(self):
        for device in self.devices:
            for connected_device in device.connected_devices:
                device.add_routing_entry(connected_device.ipv4_address, connected_device.ipv4_address)

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
        for i in range(len(path) - 1):
            sender = next(device for device in self.topology.devices if device.device_id == path[i])
            receiver = next(device for device in self.topology.devices if device.device_id == path[i + 1])
            sender_mac = sender.generate_mac_address() if not isinstance(sender, Switch) else receiver.mac_address
            receiver_mac = receiver.generate_mac_address() if not isinstance(receiver, Switch) else sender.mac_address
            if isinstance(sender, Repeater):
                sender.send_data(message, receiver_mac)
            elif isinstance(sender, Switch):
                sender.send_data({'source_mac': sender_mac, 'dest_mac': receiver_mac, 'data': message})
            else:
                sender.send_data(message)
            print(f"Message sent from {sender_mac} to {receiver_mac}")

    def run_simulation(self, num_devices, topology_type, sender_id, receiver_id, message):
        self.create_network(num_devices, topology_type)
        print("Devices in the network:", [device.device_id for device in self.topology.devices])

        path = self.check_message_path(sender_id, receiver_id)
        if path:
            self.topology.assign_ipv4_addresses()  # Assign IPv4 addresses
            self.topology.plot_topology()
            self.topology.generate_routing_tables()  # Generate routing tables

            broadcast_domains = (self.topology.calculate_broadcast_domains())-1
            collision_domains = self.topology.calculate_collision_domains()

            return True, path, broadcast_domains, collision_domains
        else:
            return False, None, 0, 0

    def create_network_with_switch(self, num_topologies, devices_per_topology):
        hubs = []
        for i in range(num_topologies):
            devices = [Device(f"Device{i+1}_{j+1}") for j in range(devices_per_topology[i])]
            hub = Hub(f"Hub{i+1}")
            hubs.append(hub)
            self.topology.create_star_topology(devices, hub)

        switch = Switch("Switch1")
        router = Device("Router1")  # Create a router device
        self.topology.add_device(router)  # Add router to the topology
        self.topology.create_connection(switch, router)  # Connect switch to router

        for hub in hubs:
            self.topology.add_device(switch)
            self.topology.create_connection(hub, switch)

    def run_simulation_with_switch(self, num_topologies, devices_per_topology, sender_id, receiver_id, message):
        self.create_network_with_switch(num_topologies, devices_per_topology)
        print("Devices in the network with switch:", [device.device_id for device in self.topology.devices])

        path = self.check_message_path(sender_id, receiver_id)
        if path:
            self.topology.assign_ipv4_addresses()  # Assign IPv4 addresses
            self.topology.plot_topology()
            self.topology.generate_routing_tables()  # Generate routing tables

            broadcast_domains = self.topology.calculate_broadcast_domains()
            collision_domains = num_topologies +1  # Number of star topologies equals collision domains

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
            success, path, broadcast_domains, collision_domains = simulation.run_simulation(num_devices, topology_type, sender_id, receiver_id, message)
            if success:
                mac_addresses = {device.device_id: device.generate_mac_address() for device in simulation.topology.devices}
                ip_addresses = {device.device_id: device.ipv4_address for device in simulation.topology.devices}
                routing_tables = {device.ipv4_address: device.routing_table for device in simulation.topology.devices}
                return render_template('index.html', plot_available=True, path=path, message=message, mac_addresses=mac_addresses, ip_addresses=ip_addresses, broadcast_domains=broadcast_domains, collision_domains=collision_domains, routing_tables=routing_tables)
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
                ip_addresses = {device.device_id: device.ipv4_address for device in simulation.topology.devices}
                routing_tables = {device.ipv4_address: device.routing_table for device in simulation.topology.devices}
                return render_template('index.html', plot_available=True, path=path, message=message, mac_addresses=mac_addresses, ip_addresses=ip_addresses, broadcast_domains=broadcast_domains, collision_domains=collision_domains, routing_tables=routing_tables)
            else:
                return render_template('index.html', plot_available=False, error_message="No path found between the sender and receiver.")
    return render_template('index.html', plot_available=False)

if __name__ == "__main__":
    app.run(debug=True)
    