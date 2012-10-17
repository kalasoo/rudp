from rudpUser import *
from time import sleep

server = rudpReceiver()

if TestOn == False:	
	data = server.receiveData()
	if data == False: print 'No data is received.'
	else: print '\nReceived Data: \n{}\n'.format(data)

else: 
	print '\n---------------------START (Server) ---------------------'
	print '===> [TEST  ID] {}'.format(TestCase[0])
	print '===> [Scenario] {}'.format(TestCase[1])
	print '===> [Solution] {}'.format(TestCase[2])
	
	if TestCase[0] in {1, 2, 6, 10, 11, 12, 16, 17, 18}:
		data = server.receiveData()
		if data == False: print 'No data is received.'
		else: print '\nReceived Data: \n{}\n'.format(data)
		print '\n---------------------END (Server)-----------------------'
	elif TestCase[0] == 3:
		server.rudp.pktId = 0
		server.rudp.desAddr = None
		#LISTEN
		server.rudp.recv(SYN, server.rudp.pktId)
		server.rudp.desAddr = server.rudp.recvData[3]
		server.rudp.pktId += 1
		print '--> Server: send NO SYN_ACK to Client'
		print '---------------------END (Server)-----------------------\n'
	elif TestCase[0] == 4 or TestCase[0] == 5:
		server2 = rudpReceiver(RCV_PORT + 1000)
		server.rudp.pktId = 0
		server.rudp.desAddr = None
		server2.rudp.pktId = 0
		server2.rudp.desAddr = None
		#LISTEN
		server.rudp.recv(SYN, server.rudp.pktId)
		server.rudp.desAddr = server.rudp.recvData[3]
		server.rudp.pktId += 1	
		server2.rudp.desAddr = server.rudp.recvData[3]
		server2.rudp.pktId+= 1
		#SYN RECEIVED
		print '--> [Case 4] Server2: send SYN_ACK to Client (wrong IPPADDR)'
		server2.rudp.send(SYN_ACK, server2.rudp.pktId, '')
		sleep(1)
		print '--> [Case 5] Server: send SYN_ACK to Client (wrong TYPE or ID)'
		# please choose either one
		server.rudp.send(ACK, server.rudp.pktId, '')
		#server.rudp.send(SYN_ACK, server.rudp.pktId + 1000, '')
		print '---------------------END (Server)-----------------------\n'
	elif TestCase[0] == 7:
		server.rudp.accept()
		print '---> Server: accept() - OK'
		print '---> Server: send NO ACK to Client'
		print '---------------------END (Server)-----------------------\n'
	elif TestCase[0] == 8:
		server.rudp.accept()
		print '---> Server: accept() - OK'
		print '---> Server2: send ACK to Client (wrong IPPADDR)'
		server2 = rudpReceiver(RCV_PORT + 1000)
		server2.rudp.pktId = server.rudp.pktId
		server2.rudp.desAddr = server.rudp.desAddr
		server2.rudp.send(ACK, server2.rudp.pktId, '')
		sleep(1)
		print '---> Server: send ACK to Client (ID = pktId - 1)'
		server.rudp.send(ACK, server.rudp.pktId - 1, '')
		print '---------------------END (Server)-----------------------\n'
	elif TestCase[0] == 9:
		server.rudp.accept()
		print '---> Server: accept() - OK'
		print '---> Server: send ACK to Client (wrong TYPE or other ID)'
		# please comment either one
		#server.rudp.send(SYN_ACK, server.rudp.pktId, '')
		server.rudp.send(ACK, server.rudp.pktId + 100, '')
		print '---------------------END (Server)-----------------------\n'
	elif TestCase[0] == 13:
		server.rudp.accept()
		print '---> Server: accept() - OK'
		while True:
			try:	server.rudp.rasTimeOut(ACK, DAT, '')
			except WRONG_TYPE:
				if server.rudp.recvData[0] == FIN and server.rudp.recvData[1] == server.rudp.pktId: break
				else: server.rudp.endRudp(True)
		print '---> Server: send NO FIN_ACK to Client'
		print '---------------------END (Server)-----------------------\n'
	elif TestCase[0] == 14:
		server.rudp.accept()
		print '---> Server: accept() - OK'
		while True:
			try:	server.rudp.rasTimeOut(ACK, DAT, '')
			except WRONG_TYPE:
				if server.rudp.recvData[0] == FIN and server.rudp.recvData[1] == server.rudp.pktId: break
				else: server.rudp.endRudp(True)
		print '---> Server2: send FIN_ACK to Client (wrong IPADDR)'
		server2 = rudpReceiver(RCV_PORT + 1000)
		server2.rudp.pktId = server.rudp.pktId
		server2.rudp.desAddr = server.rudp.desAddr
		server2.rudp.send(FIN_ACK, server2.rudp.pktId, '')
		print '---------------------END (Server)-----------------------\n'
	elif TestCase[0] == 15:
		server.rudp.accept()
		print '---> Server: accept() - OK'
		while True:
			try:	server.rudp.rasTimeOut(ACK, DAT, '')
			except WRONG_TYPE:
				if server.rudp.recvData[0] == FIN and server.rudp.recvData[1] == server.rudp.pktId: break
				else: server.rudp.endRudp(True)
		print '---> Server: send FIN_ACK to Client (wrong TYPE or ID)'
		# please comment either one
		server.rudp.send(ACK, server.rudp.pktId, '')
		#server.rudp.send(FIN_ACK, server.rudp.pktId + 1000, '')
		print '---------------------END (Server)-----------------------\n'
	else: pass
