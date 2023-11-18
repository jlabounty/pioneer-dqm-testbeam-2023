import zmq
import random
import sys
import time
import json
# import 

port = "5556"
if len(sys.argv) > 1:
    port =  sys.argv[1]
    int(port)

context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind("tcp://*:%s" % port)

# infile = './traces_20.out'
infile = './example_message.txt'
# infile = './traces_sean.out'
with open(infile, 'r') as fin:
    data = fin.readlines()
# print(data)

infile = './last.json'
with open(infile, 'r') as fin:
    odb = json.load(fin)

infile = './daq_machine_test/hist.out'
with open(infile, 'r') as fin:
    hists = json.load(fin)

counter = 0
while True:
    counter += 1
    topic = b'DATA'
    message = f'{[data[counter % len(data)],]*5}'
    message = message.replace('"event":', f'"event":{counter}, "event_raw":')
    if len(message) < 10:
        continue
    print(counter, topic,len(message), message[:15])
    socket.send_multipart([topic, message.encode()])


    topic = b'ODB'
    message = f'[{json.dumps(odb)}]'

    # if len(message) < 10:
    #     continue
    print(counter, topic,len(message), message[:5])
    socket.send_multipart([topic, message.encode()])
    time.sleep(.1)

    topic = b'HIST'
    message = f'{json.dumps(hists)}'

    # if len(message) < 10:
    #     continue
    print(counter, topic,len(message), message[:5])
    socket.send_multipart([topic, message.encode()])
    time.sleep(.1)