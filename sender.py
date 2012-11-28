from rudp import *
from random import randint

da = ('127.0.0.1', RCV_PORT)

s = rudpSocket(SDR_PORT)
strHead = 's:'

option = [0,0,0,0,0,1,1,1,1,1]

for i in option:
	if i:
		print s.sendto(strHead + 'sender -> receiver', da, True)
	else:
		print s.recvfrom()[0]

while True:
	print s.recvfrom()[0]

