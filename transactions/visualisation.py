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
        print("new graph init")
        self.transactionType = transactionType
        self.currentAddress = address.lower()
        self.api = etherscan.etherScanApi(key)

    def getTopTransactionData(self,N):
        if self.transactionType == "from":
            self.dataToShow = self.api.getTopNAddressesReceived(self.currentAddress,N+1)
            try:
                #self.dataToShow.pop(self.currentAddress)
                self.dataToShow.pop('')
            except KeyError as k:
                print(f"Nothing to pop on {self.currentAddress}")
        elif self.transactionType == "to":
            self.dataToShow = self.api.getTopNAddressesSent(self.currentAddress,N+1)
            try:
                #self.dataToShow.pop(self.currentAddress)
                self.dataToShow.pop('')
            except KeyError as k:
                print(f"Nothing to pop on {self.currentAddress}")
    
            
    
    def getNumberOfTransactions(self,account):
        
        return self.dataToShow[account]
    
    
    def createNetworkXGraph(self):
        print(f"creating graph from center {self.currentAddress}")
        self.G = nx.Graph()
        self.G.add_node(self.currentAddress)

        for address, timesUsed in self.dataToShow.items():
            self.G.add_edge(self.currentAddress, address, weight=timesUsed)

    def createPlotlyFigure(self,):
        if self.G is None:
            raise ValueError("NetworkX graph not created yet")
    
        pos = nx.spring_layout(self.G)
        fig = go.Figure()

        # Add edges to the graph
        for edge in self.G.edges(data=True):
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
        node_color_map = ['red' if node in addresses else 'black' for node in self.G.nodes()]
        isFraud = 'red' in node_color_map
        
        # Add a trace for the nodes
        node_x, node_y, hover_text = [], [], []
        for node in self.G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)

            # Multi-line hover text for each node
            if node != self.currentAddress:
                #totalEth = self.api.getEthValueTransferred(node,self.transactionType)/1000000000000000000
                #totalUsd = totalEth * self.api.getEthValue()
                node_hover_text = f"Address: {node}<br>Transactions: {self.getNumberOfTransactions(node)}<br>Total transaction value (eth): aaa eth<br>Total transaction value (usd): aaa"
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
        self.fig = fig
        
        
    def mergeWith(self,otherGraph):
        self.G = nx.compose(self.G,otherGraph.G)
        self.dataToShow.update(otherGraph.dataToShow)
    


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
