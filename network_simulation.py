from abc import ABC, abstractmethod

# Define an interface for sending and receiving data
class NetworkDevice(ABC):
    @abstractmethod
    def send_data(self, data):
        pass

    @abstractmethod
    def receive_data(self, data):
        pass

# Define a class for end devices
class EndDevice(NetworkDevice):
    def __init__(self, name):
        self.name = name
        self.connection = None  # Connection to a hub or another device

    def send_data(self, data):
        if self.connection:
            self.connection.receive_data(data)
        else:
            print(f"{self.name} has no connection to send data.")

    def receive_data(self, data):
        print(f"{self.name} received data: {data}")

    def connect_to(self, target):
        self.connection = target

# Define a class for hubs
class Hub(NetworkDevice):
    def __init__(self, name):
        self.name = name
        self.connected_devices = []

    def send_data(self, data):
        for device in self.connected_devices:
            device.receive_data(data)

    def receive_data(self, data):
        print(f"{self.name} received data: {data}")
        self.send_data(data)

    def connect_device(self, device):
        self.connected_devices.append(device)
        device.connection = self

# Function to create a star topology
def create_star_topology(devices, hub_name):
    hub = Hub(hub_name)
    for device in devices:
        hub.connect_device(device)
    return hub

# Function to create a point-to-point topology
def create_point_to_point_topology(devices):
    for i in range(len(devices) - 1):
        devices[i].connect_to(devices[i+1])

# Function to create a bus topology
def create_bus_topology(devices):
    hub = Hub("Bus Hub")
    for device in devices:
        hub.connect_device(device)
    return hub  # Return the created hub

# Function to create a ring topology
def create_ring_topology(devices):
    for i in range(len(devices)):
        devices[i].connect_to(devices[(i + 1) % len(devices)])

# Function to create a mesh topology
def create_mesh_topology(devices):
    for i in range(len(devices)):
        for j in range(len(devices)):
            if i != j:
                devices[i].connect_to(devices[j])

if __name__ == "__main__":
    # Test the network simulation
    device1 = EndDevice("Device 1")
    device2 = EndDevice("Device 2")
    device3 = EndDevice("Device 3")

    create_point_to_point_topology([device1, device2, device3])
    hub = create_star_topology([device1, device2, device3], "Star Hub")
    hub = create_bus_topology([device1, device2, device3])  # Assign the returned hub to a variable
    create_ring_topology([device1, device2, device3])
    create_mesh_topology([device1, device2, device3])

    device1.send_data("Hello from Device 1")
