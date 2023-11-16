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
match os.uname()[1]:
    case 'SB3':
        ONLINE_DIR = '/home/jlab/testbeam_example_files/online/'
        BASE_DIR = '/home/jlab/testbeam_example_files/nearline/'
        LOG_DIR = '/home/jlab/testbeam_example_files/nearline_logs/'
    case 'pioneer-nuci':
        ONLINE_DIR = None
        BASE_DIR = '/home/pioneer/dqm/nearline/'
        LOG_DIR = '/home/pioneer/dqm/nearline_logs/'
    case _:
        raise NotImplementedError
# ----------------------------------------------------------
# Helper functions for the DQM processing
# Josh LaBounty - Sept. 2023
# ----------------------------------------------------------

def read_from_socket(socket,message='TRACES'):
    '''
        Given an existing websocket, read the latest traces
    '''
    context = zmq.Context()

    port = 5556
    # port = 5555 #REAL
    match message:
        case 'TRACES':
            socket = context.socket(zmq.SUB)
            socket.connect(f"tcp://localhost:{port}")
            socket.setsockopt(zmq.SUBSCRIBE, b"DATA")
            time.sleep(0.1)
        case 'CONST':
            socket = context.socket(zmq.SUB)
            socket.connect(f"tcp://localhost:{port}")
            socket.setsockopt(zmq.SUBSCRIBE, b"ODB")
        case 'HIST':
            socket = context.socket(zmq.SUB)
            socket.connect(f"tcp://localhost:{port}")
            socket.setsockopt(zmq.SUBSCRIBE, b"HIST")
            time.sleep(0.6)
        case _:
            print(f"Warning: socket not found for message '{message}'")
    # time.sleep(.5)
    # odb_socket.setsockopt(zmq.ZMQ_RCVTIMEO, 5000)
    # odb_socket = None
    # print("Sockets:", data_socket, odb_socket)
    # with time_section(f" read_from_socket | {message} "):
    print(f"executing new call with message '{message}'")
    # topic, mout = socket.recv_multipart(zmq.NOBLOCK)
    mout = None
    for i in range(10):
        try:
            topic, mout = socket.recv_multipart(zmq.NOBLOCK)
            print('success on read', i, 'for', message)
            mout = mout.decode()
            break
        except:
            print("failed on read", i, 'for', message)
            time.sleep(.1)
    # mout = socket.recv(zmq.NOBLOCK).decode()
    # print(mout)
    return mout
        

def process_raw(data):
    '''
        Takes the raw python dictionary and does the following:
            1) loads the latest calibration constants
            2) Loads the current plotly plot configuration
            3) Seperates the hodoscope traces into seperate X/Y arrays, Breaks out the xtals
            4) Does pedestal subtraction and pulse integration
    '''
    # print("processing data")
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
                    # output[x][j] = [tjj-ped for tjj in tj]
                    output[x][j] = [tjj for tjj in tj]
                    output[intname][j] = get_integral(output[x][j], ped=ped)
    return output

def process_trends(data):
    return data


