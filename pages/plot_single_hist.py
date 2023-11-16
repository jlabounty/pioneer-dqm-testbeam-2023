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

# app = Dash(__name__)
dash.register_page(__name__)

layout = html.Div([
    html.H4('Plot a single histogram'),
    dcc.Dropdown(options=[], id='hist-dropdown'),
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
    Input('single-hist', 'figure')
)
def update_graph(options, value, data, existing_figure):
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


    return fig