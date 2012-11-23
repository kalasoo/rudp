from rudp import *

r = rudpSocket(RCV_PORT, False)

while True:
	print r.recvfrom()