import dash
from dash import Dash, html, dcc, ctx
from dash import Dash, dcc, html, Input, Output, callback
import plotly 
import zmq
import json
import jsonpickle
import dash_daq as daq
import ast
import analysis.helpers as helpers
from analysis.helpers import ONLINE_DIR, BASE_DIR, LOG_DIR
import dash_bootstrap_components as dbc
import hist
import os
import flask
import psycopg2
import pandas 

app = Dash(__name__, 
           use_pages=True,
           external_stylesheets=[dbc.themes.BOOTSTRAP]
)

# create database connection

# test values
conn = psycopg2.connect(
    host="localhost",
    database="pioneer_online",
    user="pioneer_reader",
    # password="Abcd1234"
)


# # base directories
# ONLINE_DIR = '/home/jlab/testbeam_example_files/online/'
# BASE_DIR = '/home/jlab/testbeam_example_files/nearline/'
# LOG_DIR = '/home/jlab/testbeam_example_files/nearline_logs/'

print("Connecting to hello world server...")
context = zmq.Context()
# port = 5555 # real
port = 5556 # fake

data_socket = context.socket(zmq.SUB)
data_socket.connect(f"tcp://localhost:{port}")
data_socket.setsockopt(zmq.SUBSCRIBE, b"DATA")

odb_socket = context.socket(zmq.SUB)
odb_socket.connect(f"tcp://localhost:{port}")
odb_socket.setsockopt(zmq.SUBSCRIBE, b"ODB")
# odb_socket = None
print("Sockets:", data_socket, odb_socket)

app.layout = html.Div([
    dcc.Store(id='traces'),
    dcc.Store(id='constants'), #, storage_type='session'),
    dcc.Store(id='trends'), #, storage_type='session'),
    dcc.Store(id='histograms'), #, storage_type='session'),
    dcc.Store(id='run-log'), #, storage_type='session'),
    dcc.Store(id='nearline-files'), #, storage_type='session'),
    dcc.Store(id='slow-control'), #, storage_type='session'),
    dcc.Interval(id = 'update-data',
                 interval=15*1000, # in milliseconds
                 n_intervals=0),
    dcc.Interval(id = 'update-trends',
                 interval=15*1000, # in milliseconds
                 n_intervals=0),
    dcc.Interval(id = 'update-constants',
                interval=100*1000, # in milliseconds
                n_intervals=0),
    # html.H1('Multi-page app with Dash Pages'),
    # html.Div([
    #     daq.BooleanSwitch(id='do-update', on=True,label='Update Data', style={'display': 'inline-block'}),
    #     dbc.Button('Update Now', id='do-update-now', style={'display': 'inline-block'}),
    #     dbc.Button('Reset Histograms + Trends', id='reset-histograms', style={'display': 'inline-block'}),
    #     dbc.Button('Update Constants', id='update-constants-now', n_clicks=0, style={'display': 'inline-block'}),
    #     dbc.DropdownMenu(
    #         [dbc.DropdownMenuItem(
    #         f"{page['name']}", href=page['relative_path']
    #         ) for page in  dash.page_registry.values()],
    #         label='Page Navigation',
    #         style={'display': 'inline-block'}
    #     ),
    #     dcc.Slider(
    #             id='update-rate',
    #             min=1,
    #             max=20,
    #             step=1,
    #             value=15,
    #             # style={'display': 'inline-block'}
    #         ),
    # ]),
    dbc.NavbarSimple(
        brand="PIONEER DQM",
        brand_href="/",
        color="primary",
        dark=True,
        children = [
            daq.BooleanSwitch(id='do-update', on=True,label='Update Data', style={'display': 'inline-block'}),
            dbc.Button('Update Now', id='do-update-now', style={'display': 'inline-block'}),
            dbc.Button('Reset Histograms + Trends', id='reset-histograms', style={'display': 'inline-block'}),
            dbc.Button('Update Constants', id='update-constants-now', n_clicks=0, style={'display': 'inline-block'}),
            dbc.Button('Elog',href='https://maxwell.npl.washington.edu/elog/pienuxe/R23/', target='_blank', id='elog_link', style={'display': 'inline-block'}),
            dbc.DropdownMenu(
                [dbc.DropdownMenuItem(
                f"{page['name']}", href=page['relative_path']
                ) for page in  dash.page_registry.values()],
                label='Page Navigation',
                style={'display': 'inline-block'}
            ),
        ],
    ),
    dcc.Slider(
        id='update-rate',
        min=1,
        max=20,
        step=1,
        value=15,
    ),
    dash.page_container
])

@callback(Output('update-data', 'interval'), Input('update-rate', 'value' ))
def update_refresh_rate(rate):
    return int(rate)*1000

