import zmq
import random
import sys
import time
import json

port = "5556"
if len(sys.argv) > 1:
    port =  sys.argv[1]
    int(port)

context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind("tcp://*:%s" % port)

infile = './traces_20.out'
with open(infile, 'r') as fin:
    data = fin.readlines()

infile = './last.json'
with open(infile, 'r') as fin:
    odb = json.load(fin)

counter = 0
while True:
    counter += 1
    topic = b'DATA'
    message = data[counter % len(data)]
    if len(message) < 10:
        continue
    print(counter, topic,len(message), message[:5])
    socket.send_multipart([topic, message.encode()])


    topic = b'ODB'
    message = json.dumps(odb)
    # if len(message) < 10:
    #     continue
    print(counter, topic,len(message), message[:5])
    socket.send_multipart([topic, json.dumps(odb).encode()])
    time.sleep(1)