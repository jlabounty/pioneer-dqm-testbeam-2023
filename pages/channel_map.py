from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import numpy as np
from dash import Dash, html, dcc, Output, Input, State, callback, dash_table, ctx
from dash.exceptions import PreventUpdate
import dash
from datetime import date
import pandas
import dash_bootstrap_components as dbc

import dash_daq as daq
import plotly
import plotly.graph_objects as go



# app = Dash(__name__)
dash.register_page(__name__)

layout = html.Div([
    dbc.Container([
        dash_table.DataTable(
            id='channel-map-table',
            filter_action="native",
            sort_action="native",
            sort_mode="multi",
            column_selectable="single",
            row_selectable="multi",
            selected_columns=[],
            selected_rows=[],
            page_action="native",
            page_current= 0,
            page_size= 40,
            # fixed_columns={'headers': True, 'data': 1},
            style_table={'overflowX': 'auto'},
            style_data={
                # 'whiteSpace': 'normal',
                # 'height': 'auto',
                # 'overflowX': 'scroll',
                # 'minWidth': '100%',
                # 'maxWidth': '400px'
                'minWidth': '20px', 'width': '180px', 'maxWidth': '380px',
                'overflow': 'hidden',
                'textOverflow': 'ellipsis',
            },
        ),
    ]),
    html.Button("Download Channel Map Selection", id="channel-map-download-button"),
    html.A(html.P("To update the channel mapping, see this sheet"), href="https://docs.google.com/spreadsheets/d/1agOEMP90H3Vyg1CLcl4oRgOYpwNNXyDgvBDPAprUhhY/edit",target="_blank"),
    dcc.Download(id="download-channel-map-csv"),

])


@callback(
    Output("channel-map-table", "data"), 
    Output("channel-map-table", "columns"), 
    Input('channel-map', 'data')
)
def update_channel_map_table(data):

    df = pandas.DataFrame(data)
    return df.to_dict("records"), [{"name": i, "id": i, "hideable": True, 'selectable':True} for i in df.columns if i != 'id'],

@callback(
    Output("download-channel-map-csv", "data"),
    Input("channel-map-download-button", "n_clicks"),
    Input("channel-map-table", 'data'),
    prevent_initial_call=True,
)
def download_runlog(n_clicks,data):
    if(ctx.triggered_id in ['channel-map-download-button']):
        df = pandas.DataFrame(data)
        return dcc.send_data_frame(df.to_csv, "channel_map.csv")