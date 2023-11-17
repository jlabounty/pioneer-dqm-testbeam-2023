from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import numpy as np
from dash import Dash, html, dcc, Output, Input, State, callback
from dash.exceptions import PreventUpdate
import dash
import jsonpickle
import hist
import analysis.helpers as helpers
import plotly
import dash_daq as daq
import dash_bootstrap_components as dbc

# app = Dash(__name__)
dash.register_page(__name__)

layout = html.Div([
    html.H4('Plot a single histogram'),
    html.Div([
        dbc.Row([
            dbc.Col([
                    dbc.Checklist(
                        options=[
                            {"label": "Autoscale X", "value": 1},
                            {"label": "Log X", "value": 2},
                            {"label": "Autoscale Y", "value": 3},
                            {"label": "Log Y", "value": 4},
                        ],
                        value=[1,3],
                        id="single-hist-options",
                        # inline=True,
                        switch=True,
                    ),
            ]),
            dbc.Col([
                dbc.Label("X Low"),
                dbc.Input(
                    # label='Y Low [ADC Units]',
                    # labelPosition='bottom',
                    id='single-hist-x-limit-low',
                    type='number',
                    value=0,
                ),
            ]),
            dbc.Col([
                dbc.Label("X High"),
                dbc.Input(
                    # label='Y High [ADC Units]',
                    # labelPosition='bottom',
                    id='single-hist-x-limit-high',
                    type='number',
                    value=100_000,
                ),
            ]),
            dbc.Col([
                dbc.Label("Y Low"),
                dbc.Input(
                    # label='Y Low [ADC Units]',
                    # labelPosition='bottom',
                    id='single-hist-y-limit-low',
                    type='number',
                    value=0,
                ),
            ]),
            dbc.Col([
                dbc.Label("Y High"),
                dbc.Input(
                    # label='Y High [ADC Units]',
                    # labelPosition='bottom',
                    id='single-hist-y-limit-high',
                    type='number',
                    value=300,
                ),
            ]),

        ])
    ]),
    html.Div([
        dcc.Dropdown(options=[], id='hist-dropdown'),
    ]),
    html.Div(id='hist-output-container'),
    dcc.Graph(id="single-hist"),
])


# @callback(
#     Output('dd-output-container', 'children'),
#     Input('demo-dropdown', 'value')
# )
# def update_output(value):
#     return f'You have selected {value}'

@callback(
    Output('hist-dropdown', 'options'),
    Input('histograms', 'data')
)
def update_dropdown_choices(data):
    # return f'You have selected {value}'
    # print(f'Updating options...')
    hists = jsonpickle.decode(data)
    return [x for x in hists if 'reference' not in x]

@callback(
    # Output('dd-output-container', 'children'),
    Output("single-hist", "figure"), 
    Input('hist-dropdown', 'options'),
    Input('hist-dropdown', 'value'),
    Input('histograms', 'data'),
    Input('single-hist', 'figure'),
    Input('single-hist-x-limit-low', 'value'),
    Input('single-hist-x-limit-high', 'value'),
    Input('single-hist-y-limit-low', 'value'),
    Input('single-hist-y-limit-high', 'value'),
    Input('single-hist-options', 'value'),
)
def update_graph(options, value, data, existing_figure, xlow, xhigh, ylow, yhigh, scale_controls):
    print(f'{scale_controls=}')
    hists = jsonpickle.decode(data)
    fig = plotly.subplots.make_subplots()
    hc = hists[value]
    match len(hc.axes):
        case 1:
            fig.add_trace(
                helpers.hist_to_plotly_bar(hc, name=value),
            )
        case 2:
            fig.add_trace(
                helpers.hist_to_plotly_2d(hc, name=value),
            )
    
    # {"label": "Autoscale X", "value": 1},
    #                         {"label": "Log X", "value": 2},
    #                         {"label": "Autoscale Y", "value": 3},
    #                         {"label": "Log Y", "value": 4},
    if 1 in scale_controls:
        match len(hc.axes):
            case 1:
                xmax = hc.axes[0].edges[np.where(hc.values() > 0)][-1] + hc.axes[0].widths[0]
                print(f'{xmax=}')
                fig.update_xaxes(range=[0,xmax])
            case 2:
                pass
    else:
        fig.update_xaxes(range=[xlow,xhigh])

    if 2 in scale_controls:
        fig.update_xaxes(type="log")
    else:
        pass

    if 3 in scale_controls:
        pass
    else:
        fig.update_yaxes(range=[ylow,yhigh])

    if 4 in scale_controls:
        fig.update_yaxes(type="log")
    else:
        pass


    return fig