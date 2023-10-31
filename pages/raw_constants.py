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
    # print(json.dumps(data,indent=2))
    # ding =  [html.H1('Current store value:') ]
    # ding =  [html.H1(f'Current store value: {data}') ]
    ding =  [html.H1(f'Current store value:') ]
    ding =  [html.P(f'{data}') ]
    # for key,x in data.items():
    #     # print(key, x)
    #     if 'traces' in key:
    #         ding += [html.P('traces')]
    #         for i,xi in enumerate(x):
    #             ding += [html.P(f'    Trace {i} -> {xi}')]
    #     else:
    #         ding += [html.P(f'{key}: {x}')]
    # return ding