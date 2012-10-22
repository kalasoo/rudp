from rudp import *
from time import sleep, time
from sys import argv

t = time()
print t
add1 = ('127.0.0.1', RCV_PORT)
c1 = rudpConnection(add1, False)
c1.printConnection()
sleep(1)
print time() - t
add2 = ('127.0.0.1', SDR_PORT)
c2 = rudpConnection(add2, True)
c2.printConnection()
sleep(1)
print time() - t
'''
add1 = ('127.0.0.1', RCV_PORT)
c1 = rudpConnection(add1, False)

recvPkt = rudpPacket(SYN, 0)
print rudpProcessSwitch[recvPkt['pktType']](recvPkt, c1)

for i in xrange(1, 1000):
	recvPkt = rudpPacket(DAT, i, 'a')
	print rudpProcessSwitch[recvPkt['pktType']](recvPkt, c1)

recvPkt = rudpPacket(FIN, 1000)
print rudpProcessSwitch[recvPkt['pktType']](recvPkt, c1)

add2 = ('127.0.0.1', SDR_PORT)
c2 = rudpConnection(add2, True)

recvPkt = rudpPacket(SYN_ACK, 1)
print rudpProcessSwitch[recvPkt['pktType']](recvPkt, c2)

for i in xrange(2, 10):
	recvPkt = rudpPacket(ACK, i)
	print rudpProcessSwitch[recvPkt['pktType']](recvPkt, c2)

c2.wait = FIN_ACK
recvPkt = rudpPacket(FIN_ACK, 10)
try:
	print rudpProcessSwitch[recvPkt['pktType']](recvPkt, c2)
except:
	pass
'''