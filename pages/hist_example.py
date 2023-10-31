from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import plotly.subplots
import plotly.graph_objects as go
import plotly
import numpy as np
from dash import Dash, html, dcc, Output, Input, State, callback
from dash.exceptions import PreventUpdate
import dash

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
    # # print(hists)

    for category, hc in hists.items():
        for subcategory, hi in hc.items():
            print(category, subcategory)
            fig = plotly.subplots.make_subplots(
                rows=len(hi), cols=1,
                shared_xaxes='all',
                shared_yaxes='all',
                subplot_titles=[hii.label for hii in hi],
            )
            for i, hii in enumerate(hi):
                # print(category, subcategory, i, hii)
                fig.add_trace(go.Scatter(x=hii.axes[0].centers, y=hii.values()), 
                            #   title=f'X{i}',
                            row=i+1,
                            col=1 )
            # fig.update_layout(autosize=True, height=2200, width=1200)
            fig.update_layout(autosize=True,
                # height=1600,
            )
            # return fig
            output.append(html.Div([dcc.Graph(figure=fig)]))
    print(output)
    return output