from dash import Dash, html, dcc, Output, Input, State, callback
from dash.exceptions import PreventUpdate
import json
import jsonpickle

# This stylesheet makes the buttons and table pretty.
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

import dash
from dash import html

dash.register_page(__name__)

# layout = html.Div([
#     html.H1('This is our Archive page'),
#     html.Div('This is our Archive page content.'),
# ])

layout = html.Div(
    [
        html.Div([
            html.H4(id='histogram-store-dump')
        ]),
    ]
)

@callback(Output('histogram-store-dump', 'children'), Input('histograms', 'data'))
def update_header(data):
    # print(json.dumps(data,indent=2))
    ding =  [html.H1('Current histogram values:') ]
    ding.append(html.Pre([json.dumps(json.loads(data),indent=2)]))
    
    return ding