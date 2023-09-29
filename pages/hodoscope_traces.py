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
    html.H4('Plot an array of traces'),
    dcc.Graph(id="hodo-traces"),
    # html.Div([
    # ]),
])

@callback(
    Output("hodo-traces", "figure"), 
    Input('traces', 'data')
)
def update_graph(data):
    # return f'You have selected {value}'
    # if value not in options:
    #     return
    fig = plotly.subplots.make_subplots(
        rows=data['n_hodo'], cols=2,
        # specs = [[{'colspan': 1},{'colspan': 1},{'colspan': 1},{'colspan': 1},{'colspan': 1},{'colspan': 1},{'colspan': 2, 'rowspan':2},None]]*3,
        # specs=[
        # ],
        shared_xaxes='all',
        shared_yaxes='all',
        subplot_titles=sum([[f'X{i}',f'Y{i}'] for i in range(data['n_hodo'])], []),
        # print_grid=True,
        # vertical_spacing=0.075,
        # horizontal_spacing=0.08,
        # row_heights=[1500,]*data['n_hodo'],
        # figsize= (500, 1500)
    )
    for i in range(data['n_hodo']):
        fig.add_trace(go.Scatter(x=data['samples'], y=data['traces'][i+data['hod_x'][0]]), 
                    #   title=f'X{i}',
                      row=i+1,
                      col=1 )
        fig.add_trace(go.Scatter(
            x=data['samples'], 
            y=data['traces'][i+data['hod_y'][0]],
            ), 
            # label=f'Y{i}',
                row=i+1,
                col=2 )
    # fig.update_layout(autosize=True, height=2200, width=1200)
    fig.update_layout(autosize=True,
        height=1600,
    )
    return fig