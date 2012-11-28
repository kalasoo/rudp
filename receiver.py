from rudp import *
from random import randint

da = ('127.0.0.1', SDR_PORT)

r = rudpSocket(RCV_PORT)
strHead = 'r:'

option = [0,0,0,0,0,1,1,1,1,1]

for i in option:
	if not i:
		print r.sendto(strHead + 'receiver -> sender', da, True)
	else:
		print r.recvfrom()[0]

while True:
	print r.recvfrom()[0]