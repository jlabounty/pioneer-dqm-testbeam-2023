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
    html.H4('RF Traces'),
    dcc.Graph(id="rf-trace"),
    dcc.Graph(id="rf-overlay-t0"),
    dcc.Graph(id="rf-overlay-lyso"),
    # html.Div([
    # ]),
])

@callback(
    Output("rf-trace", "figure"), 
    Input('traces', 'data')
)
def update_rf_trace(data):
    print("processing rf data...")
    print(f'{data.keys()=}')
    print(f"{len(data['traces_rf'])=}")
    fig = plotly.subplots.make_subplots()
    for i,t0_trace in enumerate(data['traces_rf']):
        print(i, t0_trace)
        samples = list(range(len(t0_trace)))
        fig.add_trace(
            go.Scatter(
                x=samples,
                y=t0_trace,
                # label=f'T0 {i}'
                # name='RF'
                # orientation='h'
            ),
        )
    return fig

@callback(
    Output("rf-overlay-t0", "figure"), 
    Input('traces', 'data')
)
def update_rf_overlay(data):
    fig = plotly.subplots.make_subplots(
        specs=[[{"secondary_y": True}]]
    )
    for i,t0_trace in enumerate(data['traces_rf']):
        samples = list(range(len(t0_trace)))
        fig.add_trace(
            go.Scatter(
                x=samples,
                y=t0_trace,
                # label=f'T0 {i}'
                name='RF',
                line_color='grey',
                # orientation='h'
            ),
            secondary_y=False
        )

    names = ['T0', 'VETO', 'RF', 'MON1', 'MON2']
    for i,t0_trace in enumerate(data['traces_t0']):
        samples = list(range(len(t0_trace)))
        fig.add_trace(
            go.Scatter(
                x=samples,
                y=t0_trace,
                # label=f'T0 {i}'
                name=names[i],
                # color='grey'
                # orientation='h'
            ),
            secondary_y=True
        )
    return fig

@callback(
    Output("rf-overlay-lyso", "figure"), 
    Input('traces', 'data')
)
def update_rf_overlay_lyso(data):
    fig = plotly.subplots.make_subplots(
        specs=[[{"secondary_y": True}]]
    )
    for i,t0_trace in enumerate(data['traces_rf']):
        samples = list(range(len(t0_trace)))
        fig.add_trace(
            go.Scatter(
                x=samples,
                y=t0_trace,
                # label=f'T0 {i}'
                name='RF',
                line_color='grey',
                # orientation='h'
            ),
            secondary_y=False
        )

    # names = ['T0', 'VETO', 'RF', 'MON1', 'MON2']
    for i,t0_trace in enumerate(data['traces_lyso']):
        samples = list(range(len(t0_trace)))
        fig.add_trace(
            go.Scatter(
                x=samples,
                y=t0_trace,
                # label=f'T0 {i}'
                name=f'LYSO {i}',
                # color='grey'
                # orientation='h'
            ),
            secondary_y=True
        )
    return fig

