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
#                        I
#                        A
#                        B
#                        L
#                        E

#-------------------#
# Constants         #
#-------------------#
MAX_DATA  = 1004
MAX_RESND = 3
RTO       = 3       #The retransmission time period
SDR_PORT  = 50007
RCV_PORT  = 50008	# 50000-50010
MAX_PKTID = 0xffffff
#-------------------#
# Constants         #
#-------------------#
DAT = 0x40000000
ACK = 0x20000000
REL = 0x01000000
	
#-------------------#
# RUDP              #
#-------------------#
def rudpPacket(pktType = None, pktId = None, isReliable = True, data = ''):
	return {'pktType': pktType, 'pktRel': isReliable, 'pktId': pktId, 'data': data}

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
        header = rudpPkt['pktType'] | rudpPkt['pktId'] | REL if rudpPkt['pktRel'] else rudpPkt['pktType'] | rudpPkt['pktId']
        return pack('i', header) + rudpPkt['data']
    raise ENCODE_DATA_FAIL()

def decode(bitStr):
    if len(bitStr) < 4:
        raise DECODE_DATA_FAIL()
    else:
	    header  = unpack('i', bitStr[:4])[0]
	    return rudpPacket(header & 0x7f000000, header & 0x00ffffff, header & REL, bitStr[4:])

#-------------------#
# RUDP Socket       #
#-------------------#
class rudpSocket():
	def __init__(self, srcPort, isClient):
		self.skt = socket(AF_INET, SOCK_DGRAM) #UDP
		self.skt.bind(('', srcPort)) #used for recv

	def __del__(self):
		self.skt.close()

	def sendto(self, rudpPkt, destAddr, isReliable = True): #destAddr = (destIP, destPort)
		if len(data) <= MAX_DATA:
			self.skt.sendto(encode(rudpPkt), destAddr)
		else:
			print 'The data to send is to large: MAX_DATA -', MAX_DATA

	def recvfrom(self):
		recvData, addr = self.skt.recvfrom(MAX_DATA)
		try:
			recvPkt = decode(recvData)
			if recvPkt['pktType'] != DAT: return None
			if recvPkt['pktRel']: sendPkt = rudpPacket(ACK, recvPkt['pktId'] + 1)
		except: return None
		else:
			if recvPkt['pktRel']: self.skt.sendto(encode(sendPkt), addr)
			return recvPkt['data']
