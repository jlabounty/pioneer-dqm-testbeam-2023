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
        fig.add_trace(go.Scatter(x=samples_x, y=data['traces_hodo_x'][i]), 
                    #   title=f'X{i}',
                      col=i+1,
                      row=1 )

        samples_y = list(range(len(data['traces_hodo_y'][i])))
        fig.add_trace(go.Scatter(
            x=samples_y, 
            y=data['traces_hodo_y'][i],
            ), 
            # label=f'Y{i}',
                col=i+1,
                row=2 )
    # fig.update_layout(autosize=True, height=2200, width=1200)
    fig.update_layout(autosize=True,
        height=800,
    )
    return fig