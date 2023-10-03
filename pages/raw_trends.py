from dash import Dash, html, dcc, Output, Input, State, callback
from dash.exceptions import PreventUpdate
import json
import pandas
from dash import dash_table
import plotly.express as px


# This stylesheet makes the buttons and table pretty.
# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

import dash
from dash import html

dash.register_page(__name__)

# layout = html.Div([
#     html.H1('This is our Archive page'),
#     html.Div('This is our Archive page content.'),
# ])

layout = html.Div(
    [
        html.Div([
            html.H4(id='trends-dump')
        ]),
        dcc.Graph(id="trends-plot"),
        
    ]
)

@callback(Output('trends-dump', 'children'), Input('trends', 'data'))
def update_header(data):
    # print(data)
    df = pandas.DataFrame(data)
    ding =  [
        html.H1(f'Current trends value'),
        dash_table.DataTable(df.to_dict('records'), [{"name": i, "id": i} for i in df.columns]) 
    ]
    # for key,x in data.items():
    #     # print(key)
    #     if 'traces' in key:
    #         ding += [html.P('traces')]
    #         for i,xi in enumerate(x):
    #             ding += [html.P(f'    Trace {i} -> {xi}')]
    #     else:
    #         ding += [html.P(f'{key}: {x}')]
    return ding

@callback(
        Output('trends-plot', 'figure'), Input('trends', 'data'))
def update_trend_graph(data):
    df = pandas.DataFrame(data)
    # df = pandas
    return px.line(df, x='time', y='x')