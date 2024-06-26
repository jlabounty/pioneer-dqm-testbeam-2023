import dash
from dash import Dash, html, dcc, ctx
from dash import Dash, dcc, html, Input, Output, callback, State
import plotly 
import zmq
import json
import orjson
import jsonpickle
import dash_daq as daq
import ast
import analysis.helpers as helpers
from analysis.helpers import ONLINE_DIR, BASE_DIR, LOG_DIR
import dash_bootstrap_components as dbc
import hist
import os
import flask
import pandas 
import time

# db access
# import psycopg2
import sqlalchemy 

# caching
from flask_caching import Cache
import diskcache
from dash import DiskcacheManager
from uuid import uuid4

# profiling performance
from werkzeug.middleware.profiler import ProfilerMiddleware


# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------
# create a native dash cache for caching callbacks / handling background callbacks
native_cache = diskcache.Cache("./cache")
launch_uid = uuid4()
background_callback_manager = DiskcacheManager(
    native_cache,
    expire=10,
    cache_by=[lambda: launch_uid],
)

app = Dash(__name__, 
           use_pages=True,
           external_stylesheets=[dbc.themes.BOOTSTRAP],
           background_callback_manager=background_callback_manager
)
server = app.server

# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------
# create cache for expensive db calls / function calls
TREND_TIMEOUT=1
ODB_TIMEOUT=10
SLOW_CONTROL_TIMEOUT=30
RUNLOG_TIMEOUT=120
NEARLINE_TIMEOUT = 60
cache = Cache(app.server, config={
    # 'CACHE_TYPE': 'filesystem',
    # 'CACHE_DIR': 'cache-directory'
    "DEBUG": True,          # some Flask specific configs
    "CACHE_TYPE": "SimpleCache",  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 300
})

# create cached versions of helper functions
# @cache.memoize(timeout=TREND_TIMEOUT)
def read_from_socket_cached(socket,message=''):
    print(f"updating cached version of 'read_from_socket' with message '{message}'...")
    return helpers.read_from_socket(socket,message)

@cache.memoize(timeout=NEARLINE_TIMEOUT)
def create_updated_subrun_list_cached(reader_engine):
    print("updating cached version of 'create_updated_subrun_list'...")
    return helpers.create_updated_subrun_list(reader_engine)

@cache.memoize(timeout=RUNLOG_TIMEOUT)
def create_updated_runlog_cached(reader_engine):
    print("updating cached version of 'create_updated_runlog'...")
    return helpers.create_updated_runlog(reader_engine)

@cache.memoize(timeout=SLOW_CONTROL_TIMEOUT)
def create_updated_slow_control_cached(reader_engine):
    print("updating cached version of 'create_updated_slow_control'...")
    return helpers.create_updated_slow_control(reader_engine)

@cache.memoize(timeout=SLOW_CONTROL_TIMEOUT)
def create_updated_channel_map_cached(reader_engine):
    print("updating cached version of 'create_updated_channel_map'...")
    return helpers.create_updated_channel_map(reader_engine)

# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------


# create database connection
db_url = sqlalchemy.URL.create(
    "postgresql",
    username="pioneer_reader",
    host="localhost",
    database="pioneer_online",
)
reader_engine = sqlalchemy.create_engine(db_url)

# connect to the zmq PUB from the online
context = zmq.Context()
# port = 5555 # real
# port = 5556 # fake
data_socket = None
odb_socket = None
print("Sockets:", data_socket, odb_socket)

