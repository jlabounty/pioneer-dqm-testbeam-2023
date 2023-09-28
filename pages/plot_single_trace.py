from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import numpy as np
from dash import Dash, html, dcc, Output, Input, State, callback
from dash.exceptions import PreventUpdate
import dash

# app = Dash(__name__)
dash.register_page(__name__)

layout = html.Div([
    html.H4('Plot a single trace'),
    dcc.Dropdown(options=[], id='demo-dropdown'),
    html.Div(id='dd-output-container'),
    dcc.Graph(id="trace"),
])


@callback(
    Output('dd-output-container', 'children'),
    Input('demo-dropdown', 'value')
)
def update_output(value):
    return f'You have selected {value}'

@callback(
    Output('demo-dropdown', 'options'),
    Input('traces', 'data')
)
def update_dropdown_choices(data):
    # return f'You have selected {value}'
    print(f'Updating options...')
    options = []
    print(data.keys())
    print(data['n_hodo'])
    for i in range(data['n_hodo']):
        options.append(f'Hodoscope X {i}')
        options.append(f'Hodoscope Y {i}')
    for i in range(data['n_lyso']):
        options.append(f'LYSO {i}')
    for i in range(data['n_nai']):
        options.append(f'LYSO {i}')
    print(f'   -> {options=}')
    return options

@callback(
    # Output('dd-output-container', 'children'),
    Output("trace", "figure"), 
    Input('demo-dropdown', 'options'),
    Input('demo-dropdown', 'value'),
    Input('traces', 'data')
)
def update_graph(options, value, data):
    # return f'You have selected {value}'
    # if value not in options:
    #     return
    index = list(options).index(value)
    ys = data['traces'][index]
    fig = px.line(
        x=data['samples'], y=ys
    )
    return fig
