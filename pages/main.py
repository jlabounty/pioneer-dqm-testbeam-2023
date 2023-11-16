from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import plotly.subplots
import plotly.graph_objects as go
import plotly
import numpy as np
from dash import Dash, html, dcc, Output, Input, State, callback
from dash.exceptions import PreventUpdate
import dash

# app = Dash(__name__)
dash.register_page(__name__, path='/')

layout = html.Div([
    # html.H4('Plot an array of traces'),
    html.Div([
        dcc.Graph(id="t0-trace" , style={'display': 'inline-block'}),
        dcc.Graph(id="trace-array", style={'display': 'inline-block'}),
        # dcc.Graph(id="nai-array", style={'display': 'inline-block'}),
    ]),
    html.Div([
        # dcc.Graph(id="hodo-array" , style={'display': 'inline-block'}),
        dcc.Graph(id="hodo-hist" , style={'display': 'inline-block'}),
        dcc.Graph(id="hodo-bar", style={'display': 'inline-block'}),
    ]),
    html.Div([
        dcc.Graph(id="nai-array", style={'display': 'inline-block'}),
    ])
])

@callback(
    Output("hodo-bar", "figure"), 
    # Output("hodo-y-bar", "figure"), 
    Input('traces', 'data')
)
def update_hodo_bar(data):
    fig = plotly.subplots.make_subplots(rows=2,cols=1)
    # fig2 = plotly.subplots.make_subplots()

    fig.add_trace(
        go.Bar({
            'x':list(range(data['n_hodo_x'])),
            'y':data['integrals_hodo_x']
        }),
        row = 1, col=1
    )

    fig.add_trace(
        go.Bar({
            'x':list(range(data['n_hodo_y'])),
            'y':data['integrals_hodo_y']
            },
            # orientation='h'
        ),
        row = 2, col=1
    )

    return fig

@callback(
    Output("t0-trace", "figure"), 
    Input('traces', 'data')
)
def update_t0_trace(data):
    fig = plotly.subplots.make_subplots()
    for i,t0_trace in enumerate(data['traces_t0']):
        samples = list(range(len(t0_trace)))
        fig.add_trace(
            go.Scatter(
                x=samples,
                y=t0_trace,
                # label=f'T0 {i}'
                # orientation='h'
            ),
        )
    return fig