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
    html.H4('Hodoscope Traces'),
    html.Div([
        dbc.Row([
            dbc.Col([
                dbc.Checklist(
                    options=[
                        # {"label": "Autoscale X", "value": 1},
                        # {"label": "Log X", "value": 2},
                        {"label": "Autoscale Y", "value": 3},
                        # {"label": "Log Y", "value": 4},
                    ],
                    value=[],
                    id="hodo-traces-options",
                    # inline=True,
                    switch=True,
                ),
            ]),
            dbc.Col([
                dbc.Label("Y Low [ADC Units]"),
                dbc.Input(
                    # label='Y Low [ADC Units]',
                    # labelPosition='bottom',
                    id='hodo-traces-limit-low',
                    type='number',
                    value=-10,
                ),
            ]),
            dbc.Col([
                dbc.Label("Y High [ADC Units]"),
                dbc.Input(
                    # label='Y High [ADC Units]',
                    # labelPosition='bottom',
                    id='hodo-traces-limit-high',
                    type='number',
                    value=300,
                ),
            ]),

        ])
    ]),
    dcc.Graph(id="hodo-traces"),
    # html.Div([
    # ]),
])

@callback(
    Output("hodo-traces", "figure"), 
    Input('traces', 'data'),
    Input('hodo-traces-limit-low', 'value'),
    Input('hodo-traces-limit-high', 'value'),
    Input('hodo-traces-options', 'value'),
)
def update_graph(data, low, high, options):
    # return f'You have selected {value}'
    # if value not in options:
    #     return
    fig = plotly.subplots.make_subplots(
        # rows=data['n_hodo_x'], cols=2,
        cols=data['n_hodo_x'], rows=2,
        # specs = [[{'colspan': 1},{'colspan': 1},{'colspan': 1},{'colspan': 1},{'colspan': 1},{'colspan': 1},{'colspan': 2, 'rowspan':2},None]]*3,
        # specs=[
        # ],
        shared_xaxes='all',
        shared_yaxes='all',
        subplot_titles=[f'X{i}' for i in range(data['n_hodo_x'])]+[f'Y{i}' for i in range(data['n_hodo_x'])],
        # print_grid=True,
        # vertical_spacing=0.075,
        # horizontal_spacing=0.08,
        # row_heights=[1500,]*data['n_hodo_x'],
        # figsize= (500, 1500)
    )

    for i in range(data['n_hodo_x']):
        samples_x = list(range(len(data['traces_hodo_x'][i])))
        fig.add_trace(go.Scatter(
            x=samples_x, 
            y=data['traces_hodo_x'][i],
            name = f'HODO X{i}'
            ), 
                    #   title=f'X{i}',
                      col=i+1,
                      row=1 )

        samples_y = list(range(len(data['traces_hodo_y'][i])))
        fig.add_trace(go.Scatter(
            x=samples_y, 
            y=data['traces_hodo_y'][i],
            name = f'HODO Y{i}'
            ), 
            # label=f'Y{i}',
                col=i+1,
                row=2 )
    # fig.update_layout(autosize=True, height=2200, width=1200)
    fig.update_layout(autosize=True,
        height=700,
    )
    if( 3 not in options ):
        fig.update_yaxes(range=[low,high])
    return fig