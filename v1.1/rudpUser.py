from rudp import *
from time import sleep

TESTING = True
#TestCase = (1, '[Handshaking] Server: No SYN for very long time', 'Server: auto shutdown')
#TestCase = (2, '[Handshaking] Server: pkts with wrong type and id received','Server: ignore')
TestCase = (3, '[Handshaking] Client: No SYN_ACK for RTO_TIME_OUT / MAX_RESND', 'Client: Re-transmission / "Close"')
#TestCase = (4, '[Handshaking] Client: SYN_ACK with wrong DESTADDR', 'Client: ignore')
#TestCase = (5, '[Handshaking] Client: SYN_ACK with wrong TYPE or ID', 'Client: "Close"')
#TestCase = (6, '[Handshaking ~ Data-Delivery] Server: SYN again after last SYN_ACK', 'Server: SYN_ACK / END_TIME_OUT')
#TestCase = (7, '[Data-Delivery] Client: No ACK for RTO_TIME_OUT / MAX_RESND', 'Client: Re-transmission / "Close"')
#TestCase = (8, '[Data-Delivery] Client: ACK with wrong DESTADDR or ID = pktId - 1', 'Client: ignore')
#TestCase = (9, '[Data-Delivery] Client: ACK with wrong TYPE or other ID', 'Client: "Close"')
#TestCase = (10,'[Data-Delivery] Server: NO DAT for END_TIME_OUT', 'Server: "End"')
#TestCase = (11,'[Data-Delivery] Server: DAT with wrong DESTADDR or ID = pktId - 1', 'Server: ignore')
#TestCase = (12,'[Data-Delivery] Server: DAT with wrong TYPE (SYN) or other ID', 'Server: "End"')  ##***
#TestCase = (13,'[Shutdown] Client: No FIN_ACK for RTO_TIME_OUT / MAX_RESND', 'Client: Re-transmission / "Close"')
#TestCase = (14,'[Shutdown] Client: FIN_ACK with wrong DESTADDR', 'Client: ignore')
#TestCase = (15,'[Shutdown] Client: FIN_ACK with wrong TYPE or other ID', 'Server: "End"')
#TestCase = (16,'[Shutdown] Server: FIN with wrong DESTADDR', 'Server: ignore')
#TestCase = (17,'[Shutdown] Server: FIN with wrong ID', 'Server: "End"')
#TestCase = (18,'[Shutdown] Server: FIN again after last FIN_ACK', 'Server: FIN_ACK / END_TIME_OUT')

TestOn = False
TEST_RCV_PORT = RCV_PORT
MAX_PKT_SIZE = 100

class rudpSender:
	def __init__(self, srcPort = SDR_PORT):
		try:	self.rudp = RUDP(srcPort)
		except BIND_FAIL:
			self.rudp.endRudp(False)
			
	def sendData(self, data, ipAddr = '127.0.0.1', desPort = TEST_RCV_PORT): # data
	# Compute total size of data and prepare data packets to be sent
		total_pkt = len(data)/MAX_PKT_SIZE + 1
		data_pkt = range(total_pkt)
		for i in xrange(0, total_pkt, 1):
			data_pkt[i] = data[i*MAX_PKT_SIZE : (i+1)*MAX_PKT_SIZE-1]
		
	# [Handshaking]	
		try: 
			self.rudp.connect(ipAddr, desPort)
		except (SEND_FAIL, RECV_FAIL, MAX_RESND_FAIL):
			self.rudp.endRudp(False)
			return False
		except:
			print "===> [Handshaking] unexpected error occurs"
			return False
			
	# [Data-Delivery]	
		for i in xrange(0, len(data_pkt), 1):
			try:
				self.rudp.sarTimeOut(DAT, ACK, data_pkt[i])			
				sleep(1)
			except (SEND_FAIL, RECV_FAIL, MAX_RESND_FAIL):
				self.rudp.endRudp(False)
				return False
			except:
				print '[Data-Delivery] unexpected error occurs'
				return False		
	
	# [Shutdown]
		self.rudp.close()
		return True

	def sendFile(self, file, ipAddr, desPort = RCV_PORT): # file - file object
		pass

class rudpReceiver:
	def __init__(self, srcPort = RCV_PORT):
		try:	self.rudp = RUDP(srcPort)
		except BIND_FAIL:
			self.rudp.endRudp(False)

	def receiveData(self):
	# Prepare buffer for data to be received
		bufferData = ''	# Testing: string only
		bufferDataSize = None
		
	# [Handshaking]
		if TESTING: print '===> Waiting for connection request from Client ...'	
		try:	self.rudp.accept()	# END_TIME timer has been set
		except (SEND_FAIL, RECV_FAIL):
			self.rudp.endRudp(False)
			return False
		except Exception as e: 
			print e.message
			return False
		except: 
			print "===> [Handshaking] WTF"
			return False
				
	# [Handshaking ~ Data-Delivery]
		while True:
			try: 
				self.rudp.recv(DAT, self.rudp.pktId)
				bufferData += self.rudp.recvData[2]
				self.rudp.pktId += 1;
				self.rudp.send(ACK, self.rudp.pktId,'')
				break
			except WRONG_TYPE:
				if self.rudp.recvData[0] == SYN and self.rudp.recvData[1] == self.rudp.pktId - 1: 
					self.rudp.send(SYN_ACK, self.rudp.pktId, '')
					continue
			except timeout:
				if TESTING: print '===> [Handshaking ~ Data-Delivery]: no DAT is received'
				self.rudp.endRudp(False)
				return False
			except (SEND_FAIL, RECV_FAIL):
				self.rudp.endRudp(False)
				return False
			except: 
				print "===> [Handshaking ~ Data-Delivery] Unexpected error occurs"
				return False
				
	# [Data-Delivery]
		if TESTING: print '===> Data transfer starts ...'
		while True:
			try:
				self.rudp.rasTimeOut(ACK, DAT, '')
				bufferData += self.rudp.recvData[2]
			except WRONG_TYPE:
				if self.rudp.recvData[0] == FIN and self.rudp.recvData[1] == self.rudp.pktId: 
					if TESTING: print '===> Request for connection shutdown is received.'
					break
				else: self.rudp.endRudp(False)
				return False
			except (SEND_FAIL, RECV_FAIL, MAX_RESND_FAIL):
				self.rudp.endRudp(False)
				return False
			except: 
				print "===> [Data-Delivery] Unexpected error occurs"
				return False
		
	# [Shutdown]
		self.rudp.end()
		return bufferData
				

	def receiveFile(self, fileName): #receive and write to fileName
		pass
