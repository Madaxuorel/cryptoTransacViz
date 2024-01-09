import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import sys
import json

sys.path.append("../")
from transactions.visualisation import Graph,emptyGraph
from api.etherscan import etherScanApi

TESTADDRESS = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
key = "TWUQ778V3WRVAW2EBX1XZZ9BNHDGQN442B"
def readCreds():
    try:
        with open("../utils/keys.json", 'r') as json_file:
            credentials = json.load(json_file)
            return credentials
    except FileNotFoundError:
        print("Config file not found.")
        return None


class Page():
    
    def __init__(self,etherScanApiKey):
        self.currentAddress = ''
        self.key = etherScanApiKey
        self.app = dash.Dash(__name__)

        # Define the initial layout
        self.app.layout = html.Div([
            html.H1("Network Graph Visualization"),
            dcc.Input(id='input-field', type='text', placeholder='Enter an address', debounce=True),
            html.Button('Submit', id='submit-button', n_clicks=0),
            dcc.Loading(id="loading-1",type="circle", children=[dcc.Graph(id='network-graph',figure=emptyGraph())]),
        ])
        self.setup_callbacks()
        
    def setup_callbacks(self):
        
        @self.app.callback(
            Output('network-graph', 'figure'),
            [Input('submit-button', 'n_clicks')],
            [State('input-field', 'value')]
        )
        def updateGraph(n_clicks, value):
            if n_clicks and value:
                self.currentAddress = value
                # Now use self.currentAddress to update the graph
                self.transactionGraph = Graph(self.key, self.currentAddress)
                self.transactionGraph.getTopTransactionData(10)
                return self.transactionGraph.createGraphFromDict()
            return dash.no_update
         
    def runApp(self):
        self.app.run(debug=True)
    
    

page = Page(key)

page.currentAddress = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
page.runApp()

