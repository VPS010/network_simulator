# Network Topology Simulator Documentation

## Setup and Environment Requirements
To run the Network Topology Simulator, you need to have the following software installed:

1. Python (version 3.6 or higher)
2. Flask (install using `pip install Flask`)
3. NetworkX (install using `pip install networkx`)
4. Matplotlib (install using `pip install matplotlib`)

## Libraries Used
- **Flask:** Used for creating the web application and handling HTTP requests.
- **NetworkX:** Used for creating and analyzing complex networks, such as the network topology in this simulator.
- **Matplotlib:** Used for plotting and visualizing the network topology graph.

## Code Overview
The Network Topology Simulator is implemented as a Flask web application. It allows users to define the number of devices, choose the type of topology (star, bus, ring, or mesh), specify sender and receiver device IDs, and provide a message for passing between devices. The simulator then generates a network topology graph and displays the path of message passing along with the message.

### Class Structure
1. **Device:** Represents a network device with a unique device ID and connections to other devices.
2. **Hub:** Subclass of Device, represents a hub device that can connect to multiple end devices.
3. **Switch:** Subclass of Device, represents a switch device that routes messages to specific devices based on their IDs.
4. **Topology:** Manages the creation of network topologies and provides methods for adding devices, creating connections, and plotting the network graph.
5. **Simulation:** Handles the simulation logic, including creating networks based on user input, checking message paths, and sending messages.

### Topology Logic
1. **Star Topology:**
   - In a star topology, multiple end devices are connected to a central hub.
   - Each end device is directly connected to the hub, enabling easy communication between devices via the hub.

2. **Bus Topology:**
   - In a bus topology, end devices are connected in a linear sequence using switches.
   - The first switch is connected to a hub or central device, and subsequent switches are connected to each other and end devices.
   - Messages are passed through switches along the linear path from sender to receiver.

3. **Ring Topology:**
   - In a ring topology, switches are connected in a circular ring, with each switch connected to two neighboring switches.
   - End devices are connected to switches, and messages can be routed through switches in the shortest circular path from sender to receiver.

4. **Mesh Topology:**
   - In a mesh topology, switches are connected to each other in a fully interconnected manner.
   - Each switch is connected to every other switch, allowing for multiple paths between devices for message passing.

### Message Passing
- When a user submits the form with sender and receiver IDs, the simulator checks if a valid path exists between the devices.
- If a valid path is found, the simulator plots the network graph and displays the path of message passing on the web interface.
- The message is sent from the sender device to the receiver device, following the specified path through switches or hubs.

## Full Specification Report
The Network Topology Simulator provides the following functionality:
1. User Interface:
   - Form for entering the number of devices, selecting topology type, and providing sender/receiver device IDs and message.
   - Submit button to initiate the simulation.
   - Displays the network topology graph and the path of message passing on the web interface.

2. Simulation Logic:
   - Creation of star, bus, ring, or mesh topologies based on user input.
   - Checking for a valid path between sender and receiver devices using NetworkX.
   - Sending messages from sender to receiver following the determined path through switches or hubs.

3. Visualization:
   - Uses Matplotlib to plot the network topology graph and display it on the web interface.
   - Shows the path of message passing between devices along with the message content.

4. Error Handling:
   - Checks for invalid input such as non-existent device IDs or topology types.
   - Displays error messages if no valid path is found between sender and receiver devices.

The code structure is modular and follows object-oriented programming principles to manage devices, topologies, and simulations efficiently. The Flask framework handles the web interface, while NetworkX and Matplotlib provide powerful tools for network analysis and visualization.

# Hands-on


## Step 1: Choose Topology Type

Select the type of network topology you want to create:
- Star
- Bus
- Ring
- Mesh

## Step 2: Enter Details

Fill in the required details:
- Number of devices
- Sender device ID
- Receiver device ID
- Message to be sent

## Step 3: Submit Form

Click the "Submit" button to create the network and simulate message passing.

## Results

If a valid path is found between the sender and receiver, the network topology graph and the message passing path will be displayed. If no path is found, an error message will be shown.

### Example Usage:

1. Choose "Star" topology.
2. Enter the following details:
   - Number of devices: 4
   - Sender device ID: Device1
   - Receiver device ID: Device3
   - Message: Hello, world!

3. Submit the form.

![Star Topology Example](path/to/star_topology.png)

Message passing path:

