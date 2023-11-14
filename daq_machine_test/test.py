import zmq
import time
context = zmq.Context()
socket = context.socket(zmq.SUB)

socket.connect("tcp://localhost:5555")
socket.setsockopt(zmq.SUBSCRIBE, b"HIST")

n = 10
t1 = time.time()
print("starting....")
for update_nbr in range(n):
    print('   -> ', update_nbr)
    string = socket.recv_string()
    print(string)
t2 = time.time()
print(1.0*(t2-t1)/n, 'seconds/event')
