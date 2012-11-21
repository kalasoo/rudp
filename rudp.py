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
	def __init__(self, srcPort, isClient):
		self.skt = socket(AF_INET, SOCK_DGRAM) #UDP
		self.skt.bind(('', srcPort)) #used for recv

	def __del__(self):
		self.skt.close()

	def sendto(self, rudpPkt, destAddr): #destAddr = (destIP, destPort)
		if len(rudpPkt['data']) <= MAX_DATA:
			self.skt.sendto(encode(rudpPkt), destAddr)
			if rudpPkt['rel']:
				print 'Looking forward ACK'
		else:
			print 'The data to send is too large: MAX_DATA -', MAX_DATA

	def recvfrom(self):
		recvData, addr = self.skt.recvfrom(MAX_DATA)
		try:
			recvPkt = decode(recvData)
			if recvPkt['type'] != DAT: return None
			if recvPkt['rel']: sendPkt = rudpPacket(ACK, recvPkt['id'] + 1)
		except: return None
		else:
			if recvPkt['rel']: self.skt.sendto(encode(sendPkt), addr)
			return recvPkt['data']

	#def resend(self, rudpPacket, destAddr, resendNum):
