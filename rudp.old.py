#-------------------------------------#
#   2012 - 2013 Final Year Project    #
#   NeP2P                             #
#   Task1: RUDP (Reliable UDP)        #
#   YIN  MING  : IE / 5, CUHK         #
#   YING XUHANG: IE / 4, CUHK         #
#-------------------------------------#
#   rudp module                       #
#-------------------------------------#
import gevent
from gevent import Timeout
from gevent.socket import *
from rudpCodec import *
from rudpException import *

#       8 BYTES    4 BYTES     MAX:1000BYTE
#      +----------+-----------+-------------+
#      |UDP HEADER|RUDP HEADER|  RUDP DATA  |
#      +----------+-----------+-------------+

#-------------------#
# Constants         #
#-------------------#
MAX_DATA  = 1004
MAX_RESND = 3
RTO       = 3      #The retransmission time period
END_WAIT  = 5      #Close Connection
SDR_PORT  = 50007
RCV_PORT  = 50008
	
#-------------------#
# RUDP              #
#-------------------#
class RUDP:
	def __init__(self, srcPort): #srcPort
		self.skt      = socket(AF_INET, SOCK_DGRAM) #UDP
		self.pktId    = 0
		self.desAddr  = None
		self.recvData = None
		try:
			self.skt.bind(('', srcPort)) #used for recv
		except: raise BIND_FAIL()

#-------------------#
# Connection        #
#-------------------#
#Connection Set Up
	def connect(self, ipAddr = '127.0.0.1', portNum = RCV_PORT, data = 'Test'): #HARDCODING for default address
		self.pktId   = 0
		self.desAddr = (ipAddr, portNum)
	#START
		self.skt.settimeout(RTO)
		self.sarTimeOut(SYN, SYN_ACK, '')
		print '[Connected to]', self.desAddr
		#self.skt.settimeout(RTO)	(**BUG**)

	def accept(self):
		self.pktId = 0
		self.desAddr = None
	#LISTEN
		self.recv(SYN, self.pktId)
		self.desAddr = self.recvData[3]
		self.pktId += 1
	#SYN RECEIVED
		self.send(SYN_ACK, self.pktId, '')
		print '[Connected to]', self.desAddr
		self.skt.settimeout(END_WAIT)

#Data Delivery
	def sarTimeOut(self, sendType, recvType = None, data = ''):
		for i in xrange(MAX_RESND):
			try:
				self.sendAndRecv(sendType, recvType, data)
				return
			except timeout:
				print 'RTO_TIME_OUT'
				continue
		raise MAX_RESND_FAIL()

	def sendAndRecv(self, sendType, recvType = None, data = ''): #sender call
		self.send(sendType, self.pktId, data)
		while True:
			try:
				self.recv(recvType, self.pktId + 1)
			except WRONG_DESTADDR: continue
			except WRONG_PKTID: 
				if self.recvData[1] < self.pktId + 1: continue
				else: raise WRONG_PKTID()
			else:
				self.pktId += 1
				break

	def rasTimeOut(self, sendType, recvType = None, data = ''):
		try:
			self.recvAndSend(sendType, recvType, data)
		except timeout:
			print 'END_TIME_OUT'
			raise END_TIME_OUT()


	def recvAndSend(self, sendType, recvType = None, data = ''):
		while True:
			try:
				self.recv(recvType, self.pktId)
			except WRONG_DESTADDR: continue
			except WRONG_PKTID: 
				if self.recvData[1] < self.pktId: continue
				else: raise WRONG_PKTID()
			else:
				self.pktId += 1
				break
		self.send(sendType, self.pktId, data)

	def send(self, typeSpec, idSpec, data):
		print '\tSent: [{}, {}, ({}), ({})]'.format(typeSpec, idSpec, data[0:15], self.desAddr) 
	
		bitStr = encode(typeSpec, idSpec, data)
		if not bitStr: 
			raise ENCODE_DATA_FAIL((typeSpec, idSpec, data))
		try: 
			self.skt.sendto(bitStr, self.desAddr)
		except: raise SENDTO_FAIL(len(bitStr))

	def recv(self, typeSpec = None, idSpec = None): #Specific type if required
		try:
			data, addr = self.skt.recvfrom(MAX_DATA)
		except timeout: raise timeout
		except: raise RECVFROM_FAIL()
		if self.desAddr and addr != self.desAddr:
			raise WRONG_DESTADDR(addr)
			self.recvData = None
		self.recvData = list(decode(data)) + [addr]
		print '\t--Recv: [{}, {}, ({}), ({})]'.format(self.recvData[0], self.recvData[1], self.recvData[2][0:15], self.recvData[3]) 
		if not self.recvData[0]: 
			raise DECODE_DATA_FAIL(data)
		if typeSpec and self.recvData[0] != typeSpec: 
			raise WRONG_TYPE(self.recvData[0])
		if idSpec and self.recvData[1] != idSpec: 
			raise WRONG_PKTID(self.recvData[1])

#Connection Shut Down
	def close(self): #close a connection, send FIN to the receiver
		try:
	#CLOSE
			self.sarTimeOut(FIN, FIN_ACK, '')
	#END
			print '[Disconnect with]', self.desAddr
			self.endRudp()
		except:
			self.endRudp()

	def end(self): #end a connection after receiving FIN from the sender
		while True:
	#END
			try:
				self.send(FIN_ACK, self.pktId + 1, '')
				while True:
					try:
						self.recv(FIN, self.pktId)
					except WRONG_DESTADDR: continue
					except WRONG_PKTID: 
						if self.recvData[1] < self.pktId + 1: continue
						else: raise WRONG_PKTID()
					else:
						break
			except timeout:
				print '[Disconnect with]', self.desAddr
				self.endRudp()
				return
			except:
				self.endRudp()
				return

#sharpEnd
	def endRudp(self, closeSKT=True):
		print 'END RUDP'
		if closeSKT: 
			self.skt.close()
			print 'SOCKET CLOSED'
		self.pktId    = 0
		self.desAddr  = None
		self.recvData = None

#-------------------#
# Sender & Receiver #
#-------------------#

# Temporarily moved to rudpUser.py

'''
class rudpSender:
	def __init__(self, srcPort = SDR_PORT):
		self.rudp = RUDP(srcPort)

	def sendData(self, data, ipAddr, desPort = RCV_PORT): # data
		pass

	def sendFile(self, file, ipAddr, desPort = RCV_PORT): # file - file object
		pass

class rudpReceiver:
	def __init__(self, srcPort = RCV_PORT):
		self.rudp = RUDP(srcPort)

	def receiveData(self):
		pass

	def receiveFile(self, fileName): #receive and write to fileName
		pass
'''
