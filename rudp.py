#-------------------------------------#
#   2012 - 2013 Final Year Project    #
#   NeP2P                             #
#   Task1: RUDP (Reliable UDP)        #
#   YIN  MING  : IE / 5, CUHK         #
#   YING XUHANG: IE / 4, CUHK         #
#-------------------------------------#
#   rudp module                       #
#-------------------------------------#
from socket import *
from struct import pack, unpack
from time import time 
from rudpException import *

#       8 BYTES    4 BYTES     MAX:1000BYTE
#      +----------+-----------+-------------+
#      |UDP HEADER|RUDP HEADER|  RUDP DATA  |
#      +----------+-----------+-------------+

#BIT:   0         8       16       24     31
#      +-+-------+--------+--------+--------+
#      |0| TYPE  |       SEQ / ACK          |
#      +-+-------+--------+--------+--------+
#      |                DATA                |
#      |                                    |
#      |                ....                |
#      +------------------------------------+

#      TYPE: _ _ _ _ _ _ _ 7 bits, each bit is either 0 or 1
#            S A F D S A A
#            Y C I A Y C C
#            N K N T N K K
#                    + + +
#                    A D F
#                    C A I
#                    K T N

#-------------------#
# Constants         #
#-------------------#
MAX_DATA  = 1004
MAX_RESND = 3
RTO       = 3       #The retransmission time period
SDR_PORT  = 50007
RCV_PORT  = 50008	# 50000-50010	
#-------------------#
# Constants         #
#-------------------#
ACK       = 0x20000000
DAT       = 0x08000000
	
#-------------------#
# RUDP              #
#-------------------#
def rudpPacket(pktType = None, pktId = None, data = ''):
	return {'pktType': pktType, 'pktId': pktId, 'data': data}
#-------------------#
# RUDP Server       #
#-------------------#
'''
#-------------------#
# RUDP Client       #
#-------------------#
def processACK(rudpPkt, c):
	if ACK == c.wait and rudpPkt['pktId'] == c.pktId + 1:
		c.pktId += 1
		return rudpPacket(DAT, c.pktId)
	raise WRONG_PKT('processACK', rudpPkt)
'''

#-------------------#
# Protocol codec    #
#-------------------#
def encode(rudpPkt): #pktId can be either ACK # or SEQ #
    if rudpPkt['pktId'] <= MAX_PKTID:
        header = rudpPkt['pktType'] | rudpPkt['pktId']
        return pack('i', header) + rudpPkt['data']
    raise ENCODE_DATA_FAIL()

def decode(bitStr):
    if len(bitStr) < 4:
        raise DECODE_DATA_FAIL()
    else:
	    header  = unpack('i', bitStr[:4])[0]
	    return rudpPacket(header & 0x7f000000, header & 0x00ffffff, bitStr[4:])

#-------------------#
# RUDP Socket       #
#-------------------#
class rudpSocket():
	def __init__(self, srcPort, isClient):
		self.skt = socket(AF_INET, SOCK_DGRAM) #UDP
		self.skt.bind(('', srcPort)) #used for recv

	def __del__(self):
		self.skt.close()

	def sendto(self, isReliable = True, rudpPkt, destAddr): #destAddr = (destIP, destPort)
		if len(data) <= MAX_DATA:
			self.skt.sendto(encode(rudpPkt), destAddr)
		else
			print 'The data to send is to large: MAX_DATA -', MAX_DATA

	def recvfrom(self, isReliable = True):
		recvData, addr = self.skt.recvfrom(MAX_DATA)
		try:
			recvPkt = decode(recvData)
			if recvPkt['pktType'] != DAT: return None
			if isReliable: sendPkt = rudpPacket(ACK, recvPkt['pktId'] + 1)
		except: return None
		else:
			if isReliable: self.skt.sendto(encode(sendPkt), addr)
			return recvPkt['data']
