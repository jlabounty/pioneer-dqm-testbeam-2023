from dash import Dash, html, dcc, Output, Input, State, callback
from dash.exceptions import PreventUpdate
import json

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
            html.H4(id='store-dump')
        ]),
    ]
)

@callback(Output('store-dump', 'children'), Input('traces', 'data'))
def update_header(data):
    # print(json.dumps(data,indent=2))
    # ding =  [html.H1('Current store value:') ]
    print(type(data), type(data['n_hodo']))
    # ding =  [html.H1(f'Current store value: {data}') ]
    ding =  [html.H1(f'Current store value:') ]
    for key,x in data.items():
        # print(key)
        if 'traces' in key:
            ding += [html.P('traces')]
            for i,xi in enumerate(x):
                ding += [html.P(f'    Trace {i} -> {xi}')]
        else:
            ding += [html.P(f'{key}: {x}')]
    return ding