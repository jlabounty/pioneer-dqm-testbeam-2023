from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import plotly.subplots
import plotly.graph_objects as go
import plotly
import numpy as np
from dash import Dash, html, dcc, Output, Input, State, callback
from dash.exceptions import PreventUpdate
import dash
import dash_daq as daq
import dash_bootstrap_components as dbc

# app = Dash(__name__)
dash.register_page(__name__)

layout = html.Div([
    html.H4('LED Monitor Traces'),
    dcc.Graph(id="led-monitor-trace"),
    # html.Div([
    # ]),
])

@callback(
    Output("led-monitor-trace", "figure"), 
    Input('traces', 'data')
)
def update_led_monitor_trace(data):
    fig = plotly.subplots.make_subplots()
    print(data.keys())
    for i,trace in enumerate(data['traces_monitor']):
        print(f"{data['integrals_monitor']=}")
        samples = list(range(len(trace)))
        fig.add_trace(
            go.Scatter(
                x=samples,
                y=trace,
                # label=f'T0 {i}'
                name=f'Monitor {i}'
                # orientation='h'
            ),
        )
    return fig