app.layout = html.Div([
    dcc.Store(id='traces', storage_type='session'),
    dcc.Store(id='constants', storage_type='session'),
    # dcc.Store(id='trends', storage_type='session'),
    dcc.Store(id='histograms'),#, storage_type='session'),
    dcc.Store(id='run-log', storage_type='session'),
    dcc.Store(id='nearline-files', storage_type='session'),
    dcc.Store(id='slow-control', storage_type='session'),
    dcc.Store(id='channel-map', storage_type='session'),
    dcc.Interval(id = 'update-data',
                 interval=15*1000, # in milliseconds
                 n_intervals=0),
    dcc.Interval(id = 'update-trends',
                 interval=15*1000, # in milliseconds
                 n_intervals=0),
    dcc.Interval(id = 'update-constants',
                interval=100*1000, # in milliseconds
                n_intervals=0),
    # dbc.NavbarSimple(
    dbc.Navbar(
        [
        dbc.Container([
            html.A(
                dbc.Row([
                    dbc.Col([
                        dbc.Row([html.Img(src='/logo', height="50px"),],align='center'),
                        dbc.Row([dbc.NavbarBrand("Testbeam 2023 DQM")],align='center'),
                    ]),
                    # dbc.Col(dbc.NavbarBrand("Testbeam 2023 DQM")),
                ],align='center'),
            href='/'),
            dbc.Row(
                [
                    dbc.Col(html.Div(id='run-tracker'), width='auto'),
                    dbc.Col(daq.NumericInput(
                        id='update-rate',
                        value=3,
                        min=1,
                        max=30,
                        label='Update Frequency (s)',
                        labelPosition='bottom',
                        # style={'display': 'inline-block'}
                    ), width="auto"),
                    dbc.Col(daq.BooleanSwitch(id='do-update', on=True,label='Update Data', labelPosition='bottom', style={'display': 'inline-block'}), width="auto"),

                ], align='center'
            )
            # style={'display': 'inline-block'}
        ],

        ),
        dbc.Container([
            dbc.Button('Update Traces', id='do-update-now', style={'display': 'inline-block'}, href='#', size="sm"),
            dbc.Button('Update Constants', id='update-constants-now', n_clicks=0, style={'display': 'inline-block'}, href='#', size="sm"),
            dbc.Button('Reset Hists', id='reset-histograms', style={'display': 'inline-block'}, href='#', size="sm", disabled=False),
            dbc.Button("Open Plot Controls", id='open-display-options',size='sm', style={'display': 'inline-block'}),
            # html.Button('', id='reset-histograms', style={'display': 'inline-block'}, hidden=True),
            dbc.Button('Midas',href='http://localhost:8080', target='_blank', id='midas-button', style={'display': 'inline-block'}, size="sm"),
            dbc.Button('Elog',href='https://maxwell.npl.washington.edu/elog/pienuxe/R23/', target='_blank', id='elog_link', style={'display': 'inline-block'}, size="sm"),
            dbc.Button('Run Priorities',href='https://docs.google.com/spreadsheets/d/1gfpCICcEc2EJ55aq40GWMzIJlA6JtqRwJkGiXH2-Nsw/edit#gid=0', target='_blank', id='run_priority_link', style={'display': 'inline-block'}, size="sm"),
            dbc.DropdownMenu(
                [dbc.DropdownMenuItem(
                f"{page['name']}", href=page['relative_path']
                ) for page in  dash.page_registry.values()],
                label='Page Navigation',
                style={'display': 'inline-block'},
                align_end=True
            ),
        ]),
        ],
        # brand="PIONEER DQM",
        # brand_href="/",
        color="primary" if not (os.uname()[1] == 'SB3') else "orange",
        dark=True,
        # style={'padding':10}
        # style={"margin-top": "15px"},
    ),
    # dcc.Slider(
    #     id='update-rate',
    #     min=1,
    #     max=20,
    #     step=1,
    #     value=15,
    # ),
    dbc.Toast(
        "Updating traces...",
        id="trace-update-toast",
        header="INFO:",
        is_open=False,
        dismissable=True,
        icon="danger",
        # top: 66 positions the toast below the navbar
        # style={"position": "fixed", "top": 66, "right": 10, "width": 350, "z-index":9999},
    ),
    dbc.Toast(
        "Unable to connect to psql database",
        id="db-update-toast",
        header="Warning:",
        is_open=False,
        dismissable=True,
        icon="danger",
        # top: 66 positions the toast below the navbar
        style={"position": "fixed", "top": 10, "left": 10, "width": 200, "z-index":9999},
    ),
    dbc.Toast(
        "Unable to read from ODB",
        id="odb-update-toast",
        header="Warning:",
        is_open=False,
        dismissable=True,
        icon="danger",
        # top: 66 positions the toast below the navbar
        style={"position": "fixed", "top": 10, "left": 10, "width": 200, "z-index":9999},
    ),
    dbc.Toast(
        "Unable to fetch new traces",
        id="trace-update-failure-toast",
        header="Error",
        is_open=False,
        dismissable=True,
        icon="danger",
        # top: 66 positions the toast below the navbar
        style={"position": "fixed", "top": 10, "left": 10, "width": 200, "z-index":9999},
    ),
    dbc.Toast(
        "Unable to fetch new histograms",
        id="hist-update-failure-toast",
        header="Error",
        is_open=False,
        dismissable=True,
        icon="danger",
        # top: 66 positions the toast below the navbar
        style={"position": "fixed", "top": 10, "left": 10, "width": 200, "z-index":9999},
    ),
    dbc.Collapse([
        html.Div([
            dbc.Row([
                dbc.Col([dbc.Label("Trace Controls")]),
                dbc.Col([
                    # dbc.Label("ding")
                    dbc.Checklist(
                        options=[
                            {"label": "Subtract Pedestal", "value": 1},
                        ],
                        value=[1],
                        id="trace-options",
                        switch=True,
                    )
                ])
            ]),
            html.Div([
                dbc.Row([
                    dbc.Col([dbc.Label("LYSO Plot Controls")]),
                    dbc.Col([
                            dbc.Checklist(
                                options=[
                                    {"label": "Autoscale X", "value": 1},
                                    # {"label": "Log X", "value": 2},
                                    {"label": "Autoscale Y", "value": 3},
                                    # {"label": "Log Y", "value": 4},
                                ],
                                value=[1,3],
                                id="lyso-trace-options",
                                # inline=True,
                                switch=True,
                            ),
                    ]),
                    dbc.Col([
                        dbc.Label("X Low"),
                        dbc.Input(
                            # label='Y Low [ADC Units]',
                            # labelPosition='bottom',
                            id='lyso-trace-x-limit-low',
                            type='number',
                            value=0,
                        ),
                    ]),
                    dbc.Col([
                        dbc.Label("X High"),
                        dbc.Input(
                            # label='Y High [ADC Units]',
                            # labelPosition='bottom',
                            id='lyso-trace-x-limit-high',
                            type='number',
                            value=800,
                        ),
                    ]),
                    dbc.Col([
                        dbc.Label("Y Low"),
                        dbc.Input(
                            # label='Y Low [ADC Units]',
                            # labelPosition='bottom',
                            id='lyso-trace-y-limit-low',
                            type='number',
                            value=-20,
                        ),
                    ]),
                    dbc.Col([
                        dbc.Label("Y High"),
                        dbc.Input(
                            # label='Y High [ADC Units]',
                            # labelPosition='bottom',
                            id='lyso-trace-y-limit-high',
                            type='number',
                            value=300,
                        ),
                    ]),
                ],
                style={"background":"lightblue"}
                )
            ]),
            html.Div([
                dbc.Row([
                    dbc.Col([dbc.Label("Histogram Controls")]),
                    dbc.Col([
                            dbc.Checklist(
                                options=[
                                    {"label": "Autoscale X", "value": 1},
                                    {"label": "Log X", "value": 2},
                                    {"label": "Autoscale Y", "value": 3},
                                    {"label": "Log Y", "value": 4},
                                ],
                                value=[1,3],
                                id="single-hist-options",
                                # inline=True,
                                switch=True,
                            ),
                    ]),
                    dbc.Col([
                        dbc.Label("X Low"),
                        dbc.Input(
                            # label='Y Low [ADC Units]',
                            # labelPosition='bottom',
                            id='single-hist-x-limit-low',
                            type='number',
                            value=0,
                        ),
                    ]),
                    dbc.Col([
                        dbc.Label("X High"),
                        dbc.Input(
                            # label='Y High [ADC Units]',
                            # labelPosition='bottom',
                            id='single-hist-x-limit-high',
                            type='number',
                            value=100_000,
                        ),
                    ]),
                    dbc.Col([
                        dbc.Label("Y Low"),
                        dbc.Input(
                            # label='Y Low [ADC Units]',
                            # labelPosition='bottom',
                            id='single-hist-y-limit-low',
                            type='number',
                            value=0,
                        ),
                    ]),
                    dbc.Col([
                        dbc.Label("Y High"),
                        dbc.Input(
                            # label='Y High [ADC Units]',
                            # labelPosition='bottom',
                            id='single-hist-y-limit-high',
                            type='number',
                            value=300,
                        ),
                    ]),

                ], style={"background":"#fdaa48"})

            ]),
            html.Div([
                dbc.Row([
                    dbc.Col([dbc.Label("Hodoscope Plot Controls")]),
                    dbc.Col([
                        dbc.Checklist(
                            options=[
                                # {"label": "Autoscale X", "value": 1},
                                # {"label": "Log X", "value": 2},
                                {"label": "Autoscale Y", "value": 3},
                                # {"label": "Log Y", "value": 4},
                            ],
                            value=[],
                            id="hodo-traces-options",
                            # inline=True,
                            switch=True,
                        ),
                    ]),
                    dbc.Col([
                        dbc.Label("Y Low [ADC Units]"),
                        dbc.Input(
                            # label='Y Low [ADC Units]',
                            # labelPosition='bottom',
                            id='hodo-traces-limit-low',
                            type='number',
                            value=-10,
                        ),
                    ]),
                    dbc.Col([
                        dbc.Label("Y High [ADC Units]"),
                        dbc.Input(
                            # label='Y High [ADC Units]',
                            # labelPosition='bottom',
                            id='hodo-traces-limit-high',
                            type='number',
                            value=300,
                        ),
                    ]),

                ],style={"background":"lightblue"})
            ]),
            html.Div([
                dbc.Row([
                    dbc.Col([dbc.Label("Hodoscope Integral Histogram Controls")]),
                    dbc.Col([
                        dbc.Checklist(
                            options=[
                                # {"label": "Autoscale X", "value": 1},
                                # {"label": "Log X", "value": 2},
                                {"label": "Autoscale Y", "value": 3},
                                # {"label": "Log Y", "value": 4},
                            ],
                            value=[],
                            id="hodo-bar-options",
                            # inline=True,
                            switch=True,
                        ),
                    ]),
                    dbc.Col([
                        dbc.Label("Y Low [ADC Units]"),
                        dbc.Input(
                            # label='Y Low [ADC Units]',
                            # labelPosition='bottom',
                            id='hodo-bar-limit-low',
                            type='number',
                            value=-100,
                        ),
                    ]),
                    dbc.Col([
                        dbc.Label("Y High [ADC Units]"),
                        dbc.Input(
                            # label='Y High [ADC Units]',
                            # labelPosition='bottom',
                            id='hodo-bar-limit-high',
                            type='number',
                            value=8000,
                        ),
                    ]),

                ],style={"background":"lightblue"})
            ]),

        ])
        ],

        is_open=False,
        id = 'display-options-collapse',
    ),
    dash.page_container,
    # html.Div([
    #     dbc.Checklist(
    #         options=[
    #             {"label": "Subtract Pedestal", "value": 1},
    #         ],
    #         value=[1],
    #         id="trace-options",
    #         switch=True,
    #     ),
    # ]),
    
])

