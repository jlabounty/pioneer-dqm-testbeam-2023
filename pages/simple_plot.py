from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import numpy as np
from dash import Dash, html, dcc, Output, Input, State, callback
from dash.exceptions import PreventUpdate
import dash

# app = Dash(__name__)
dash.register_page(__name__)


layout = html.Div([
    html.H4('Interactive normal distribution'),
    dcc.Graph(id="graph"),
    html.P("Mean:"),
    dcc.Slider(id="mean", min=-3, max=3, value=0, 
               marks={-3: '-3', 3: '3'}),
    html.P("Standard Deviation:"),
    dcc.Slider(id="std", min=1, max=3, value=1, 
               marks={1: '1', 3: '3'}),
])


@callback(
    Output("graph", "figure"), 
    Input("mean", "value"), 
    Input("std", "value"))
def display_color(mean, std):
    data = np.random.normal(mean, std, size=500) # replace with your own data source
    fig = px.histogram(data, range_x=[-10, 10])
    return fig