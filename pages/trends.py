from dash import Dash, html, dcc, Output, Input, State, callback
from dash.exceptions import PreventUpdate
import json
import pandas
from dash import dash_table


# This stylesheet makes the buttons and table pretty.
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

import dash
from dash import html

dash.register_page(__name__)

# layout = html.Div([
#     html.H1('This is our Archive page'),
#     html.Div('This is our Archive page content.'),
# ])

layout = html.Div(
    [
        # dcc.DropDown
        html.Div([
            html.H4(id='trends-plot')
        ]),
    ]
)

@callback(
        Output('trends-plot', 'children'), 
        Input('trends', 'data')
)
def update_header(data):
    # print(data)
    df = pandas.DataFrame(data)
    ding =  [
        html.H1(f'Current trends value'),
        # dash_table.DataTable(df.to_dict('records'), [{"name": i, "id": i} for i in df.columns]) 
    ]



    return ding