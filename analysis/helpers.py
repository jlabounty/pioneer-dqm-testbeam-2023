import numpy as np
import os
import sys
import numpy as np
import jsonpickle
import json
import ast
import time
import pandas
import hist
import psycopg2
import pandas
import pandas.io.sql as sqlio
import plotly.graph_objects as go
import zmq

# base directories
ONLINE_DIR = '/home/jlab/testbeam_example_files/online/'
BASE_DIR = '/home/jlab/testbeam_example_files/nearline/'
LOG_DIR = '/home/jlab/testbeam_example_files/nearline_logs/'

# ----------------------------------------------------------
# Helper functions for the DQM processing
# Josh LaBounty - Sept. 2023
# ----------------------------------------------------------

def read_from_socket(socket,message='TRACES'):
    '''
        Given an existing websocket, read the latest traces
    '''
    # with time_section(f" read_from_socket | {message} "):
    print(f"executing new call with message '{message}'")
    topic, mout = socket.recv_multipart(zmq.NOBLOCK)
    mout = mout.decode()
    return mout
        

def process_raw(data):
    '''
        Takes the raw python dictionary and does the following:
            1) loads the latest calibration constants
            2) Loads the current plotly plot configuration
            3) Seperates the hodoscope traces into seperate X/Y arrays, Breaks out the xtals
            4) Does pedestal subtraction and pulse integration
    '''
    # output = data.copy()
    output = data
    keys = list(data.keys())
    for i,x in enumerate(keys):
        if 'traces' in x:
            intname = x.replace("traces_",'integrals_')
            output[intname] = [0 for _ in data[x]]
            # print('   -> processing traces:', x)
            for j, tj in enumerate(data[x]):
                # print(j, tj)
                if(len(tj) < 1):
                    output[x][j] = [0.0 for _ in range(10)]
                    output[intname][j] = 0.0
                else:
                    ped = find_pedestal(tj)
                    output[x][j] = [tjj-ped for tjj in tj]
                    output[intname][j] = np.sum(output[x][j])
    return output

def process_trends(data):
    return data


def find_pedestal(trace, n=5):
    return int(np.average(trace[:n]))

def get_integral(trace,ped=None):
    if ped is None:
        ped = find_pedestal(trace)
    return np.sum( [x-ped for x in trace] )

def get_highest_index(integrals, r1=0, r2=-1):
    maxi = np.max(integrals[r1:r2])
    return integrals.index(maxi)

def create_histograms(processed):
    # create histogram structure
    hists = {}
    for x in processed[0]:
        if 'trace' in x:
            hists[x] = {'integrals':[]}
            for i,y in enumerate(processed[0][x]):
                hists[x]['integrals'].append(hist.Hist(hist.axis.Regular(100,0,200000,label='Pulse Integral'), label=f'{x} | {i}'))
    return append_histograms(jsonpickle.encode(hists), processed)

def append_histograms(existing_histograms, processed):
    # fill existing histograms
    if existing_histograms is None:
        existing_histograms = create_histograms(processed)
    # with time_section("append_histograms"):
    hists = jsonpickle.decode(existing_histograms)
    # print(f"Appending {len(processed)} items to existing histograms")
    for data in processed:
        for x, traces in data.items():
            if('trace' in x):
                for j,trace in enumerate(traces):
                    hists[x]['integrals'][j].fill(data[x.replace("traces_",'integrals_')][j])
    return jsonpickle.encode(hists)



class time_section:
    def __init__(self, tag = ""):
        self.tag = tag
        pass 
    def __enter__(self):
        print(f'****************ENTER {self.tag}******************')
        self.t1 = time.time()
    def __exit__(self,  exc_type, exc_value, tb):
        # print(exc_type, exc_value, tb)
        self.t2 = time.time()
        print(f"Section '{self.tag}' executed in {self.t2-self.t1:.4f} seconds")
        print(f'****************EXIT {self.tag}******************')


def process_odb_json_for_runlog(fi):
    with open(fi,'r') as fin:
        odb = json.load(fin)
    # print(odb)
    runinfo = odb['Runinfo']
    output = {}
    try:
        output = {
            'Run':        runinfo['Run number'] ,
            'Start Time': runinfo['Start time'] ,
            'Stop Time':  runinfo['Stop time'] ,
        }
        output['NSubruns'] = int(odb['Logger']['Channels']['0']['Settings']['Current filename'].split("_")[-1].split(".mid")[0])
        output['Type'] = odb['Experiment']['Run Parameters']['Run Type']
        output['Comment'] = odb['Experiment']['Run Parameters']['Comment']
        output['Shifters'] = odb['Experiment']['Run Parameters']['Operator']
    except:
        # print("Warning: Unable to fully process:", fi)
        pass
        # continue
    return output

def read_from_db(
    command,
    db_connection
):
    # return sqlio.read_sql_query(command, db_connection)
    # with time_section(f"read from db {command}"):
    with db_connection.connect() as connection:
        return pandas.read_sql(command, connection)


def create_updated_runlog(
    db_connection,
):
    '''reads in the online database filled by midas and udpates the internal nearline run log'''
    df = read_from_db('select * from online order by run_number desc;', db_connection)

    return df

def create_updated_subrun_list(
    db_connection,
):
    '''looks for files in the specified directories and creates a list of files for jsroot to open
        assume the file looks like: /path/to/nearline_hists_run00338_00005.root
    '''
    df = read_from_db('select * from nearline_processing order by (run_number, subrun_number) desc;', db_connection)
    return df

def create_updated_slow_control(
    db_connection,
    limit = 10_000
):
    '''looks for files in the specified directories and creates a list of files for jsroot to open
        assume the file looks like: /path/to/nearline_hists_run00338_00005.root
    '''
    # with time_section("fetch slow control"):
    df = read_from_db(f'select * from slow_control order by time desc limit {limit};', db_connection)
    # df.sort_values(by='time', inplace=True)
    return df

def make_nearline_file_path(run,subrun):
    return os.path.join(BASE_DIR, f'nearline_hists_run{int(run):05}_{int(subrun):05}.root')

def make_nearline_log_file_path(run,subrun):
    return os.path.join(LOG_DIR, f'nearline_run{int(run):05}_{int(subrun):05}.log')



def hist_to_plotly_bar(h:hist.Hist):
    return go.Bar(
        x = h.axes[0].centers,
        y = h.values(),
    )