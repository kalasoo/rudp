from rudpUser import *
from time import sleep

client = rudpSender()
destPort = RCV_PORT
destAddr = '127.0.0.1'

data = '[START] (From The Standard)...Regrettably, his inflexible and headstrong handling of the national education controversy has reinforced among some people the deep-seated mistrust of CY that he is a lackey of the Chinese Communist Party. Does he realize that his "communist comrade" image is so strong that even after he openly and publicly signed a declaration that he did not belong to any "political" party, the public largely held him to do so anyway? What"s wrong with this? Trust is the key to this bizarre attitude among the public towards CY....[END]'

if TestOn == False:
	print 'Client is going to transfer a large amount of data.'	
	if client.sendData(data, destAddr, destPort): print '\nClient: data delivery - OK\n'
	else: print '\nClient: data delivery - failure\n'
else:
	print '\n---------------------START (Client)---------------------'
	print '===> [TEST  ID] {}'.format(TestCase[0])
	print '===> [Scenario] {}'.format(TestCase[1])
	print '===> [Solution] {}'.format(TestCase[2])
		
	if TestCase[0] == 1:		
		print '--> Client will not sending any data to Server'
		print '---------------------END (Client)-----------------------\n'
	elif TestCase[0] == 2:
		client.rudp.desAddr = (destAddr, destPort)	
		print '--> Client: send SYN to Server (wrong TYPE)'
		client.rudp.send(DAT, client.rudp.pktId, '')
		sleep(1)
		print '--> Client: send data normally'
		client.sendData(data, destAddr, destPort)
		print '---------------------END (Client)-----------------------\n'
	elif TestCase[0] in {3, 4, 5, 7, 8, 9, 13, 14, 15}:
		print '--> Client: send data normally'	
		if client.sendData(data, destAddr, destPort): print '--> Client: data delivery - OK'
		else: print '--> Client: data delivery - failure'
		print '---------------------END (Client)-----------------------\n'
	elif TestCase[0] == 6:
		client.rudp.connect(destAddr, destPort)
		print '---> Client: connect() - OK'
		print '---> Client: send SYN again after Handshaking'
		for i in xrange(2):
			print '---> Client: send SYN to Server (duplicate)'
			client.rudp.send(SYN, client.rudp.pktId - 1, '')
			client.rudp.recv()
			sleep(1)
		print '--> Client: send data normally'	
		if client.sendData(data, destAddr, destPort): print '--> Client: data delivery - OK'
		else: print '--> Client: data delivery - failure'
		print '---------------------END (Client)-----------------------\n'
	elif TestCase[0]==10:
		client.rudp.connect(destAddr, destPort)
		print '---> Client: connect() - OK'
		print '---> Client: send only one DAT to Server'
		client.rudp.send(DAT, client.rudp.pktId, 'the only DAT')
		client.rudp.pktId += 1
		print '---------------------END (Client)-----------------------\n'
	elif TestCase[0]==11:
		client.rudp.connect(destAddr, destPort)
		print '---> Client: connect() - OK'
		client.rudp.send(DAT, client.rudp.pktId, 'the only DAT')
		client.rudp.pktId += 1
		print '---> Client2: send DAT to Client (wrong IPADDR)'
		client2 = rudpSender(SDR_PORT + 1000)
		client2.rudp.pktId = client.rudp.pktId
		client2.rudp.desAddr = client.rudp.desAddr
		client2.rudp.send(DAT, client2.rudp.pktId, '')
		sleep(1)
		print '---> Client: send DAT to Client (ID = pktId - 1)'
		client.rudp.send(DAT, client.rudp.pktId - 1, '')
		print '---------------------END (Client)-----------------------\n'
	elif TestCase[0] == 12:
		client.rudp.connect(destAddr, destPort)
		print '---> Client: connect() - OK'
		client.rudp.send(DAT, client.rudp.pktId, 'the only DAT')
		client.rudp.pktId += 1
		print '---> Client: send DAT to Client (wrong TYPE or other ID)'
		# please comment either one
		client.rudp.send(SYN, client.rudp.pktId, '')
		#client.rudp.send(DAT, client.rudp.pktId + 100, '')
		print '---------------------END (Client)-----------------------\n'
	elif TestCase[0] == 16:
		client.rudp.connect(destAddr, destPort)
		print '---> Client: connect() - OK'
		client.rudp.send(DAT, client.rudp.pktId, 'the only DAT')
		client.rudp.pktId += 1
		print '---> Client: Enter Data-Delivery'
		print '---> Client: Closing the connection'
		print '---> Client2: send FIN to Server'
		client2 = rudpSender(SDR_PORT + 1000)
		client2.rudp.pktId = client.rudp.pktId
		client2.rudp.desAddr = client.rudp.desAddr
		client2.rudp.send(FIN, client2.rudp.pktId, '')
		print '---------------------END (Client)-----------------------\n'
	elif TestCase[0] == 17:
		client.rudp.connect(destAddr, destPort)
		print '---> Client: connect() - OK'
		client.rudp.send(DAT, client.rudp.pktId, 'the only DAT')
		client.rudp.pktId += 1
		print '---> Client: Enter Data-Delivery'
		print '---> Client: Closing the connection'
		print '---> Client: send FIN to Server (wrong ID)'
		client.rudp.send(FIN, client.rudp.pktId + 100, '')
		print '---------------------END (Client)-----------------------\n'
	elif TestCase[0] == 18:
		client.rudp.connect(destAddr, destPort)
		print '---> Client: connect() - OK'
		client.rudp.send(DAT, client.rudp.pktId, 'the only DAT')
		client.rudp.pktId += 1
		print '---> Client: Enter Data-Delivery'
		print '---> Client: Closing the connection'
		print '---> Client: send FIN to Server (repeatedly)'
		for i in xrange(5):
			client.rudp.send(FIN, client.rudp.pktId, '')
			sleep(2)
		print '---------------------END (Client)-----------------------\n'
	else: pass
