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

# ----------------------------------------------------------
# Helper functions for the DQM processing
# Josh LaBounty - Sept. 2023
# ----------------------------------------------------------

def read_from_socket(socket,message='TRACES'):
    '''
        Given an existing websocket, read the latest traces
    '''
    # TODO: make this robust against timeout
    print("reading")
    with time_section(f" read_from_socket | {message} "):
        # #TODO: clean this up now that we're in PUB/SUB mode
        topic, mout = socket.recv_multipart()
        mout = mout.decode()
        # print(topic, mout[:10])
        lenmsg = len(mout)
        try:
            mout = ast.literal_eval(mout)
        except:
            print(f"Warning: error doing 'literal_eval' of {topic} -> '{mout[:10]}...'")
            # print(e)
        # print(len(mout))
        if(len(mout) > 0):
            with open(f"{message}.out",'a') as fout:
                fout.write(str(mout)+"\n")
                # raise ValueError
        # for x in mout:
        #     print(x[0])
        # return json.loads(mout)
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
    output = data.copy()
    for i,x in enumerate(data):
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
    with time_section("append_histograms"):
        hists = jsonpickle.decode(existing_histograms)
        print(f"Appending {len(processed)} items to existing histograms")
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

def create_updated_runlog(
    df=None, 
    midas_indir='/home/jlab/testbeam_example_files/online'
):
    '''reads in the .json files produced by midas and udpates the run log'''
    files = [os.path.join(midas_indir, x) for x in os.listdir(midas_indir) if '.json' in x[-7:] and 'last' not in x]
    if(df is None):
        df = pandas.DataFrame(columns=['Run', 'Type', 'Comment', 'Shifters', 'Start Time', 'Stop Time', 'NSubruns'])
    for i, fi in enumerate(files):
        run = int(fi.split("run")[1].split(".json")[0])
        if(run in df['Run'].unique()):
            # print("   -> Run found")
            continue
        else:
            print(i, fi)    
            print("   -> Run not found in log, processing!")
            processed_odb = process_odb_json_for_runlog(fi)
            df.loc[-1] = processed_odb
            df.index = df.index + 1

            print(processed_odb)
            # break
    df.sort_values(by='Run', ascending=False, inplace=True)
    return df

def create_updated_subrun_list(
    df=None,
    file_indir='/home/jlab/testbeam_example_files/nearline',
    log_indir='/home/jlab/testbeam_example_files/nearline_logs',
):
    '''looks for files in the specified directories and creates a list of files for jsroot to open
        assume the file looks like: /path/to/nearline_hists_run00338_00005.root
    '''
    if(df is None):
        columns = ['Run', 'Subrun', 'path']
        df = pandas.DataFrame(columns=columns)
    else:
        df = pandas.DataFrame(df)
    files = [os.path.join(file_indir,x) for x in os.listdir(file_indir) if '.root' in x[-5:]]
    # print()
    processed_files = df['path'].unique()
    for i, fi in enumerate(files):
        if(fi in processed_files):
            continue 
        # print(f'processing {fi}')
        run = int(fi.split('_run')[-1].split('_')[0])
        subrun = int(fi.split('_')[-1].split('.root')[0])
        df.loc[-1] = {'Run':run, 'Subrun':subrun, 'path':fi}
        df.index = df.index + 1
        # print(df.loc[0])
    # print(f'{df.shape=}')
    df.sort_values(by=['Run', 'Subrun'], inplace=True)
    return df
