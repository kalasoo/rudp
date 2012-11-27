#-------------------------------------#
#   2012 - 2013 Final Year Project    #
#   NeP2P                             #
#   Task1: RUDP (Reliable UDP)        #
#   YIN  MING  : IE / 5, CUHK         #
#   YING XUHANG: IE / 4, CUHK         #
#-------------------------------------#
#   rudp module                       #
#-------------------------------------#

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
# Libraries         #
#-------------------#
from gevent.socket import *
from rudpException import *
from struct import pack, unpack
from gevent import sleep, spawn
from gevent.pool import Pool
from time import time
from Queue import Queue
from Collections import OrderedDict as oDict
#-------------------#
# RUDP Constants    #
#-------------------#
MAX_DATA  = 1004
MAX_RESND = 3
RTO       = 1       #The retransmission time period
SDR_PORT  = 50007
RCV_PORT  = 50008	# 50000-50010
MAX_PKTID = 0xffffff
MAX_CONN  = 1000
ACK_LMT   = 100
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
	#UDP socket
		self.skt  = socket(AF_INET, SOCK_DGRAM) 	#UDP
		self.skt.bind(('', srcPort)) 			#used for recv
	#receivers, senders and ACK waiting list
		self.snds = oDict()						#destAddr => a list of acceptable pktId
		self.rcvs = oDict()						#destAddr => lastPktId
		self.acks = oDict()						#(pktId, destAddr) => (timestamp, resendNum, sendPkt)
	#coroutine
		spawn(self.recvLoop)
		spawn(self.ackLoop)
	#packet Buffer
		datPkts   = Queue()
	def __del__(self):
		self.skt.close()

	def recvLoop(self):
		while True:
			data, addr = self.skt.recvfrom(MAX_DATA)
			try:
				recvPkt = decode(data)
			#type
				if recvPkt['type'] == DAT: self.proDAT(recvPkt, addr)
				elif recvPkt['type'] == ACK: self.proACK(recvPkt, addr)
				else: continue
			except Exception as e:
				print e.message
			sleep(0)

	def ackLoop(self):
		while True:
			sleep(0)

	def proDAT(self, recvPkt, addr):
		pass

	def proACK(self, recvPkt, addr):
		pass


	#Assumption: you cannot send to different destinations concurrently
	def sendto(self, string, destAddr, isReliable = False): #destAddr = (destIP, destPort)
		if len(string) > MAX_DATA: return None
	#not reliable
		if not isReliable: return self.skt.sendto( encode(sendPkt), destAddr )
	#reliable
		try:
			sndId = self.snds[destAddr]
		except KeyError:
			if len(self.snds) == MAX_CONN: self.snds.popitem(False)
			self.snds[destAddr], sndId = 0, 0
	#send pkt
		ret = self.skt.sendto( encode(sendPkt), destAddr )
		self.ends[destAddr] += 1
	#ACK oDict
		print 'Looking forward ACK'
		self.acks[(sndId + 1, destAddr)] = (time, 0, sendPkt)
		return ret

	def recvfrom(self):
		recvPkt, addr = datPkts.get() #Blocking
		if recvPkt['type'] != DAT: return None
		isReturn = True
		try:
		#id
			pktId, rcv = recvPkt['id'], self.rcvs[addr]
		except KeyError:
		#initiate + replacement
			if pktId == 0:
				if len(self.rcvs) == MAX_CONN: self.rcvs.popitem(False)
				self.rcvs[addr] = [1]
			else: 
				recvPkt['rel'], isReturn = False, False
		else:
		#rel
			if recvPkt['rel']:
				try:
				#reset
					if pktId == 0: self.rcvs[addr] = [1]
				#normal	
					if pktId == rcv[-1]: rcv[-1] += 1
					else: rcv.remove(x) # => ValueError
				except ValueError:
				#shutdown
					if pktId == MAX_PKTID: del self.rcvs[addr]
					elif pktId > rcv[-1]:
						rcv.extend( range(rcv[-1] + 1, pktId) )
						rcv.append( pktId + 1 )
					else: isReturn = False
		if recvPkt['rel']:
		#ACK Packet
			sendPkt = rudpPacket(ACK, pktId + 1)
			self.skt.sendto( encode(sendPkt), addr )
		if isReturn: return recvPkt['data'], addr

