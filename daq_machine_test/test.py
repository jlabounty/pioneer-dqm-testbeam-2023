import zmq
import time
context = zmq.Context()
socket = context.socket(zmq.SUB)

print("Collecting updates from weather server...")
socket.connect("tcp://localhost:5555")
socket.setsockopt(zmq.SUBSCRIBE, b"DATA")

n = 100
t1 = time.time()
for update_nbr in range(100):
    string = socket.recv_string()
    print(string)
t2 = time.time()
print(1.0*(t2-t1)/n, 'seconds/event')