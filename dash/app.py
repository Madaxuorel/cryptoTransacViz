import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import sys
import json

sys.path.append("../")
from transactions.visualisation import Graph,emptyGraph
from api.etherscan import etherScanApi
from transactions.fraudAccounts import blacklistedAddresses

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
    
    """
    Page html code, modified by callbacks    
    """
    def __init__(self,etherScanApiKey):
        self.currentAddress = ''
        self.blacklist = blacklistedAddresses()
        self.key = etherScanApiKey
        self.app = dash.Dash(__name__)

        # Define the initial layout
        self.app.layout = html.Div([
    html.H1("Network Graph Visualization", style={'textAlign': 'center'}),
    html.Div(
        [
            dcc.Input(
                id='input-field',
                type='text',
                placeholder='Enter an address',
                debounce=True,
                style={'flex': '1', 'marginRight': '10px'}
            ),
            dcc.Dropdown(
                id='dropdown',
                options=[
                    {'label': 'From', 'value': 'from'},
                    {'label': 'To', 'value': 'to'}
                ],
                value='received',  # Default value
                style={'marginRight': '10px'}
            ),
            html.Button('Submit', id='submit-button', n_clicks=0)
        ],
        style={
            'display': 'flex', 
            'justifyContent': 'center', 
            'alignItems': 'center',
            'width': '80%', 
            'margin': '0 auto'
        }
    ),
    dcc.Loading(
        id="loading-1",
        type="default",
        children=[dcc.Graph(id='network-graph',figure=emptyGraph())]
    ),
])
        self.setup_callbacks()
        
        
        
    """
    All callbacks
    """
    def setup_callbacks(self):
        
        @self.app.callback(
            Output('network-graph', 'figure'),
            [Input('submit-button', 'n_clicks')],
            [State('input-field', 'value'), State('dropdown', 'value')]        
            )
        def updateGraph(n_clicks, value, transactionType):
            if n_clicks and value:
                self.currentAddress = value
                # Now use self.currentAddress to update the graph
                self.transactionGraph = Graph(self.key, self.currentAddress,transactionType)
                self.transactionGraph.getTopTransactionData(10)
                toDisplay = self.transactionGraph.createGraphFromDict()
                #toDisplay.update_layout(height=900)
                return toDisplay
            return dash.no_update
         
    def runApp(self):
        self.app.run(debug=True)
    
    
    

page = Page(key)

page.currentAddress = "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"
page.runApp()

