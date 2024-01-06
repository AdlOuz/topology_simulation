import random
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from collections import deque
import time
import sys

class NetworkTopology:
    def __init__(self, num_nodes):
        # Initialize the NetworkTopology class with the number of nodes
        self.num_nodes = num_nodes
        
        # Create an adjacency matrix representing connections between nodes, initialized with zeros
        self.adjacency_matrix = [[0 for _ in range(num_nodes)] for _ in range(num_nodes)]
        
        # Generate the network topology by connecting nodes
        self.generate_topology()
        
        # Initialize empty dictionaries for routing and forwarding tables
        self.routing_table = {}
        self.forwarding_table = {}

    def generate_topology(self):
        # Randomly connect nodes to form a network using a nested loop
        for i in range(self.num_nodes):
            for j in range(i + 1, self.num_nodes):
                # Randomly determine if there should be a connection based on probability (50% chance)
                if random.random() > 0.7:  # Adjust probability for connection
                    # Assign a random weight/cost to the connection (range: 1 to 10)
                    weight = random.randint(1, 10)
                    
                    # Update the adjacency matrix to represent the connection between nodes
                    self.adjacency_matrix[i][j] = weight
                    self.adjacency_matrix[j][i] = weight  # Since it's an undirected graph

        # Check connectivity after generating the connections
        if not self.is_connected():
            # Retry generating topology until it's connected
            self.generate_topology()


    def is_connected(self):
        # Start BFS from node 0 and check if all nodes are reachable

        # Create a list to track visited nodes
        visited = [False] * self.num_nodes

        # Initialize a queue for BFS starting from node 0
        queue = deque([0])
        visited[0] = True  # Mark the starting node as visited

        while queue:
            # Dequeue a node from the front of the queue
            node = queue.popleft()

            # Iterate through all adjacent nodes
            for adjacent, weight in enumerate(self.adjacency_matrix[node]):
                # Check if the node is connected and not visited
                if weight > 0 and not visited[adjacent]:
                    visited[adjacent] = True  # Mark the node as visited
                    queue.append(adjacent)  # Enqueue the adjacent node

        # Check if all nodes have been visited
        return all(visited)

    def dijkstra(self, src):
        # Initialize distances dictionary with all nodes having infinite distance
        distances = {node: float('inf') for node in range(self.num_nodes)}
        distances[src] = 0  # Set the distance of the source node to 0
        visited = [False] * self.num_nodes  # Track visited nodes

        # Iterate through the nodes to find shortest paths
        for _ in range(self.num_nodes):
            min_dist = float('inf')  # Initialize minimum distance to infinity
            min_idx = -1  # Initialize index for the minimum distance node

            # Find the node with the minimum distance that has not been visited yet
            for i in range(self.num_nodes):
                if not visited[i] and distances[i] < min_dist:
                    min_dist = distances[i]
                    min_idx = i

            visited[min_idx] = True  # Mark the minimum distance node as visited

            # Update distances for neighboring nodes of the current node
            for j in range(self.num_nodes):
                # Check unvisited nodes connected to the current node
                if (not visited[j]) and (self.adjacency_matrix[min_idx][j] > 0):
                    # Calculate the new distance through the current node
                    new_dist = distances[min_idx] + self.adjacency_matrix[min_idx][j]
                    
                    # Update distance if the new distance is shorter than the recorded distance
                    if new_dist < distances[j]:
                        distances[j] = new_dist  # Update distance for the node

        return distances  # Return the computed shortest distances from the source node

    
    def bellman_ford(self, src):
        # Initialize distances dictionary with all nodes having infinite distance
        distances = {node: float('inf') for node in range(self.num_nodes)}
        distances[src] = 0  # Set the distance of the source node to 0

        # Iterate through the nodes multiple times to relax edges and find shortest paths
        for _ in range(self.num_nodes - 1):
            # Iterate through all nodes
            for u in range(self.num_nodes):
                # Iterate through all nodes again to check for possible shorter paths
                for v in range(self.num_nodes):
                    # Check if there is a valid edge between nodes u and v
                    if self.adjacency_matrix[u][v] > 0:
                        # Relax the edge: Update distance if a shorter path is found
                        if distances[u] + self.adjacency_matrix[u][v] < distances[v]:
                            distances[v] = distances[u] + self.adjacency_matrix[u][v]

        return distances  # Return the computed shortest distances from the source node using Bellman-Ford algorithm


    def calculate_routing_table(self, algorithm):
        # Calculate routing tables based on the selected algorithm
        
        # If the algorithm chosen is "Link State Routing"
        if algorithm == "Link State Routing":
            # Clear existing routing and forwarding tables
            self.routing_table = {}
            self.forwarding_table = {}
            
            # Calculate routing table for each node using Dijkstra's algorithm
            for node in range(self.num_nodes):
                self.routing_table[node] = self.dijkstra(node)
        
        # If the algorithm chosen is "Distance Vector Routing"
        if algorithm == "Distance Vector Routing":
            # Clear existing routing and forwarding tables
            self.routing_table = {}
            self.forwarding_table = {}
            
            # Calculate routing table for each node using Bellman-Ford algorithm
            for node in range(self.num_nodes):
                self.routing_table[node] = self.bellman_ford(node)


    def generate_forwarding_table(self, algorithm):
        # Ensure the routing table is up to date based on the selected algorithm
        self.calculate_routing_table(algorithm)
        
        # Iterate through all source nodes
        for src in range(self.num_nodes):
            self.forwarding_table[src] = {}  # Initialize forwarding table for the source node
            
            # Iterate through all destination nodes
            for dest in range(self.num_nodes):
                if dest != src:  # Skip setting forwarding for the same source and destination nodes
                    next_hop = None  # Initialize the next hop for routing
                    
                    available_nodes = []
                    
                    # Collect available nodes based on adjacency matrix for the source node
                    for node, weight in enumerate(self.adjacency_matrix[src]):
                        if weight != 0:
                            available_nodes.append(node)
                    
                    # Check for possible intermediate nodes for forwarding
                    for intermediate_node in available_nodes:
                        # Check if the intermediate node helps in forwarding to the destination
                        if self.routing_table[src][intermediate_node] + self.routing_table[intermediate_node][dest] == self.routing_table[src][dest]:
                            next_hop = intermediate_node  # Set the intermediate node as the next hop
                            break
                    
                    # Set the forwarding based on whether a next hop is found or not
                    if next_hop is None:
                        self.forwarding_table[src][dest] = dest  # No intermediate node found; set destination as next hop
                    else:
                        self.forwarding_table[src][dest] = next_hop  # Set the next hop found as the forwarding destination


    def visualize_topology(self):
        # Create an empty graph using NetworkX library
        G = nx.Graph()
        
        # Iterate through nodes to establish edges based on adjacency matrix
        for i in range(self.num_nodes):
            for j in range(i + 1, self.num_nodes):
                # Check if there is a connection between nodes i and j in the adjacency matrix
                if self.adjacency_matrix[i][j] > 0:
                    # Add an edge between nodes i and j with a weight from the adjacency matrix
                    G.add_edge(i, j, weight=self.adjacency_matrix[i][j])

        return G  # Return the graph representing the network topology

    
    def visualize_route(self, source, destination):
        # Create an empty graph using NetworkX library
        G = nx.Graph()

        # List to store edges representing the forwarding path
        forwarding_edges = []

        # Loop through all nodes except the source node
        for dst in range(self.num_nodes):
            if dst != source:
                start = source  # Set the starting node as the source node
                next_node = self.forwarding_table[source][dst]  # Get the next node in the forwarding table

                # Traverse the path until the destination is reached
                while next_node != dst:
                    # Add edges to the graph representing the forwarding path
                    G.add_edge(start, next_node, weight=self.adjacency_matrix[start][next_node])
                    
                    # Check if the current destination is the final destination, store forwarding edges
                    if dst == destination:
                        forwarding_edges.append((start, next_node))
                    
                    start = next_node  # Update the start node
                    next_node = self.forwarding_table[next_node][dst]  # Move to the next node in the forwarding table

                # Add the final edge to the graph for the path
                G.add_edge(start, next_node, weight=self.adjacency_matrix[start][next_node])
                
                # Check if the current destination is the final destination, store forwarding edges
                if dst == destination:
                    forwarding_edges.append((start, next_node))

        return G, forwarding_edges  # Return the graph and forwarding edges representing the route


