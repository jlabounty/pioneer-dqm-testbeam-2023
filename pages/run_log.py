from dash import Dash, dcc, html, Input, Output, ctx
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
import analysis.helpers as helpers
import os

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# app = Dash(__name__)
dash.register_page(__name__)
from dash import Dash, Input, Output, callback, dash_table
import pandas
import dash_bootstrap_components as dbc

layout = html.Div([
    html.H4('Run Log:'),
    html.P('(Hover to see full text)'),
    dbc.Container([
        html.Button("Download Runlog", id="btn_csv"),
        dcc.Download(id="download-runlog-csv"),
        dash_table.DataTable(
            id='runlog-table',
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
        html.Div(id='nearline_file_list'),
        # dbc.Alert(id='runlog_table_out'),
        ],
        # style={'overflowX': 'scroll'}
    )
])

@callback(
    Output("runlog-table", 'data'),
    Output("runlog-table", 'columns'),
    Output("runlog-table", 'tooltip_data'),
    # Output("run-log", 'data'),
    Input('update-constants', 'n_intervals'), 
    Input('do-update', 'on'),
    Input('update-constants-now', 'n_clicks'),
    Input("runlog-table", 'data'),
    Input("runlog-table", 'columns'),
    Input("runlog-table", 'tooltip_data'),
    Input("run-log", 'data'),
)
def fill_columns(update_constants, do_update, update_constants_now, existing_data, existing_columns, existing_tooltips, run_log_data):
    # with helpers.time_section("fill-datatable"):
    # print(f'{existing_data=}')
    if(run_log_data is not None):
        df = pandas.DataFrame(run_log_data)
    elif(existing_data is not None):
        df = pandas.DataFrame(existing_data)
    else:
        print("Please wait for database call...")
        return existing_data, existing_columns
    df['id'] = df.index.astype(int)
    if(do_update or ctx.triggered_id == 'update-constants-now'):

        records = df.to_dict("records")
        columns = [{"name": i, "id": i, "hideable": True, 'selectable':True} for i in df.columns if i != 'id']
        tooltips = [
            {
                column: {'value': str(value), 'type': 'markdown'}
                for column, value in row.items()
            } for row in records
        ]

        return (records,
            columns,
            tooltips
            # df.to_dict('records'))
        )
    else:
        return existing_data, existing_columns, existing_tooltips

# @callback(
#     Output('runlog_table_out', 'children'), 
#     Input('runlog-table', 'active_cell')
# )
# def update_graphs(active_cell):
#     print(f'{active_cell=}')
#     return str(active_cell) if active_cell else "Click the table"


@callback(
    Output('nearline_file_list', 'children'), 
    Input('runlog-table', 'derived_virtual_selected_rows'),
    Input('runlog-table', 'active_cell'),
    Input("run-log", 'data'),
    Input("nearline-files", 'data'),
)
def show_nearline_files_selected_rows(selected_rows, selected_cells, run_log_data, nearline_file_data):
    if ((selected_rows is None or len(selected_rows) == 0) and selected_cells is None):
        return [html.H4("Select a row to see nearline files")]
    active_row_id = selected_cells['row_id'] if selected_cells else None
    if(active_row_id is not None):
        selected_rows += [active_row_id,]
    # print(f'{selected_rows=}')
    # print(f'{selected_cells=}')
    df = pandas.DataFrame(run_log_data)
    nl = pandas.DataFrame(nearline_file_data)
    # nl.sort_values(by=['run_number', 'subrun_number'], inplace=True)
    # print(f'{nearline_file_data=}')
    print(f'{nl.head()=}')
    found = 0
    if(len(selected_rows) > 0):
        output = [
            html.H4("Available nearline files:")
        ]
        for x in selected_rows:
            row = df.iloc[x]
            # print(f'Found row: {row["run_number"]}')
            # print(row)
            nli = nl.loc[nl['run_number'] == row['run_number']]#.loc[nl['Subrun'] == row['Subrun']]
            
            if nli.shape[0] > 0:
                found += 1
                for _,nlii in nli.iterrows():
                    # output.append(html.P([html.A(f'{nlii}\n', href=f'/display/{nlii["Run"]}/{nlii["Subrun"]}', target="_blank")]))
                    ding = [
                        f'Run {nlii["run_number"]} subrun {nlii["subrun_number"]} -> ',
                    ]
                    if os.path.exists(helpers.make_nearline_file_path(nlii["run_number"], nlii["subrun_number"])):
                        ding += [
                                    html.A('Display', href=f'/display/{nlii["run_number"]}/{nlii["subrun_number"]}', target="_blank"),
                                    ' | ',
                                    html.A(f'Download', href=f'/files/{nlii["run_number"]}/{nlii["subrun_number"]}'),
                                    ' | ',
                                    # html.A(f'Log File', href=f'/logs/{nlii["run_number"]}/{nlii["subrun_number"]}'),
                                ]
                    ding.append(
                                html.A(f'Log File', href=f'/logs/{nlii["run_number"]}/{nlii["subrun_number"]}')
                    )
                    # print(ding)
                    output.append(html.P(ding))
        # return this_string
    if found > 0:
        return output
    else:
        output = [html.H4("No available nearline files from this selection..."),]
    return output

@callback(
    Output("download-runlog-csv", "data"),
    Input("btn_csv", "n_clicks"),
    Input("runlog-table", 'data'),
    prevent_initial_call=True,
)
def download_runlog(n_clicks,data):
    if(ctx.triggered_id in ['btn_csv']):
        # print('downloading!!')
        # print("   -> passed")
        df = pandas.DataFrame(data)
        return dcc.send_data_frame(df.to_csv, "runlog.csv")