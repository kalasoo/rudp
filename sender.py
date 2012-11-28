from rudp import *
from random import randint

da = ('127.0.0.1', RCV_PORT)

s1 = rudpSocket(SDR_PORT)
s2 = rudpSocket(SDR_PORT - 1)
strHead1 = 's1:'
strHead2 = 's2:'

for i in xrange(10):
	if randint(0, 1):
		s1.sendto(strHead1 + str(i), da, True)
	else:
		s2.sendto(strHead2 + str(i), da, True)
sleep(3)
for i in xrange(10):
	if randint(0, 1):
		s1.sendto(strHead1 + str(i), da, True)
	else:
		s2.sendto(strHead2 + str(i), da, True)

sleep(10000)
