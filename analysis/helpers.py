import numpy as np
import os
import sys
import numpy as np

# ----------------------------------------------------------
# Helper functions for the DQM processing
# Josh LaBounty - Sept. 2023
# ----------------------------------------------------------

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

    output['hod_x'] = 0,output['n_hodo']
    output['hod_y'] = output['n_hodo'], 2*output['n_hodo']
    output['lyso']  = 2*output['n_hodo'], 2*output['n_hodo'] + output['n_lyso']
    output['nai']  = 2*output['n_hodo'] + output['n_lyso'], len(output['traces'])
    print(
        output['hod_x'],
        output['hod_y'],
        output['lyso'],
        output['nai'],
    )
    return output


def find_pedestal(trace, n=5):
    return int(np.average(trace[:n]))