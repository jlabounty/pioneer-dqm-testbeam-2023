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


# @callback(
#     Output('dd-output-container', 'children'),
#     Input('demo-dropdown', 'value')
# )
# def update_output(value):
#     return f'You have selected {value}'

@callback(
    Output('demo-dropdown', 'options'),
    Input('traces', 'data')
)
def update_dropdown_choices(data):
    # return f'You have selected {value}'
    # print(f'Updating options...')
    options = []
    # print(data.keys())
    for i in range(data['n_lyso']):
        options.append(f'LYSO {i}')
    for i in range(data['n_hodo_x']):
        options.append(f'Hodoscope X {i}')
    for i in range(data['n_hodo_y']):
        options.append(f'Hodoscope Y {i}')
    for i in range(data['n_nai']):
        options.append(f'NaI {i}')
    for i in range(data['n_t0']):
        options.append(f'T0 {i}')
    # print(f'   -> {options=}')
    return options

@callback(
    # Output('dd-output-container', 'children'),
    Output("trace", "figure"), 
    Input('demo-dropdown', 'options'),
    Input('demo-dropdown', 'value'),
    Input('traces', 'data'),
    Input('trace', 'figure')
)
def update_graph(options, value, data, existing_figure):
    # return f'You have selected {value}'
    # if value not in options:
    #     return
    # index = list(options).index(value)
    # if(value is None):
    #     return existing_figure
    index = int(value.split(" ")[-1])
    if 'Hodoscope X' in value:
        key = 'traces_hodo_x'
    elif 'Hodoscope Y' in value:
        key = 'traces_hodo_y'
    elif 'LYSO' in value:
        key = 'traces_lyso'
    elif 'NaI' in value:
        key = 'traces_nai'
    elif 'T0' in value:
        key = 'traces_t0'
    else:
        print("Warning: no trace found for selection", value)
    ys = data[key][index]
    samples = list(range(len(ys)))
    fig = px.line(
        x=samples, y=ys
    )
    return fig
