from rudp import *
from random import randint

da = ('127.0.0.1', SDR_PORT)

r = rudpSocket(RCV_PORT)
strHead = 'r:'

while True:
	print r.recvfrom()[0]