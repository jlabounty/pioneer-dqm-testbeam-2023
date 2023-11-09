from dash import Dash, html, dcc, Output, Input, State, callback
from dash.exceptions import PreventUpdate
import json

# This stylesheet makes the buttons and table pretty.
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

import dash
from dash import html
import dash_bootstrap_components as dbc


dash.register_page(__name__)

layout = html.Div(
    [
        html.Div([
            html.H4(id='constants-dump')
        ]),
    ]
)

@callback(Output('constants-dump', 'children'), Input('constants', 'data'))
def update_header(data):
    # print(data)
    ding =  [html.H1(f'Current store value:') ]
    ding.append(html.Pre([json.dumps(json.loads(data),indent=2)]))
    # for x in .split("\n"):
    #     # print(x)
    #     ding.append(html.P(x))
    return ding