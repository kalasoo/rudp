#-------------------------------------#
#   2012 - 2013 Final Year Project    #
#   NeP2P                             #
#   Task1: RUDP (Reliable UDP)        #
#   YIN  MING  : IE / 5, CUHK         #
#   YING XUHANG: IE / 4, CUHK         #
#-------------------------------------#
#   rudp utilities                    #
#-------------------------------------#
from rudp import *
from math import ceil

SERVER_IP   		= '127.0.0.1'
SERVER_PORT 		= RCV_PORT
MAX_PKT_SIZE 		= 1000
MAX_BLOCK_SIZE 		= 1000000
TIME_CHECK_PERIOD 	= 3

#-------------------#
# RUDP Dumb Receiver#
# x Setup, Shutdown #
#-------------------#
class rudpDumbReceiver:
	def __init__(self, srcPort):
		self.skt = socket(AF_INET, SOCK_DGRAM) #UDP
		self.skt.bind(('', srcPort)) #used for recv
		
	def __del__(self):
		self.skt.close()

	#return the data received and send the corresponding ACK
	def receive(self): 
		recvData, addr = self.skt.recvfrom(MAX_DATA)
		try:
			recvPkt = decode(recvData)
			if recvPkt['pktType'] != DAT: return None
			sendPkt = rudpPacket(ACK, recvPkt['pktId'] + 1)
		except: None
		else:
			self.skt.sendto(encode(sendPkt), addr)
			return recvPkt['data']

#-------------------#
# RUDP Dumb Client  #
# x Setup, Shutdown #
#-------------------#
class rudpDumbSender:
	def __init__(self, srcPort, destIP = SERVER_IP, destPort = SERVER_PORT):
		self.skt = socket(AF_INET, SOCK_DGRAM) #UDP
		self.skt.bind(('', srcPort)) #used for recv
		self.skt.settimeout(RTO)
		self.conn = rudpConnection(None, True)
		self.conn.wait = ACK
		self.conn.destAddr = (destIP, destPort)
		
	def __del__(self):
		self.skt.close()

	def srs(self, sendPkt): #sendPkt --> recvPkt --> sendPkt
		for i in xrange(MAX_RESND):
			try:
				self.skt.sendto(encode(sendPkt), self.conn.destAddr)
				while True:
					recvData, addr = self.skt.recvfrom(MAX_DATA)
					try:
						recvPkt = decode(recvData)
						return rudpProcessSwitch[recvPkt['pktType']](recvPkt, self.conn)
					except WRONG_PKT, KeyError: continue
			except timeout: continue
		raise MAX_RESND_FAIL()

	def sendData(self, data):
		pktNum = int(ceil(len(data) / float(MAX_PKT_SIZE)))
		#data[i*MAX_PKT_SIZE : (i+1)*MAX_PKT_SIZE]

		# [Data-Delivery]
		sendPkt = rudpPacket(DAT, self.conn.pktId)
		for i in xrange(pktNum):
			sendPkt['data'] = data[i * MAX_PKT_SIZE : (i + 1) * MAX_PKT_SIZE]
			try:
				sendPkt = self.srs( sendPkt )
			except Exception as e:
				#print e.message
				return False
		return True