@callback(Output('traces', 'data'),
        Output('histograms', 'data'),
        Input('update-data', 'n_intervals'), 
        Input('do-update', 'on'),
        Input('do-update-now', 'n_clicks'), 
        Input('reset-histograms', 'n_clicks'), 
        Input('traces', 'data'),
        Input('histograms', 'data'),
)
def update_traces(n, do_update, do_update_now, reset_histograms, existing_data, existing_histograms, socket=data_socket):
    # print(type(existing_data))
    if(do_update or ctx.triggered_id in ['do-update-now', 'reset-histograms']):
        # with helpers.time_section(tag='update_traces'):
        # TODO: Make robust against timeout/other error
        try:
            data = helpers.read_from_socket(socket,message='TRACES')
        except:
            print("Warning: Unable to get next traces")
            return existing_data, existing_histograms

        processed = [helpers.process_raw(ast.literal_eval(x)) for x in data]
        if( ctx.triggered_id == 'reset-histograms' ):
            return helpers.process_raw(processed[-1]), helpers.create_histograms(processed) # only add the latest traces to the data store
        else:
            return helpers.process_raw(processed[-1]), helpers.append_histograms(existing_histograms, processed) # only add the latest traces to the data store
        
    else:
        return existing_data, helpers.append_histograms(existing_histograms, processed)
    
@callback(Output('trends', 'data'),
        Input('update-data', 'n_intervals'), 
        Input('do-update', 'on'),
        Input('do-update-now', 'n_clicks'), 
        Input('reset-histograms', 'n_clicks'), 
        Input('traces', 'data'),
)
def update_trends(n, do_update, do_update_now, reset_histograms, existing_data, socket=odb_socket):
    # print(type(existing_data))
    return None
    if(do_update or ctx.triggered_id in ['do-update-now', 'reset-histograms']):
        # TODO: Make robust against timeout/other error
        if( ctx.triggered_id == 'reset-histograms' ):
            message = 'RESETTREND'
        else:
            message = 'TREND'
        data = helpers.read_from_socket(socket,message=message)
        # print('trend data:', data)
        return helpers.process_trends(data)
    else:
        return existing_data

@callback(Output('constants', 'data'),
        Input('update-constants', 'n_intervals'), 
        Input('do-update', 'on'),
        Input('constants', 'data'),
        Input('update-constants-now', 'n_clicks'),
)
def update_constants(n, do_update, existing_data, button_clicks, socket=odb_socket):
    # print(type(existing_data))
    # print(existing_data)
    if(do_update or ctx.triggered_id == 'update-constants-now'):
        # TODO: Make robust against timeout/other error
        # print("*****************************************************************reading constants")
        try:
            data = helpers.read_from_socket(socket, message='CONST')
            # print(data)
            return data
        except:
            print("Warning: unable to read ODB")
            return existing_data
    else:
        return existing_data

@callback(Output('nearline-files', 'data'),
        Input('update-constants', 'n_intervals'), 
        Input('do-update', 'on'),
        Input('update-constants-now', 'n_clicks'),
        Input('nearline-files', 'data'),
)
def update_nearline_file_list(n, do_update, button_clicks, existing_data):
    # print(type(existing_data))
    if(do_update or ctx.triggered_id == 'update-constants-now'):
        ding =  helpers.create_updated_subrun_list(conn)
        # print(ding)
        ding['available'] = ding['nearline_file_location'].apply(os.path.exists)
        return ding.to_dict()
    else:
        return existing_data

@callback(Output('run-log', 'data'),
        Input('update-constants', 'n_intervals'), 
        Input('do-update', 'on'),
        Input('update-constants-now', 'n_clicks'),
        Input('run-log', 'data'),
)
def update_run_log(n, do_update, button_clicks, existing_data):
    # print(type(existing_data))
    if(do_update or ctx.triggered_id == 'update-constants-now'):
        ding = helpers.create_updated_runlog(None, conn).to_dict() 
        # print(ding)
        return ding
    else:
        return existing_data

@callback(Output('slow-control', 'data'),
        Input('update-constants', 'n_intervals'), 
        Input('do-update', 'on'),
        Input('update-constants-now', 'n_clicks'),
        Input('slow-control', 'data'),
)
def update_slow_control_data(n, do_update, button_clicks, existing_data):
    # print(type(existing_data))
    if(do_update or ctx.triggered_id == 'update-constants-now'):
        ding = helpers.create_updated_slow_control(conn).to_dict() 
        # print(ding)
        return ding
    else:
        return existing_data


# Functions to display jsroot files


@app.server.route("/files/<run>/<subrun>")
def serve_nearline_file(run, subrun):
    this_file = helpers.make_nearline_file_path(run,subrun)
    print("Looking for file:", this_file)
    if(os.path.exists(this_file)):
        return flask.send_file(os.path.abspath(this_file))
    else:
        return flask.abort(404)

@app.server.route("/logs/<run>/<subrun>")
def serve_nearline_log_file(run, subrun):
    this_file = helpers.make_nearline_log_file_path(run,subrun)
    print("Looking for file:", this_file)
    if(os.path.exists(this_file)):
        return flask.send_file(os.path.abspath(this_file))
    else:
        return flask.abort(404)

@app.server.route("/jsroot")
def jsroot():
    return flask.render_template('jsroot.html')

@app.server.route("/display/<int:run>/<int:subrun>")
def jsroot_subrun(run,subrun):
    return flask.redirect(f'/jsroot?file=/files/{run}/{subrun}')
    
@app.server.errorhandler(404) 
def not_found(e): 
    # inbuilt function which takes error as parameter 
    # defining function 
    return flask.render_template("404.html") 


if __name__ == '__main__':
    print("Starting app...")
    app.run(debug=True)