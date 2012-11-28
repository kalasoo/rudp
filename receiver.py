from rudp import *
from random import randint

da = ('127.0.0.1', SDR_PORT)

r = rudpSocket(RCV_PORT)
strHead = 'r:'

while True:
	try:
		r.recvfrom()[0]
	except NO_RECV_DATA:
		print 'no data'
	sleep(0.5)