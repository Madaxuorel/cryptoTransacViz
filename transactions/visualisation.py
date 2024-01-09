import sys
sys.path.append("../")
import numpy as np
from api import etherscan
import networkx as nx
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import matplotlib
import json

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

    def getTopTransactionData(self,N):
        self.dataToShow = self.api.getTopNAddressesReceived(self.currentAddress,N+1)
        print(self.dataToShow)
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

        # Add a trace for the nodes
        for node in G.nodes():
            x, y = pos[node]
            fig.add_trace(go.Scatter(
                x=[x], y=[y],
                mode='markers+text',
                text=[node,"tto "],
                marker=dict(size=10, color='Black'),
                hoverinfo='text'
            ))

        # Customize the appearance of the graph
        fig.update_layout(
            height=900,
            title=f"Graph of Addresses with Center: {self.currentAddress}",
            showlegend=False,
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor='rgba(0,0,0,0)'  # Transparent background
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

