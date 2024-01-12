import dash
from dash import dcc,html,callback_context
from dash.dependencies import Input, Output, State
import sys
import json
import networkx as nx

sys.path.append("../")
from transactions.visualisation import Graph,emptyGraph
from api.etherscan import etherScanApi
from transactions.fraudAccounts import blacklistedAddresses

key = "TWUQ778V3WRVAW2EBX1XZZ9BNHDGQN442B"
"""
Reads the credentials 
TODO : move to separate file + security
"""
def readCreds():
    try:
        with open("../utils/keys.json", 'r') as json_file:
            credentials = json.load(json_file)
            return credentials
    except FileNotFoundError:
        print("Config file not found.")
        return None

"""
Main webapp object, contains the vars and methods to display the graph and update it. 
"""
class Page():

    """
    Initialise the page layout
    """
    def __init__(self,etherScanApiKey):
        self.currentAddress = ''
        self.blacklist = blacklistedAddresses()
        self.key = etherScanApiKey
        self.app = dash.Dash(__name__, suppress_callback_exceptions=True,
                             prevent_initial_callbacks='initial_duplicate')

        # Define the initial layout
        self.app.layout = html.Div([
    html.H1("Network Graph Visualization", style={'textAlign': 'center'}),
    html.Div(id='dummy-output', style={'display': 'none'}),
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
            
        """
        Reads the input in the search bar + the search category, or the clicked node,
        and generates a new graph from it.
        """
        @self.app.callback(
            Output('network-graph', 'figure'),
            [Input('submit-button', 'n_clicks'), Input('network-graph', 'clickData')],
            [State('input-field', 'value'), State('dropdown', 'value')]
        )
        def update_graph(n_clicks, clickData, value, transactionType):
            # Determine which input triggered the callback
            ctx = callback_context
            trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
            if trigger_id == 'submit-button' and value:
                
                self.currentAddress = value
                self.transactionGraph = Graph(self.key, self.currentAddress, transactionType)
                self.transactionGraph.getTopTransactionData(10)
                self.transactionGraph.createNetworkXGraph()
                print(self.transactionGraph.G)
                self.transactionGraph.createPlotlyFigure()
                return self.transactionGraph.fig
            
            elif trigger_id == 'network-graph' and clickData:
                clicked_node = clickData['points'][0]['text'].split('<br>')[0].split(":")[1].strip()
                
                newGraph = Graph(self.key,clicked_node,transactionType)
                newGraph.getTopTransactionData(10)       
                newGraph.createNetworkXGraph()
                newGraph.mergeWith(self.transactionGraph)
                
                print(newGraph.G)
                newGraph.createPlotlyFigure()
                self.transactionGraph = newGraph
                
                return self.transactionGraph.fig

            return dash.no_update
            
        
        
    
    """
    Runs the app.
    """
    def runApp(self):
        self.app.run(debug=True)
    
    
    

page = Page(key)
page.runApp()

