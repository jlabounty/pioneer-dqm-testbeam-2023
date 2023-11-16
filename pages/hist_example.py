from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import plotly.subplots
import plotly.graph_objects as go
import plotly
import numpy as np
from dash import Dash, html, dcc, Output, Input, State, callback
from dash.exceptions import PreventUpdate
import dash
import analysis.helpers as helpers

import json
import jsonpickle 
import hist

# app = Dash(__name__)
dash.register_page(__name__)

layout = html.Div([
    html.H4('Plot an array of histograms'),
    # dcc.Graph(id="hist-example-graph"),
    html.Div([
        html.H4(id='hist-example-holder')
    ],
    ),
])

@callback(
    # Output("hist-example-graph", "figure"), 
    Output("hist-example-holder", "children"), 
    Input('histograms', 'data')
)
def update_graph(data):
    # return f'You have selected {value}'
    # if value not in options:
    #     return
    output = [
        html.H4("Histogram Display"),
    ]

    hists = jsonpickle.decode(data)
    # print(hists)

    fig = plotly.subplots.make_subplots(
        rows=len(hists.keys()), cols=1,
        # shared_xaxes='all',
        # shared_yaxes='all',
        # subplot_titles=[hii.label for hii in hi],
    )
    for i,(category, hc) in enumerate(hists.items()):
        if category == 'reference':
            continue
        match len(hc.axes):
            case 1:
                fig.add_trace(
                    helpers.hist_to_plotly_bar(hc, name=category),
                    #   title=f'X{i}',
                    # name=category,
                    row=i+1,
                    col=1 
                )
            case 2:
                fig.add_trace(
                    helpers.hist_to_plotly_2d(hc, name=category),
                    #   title=f'X{i}',
                    # name=category,
                    row=i+1,
                    col=1 
                )
    fig.update_layout(autosize=True,
        height=3800,
    )
    output.append(html.Div([dcc.Graph(figure=fig)]))
    # print(output)
    return output