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
import analysis.helpers as helpers


# app = Dash(__name__)
dash.register_page(__name__)
from dash import Dash, Input, Output, callback, dash_table
import pandas as pd
import dash_bootstrap_components as dbc

layout = html.Div([
    html.H4('Run Log:'),
    # dcc.Graph(id="hist-example-graph"),
    dbc.Container([
        dbc.Label('Click a cell in the table:'),
        # dash_table.DataTable(df.to_dict('records'),[{"name": i, "id": i} for i in df.columns], id='tbl'),
        dash_table.DataTable(
            id='tbl',
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
            style_data={
                'whiteSpace': 'normal',
                'height': 'auto',
                'overflowX': 'auto'
            },
        ),
        # dbc.Alert(id='nearline_file_list'),
        html.Div(id='nearline_file_list'),
        dbc.Alert(id='tbl_out'),
    ])
])

@callback(
    Output("tbl", 'data'),
    Output("tbl", 'columns'),
    Output("run-log", 'data'),
    Input('update-constants', 'n_intervals'), 
    Input('do-update', 'on'),
    Input('update-constants-now', 'n_clicks'),
    Input("tbl", 'data'),
    Input("tbl", 'columns'),
    Input("run-log", 'data'),
)
def fill_columns(update_constants, do_update, update_constants_now, existing_data, existing_columns, run_log_store):
    with helpers.time_section("fill-datatable"):
        if(existing_data is not None):
            dfi = pd.DataFrame(existing_data)
            df = helpers.create_updated_runlog(dfi)
        elif run_log_store is not None:
            dfi = pd.DataFrame(run_log_store)
            df = helpers.create_updated_runlog(dfi)
        else:
            df = helpers.create_updated_runlog()
        df['id'] = df.index
        if(do_update or ctx.triggered_id == 'update-constants-now'):
            return (df.to_dict('records'), 
                [{"name": i, "id": i, "hideable": True, 'selectable':True} for i in df.columns if i != 'id'],
                df.to_dict('records'))
        else:
            return existing_data, existing_columns, existing_data

@callback(
    Output('tbl_out', 'children'), 
    Input('tbl', 'active_cell')
)
def update_graphs(active_cell):
    print(f'{active_cell=}')
    return str(active_cell) if active_cell else "Click the table"


@callback(
    Output('nearline_file_list', 'children'), 
    Input('tbl', 'derived_virtual_selected_rows'),
    Input('tbl', 'active_cell'),
    Input("run-log", 'data'),
    Input("nearline-files", 'data'),
)
def show_nearline_files_selected_rows(selected_rows, selected_cells, run_log_data, nearline_file_data):
    if ((selected_rows is None or len(selected_rows) == 0) and selected_cells is None):
        return [html.H4("Select a row to see nearline files")]
    active_row_id = selected_cells['row_id'] if selected_cells else None
    if(active_row_id is not None):
        selected_rows += [active_row_id,]
    print(f'{selected_rows=}')
    print(f'{selected_cells=}')
    df = pd.DataFrame(run_log_data)
    nl = pd.DataFrame(nearline_file_data)
    nl.sort_values(by=['Run', 'Subrun'], inplace=True)
    print(f'{nearline_file_data=}')
    print(f'{nl=}')
    found = 0
    if(len(selected_rows) > 0):
        output = [
            html.H4("Available nearline files:")
        ]
        for x in selected_rows:
            row = df.iloc[x]
            print(f'Found row: {row}')
            nli = nl.loc[nl['Run'] == row['Run']]#.loc[nl['Subrun'] == row['Subrun']]
            if nli.shape[0] > 0:
                found += 1
                for _,nlii in nli.iterrows():
                    # output.append(html.P([html.A(f'{nlii}\n', href=f'/display/{nlii["Run"]}/{nlii["Subrun"]}', target="_blank")]))
                    output.append(
                        html.P(
                            [
                                f'Run {nlii["Run"]} subrun {nlii["Subrun"]} -> ',
                                html.A('Display', href=f'/display/{nlii["Run"]}/{nlii["Subrun"]}', target="_blank"),
                                ' | ',
                                html.A(f'Download', href=f'/files/{nlii["Run"]}/{nlii["Subrun"]}'),
                            ])
                    )
        # return this_string
    if found > 0:
        return output
    else:
        output = [html.H4("No available nearline files from this selection..."),]
    return output