@callback(
    Output("display-options-collapse", "is_open"),
    [Input("open-display-options", "n_clicks")],
    [State("display-options-collapse", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

@callback(Output('update-data', 'interval'), Input('update-rate', 'value' ))
def update_refresh_rate(rate):
    # print('updating update rate:', rate)
    return int(rate)*1000

@callback(Output('run-tracker', 'children'),
        Input('traces', 'data'),
)
def update_run_tracker(data):
    run = data['run']
    subrun = data['subRun']
    event = data['event']
    trace_recieve_time = data['time']
    return [
        html.P(f"Run/Event: {run}/{event}",style={'color':'white'}),
        html.P(f"Last event recieved: {trace_recieve_time}",style={'color':'white'}),
    ]


# @cache.cached(timeout=TREND_TIMEOUT)
@callback(Output('traces', 'data'),
        Output('trace-update-failure-toast', 'is_open'),
        Input('update-data', 'n_intervals'), 
        Input('do-update', 'on'),
        Input('do-update-now', 'n_clicks'), 
        Input('reset-histograms', 'n_clicks'), 
        Input('traces', 'data'),
        Input("trace-options",'value'),
        # Input('histograms', 'data'),
        # cache_args_to_ignore=[0,1,2,3,4,5],
        # background=True,
        # # manager=background_callback_manager,
        # running=[
        #     (Output("trace-update-toast", "is_open"), True, False),
        # ],
)
def update_traces(n, do_update, do_update_now, reset_histograms, existing_data, trace_options, socket=data_socket):
    # print(type(existing_data))
    # print(f'{trace_options=}')
    if(do_update or ctx.triggered_id in ['do-update-now', 'reset-histograms']):
        # print("updating traces...")
        # with helpers.time_section(tag='update_traces'):
        try:
            # data = helpers.read_from_socket(socket,message='TRACES')
            # with helpers.time_section("cached_read_traces"):
            data = ast.literal_eval(read_from_socket_cached(socket,message='TRACES'))
            #print(data)
        except:
            print("Warning: Unable to get next traces")
            return existing_data, True
        # print(data)
        processed = [helpers.process_raw(orjson.loads(x), subtract_pedestals = 1 in trace_options ) for x in data]
        #print(processed[-1])
        print("displaying event: ", processed[-1]['event'])
        if( ctx.triggered_id == 'reset-histograms' ):
            return processed[-1], False
        else:
            return processed[-1], False
            
    else:
        # return existing_data, helpers.append_histograms(existing_histograms, processed)
        # raise ValueError
        return existing_data, False
    

@callback( Output('histograms', 'data'),
        Output('hist-update-failure-toast', 'is_open'),
        Input('update-data', 'n_intervals'), 
        Input('do-update', 'on'),
        Input('do-update-now', 'n_clicks'), 
        Input('reset-histograms', 'n_clicks'), 
        # Input('traces', 'data'),
        Input('histograms', 'data'),
        # cache_args_to_ignore=[0,1,2,3,4,5],
        # background=True,
        # # manager=background_callback_manager,
        # running=[
        #     (Output("trace-update-toast", "is_open"), True, False),
        # ],
)
# @cache.cached(timeout=TREND_TIMEOUT)
def update_histograms(n, do_update, do_update_now, reset_histograms, existing_histograms, socket=data_socket):
    # print(f'{type(existing_histograms)=}')
    print("Update histograms triggered by", ctx.triggered_id )
    if(do_update or ctx.triggered_id in ['do-update-now', 'reset-histograms']):
        # print("updating traces...")
        # with helpers.time_section(tag='update_traces'):
        # print(data)
        # print(type(data))
        try:  
            data = orjson.loads(ast.literal_eval(read_from_socket_cached(socket,message='HIST'))[0])
            # print(data)
        #     # data = helpers.read_from_socket(socket,message='TRACES')
        #     # with helpers.time_section("cached_read_traces"):
        #     # data = ast.literal_eval(read_from_socket_cached(socket,message='HIST'))
        #     #print(data)
        except:
            print("Warning: Unable to get next HISTOGRAMS")
            return existing_histograms, True
        # ding = helpers.append_histograms(existing_histograms,data,reset=False)
        # print(ding)
        
        if( ctx.triggered_id == 'reset-histograms'):
            # histogram_snapshot = data.copy()
            print('Setting new reference points based on ', ctx.triggered_id )
            return helpers.append_histograms(existing_histograms,data,reset=True), False
        else:
            return helpers.append_histograms(existing_histograms,data,reset=False), False
            
    else:
        # return existing_data, helpers.append_histograms(existing_histograms, processed)
        # raise ValueError
        return existing_histograms, False
    

# @callback(Output('trends', 'data'),
#         Output('db-update-toast', 'is_open', allow_duplicate=True),
#         Input('update-data', 'n_intervals'), 
#         Input('do-update', 'on'),
#         Input('do-update-now', 'n_clicks'), 
#         Input('reset-histograms', 'n_clicks'), 
#         Input('traces', 'data'),
#         prevent_initial_call=True
# )
# # @cache.cached(timeout=TREND_TIMEOUT)
# def update_trends(n, do_update, do_update_now, reset_histograms, existing_data, socket=odb_socket):
#     # print(type(existing_data))
#     return None, False
#     if(do_update or ctx.triggered_id in ['do-update-now', 'reset-histograms']):
#         if( ctx.triggered_id == 'reset-histograms' ):
#             message = 'RESETTREND'
#         else:
#             message = 'TREND'
#         # data = helpers.read_from_socket(socket,message=message)
#         data = read_from_socket_cached(socket,message=message)
#         # print('trend data:', data)
#         return helpers.process_trends(data)
#     else:
#         return existing_data

@callback(Output('constants', 'data'),
        # Output('db-update-toast', 'is_open', allow_duplicate=True),
        Output('odb-update-toast', 'is_open'),
        Input('update-constants', 'n_intervals'), 
        Input('do-update', 'on'),
        Input('constants', 'data'),
        Input('update-constants-now', 'n_clicks'),
        prevent_initial_call=True
)
# @cache.cached(timeout=ODB_TIMEOUT)
def update_constants(n, do_update, existing_data, button_clicks, socket=odb_socket):
    # print(type(existing_data))
    # print(existing_data)
    if(do_update or ctx.triggered_id == 'update-constants-now'):
        # print("*****************************************************************reading constants")
        try:
            data = read_from_socket_cached(socket, message='CONST')
            # print(data)
            return data, False
        except:
            print("Warning: unable to read ODB")
            return existing_data, True
    else:
        return existing_data, False

@callback(Output('nearline-files', 'data'),
        Output('db-update-toast', 'is_open', allow_duplicate=True),
        Input('update-constants', 'n_intervals'), 
        Input('do-update', 'on'),
        Input('update-constants-now', 'n_clicks'),
        Input('nearline-files', 'data'),
        prevent_initial_call=True
)
# @cache.cached(timeout=NEARLINE_TIMEOUT)
def update_nearline_file_list(n, do_update, button_clicks, existing_data):
    # print(type(existing_data))
    if(do_update or ctx.triggered_id == 'update-constants-now'):
        try:
            ding = create_updated_subrun_list_cached(reader_engine)
        except:
            print("Warning: unable to get updates nearline files")
            return existing_data, True
        # print(ding)
        ding['available'] = ding['nearline_file_location'].apply(os.path.exists)
        return ding.to_dict(),False
    else:
        return existing_data,False

@callback(Output('run-log', 'data'),
        Output('db-update-toast', 'is_open'),
        Input('update-constants', 'n_intervals'), 
        Input('do-update', 'on'),
        Input('update-constants-now', 'n_clicks'),
        Input('run-log', 'data'),
        prevent_initial_call=True
)
# @cache.cached(timeout=RUNLOG_TIMEOUT)
def update_run_log(n, do_update, button_clicks, existing_data):
    # print(type(existing_data))
    if(do_update or ctx.triggered_id == 'update-constants-now'):
        try:
            ding = create_updated_runlog_cached(reader_engine).to_dict() 
        except:
            print("Warning: unable to get updated run log")
            return existing_data, True
        # print(ding)
        return ding,False
    else:
        return existing_data,False

@callback(Output('slow-control', 'data'),
        Output('db-update-toast', 'is_open', allow_duplicate=True),
        Input('update-constants', 'n_intervals'), 
        Input('do-update', 'on'),
        Input('update-constants-now', 'n_clicks'),
        Input('slow-control', 'data'),
        prevent_initial_call=True
)
# @cache.cached(timeout=SLOW_CONTROL_TIMEOUT)
def update_slow_control_data(n, do_update, button_clicks, existing_data):
    # print(type(existing_data))
    if(do_update or ctx.triggered_id == 'update-constants-now'):
        try:
            ding = create_updated_slow_control_cached(reader_engine).to_dict() 
        except:
            print("Warning: unable to get slow control")
            return existing_data, True
        # print(ding)
        return ding,False
    else:
        return existing_data,False

@callback(Output('channel-map', 'data'),
        Output('db-update-toast', 'is_open', allow_duplicate=True),
        Input('update-constants', 'n_intervals'), 
        Input('do-update', 'on'),
        Input('update-constants-now', 'n_clicks'),
        Input('channel-map', 'data'),
        prevent_initial_call=True
)
# @cache.cached(timeout=SLOW_CONTROL_TIMEOUT)
def update_channel_map_data(n, do_update, button_clicks, existing_data):
    # print(type(existing_data))
    if(do_update or ctx.triggered_id == 'update-constants-now'):
        try:
            ding = create_updated_channel_map_cached(reader_engine).to_dict() 
        except:
            print("Warning: unable to get channel mapping")
            return existing_data, True
        # print(ding)
        return ding,False
    else:
        return existing_data,False


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

@app.server.route('/logo')
def logo():
    return flask.send_file("static/pioneer-logo.png")

if __name__ == '__main__':
    print("Starting app...")

    # profiler mode
    # app.server.config["PROFILE"] = True
    # app.server.wsgi_app = ProfilerMiddleware(
    #     app.server.wsgi_app, 
    #     sort_by=("cumtime", "tottime"), 
    #     restrictions=[50],
    #     stream=None,
    #     profile_dir='./profile-logs/'
    # )
    match os.uname()[1]:
        case 'SB3':
            app.run(debug=True, port=8051) #debug mode
        case 'pioneer-nuci':
            print("Warning: you should be running this with gunicorn")
            app.run(debug=True) #debug mode
        case 'cenpa-pioneer':
            print("Warning: you should be running this with gunicorn")
            app.run(debug=False, port=8052) #debug mode
        case _:
            raise NotImplementedError

    # app.run_server() #works with gunicorn
