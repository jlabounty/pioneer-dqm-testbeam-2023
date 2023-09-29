# A zmq server which exists to fake data for the testing of the pioneer dqm
# Josh LaBounty - 9-28-2023

import time
import zmq
import json
import numpy as np
import hist
import analysis.helpers as helpers

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

n_hodo = 12
n_lyso = 10
lyso_layout = [3,4,3]
n_nai = 4
len_traces = 40
pedestal = -1700

h1 = np.zeros((n_hodo,n_hodo))
h2 = np.zeros((10,5))


def make_trace(i=len_traces, has_pulse=False, pulse_amplitude=100,noise=10,ped=pedestal):
    trace = np.random.randint(-noise,noise,i, dtype=int) + pedestal
    if(has_pulse):
        trace[10:20] += pulse_amplitude
    return [int(x) for x in trace]


while True:
    #  Wait for next request from client
    message = socket.recv()
    print(f"Received request: {message}")
    match message.decode().strip():
        case 'CONST':
            constants = {f'Calibration {i}': np.random.random() for i in range(100) }
            print("Sending constants...")
            socket.send_json(json.dumps(constants))
        case 'TRACES' | 'RESETHIST':
            if 'RESET' in message.decode():
                h1 = np.zeros((n_hodo,n_hodo))
                h2 = np.zeros((10,5))
            print("Sending traces...")
            # socket.send_json(json.dumps({'n_hodo':12}))
            # continue
            t1 = time.time()

            #  Do some 'work'
            # time.sleep(1)

            #  Send reply back to client
            # socket.send_string("World")
            x_location = np.random.randint(0,n_hodo)
            y_location = np.random.randint(0,n_hodo)

            traces = []
            for i in range(n_hodo):
                traces.append( make_trace(has_pulse=(i==x_location)) )
                h1[i,:] += np.sum( helpers.get_integral(traces[-1]) )
            for i in range(n_hodo):
                # traces.append( make_trace() )
                traces.append( make_trace(has_pulse=(i==y_location)) )
                h1[:,i] += np.sum( helpers.get_integral(traces[-1]) )
            for i in range(n_lyso):
                traces.append( make_trace() )
                row = 1
                column = 0
                if(i < lyso_layout[0]):
                    column = i*2 + 2
                elif(i < lyso_layout[0]+lyso_layout[1]):
                    column = (i-lyso_layout[0])*2 + 1
                    row = 2
                else:
                    row = 3
                    column = (i-lyso_layout[0] - lyso_layout[1])*2 + 2
                print(i, column, row)
                h2[column:column+2, row] += helpers.get_integral(traces[-1])
            for i in range(n_nai):
                traces.append( make_trace() )
                match i:
                    case 0:
                        h2[0,1:-1] += helpers.get_integral(traces[-1])
                    case 1:
                        h2[1:-1,0] += helpers.get_integral(traces[-1])
                    case 2:
                        h2[-1,1:-1] += helpers.get_integral(traces[-1])
                    case 3:
                        h2[1:-1,-1] += helpers.get_integral(traces[-1])
            dicti = {
                'n_hodo':n_hodo,
                'n_lyso':n_lyso,
                'n_nai':n_nai,
                'run':int(np.random.randint(0,100)),
                'subrun':int(np.random.randint(0,500)),
                'event':int(np.random.randint(0,500)),
                'traces':traces,
                'samples':[i for i in range(len_traces)],
                'histograms':{
                    'hodo':h1.tolist(),
                    'xtals':h2.tolist(),
                },
                'odb':{
                    'odb_x':x_location, # + np.random.normal(0,2),
                    'odb_y':y_location, # + np.random.normal(0,2),
                }
            }
            # print(dicti)
            # print(type(traces[-1][-2]))
            # print(type(dicti), type(json.dumps(dicti)))
            t2 = time.time()
            print("Message created in:", t2-t1)
            socket.send_json(json.dumps(dicti))
        case _:
            print("Sending error...")
            socket.send_json(json.dumps({'error':404})) #TODO: send proper error message