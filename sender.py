from rudp import *
from random import randint
from time import sleep as tsleep

da = ('127.0.0.1', RCV_PORT)

s = rudpSocket(SDR_PORT)
strHead = 's:'

for i in xrange(1):
	s.sendto(strHead + str(i), da, True)
	tsleep(0.5)