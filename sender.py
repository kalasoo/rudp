from rudp import *
from random import randint

da = ('127.0.0.1', RCV_PORT)

s = rudpSocket(SDR_PORT)
strHead = 's:'


for i in xrange(10):
	print s.sendto(strHead + str(i), da, True)
	sleep(1)