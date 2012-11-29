from rudp import *
from random import randint

da = ('127.0.0.1', RCV_PORT)
s = []
strHead =[]

for i in xrange(10):
	s.append( rudpSocket(SDR_PORT - 9 + i) )
	strHead.append('s'+str(i)+':')

for i in xrange(10000):
	r = randint(0, 9)
	s[r].sendto(strHead[r] + str(i), da , True)
	sleep(0.5)
sleep(10000)
