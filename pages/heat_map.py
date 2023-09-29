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
dash.register_page(__name__)

layout = html.Div([
    html.H4('Plot the heatmap of the traces'),
    # html.Button('Reset Heatmaps', id='reset-histograms')
    html.Div([
        dcc.Graph(id="hodo-heatmap" , style={'display': 'inline-block'}),
        dcc.Graph(id="trace-heatmap", style={'display': 'inline-block'}),
    ]),
])


@callback(
    Output("trace-heatmap", "figure"), 
    Input('traces', 'data')
)
def update_xtal_heatmap(data):
    fig =  px.imshow(
        np.array(data['histograms']['xtals']).T
    )

    # TODO: Put these into a config file / create inteface to edit those configurations
    odb_xtal_conversion_x = 10.0 / data['n_hodo']
    odb_xtal_conversion_y = 5.0 / data['n_hodo']

    fig.add_trace(
        go.Scatter(
            x=[data['odb']['odb_x'] * odb_xtal_conversion_x],
            y=[data['odb']['odb_y'] * odb_xtal_conversion_y],
        ),
        # row=2, col=2
    )



    return fig

    

@callback(
    Output("hodo-heatmap", "figure"), 
    Input('traces', 'data')
)
def update_xtal_heatmap(data):

    # fig = plotly.subplots.make_subplots()

    # fig.add_trace(
    #     go.Imshow(np.array(data['histograms']['hodo']).T)
    # )
    fig = px.imshow(np.array(data['histograms']['hodo']).T, 
        color_continuous_scale='RdBu_r', 
        aspect='equal'
    )


    fig.add_trace(
        go.Scatter(
            x=[data['odb']['odb_x']],
            y=[data['odb']['odb_y']],
        ),
        # row=2, col=2
    )

    return fig