class NetworkTopologyGUI:
    def __init__(self, root):
        # Initialize the GUI with a root window
        self.root = root
        self.root.title("Network Topology Visualization")  # Set the title of the window
        self.root.geometry("800x600")  # Set the initial size of the window

        # Initialize attributes for the network and nodes
        self.network = None
        self.num_nodes = None
        self.source_node = None
        self.destination_node = None

        # Initialize canvas elements
        self.canvas = None
        self.algo_canvas = None

        # Initialize label text and label widget for user instructions
        self.label_text = tk.StringVar()
        self.label_text.set("Number of Nodes")
        self.label = tk.Label(self.root, textvariable=self.label_text)
        self.label.pack()  # Pack the label widget into the window

        # Entry field to accept number of nodes; binding to validate input
        self.num_nodes_entry = tk.Entry(self.root)
        self.num_nodes_entry.pack(side="top")  # Pack the entry field into the window
        self.num_nodes_entry.bind("<KeyRelease>", self.validate_input)  # Validate input on key release

        # Button to create the network topology (initially disabled)
        self.create_topology_button = tk.Button(self.root, text="Create Topology", command=self.generate_topology, state=tk.DISABLED)
        self.create_topology_button.pack()

        # Button for Link State Routing (initially disabled)
        self.link_state_button = tk.Button(self.root, text="Link State Routing", command=self.link_state_routing, state=tk.DISABLED)
        self.link_state_button.pack()

        # Button for Distance Vector Routing (initially disabled)
        self.distance_vector_button = tk.Button(self.root, text="Distance Vector Routing", command=self.distance_vector_routing, state=tk.DISABLED)
        self.distance_vector_button.pack()

        # Handle window closing event
        self.root.protocol("WM_DELETE_WINDOW", self.exit_application)


    def validate_input(self, event):
        # Function to validate the input for number of nodes
        input_text = self.num_nodes_entry.get()  # Retrieve the input text
        if input_text.isdigit() and int(input_text) > 0:  # Check if input is a positive integer
            self.create_topology_button['state'] = tk.NORMAL  # Enable the 'Create Topology' button
        else:
            self.create_topology_button['state'] = tk.DISABLED  # Disable the 'Create Topology' button if input is invalid

    def validate_source_destination(self, event):
        # Function to validate the input for source and destination nodes
        source_text = self.source_entry.get()  # Retrieve the source node input text
        destination_text = self.destination_entry.get()  # Retrieve the destination node input text

        # Check if both inputs are integers and within valid node range, and source is not equal to destination
        if (source_text.isdigit() and destination_text.isdigit() and
                self.network.num_nodes > int(source_text) >= 0 and
                self.network.num_nodes > int(destination_text) >= 0 and
                int(source_text) != int(destination_text)):
            self.execute_button['state'] = tk.NORMAL  # Enable the execution button
        else:
            self.execute_button['state'] = tk.DISABLED  # Disable the execution button if input is invalid


    def generate_topology(self):
        # Check if a canvas exists and close it to prepare for new visualization
        if self.canvas:
            plt.close()  # Close the existing plot
            self.canvas.get_tk_widget().pack_forget()  # Remove the canvas from the window
            self.canvas = None  # Reset the canvas

        self.num_nodes = int(self.num_nodes_entry.get())  # Get the number of nodes from user input

        self.network = NetworkTopology(self.num_nodes)  # Create a NetworkTopology object with the specified number of nodes

        # Enable the Link State Routing and Distance Vector Routing buttons after creating the topology
        self.link_state_button['state'] = tk.NORMAL
        self.distance_vector_button['state'] = tk.NORMAL

        self.visualize_network()  # Call the method to visualize the network topology


    def visualize_network(self):
        # Check if a network exists
        if self.network:
            # Generate a graph representation of the network using NetworkTopology's visualize_topology method
            G = self.network.visualize_topology()

            # Create a new plot figure
            plt.figure()

            # Generate layout positions for nodes using spring layout algorithm
            pos = nx.spring_layout(G)

            # Retrieve edge labels (weights) from the graph
            labels = nx.get_edge_attributes(G, 'weight')

            # Draw the graph with nodes, labels, and edges
            nx.draw(G, pos, with_labels=True)
            nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)

            # Create a canvas to display the generated plot within the GUI window
            self.canvas = FigureCanvasTkAgg(plt.gcf(), master=self.root)
            self.canvas.draw()
            self.canvas.get_tk_widget().pack()  # Display the canvas in the GUI window


    def link_state_routing(self):
        # Trigger method to open a window for Link State Routing with specified parameters
        self.open_algorithm_window("Link State Routing")

    def distance_vector_routing(self):
        # Trigger method to open a window for Distance Vector Routing with specified parameters
        self.open_algorithm_window("Distance Vector Routing")

    def open_algorithm_window(self, algorithm):
        # Method to open a window for the specified routing algorithm and input parameters
        self.algorithm_window = tk.Toplevel(self.root)  # Create a new top-level window for the algorithm
        self.algorithm_window.title(f"{algorithm} Parameters")  # Set window title with the algorithm name
        self.algorithm_window.geometry("800x600")  # Set window dimensions

        # Add labels and entry fields for source and destination nodes in the algorithm window
        source_label = tk.Label(self.algorithm_window, text="Source Node:")
        source_label.pack()

        self.source_entry = tk.Entry(self.algorithm_window)  # Entry field for source node
        self.source_entry.pack()

        destination_label = tk.Label(self.algorithm_window, text="Destination Node:")
        destination_label.pack()

        self.destination_entry = tk.Entry(self.algorithm_window)  # Entry field for destination node
        self.destination_entry.pack()

        # Bind validation functions to check the validity of source and destination nodes
        self.source_entry.bind("<KeyRelease>", self.validate_source_destination)
        self.destination_entry.bind("<KeyRelease>", self.validate_source_destination)

        # Button to execute the selected algorithm with the provided source and destination nodes
        self.execute_button = tk.Button(self.algorithm_window, text=f"Execute {algorithm}", state=tk.DISABLED,
                                        command=lambda: self.execute_algorithm(algorithm, self.source_entry.get(), self.destination_entry.get()))
        self.execute_button.pack()

        # Handle window closing event for the algorithm window
        self.algorithm_window.protocol("WM_DELETE_WINDOW", self.exit_algo)

        # Set focus on the algorithm window and prevent interaction with other windows until closed
        self.algorithm_window.grab_set()


    def execute_algorithm(self, algorithm, source, destination):
        # Close the canvas if it exists and prepare for a new visualization
        if self.algo_canvas:
            plt.close()
            self.algo_canvas.get_tk_widget().pack_forget()
            self.algo_canvas = None

        # Check if a network topology exists
        if self.network:
            start_time = time.perf_counter()  # Measure algorithm runtime start

            # Generate the forwarding table using the specified algorithm
            self.network.generate_forwarding_table(algorithm)

            end_time = time.perf_counter()  # Measure algorithm runtime end

            # Visualize the route from source to destination
            G, forwarding_edges = self.network.visualize_route(int(source), int(destination))

            # Set edge colors based on forwarding edges for visualization
            edge_colors = ["red" if edge in forwarding_edges else "black" for edge in G.edges()]

            # Create a new plot figure for route visualization
            plt.figure()
            pos = nx.spring_layout(G)
            labels = nx.get_edge_attributes(G, 'weight')
            nx.draw(G, pos, with_labels=True, edge_color=edge_colors)
            nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)

            # Create a canvas to display the route visualization
            self.algo_canvas = FigureCanvasTkAgg(plt.gcf(), master=self.algorithm_window)
            self.algo_canvas.draw()
            self.algo_canvas.get_tk_widget().pack()

            # Create a new window to display algorithm metrics
            self.metrics_window = tk.Toplevel(self.root)
            self.metrics_window.title(f"{algorithm} Algorithm Metrics")

            # Release focus from algorithm window and set focus on metrics window
            self.algorithm_window.grab_release()
            self.metrics_window.grab_set()

            # Handle window closing event for the metrics window
            self.metrics_window.protocol("WM_DELETE_WINDOW", self.exit_metrics)

            # Create a frame in the metrics window to display algorithm metrics
            metrics_frame = tk.Frame(self.metrics_window)
            metrics_frame.pack()

            # Calculate algorithm runtime in milliseconds
            runtime_ms = (end_time - start_time) * 1000

            # Display various algorithm metrics in the metrics window
            tk.Label(metrics_frame, text=f"Packet Transmission Delay (End-to-End): {self.network.routing_table[int(source)][int(destination)]*(random.random() + 0.7)} milliseconds").pack()
            tk.Label(metrics_frame, text=f"Total Cost of the Path Chosen: {self.network.routing_table[int(source)][int(destination)]}").pack()
            tk.Label(metrics_frame, text=f"Run Time of the Algorithm: {runtime_ms:.6f} milliseconds").pack()
            tk.Label(metrics_frame, text=f"Number of Hop Counts (End-to-End): {len(forwarding_edges)}").pack()

            # Create a frame in the metrics window to display the forwarding table
            forwarding_table_frame = tk.Frame(self.metrics_window)
            forwarding_table_frame.pack()

            tk.Label(forwarding_table_frame, text="Forwarding Table:").pack()

            # Display the forwarding table information for each node in the network
            for node, forwarding_info in self.network.forwarding_table.items():
                tk.Label(forwarding_table_frame, text=f"Node {node}: {forwarding_info}").pack()

            # Button to save metrics to a file
            save_button = tk.Button(self.metrics_window, text="Save", command=lambda: self.save_metrics_to_file(runtime=runtime_ms,
                                                                                                                num_hopes=len(forwarding_edges),
                                                                                                                source=source,
                                                                                                                destination=destination,
                                                                                                                algorithm=algorithm))
            save_button.pack(side=tk.BOTTOM)


    def save_metrics_to_file(self, source, destination, runtime, num_hopes, algorithm):
        # Determine the output file name based on the selected algorithm
        out_file_name = "link_state_routing_algorithm_metrics.txt" if algorithm == "Link State Routing" else "distance_vector_routing_algorithm_metrics.txt"

        # Write the metrics to the output file
        with open(out_file_name, "w") as file:
            file.write("Topology:\n")
            
            # Write the network's adjacency matrix to the file
            for row in self.network.adjacency_matrix:
                file.write(f"\t{row}\n")
            
            file.write("\n")
            file.write("Forwarding Tables:\n")
            
            # Write the forwarding tables information for each node to the file
            for node, forwarding_info in self.network.forwarding_table.items():
                file.write(f"\tNode {node}: {forwarding_info}\n")
            
            # Write various routing metrics to the file
            file.write("\n")
            file.write(f"Source Node: {source}\n")
            file.write(f"Destination Node: {destination}\n")           
            file.write(f"Packet Transmission Delay (End-to-End): {self.network.routing_table[int(source)][int(destination)]*(random.random() + 0.7)} milliseconds\n")
            file.write(f"Total Cost of the Path Chosen: {self.network.routing_table[int(source)][int(destination)]}\n")
            file.write(f"Run Time of the Algorithm: {runtime:.6f} milliseconds\n")
            file.write(f"Number of Hop Counts (End-to-End): {num_hopes}\n")

    def exit_application(self):
        # Check if a canvas exists and close it before destroying the main application window
        if self.canvas:
            plt.close()
        self.root.destroy()  # Destroy the main application window
        sys.exit()  # Exit the application

    def exit_algo(self):
        # Check if an algorithm canvas exists and close it before destroying the algorithm window
        if self.algo_canvas:
            plt.close()
        self.algorithm_window.grab_release()  # Release focus from the algorithm window
        self.algorithm_window.destroy()  # Destroy the algorithm window

    def exit_metrics(self):
        # Release focus from the metrics window and set focus back to the algorithm window
        self.metrics_window.grab_release()
        self.algorithm_window.grab_set()
        self.metrics_window.destroy()  # Destroy the metrics window


# Check if this script is the main entry point of the program
if __name__ == "__main__":
    # Create a Tkinter root window
    root = tk.Tk()
    
    # Create an instance of the NetworkTopologyGUI class, passing the root window as an argument
    app = NetworkTopologyGUI(root)
    
    # Start the main event loop to handle user inputs and events in the GUI
    root.mainloop()
