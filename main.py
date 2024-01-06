import random
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
import tkinter.messagebox as msgbox
import time
import sys

class NetworkTopology:
    def __init__(self, num_nodes):
        self.num_nodes = num_nodes
        self.adjacency_matrix = [[0 for _ in range(num_nodes)] for _ in range(num_nodes)]
        self.generate_topology()
        self.routing_table = {}
        self.forwarding_table = {}

    def generate_topology(self):
        # Randomly connect nodes to form a network
        for i in range(self.num_nodes):
            for j in range(i + 1, self.num_nodes):
                if random.random() > 0.5:  # Adjust probability for connection
                    weight = random.randint(1, 10)  # Assign a random weight/cost
                    self.adjacency_matrix[i][j] = weight
                    self.adjacency_matrix[j][i] = weight  # Since it's an undirected graph

    def dijkstra(self, src):
        distances = {node: float('inf') for node in range(self.num_nodes)}
        distances[src] = 0
        visited = [False] * self.num_nodes

        for _ in range(self.num_nodes):
            min_dist = float('inf')
            min_idx = -1

            for i in range(self.num_nodes):
                if not visited[i] and distances[i] < min_dist:
                    min_dist = distances[i]
                    min_idx = i

            visited[min_idx] = True

            for j in range(self.num_nodes):
                if (not visited[j]) and (self.adjacency_matrix[min_idx][j] > 0):
                    new_dist = distances[min_idx] + self.adjacency_matrix[min_idx][j]
                    if new_dist < distances[j]:
                        distances[j] = new_dist

        return distances
    
    def bellman_ford(self, src):
        distances = {node: float('inf') for node in range(self.num_nodes)}
        distances[src] = 0

        for _ in range(self.num_nodes - 1):
            for u in range(self.num_nodes):
                for v in range(self.num_nodes):
                    if self.adjacency_matrix[u][v] > 0:
                        if distances[u] + self.adjacency_matrix[u][v] < distances[v]:
                            distances[v] = distances[u] + self.adjacency_matrix[u][v]

        return distances

    def calculate_routing_table(self, algorithm):
        if algorithm == "Link State Routing":
            self.routing_table = {}
            self.forwarding_table = {}
            for node in range(self.num_nodes):
                self.routing_table[node] = self.dijkstra(node)
        if algorithm == "Distance Vector Routing":
            self.routing_table = {}
            self.forwarding_table = {}
            for node in range(self.num_nodes):
                self.routing_table[node] = self.bellman_ford(node)

    def generate_forwarding_table(self, algorithm):
        self.calculate_routing_table(algorithm)  # Ensure routing table is up to date
        for src in range(self.num_nodes):
            self.forwarding_table[src] = {}
            for dest in range(self.num_nodes):
                if dest != src:
                    next_hop = None
                    available_nodes = []
                    for node, weight in enumerate(self.adjacency_matrix[src]):
                        if weight != 0:
                            available_nodes.append(node)
                    
                    for intermediate_node in available_nodes:
                        if self.routing_table[src][intermediate_node] + self.routing_table[intermediate_node][dest] == self.routing_table[src][dest]:
                            next_hop = intermediate_node
                            break
                    if next_hop == None:
                        self.forwarding_table[src][dest] = dest
                    else:
                        self.forwarding_table[src][dest] = next_hop

    def visualize_topology(self):
        G = nx.Graph()
        for i in range(self.num_nodes):
            for j in range(i + 1, self.num_nodes):
                if self.adjacency_matrix[i][j] > 0:
                    G.add_edge(i, j, weight=self.adjacency_matrix[i][j])

        return G
    
    def visualize_route(self, source, destination):
        G = nx.Graph()

        forwarding_edges = [] 

        for dst in range(self.num_nodes):
            if dst != source:
                start = source
                next_node = self.forwarding_table[source][dst]
                while next_node != dst:
                    G.add_edge(start, next_node, weight=self.adjacency_matrix[start][next_node])
                    if dst == destination:
                        forwarding_edges.append((start, next_node))
                    start =  next_node
                    next_node = self.forwarding_table[next_node][dst]
                G.add_edge(start, next_node, weight=self.adjacency_matrix[start][next_node])
                if dst == destination:
                        forwarding_edges.append((start, next_node))


        return G, forwarding_edges

class NetworkTopologyGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Network Topology Visualization")
        self.root.geometry("800x600")

        self.network = None

        self.num_nodes = None
        self.source_node = None
        self.destination_node = None
        
        self.canvas = None
        self.algo_canvas = None

        self.label_text = tk.StringVar()
        self.label_text.set("Number of Nodes")
        self.label = tk.Label(self.root, textvariable=self.label_text)
        self.label.pack()

        self.num_nodes_entry = tk.Entry(self.root)
        self.num_nodes_entry.pack(side="top")

        self.num_nodes_entry.bind("<KeyRelease>", self.validate_input)

        self.create_topology_button = tk.Button(self.root, text="Create Topology", command=self.generate_topology, state=tk.DISABLED)
        self.create_topology_button.pack()

        # Add Link State Routing button (initially disabled)
        self.link_state_button = tk.Button(self.root, text="Link State Routing", command=self.link_state_routing, state=tk.DISABLED)
        self.link_state_button.pack()

        # Add Distance Vector Routing button (initially disabled)
        self.distance_vector_button = tk.Button(self.root, text="Distance Vector Routing", command=self.distance_vector_routing, state=tk.DISABLED)
        self.distance_vector_button.pack()

        self.root.protocol("WM_DELETE_WINDOW", self.exit_application)

    def validate_input(self, event):
        input_text = self.num_nodes_entry.get()
        if input_text.isdigit() and int(input_text) > 0:
            self.create_topology_button['state'] = tk.NORMAL
        else:
            self.create_topology_button['state'] = tk.DISABLED

    def validate_source_destination(self, event):
        source_text = self.source_entry.get()
        destination_text = self.destination_entry.get()

        if source_text.isdigit() and destination_text.isdigit() and self.network.num_nodes > int(source_text) >= 0 and self.network.num_nodes > int(destination_text) >= 0 and int(source_text) != int(destination_text):
            self.execute_button['state'] = tk.NORMAL
        else:
            self.execute_button['state'] = tk.DISABLED

    def generate_topology(self):
        if self.canvas:
            plt.close()
            self.canvas.get_tk_widget().pack_forget()
            self.canvas = None

        self.num_nodes = int(self.num_nodes_entry.get())

        self.network = NetworkTopology(self.num_nodes)

        # Enable Link State Routing and Distance Vector Routing buttons
        self.link_state_button['state'] = tk.NORMAL
        self.distance_vector_button['state'] = tk.NORMAL

        self.visualize_network()

    def visualize_network(self):
        if self.network:
            G = self.network.visualize_topology()

            plt.figure()
            pos = nx.spring_layout(G)
            labels = nx.get_edge_attributes(G, 'weight')
            nx.draw(G, pos, with_labels=True)
            nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
            self.canvas = FigureCanvasTkAgg(plt.gcf(), master=self.root)
            self.canvas.draw()
            self.canvas.get_tk_widget().pack()

    def link_state_routing(self):
        self.open_algorithm_window("Link State Routing")

    def distance_vector_routing(self):
        self.open_algorithm_window("Distance Vector Routing")

    def open_algorithm_window(self, algorithm):
        self.algorithm_window = tk.Toplevel(self.root)
        self.algorithm_window.title(f"{algorithm} Parameters")
        self.algorithm_window.geometry("800x600")

        source_label = tk.Label(self.algorithm_window, text="Source Node:")
        source_label.pack()

        self.source_entry = tk.Entry(self.algorithm_window)
        self.source_entry.pack()

        destination_label = tk.Label(self.algorithm_window, text="Destination Node:")
        destination_label.pack()

        self.destination_entry = tk.Entry(self.algorithm_window)
        self.destination_entry.pack()

        self.source_entry.bind("<KeyRelease>", self.validate_source_destination)
        self.destination_entry.bind("<KeyRelease>", self.validate_source_destination)

        self.execute_button = tk.Button(self.algorithm_window, text=f"Execute {algorithm}", state=tk.DISABLED,
                                        command=lambda: self.execute_algorithm(algorithm, self.source_entry.get(), self.destination_entry.get()))
        self.execute_button.pack()

        self.algorithm_window.protocol("WM_DELETE_WINDOW", self.exit_algo)

        self.algorithm_window.grab_set()

    def execute_algorithm(self, algorithm, source, destination):
        if self.algo_canvas:
            plt.close()
            self.algo_canvas.get_tk_widget().pack_forget()
            self.algo_canvas = None

        if self.network:
            start_time = time.perf_counter()  # Measure algorithm runtime
            self.network.generate_forwarding_table(algorithm)
            end_time = time.perf_counter()

            G, forwarding_edges = self.network.visualize_route(int(source), int(destination))
            edge_colors = ["red" if edge in forwarding_edges else "black" for edge in G.edges()]
            plt.figure()
            pos = nx.spring_layout(G)
            labels = nx.get_edge_attributes(G, 'weight')
            nx.draw(G, pos, with_labels=True, edge_color=edge_colors)
            nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
            self.algo_canvas = FigureCanvasTkAgg(plt.gcf(), master=self.algorithm_window)
            self.algo_canvas.draw()
            self.algo_canvas.get_tk_widget().pack()

            self.metrics_window = tk.Toplevel(self.root)
            self.metrics_window.title(f"{algorithm} Algorithm Metrics")
            self.algorithm_window.grab_release()
            self.metrics_window.grab_set()

            self.metrics_window.protocol("WM_DELETE_WINDOW", self.exit_metrics)

            metrics_frame = tk.Frame(self.metrics_window)
            metrics_frame.pack()
            
            runtime_ms = (end_time - start_time) * 1000

            tk.Label(metrics_frame, text=f"Packet Transmission Delay (End-to-End): {self.network.routing_table[int(source)][int(destination)]*(random.random() + 0.7)} milliseconds").pack()
            tk.Label(metrics_frame, text=f"Total Cost of the Path Chosen: {self.network.routing_table[int(source)][int(destination)]}").pack()
            tk.Label(metrics_frame, text=f"Run Time of the Algorithm: {runtime_ms:.6f} milliseconds").pack()
            tk.Label(metrics_frame, text=f"Number of Hop Counts (End-to-End): {len(forwarding_edges)}").pack()
            
            forwarding_table_frame = tk.Frame(self.metrics_window)
            forwarding_table_frame.pack()

            tk.Label(forwarding_table_frame, text="Forwarding Table:").pack()

            for node, forwarding_info in self.network.forwarding_table.items():
                tk.Label(forwarding_table_frame, text=f"Node {node}: {forwarding_info}").pack()

            save_button = tk.Button(self.metrics_window, text="Save", command=lambda: self.save_metrics_to_file(runtime=runtime_ms,
                                                                                                                num_hopes=len(forwarding_edges),
                                                                                                                source=source,
                                                                                                                destination=destination,
                                                                                                                algorithm=algorithm))
            save_button.pack(side=tk.BOTTOM)

    def save_metrics_to_file(self, source, destination, runtime, num_hopes, algorithm):
        out_file_name = "link_state_routing_algorithm_metrics.txt" if algorithm == "Link State Routing" else "distance_vector_routing_algorithm_metrics.txt"
        with open(out_file_name, "w") as file:
            file.write("Topology:\n")
            for row in self.network.adjacency_matrix:
                file.write(f"{row}\n")
            file.write("Forwarding Tables:\n")
            for node, forwarding_info in self.network.forwarding_table.items():
                file.write(f"Node {node}: {forwarding_info}\n")
            file.write(f"Packet Transmission Delay (End-to-End): {self.network.routing_table[int(source)][int(destination)]*(random.random() + 0.7)} milliseconds\n")
            file.write(f"Total Cost of the Path Chosen: {self.network.routing_table[int(source)][int(destination)]}\n")
            file.write(f"Run Time of the Algorithm: {runtime:.6f} milliseconds\n")
            file.write(f"Number of Hop Counts (End-to-End): {num_hopes}\n")

    def exit_application(self):
        if self.canvas:
            plt.close()
        self.root.destroy()
        sys.exit()

    def exit_algo(self):
        if self.algo_canvas:
            plt.close()
        self.algorithm_window.grab_release()
        self.algorithm_window.destroy()

    def exit_metrics(self):
        self.metrics_window.grab_release()
        self.algorithm_window.grab_set()
        self.metrics_window.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = NetworkTopologyGUI(root)
    root.mainloop()