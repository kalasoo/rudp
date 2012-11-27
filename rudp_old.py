#-------------------------------------#
#   2012 - 2013 Final Year Project    #
#   NeP2P                             #
#   Task1: RUDP (Reliable UDP)        #
#   YIN  MING  : IE / 5, CUHK         #
#   YING XUHANG: IE / 4, CUHK         #
#-------------------------------------#
#   rudp module                       #
#-------------------------------------#
from gevent.socket import *
from rudpException import *
from struct import pack, unpack
from gevent import sleep, spawn
from gevent.pool import Pool

#       8 BYTES    4 BYTES     MAX:1000BYTE
#      +----------+-----------+-------------+
#      |UDP HEADER|RUDP HEADER|  RUDP DATA  |
#      +----------+-----------+-------------+

#BIT:   0         8       16       24     31
#      +-+-------+--------+--------+--------+
#      |0| FLAG  |       DAT / ACK          |
#      +-+-------+--------+--------+--------+
#      |                DATA                |
#      |                                    |
#      |                ....                |
#      +------------------------------------+

#      FLAG: _ _ _ _ _ _ _ 7 bits, each bit is either 0 or 1
#            D A         R
#            A C         E
#            T K         L

#-------------------#
# Constants         #
#-------------------#
MAX_DATA  = 1004
MAX_RESND = 3
RTO       = 1       #The retransmission time period
SDR_PORT  = 50007
RCV_PORT  = 50008	# 50000-50010
MAX_PKTID = 0xffffff
MAX_CONN  = 1000
ACK_LMT   = 100
#-------------------#
# Constants         #
#-------------------#
DAT = 0x40000000
ACK = 0x20000000
REL = 0x01000000
	
#-------------------#
# RUDP              #
#-------------------#
def rudpPacket(pktType = None, pktId = 0, isReliable = True, data = ''):
	return {'type': pktType, 'rel': isReliable, 'id': pktId, 'data': data}

#-------------------#
# Protocol codec    #
#-------------------#
def encode(rudpPkt): #pktId can be either ACK # or SEQ #
    if rudpPkt['id'] <= MAX_PKTID:
        header = rudpPkt['type'] | rudpPkt['id'] | REL if rudpPkt['rel'] else rudpPkt['type'] | rudpPkt['id']
        return pack('i', header) + rudpPkt['data']
    raise ENCODE_DATA_FAIL()

def decode(bitStr):
    if len(bitStr) < 4:
        raise DECODE_DATA_FAIL()
    else:
	    header  = unpack('i', bitStr[:4])[0]
	    return rudpPacket(header & 0x70000000, header & 0x00ffffff, header & REL, bitStr[4:])

#-------------------#
# RUDP Socket       #
#-------------------#
class rudpSocket():
	def __init__(self, srcPort):
		self.skt = socket(AF_INET, SOCK_DGRAM) 	#UDP
		self.skt.bind(('', srcPort)) 			#used for recv
		self.seq = 0

	def __del__(self):
		self.skt.close()
		self.pool.kill()

	def waitACK(self):
		while True:
		#receive ACK
			recvData, addr = self.skt.recvfrom(MAX_DATA)
			try:
			#decode received data
				recvPktInfo = ( decode(recvData)['id'], addr )
				print recvPktInfo
			#stop the coroutine
				self.pool.killone(self.ackPool[recvPktInfo])
			#delete the ackTuple
				del self.ackPool[recvPktInfo]
				print len(self.ackPool)
			except KeyError: continue

	def addListener(self, sendPktInfo): #sendPktInfo = (sendPkt, destAddr)
		if self.pool.full():
			raise Exception('At maximum pool size')
		else:
			recvPktInfo = (sendPktInfo[0]['id'] + 1, sendPktInfo[1])
			self.ackPool[recvPktInfo] = self.pool.spawn(self.ackListener, sendPktInfo, recvPktInfo)
			#self.ackPool[recvPktInfo].join()
	
	def ackListener(self, sendPktInfo, recvPktInfo):
		for i in xrange(3):
			sleep(RTO)
			print '\t', i, 'times'
			self.skt.sendto( encode(sendPktInfo[0]), sendPktInfo[1] )
		del self.ackPool[recvPktInfo]
		print '\ttimeout 3 times:'

	def sendto(self, string, destAddr, isReliable = False):
		result = self._sendto(string, destAddr, isReliable)
		sleep(0.001)
		return result

	#Assumption: you cannot send to different destinations concurrently
	def _sendto(self, string, destAddr, isReliable = False): #destAddr = (destIP, destPort)
		if not hasattr(self, 'pool'):
			self.ackPool = dict() #(pktId, addr) => ackTuple, ackTuple = (resndNum, greenlet)
			self.pool    = Pool(ACK_LMT)
			self.pool.spawn(self.waitACK)
		if len(string) > MAX_DATA: return None
	#pkt
		sendPkt = rudpPacket(DAT, self.seq, isReliable, string)
	#send pkt
		try:
			self.skt.sendto( encode(sendPkt), destAddr )
			if isReliable:
				print 'Looking forward ACK'
				self.addListener( (sendPkt, destAddr) )
			self.seq = (self.seq + 1) % MAX_PKTID
		except Exception as e:
			print e.message 
			return None
		else: return len(string)

	def recvfrom(self):
		if hasattr(self, 'pool'):
			self.ackPool = dict()
			self.pool.kill()
		recvData, addr = self.skt.recvfrom(MAX_DATA)
		try:
			recvPkt = decode(recvData)
		#type
			if recvPkt['type'] != DAT: return None
		#rel
			if recvPkt['rel']:
			#ACK Packet
				sendPkt = rudpPacket(ACK, recvPkt['id'] + 1)
				self.skt.sendto(encode(sendPkt), addr)
		except Exception as e:
			print e.message 
			return None
		else:
			return recvPkt['data'], addr


