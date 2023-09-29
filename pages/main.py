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
    html.H4('Plot an array of traces'),
    html.Div([
        dcc.Graph(id="t0-trace" , style={'display': 'inline-block'}),
        # dcc.Graph(id="t0-proton" , style={'display': 'inline-block'}),
        dcc.Graph(id="hodo-bar", style={'display': 'inline-block'}),
        # html.Div([
        #     dcc.Graph(id="hodo-y-bar", style={'display': 'inline-block'}),
        # ]),
    ]),
    html.Div([
        dcc.Graph(id="hodo-array" , style={'display': 'inline-block'}),
        dcc.Graph(id="trace-array", style={'display': 'inline-block'}),
    ]),
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
            'x':list(range(data['n_hodo'])),
            'y':data['integrals'][data['hod_x'][0]:data['hod_x'][1]]
        }),
        row = 1, col=1
    )

    fig.add_trace(
        go.Bar({
            'x':list(range(data['n_hodo'])),
            'y':data['integrals'][data['hod_y'][0]:data['hod_y'][1]],
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
    return px.line(
        x=data['samples'],
        y=data['t0_trace'],
        title='T0 Profile',
        # ylabel='ADC Counts',
        # xlabel='Sample Number'
        labels={
            'x':'Sample Number',
            'y':'ADC Counts'
        }
    )