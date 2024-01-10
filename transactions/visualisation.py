import sys
sys.path.append("../")
sys.path.append("../transactions")
import numpy as np
from api import etherscan
import networkx as nx
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import matplotlib
import json
from transactions.fraudAccounts import blacklistedAddresses

TESTADDRESS = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"

def readCreds():
    try:
        with open("../utils/keys.json", 'r') as json_file:
            credentials = json.load(json_file)
            return credentials
    except FileNotFoundError:
        print("Config file not found.")
        return None


class Graph():
    def __init__(self,key,address):
        self.currentAddress = address.lower()
        self.api = etherscan.etherScanApi(key)

    def getTopTransactionData(self,N,transactionType):
        if transactionType == "from":
            self.dataToShow = self.api.getTopNAddressesReceived(self.currentAddress,N+1)
            try:
                self.dataToShow.pop(self.currentAddress)
            except KeyError as k:
                print(f"Nothing to pop on {self.currentAddress}")
        elif transactionType == "to":
            self.dataToShow = self.api.getTopNAddressesSent(self.currentAddress,N+1)
            try:
                self.dataToShow.pop(self.currentAddress)
            except KeyError as k:
                print(f"Nothing to pop on {self.currentAddress}")
            
        
    
    def createGraphFromDict(self):
        # Initialize a NetworkX graph and add the central node
        G = nx.Graph()
        G.add_node(self.currentAddress)

        # Add edges to the NetworkX graph with 'timesUsed' as the weight
        for address, timesUsed in self.dataToShow.items():
            G.add_edge(self.currentAddress, address, weight=timesUsed)

        # Apply spring layout to position nodes
        pos = nx.spring_layout(G)

        # Create a plotly graph
        fig = go.Figure()

        # Add edges to the graph with a color gradient based on 'timesUsed'
        for edge in G.edges(data=True):
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            weight = edge[2]['weight']
            # Normalize the weight to a 0-1 range for the color scale
            normalized_weight = weight / max(self.dataToShow.values())
            # Convert the normalized weight to a color
            color = plt.cm.viridis(normalized_weight)
            color = matplotlib.colors.rgb2hex(color)
        
            fig.add_trace(go.Scatter(
                x=[x0, x1, None],  # Add None to create a segment
                y=[y0, y1, None],
                line=dict(width=2, color=color),
                mode='lines'
            ))

        # Assume 'addresses' is a list of address strings that you want to color red
        addresses =  blacklistedAddresses() # Populate this list with the actual addresses

        # Create a color map based on whether the node address is in the 'addresses' list
        node_color_map = ['red' if node in addresses else 'black' for node in G.nodes()]
        isFraud = 'red' in node_color_map
        annotations = []
        if isFraud:
            annotations.append(
                go.layout.Annotation(
                    text="This address has been reported as fraud",
                    font=dict(size=16, color='red'),
                    xref="paper",
                    yref="paper",
                    showarrow=True,
                )
            )
        
        
        # Add a trace for the nodes
        node_x = []
        node_y = []
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)

        # Create the node trace using the color map
        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            text=list(G.nodes()),  # Or any other text you want to display
            marker=dict(
                size=10,
                color=node_color_map,  # Use the color map here
                line=dict(width=2)
            ),
            hoverinfo='text'
        )

        # Add the node trace to the figure
        fig.add_trace(node_trace)



        
        
        # Customize the appearance of the graph
        fig.update_layout(
            height=900,
            title=f"Graph of Addresses with Center: {self.currentAddress}",
            showlegend=False,
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor='rgba(0,0,0,0)',  # Transparent background
            annotations=annotations
        )

        # Show the graph
        return fig


def emptyGraph():
        initial_figure = go.Figure(
            data=[],
            layout=go.Layout(
                height=900,
                title="Enter an address to display the network graph",
                xaxis={'visible': False},
                yaxis={'visible': False},
                annotations=[
                    {
                        "text": "No data yet - please enter an address.",
                        "xref": "paper",
                        "yref": "paper",
                        "showarrow": False,
                        "font": {
                            "size": 20
                        }
                    }
                ]
            )
        )
        return initial_figure

