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

    def generate_topology(self):
        # Randomly connect nodes to form a network
        for i in range(self.num_nodes):
            for j in range(i + 1, self.num_nodes):
                if random.random() > 0.6:  # Adjust probability for connection
                    weight = random.randint(1, 10)  # Assign a random weight/cost
                    self.adjacency_matrix[i][j] = weight
                    self.adjacency_matrix[j][i] = weight  # Since it's an undirected graph

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

        # Setting a larger window size
        self.root.geometry("800x600")

        self.num_nodes = None
        self.network = None
        self.canvas = None

        self.label_text = tk.StringVar()
        self.label_text.set("Number of Nodes")
        self.label = tk.Label(self.root, textvariable=self.label_text)
        self.label.pack()

        self.num_nodes_entry = tk.Entry(self.root)
        self.num_nodes_entry.pack(side="top")  # Centering with padding

        self.num_nodes_entry.bind("<KeyRelease>", self.validate_input)  # Validate input on key release

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
            plt.close()  # Close the matplotlib figure
            self.canvas.get_tk_widget().pack_forget()
            self.canvas = None

        self.num_nodes = int(self.num_nodes_entry.get())

        self.network = NetworkTopology(self.num_nodes)
        self.visualize_network()

    def visualize_network(self):
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
            plt.close()  # Close the matplotlib figure
        self.root.destroy()
        sys.exit()

if __name__ == "__main__":
    root = tk.Tk()
    app = NetworkTopologyGUI(root)
    root.mainloop()
