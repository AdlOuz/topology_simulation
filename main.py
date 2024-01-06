import random
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
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

    def calculate_routing_table(self):
        for node in range(self.num_nodes):
            self.routing_table[node] = self.dijkstra(node)

    def generate_forwarding_table(self):
        self.calculate_routing_table()  # Ensure routing table is up to date
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


class NetworkTopologyGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Network Topology Visualization")
        self.root.geometry("800x600")

        self.num_nodes = None
        self.network = None
        self.canvas = None

        self.label_text = tk.StringVar()
        self.label_text.set("Number of Nodes")
        self.label = tk.Label(self.root, textvariable=self.label_text)
        self.label.pack()

        self.num_nodes_entry = tk.Entry(self.root)
        self.num_nodes_entry.pack(side="top")

        self.num_nodes_entry.bind("<KeyRelease>", self.validate_input)

        self.create_topology_button = tk.Button(self.root, text="Create Topology", command=self.generate_topology, state=tk.DISABLED)
        self.create_topology_button.pack()

        self.root.protocol("WM_DELETE_WINDOW", self.exit_application)

    def validate_input(self, event):
        input_text = self.num_nodes_entry.get()
        if input_text.isdigit() and int(input_text) > 0:
            self.create_topology_button['state'] = tk.NORMAL
        else:
            self.create_topology_button['state'] = tk.DISABLED

    def generate_topology(self):
        if self.canvas:
            plt.close()
            self.canvas.get_tk_widget().pack_forget()
            self.canvas = None

        self.num_nodes = int(self.num_nodes_entry.get())

        self.network = NetworkTopology(self.num_nodes)

        self.network.calculate_routing_table()
        self.network.generate_forwarding_table()

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

    def exit_application(self):
        if self.canvas:
            plt.close()
        self.root.destroy()
        sys.exit()

if __name__ == "__main__":
    root = tk.Tk()
    app = NetworkTopologyGUI(root)
    root.mainloop()