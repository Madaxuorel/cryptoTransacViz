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
    def __init__(self,key,address,transactionType):
        self.transactionType = transactionType
        self.currentAddress = address.lower()
        self.api = etherscan.etherScanApi(key)

    def getTopTransactionData(self,N):
        if self.transactionType == "from":
            self.dataToShow = self.api.getTopNAddressesReceived(self.currentAddress,N+1)
            try:
                self.dataToShow.pop(self.currentAddress)
                self.dataToShow.pop('')
            except KeyError as k:
                print(f"Nothing to pop on {self.currentAddress}")
        elif self.transactionType == "to":
            self.dataToShow = self.api.getTopNAddressesSent(self.currentAddress,N+1)
            try:
                self.dataToShow.pop(self.currentAddress)
                self.dataToShow.pop('')
            except KeyError as k:
                print(f"Nothing to pop on {self.currentAddress}")
    
            
    
    def getNumberOfTransactions(self,account):
        
        return self.dataToShow[account]
    
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

        # Add edges to the graph
        for edge in G.edges(data=True):
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            weight = edge[2]['weight']
            normalized_weight = weight / max(self.dataToShow.values())
            color = plt.cm.viridis(normalized_weight)
            color = matplotlib.colors.rgb2hex(color)

            fig.add_trace(go.Scatter(
                x=[x0, x1, None],
                y=[y0, y1, None],
                line=dict(width=2, color=color),
                mode='lines'
            ))

        # Check for fraudulent addresses
        addresses = blacklistedAddresses()
        node_color_map = ['red' if node in addresses else 'black' for node in G.nodes()]
        isFraud = 'red' in node_color_map

        # Add a trace for the nodes
        node_x, node_y, hover_text = [], [], []
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)

            # Multi-line hover text for each node
            if node != self.currentAddress:
                totalEth = self.api.getEthValueTransferred(node,self.transactionType)
                print(totalEth)
                node_hover_text = f"Address: {node}<br>Transactions: {self.getNumberOfTransactions(node)}<br>Total transaction value (eth): {totalEth/1000000000000000000} eth<br>Total transaction value (usd): $test"
            else:
                node_hover_text = f"Address: {node}"
            hover_text.append(node_hover_text)

        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers',
            text=hover_text,
            marker=dict(size=10, color=node_color_map, line=dict(width=2)),
            hoverinfo='text'
        )

        fig.add_trace(node_trace)

        # Add annotations for fraud alert
        annotations = []
        if isFraud:
            annotations.append(
                go.layout.Annotation(
                    text="This address has been reported as fraud",
                    xref="paper",
                    yref="paper",
                    x=0.5,
                    y=1.1,
                    showarrow=False,
                    font=dict(size=16, color='red'),
                    align='center'
                )
            )

        # Customize the appearance of the graph
        fig.update_layout(
            height=900,
            title=f"Graph of Addresses with Center: {self.currentAddress}",
            showlegend=False,
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor='rgba(0,0,0,0)',
            annotations=annotations
        )

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

