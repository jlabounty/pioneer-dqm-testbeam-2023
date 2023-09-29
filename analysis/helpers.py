import numpy as np
import os
import sys
import numpy as np
import json
import ast

# ----------------------------------------------------------
# Helper functions for the DQM processing
# Josh LaBounty - Sept. 2023
# ----------------------------------------------------------

def read_from_socket(socket,message='TRACES'):
    '''
        Given an existing websocket, read the latest traces
    '''
    # TODO: make this robust against timeout
    socket.send_string(str(message))
    message = socket.recv().decode()
    return json.loads(ast.literal_eval(message))
        

def process_raw(data):
    '''
        Takes the raw python dictionary and does the following:
            1) loads the latest calibration constants
            2) Loads the current plotly plot configuration
            3) Seperates the hodoscope traces into seperate X/Y arrays, Breaks out the xtals
            4) Does pedestal subtraction and pulse integration
    '''
    output = data.copy()
    output['traces_raw'] = output['traces'].copy()
    output['integrals'] = []
    for i,trace in enumerate(output['traces_raw']):
        ped = find_pedestal(trace)
        output['traces'][i] = [x-ped for x in trace]
        output['integrals'].append(np.sum(output['traces'][i]))

    output['t0_trace'] = output['traces_raw'][0] #just pick a random trace
    output['hod_x'] = 0,output['n_hodo']
    output['hod_y'] = output['n_hodo'], 2*output['n_hodo']
    output['lyso']  = 2*output['n_hodo'], 2*output['n_hodo'] + output['n_lyso']
    output['nai']  = 2*output['n_hodo'] + output['n_lyso'], len(output['traces'])
    # print(
    #     output['hod_x'],
    #     output['hod_y'],
    #     output['lyso'],
    #     output['nai'],
    # )
    return output


def find_pedestal(trace, n=5):
    return int(np.average(trace[:n]))

def get_integral(trace,ped=None):
    if ped is None:
        ped = find_pedestal(trace)
    return np.sum( [x-ped for x in trace] )

def get_highest_index(integrals, r1=0, r2=-1):
    maxi = np.max(integrals[r1:r2])
    return integrals.index(maxi)