from rudp import *
from random import randint
from time import sleep

da = ('127.0.0.1', SDR_PORT)

r = rudpSocket(RCV_PORT)

while True:
	print r.recvfrom()[0]