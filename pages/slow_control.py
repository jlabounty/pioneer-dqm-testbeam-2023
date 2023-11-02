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
    html.H4('Plot the slow control information'),
    html.Div(id='dd-output-container'),
    html.Div(
        [
            dbc.Row(
                [
                    dbc.Col([
                        dcc.DatePickerRange(
                            month_format='D-M-Y',
                            end_date_placeholder_text='D-M-Y',
                            start_date=date(2023,10,1),
                            end_date=date(2023,12,1),
                            id='slow-control-date-range'
                        ),
                    ]),
                    dbc.Col([
                        daq.Slider(
                            min=0,
                            max=2400,
                            value=0,
                            handleLabel={"showCurrentValue": True,"label": "Start Time"},
                            step=30,
                            id='slow-control-min-time',
                        ),
                    ]),
                    dbc.Col([
                        daq.Slider(
                            min=0,
                            max=2400,
                            value=2400,
                            handleLabel={"showCurrentValue": True,"label": "Stop Time"},
                            step=30,
                            id='slow-control-max-time',
                        ),
                    ]),
                ],
                # style={'display': 'inline-block'}
            ),

        ]
    ),
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(options=[], id='slow-control-ids', multi=True),
        ]),
        dbc.Col([
            dcc.Dropdown(options=[], id='slow-control-categories', multi=True),
        ]),
    ]),
    dbc.Toast(
        "",
        id="slow-control-bad-selection-toast",
        header="Warning: invalid selection",
        is_open=False,
        dismissable=True,
        icon="danger",
        # top: 66 positions the toast below the navbar
        # style={"position": "fixed", "top": 66, "right": 10, "width": 350},
    ),
    dcc.Graph(id="slow-control-plot"),
    dbc.Container([
        dash_table.DataTable(
            id='slow-control-table',
            filter_action="native",
            sort_action="native",
            sort_mode="multi",
            column_selectable="single",
            row_selectable="multi",
            selected_columns=[],
            selected_rows=[],
            page_action="native",
            page_current= 0,
            page_size= 10,
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
    html.Button("Download Slow Control Selection", id="slow-control-download-button"),
    dcc.Download(id="download-slow-control-csv"),
])

@callback(
    Output('slow-control-ids', 'options'),
    Output('slow-control-categories', 'options'),
    Input( 'slow-control', 'data')
)
def update_slow_control_ids_categories(data):
    # return f'You have selected {value}'
    # print('slow control data:', data)
    if(data is None):
        return [],[]
    df = pandas.DataFrame(data)
    # print(df.head())
    cats = list(df['reading_type'].unique())
    ids  = list(df['channel_id'].unique()  )

    return ids,cats

@callback(
    Output("slow-control-bad-selection-toast", "is_open"),
    Output("slow-control-bad-selection-toast", "children"),
    Input('slow-control-ids', 'value'),
    Input('slow-control-categories', 'value'),
)
def open_toast(ids, cats):
    if len(cats) > 2:
        return True, 'Please select 1-2 options only.'
    return False, ''

@callback(
    Output("slow-control-plot", "figure"), 
    Output("slow-control-table", "data"), 
    Output("slow-control-table", "columns"), 
    Input('slow-control-ids', 'value'),
    Input('slow-control-categories', 'value'),
    Input('slow-control-date-range', 'start_date'),
    Input('slow-control-date-range', 'end_date'),
    Input('slow-control-min-time', 'value'),
    Input('slow-control-max-time', 'value'),
    Input('slow-control', 'data')
)
def update_graph(ids, cats, start_date, end_date, start_time, end_time, data):

    t0 = pandas.to_datetime(start_date) + pandas.Timedelta(minutes=start_time*3600/2400.)
    t1 = pandas.to_datetime(end_date) + pandas.Timedelta(minutes=end_time*3600/2400.,days=-1)
    fig = plotly.subplots.make_subplots(
        specs=[[{"secondary_y": True}]]
        # secondary_y=True
    )
    if ids is None or cats is None or len(ids) < 1 or len(cats) < 1:
        return fig, None, None

    df = pandas.DataFrame(data)
    df['time'] = pandas.to_datetime(df['time'])
    df = df.loc[df['time'] >= t0].loc[df['time'] <= t1]
    df.sort_values(by='time', inplace=True)
    # print(df.shape)

    indices = []
    for i, cati in enumerate(cats):
        is_secondary = (i % 2 != 0)
        # print(i, cati, is_secondary)
        for j, idj in enumerate(ids):
            dfi = df.loc[df['channel_id'] == idj].loc[df['reading_type'] == cati]
            # print(dfi.head())
            fig.add_trace(
                go.Scatter(
                    x=dfi['time'], 
                    y=dfi['reading'],
                    name=f'{idj} | {cati}'
                ),
                secondary_y=is_secondary,
            )
            # print(dfi.index)
            # print(df.index)
            # this_index = dfi.index[0]
            # print(this_index)
            # print(dfi.loc[this_index])
            # print(df.loc[this_index])
            indices += list(dfi.index)
    # print(indices)
    # print(df.shape)
    # print(df.loc[indices].shape)


    return fig, df.loc[indices].to_dict("records"), [{"name": i, "id": i, "hideable": True, 'selectable':True} for i in df.columns if i != 'id'],


@callback(
    Output("download-slow-control-csv", "data"),
    Input("slow-control-download-button", "n_clicks"),
    Input("slow-control-table", 'data'),
    prevent_initial_call=True,
)
def download_runlog(n_clicks,data):
    if(ctx.triggered_id in ['slow-control-download-button']):
        df = pandas.DataFrame(data)
        return dcc.send_data_frame(df.to_csv, "slowcontrol.csv")