def find_pedestal(trace, n=5):
    return int(
        np.min(
            [
                np.average(trace[:n]),
                np.average(trace[n:]),
                np.average(trace[len(trace)//2-n:len(trace)//2]),
            ]
        )
    )
    # return int(np.average(trace[:n]))

def get_integral(trace,ped=None):
    if ped is None:
        ped = find_pedestal(trace)
    return np.sum( [x-ped for x in trace] )

def get_highest_index(integrals, r1=0, r2=-1):
    maxi = np.max(integrals[r1:r2])
    return integrals.index(maxi)

def create_histograms(processed):
    # create histogram structure
    hists = {'reference':None}
    # print(f'{processed=}')
    for name,hi in processed.items():
        # print('   ->', name)
        hists[name] = JsonToHist(hi).output
    # print(np.sum(hists[name].values()))
    hists['events'] = np.sum(hists[name].values())
    # print(hists)
    return hists

def append_histograms(existing_histograms, processed, reset=False):
    # fill existing histograms
    if existing_histograms is None:
        # print("No reference point")
        return jsonpickle.encode( create_histograms(processed) )
    else:
        hists = create_histograms(processed)
        previous = jsonpickle.decode(existing_histograms)
        print(f"{hists.keys()=}")
        print(f'{hists["reference"]=}')
        print(f"{previous.keys()=}")
        print(f"{previous['reference']=}")

        # hists['events'] = np.sum(hists['XY_hodoscope'].values())
        print(hists['events'])
        print(f"{hists['events']=}")
        print(f"{hists['events']=},{previous['events']=}")
        if hists['events'] < previous['events']:
            reset = True
        if(reset):
            print("saving new reference point")
            hists['reference'] = previous.copy()
        else:
            hists['reference'] = previous['reference']
        print(f"{hists['reference']=}")
        if(hists['reference'] is not None):
            for name,hi in hists.items():
                if name == 'reference':
                    continue
                # print( f'Reference hist:', [name] )
                if 'XY_' in name:
                    print('this histogram:', hi)
                    print('reference histogram:',hists['reference'][name])
                hists[name] = hi - hists['reference'][name]
            

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
    df = read_from_db('select * from nearline_processing order by (run_number, subrun_number) desc;', db_connection)
    return df

def create_updated_slow_control(
    db_connection,
    limit = 10_000
):
    # with time_section("fetch slow control"):
    df = read_from_db(f'select * from slow_control order by time desc limit {limit};', db_connection)
    # df.sort_values(by='time', inplace=True)
    return df

def create_updated_channel_map(
    db_connection,
    limit = 10_000
):
    # with time_section("fetch slow control"):
    # print('reading channel mapping')
    df = read_from_db(f'select * from channel_mapping order by configuration_id DESC, wfd5 ASC, channel ASC limit {limit};', db_connection)
    # print(df)
    # df.sort_values(by='time', inplace=True)
    return df

def make_nearline_file_path(run,subrun):
    return os.path.join(BASE_DIR, f'nearline_hists_run{int(run):05}_{int(subrun):05}.root')

def make_nearline_log_file_path(run,subrun):
    return os.path.join(LOG_DIR, f'nearline_run{int(run):05}_{int(subrun):05}.log')



def hist_to_plotly_bar(h:hist.Hist,name=None,**kwargs):
    return go.Bar(
        x = h.axes[0].centers,
        y = h.values(),
        name=name,
        **kwargs
    )


def hist_to_plotly_2d(h:hist.Hist,name=None,**kwargs):
    return go.Heatmap(
        x = h.axes[0].centers,
        y = h.axes[1].centers,
        z = h.values(),
        name=name,
        **kwargs
    )


class JsonToHist:
    def __init__(self, h) -> None:
        self.h = h
        self.output = self.process()
        # pass

    def process(self):
        htype = self.h['_typename']
        naxes = int(htype.split("TH")[1][0])
        axes_names = ['fXaxis', 'fYaxis', 'fZaxis']
        # print(htype, naxes)
        ding = [self.process_regular_axis(axes_names[i]) for i in range(naxes) ]
        bins,axes = zip(*ding)
        # print(bins, axes)
        hout = hist.Hist(*axes)
        vals = hout.values(flow=True)
        these_values = self.get_shaped_contents(bins)
        vals += these_values
        return hout
        
    def get_shaped_contents(self, bins):
        flat = self.h['fArray']
        ding = [b+2 for b in bins]
        # if(len(ding) > 1):
        #     print(f'reshaping for a {ding} array')
        return np.array(flat).reshape(*ding)

    def process_regular_axis(self, key):
        # print(self.h[key]['fNbins'],self.h[key]['fXmin'],self.h[key]['fXmax'])
        # print(type(self.h[key]['fNbins']),type(self.h[key]['fXmin']),type(self.h[key]['fXmax']))
        # print(key)
        label = key if 'fTitle' not in self.h[key].keys() else self.h[key]['fTitle'] 
        return self.h[key]['fNbins'], hist.axis.Regular(
            self.h[key]['fNbins'],self.h[key]['fXmin'],self.h[key]['fXmax'],label=label
        )
    