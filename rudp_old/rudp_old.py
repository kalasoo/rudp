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
END_WAIT  = 10      #Close Connection
SDR_PORT  = 50007
RCV_PORT  = 50008	# 50000-50010	
#-------------------#
# Constants         #
#-------------------#
SYN       = 0x40000000
ACK       = 0x20000000
FIN       = 0x10000000
DAT       = 0x08000000
SYN_ACK   = 0x04000000
ACK_DAT   = 0x02000000
FIN_ACK   = 0x01000000
MAX_PKTID = 0xffffff
	
#-------------------#
# RUDP              #
#-------------------#
def rudpPacket(pktType = None, pktId = None, data = ''):
	return {'pktType': pktType, 'pktId': pktId, 'data': data}
#-------------------#
# RUDP Server       #
#-------------------#
def processSYN(rudpPkt, c):
	if SYN in c.accept:
		if c.wait == SYN: c.accept += [DAT, FIN]
		c.pktId = rudpPkt['pktId'] + 1
		c.wait  = DAT
		c.time  = time()
		return rudpPacket(SYN_ACK, c.pktId)
	raise WRONG_PKT('processSYN', rudpPkt)
def processDAT(rudpPkt, c):
	if DAT == c.wait:
		if rudpPkt['pktId'] == c.pktId:
			if SYN in c.accept: c.accept.remove(SYN)
			c.pktId += 1
			c.data  += rudpPkt['data']
			c.time   = time() 
			return rudpPacket(ACK, c.pktId)
		elif rudpPkt['pktId'] == c.pktId - 1: 
			c.time   = time()
			return rudpPacket(ACK, c.pktId)
		elif rudpPkt['pktId'] < c.pktId - 1: raise WRONG_PKT('processDAT [Duplicated]', rudpPkt) # Bugs
	raise WRONG_PKT('processDAT', rudpPkt)
def processFIN(rudpPkt, c):
	if FIN in c.accept and rudpPkt['pktId'] == c.pktId:
		if DAT in c.accept: c.accept.remove(DAT)
		c.wait = FIN
		c.time = time()
		return rudpPacket(FIN_ACK, c.pktId + 1)
	raise WRONG_PKT('processFIN', rudpPkt)
#-------------------#
# RUDP Client       #
#-------------------#
def processSYN_ACK(rudpPkt, c):
	if SYN_ACK == c.wait and rudpPkt['pktId'] == c.pktId + 1:
		c.wait = ACK
		c.pktId += 1
		return rudpPacket(DAT, c.pktId)
	raise WRONG_PKT('processSYN_ACK', rudpPkt)
def processACK(rudpPkt, c):
	if ACK == c.wait and rudpPkt['pktId'] == c.pktId + 1:
		c.pktId += 1
		return rudpPacket(DAT, c.pktId)
	raise WRONG_PKT('processACK', rudpPkt)
def processFIN_ACK(rudpPkt, c):
	if FIN_ACK == c.wait and rudpPkt['pktId'] == c.pktId + 1:
		c.pktId += 1
		raise END_CONNECTION(c)
	raise WRONG_PKT('processFIN_ACK', rudpPkt)

#rudpProcessSwitch[rudpPkt['pktType']](rudpPkt, c) <-- how you use process functions
rudpProcessSwitch = {SYN: processSYN, SYN_ACK: processSYN_ACK, DAT: processDAT, ACK: processACK, FIN: processFIN, FIN_ACK: processFIN_ACK}
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
# RUDP Connection   #
#-------------------#
class rudpConnection():
	def __init__(self, destAddr, isClient):
		self.destAddr = destAddr
		self.wait     = SYN_ACK if isClient else SYN
		self.pktId    = 0
		if not isClient: 
			self.accept = [SYN] #[SYN, DAT, FIN]
			self.time   = 0
			self.data   = ''
    
    	def checkTime(self, time):
    		if time - self.time > END_WAIT:
    			return False
    		return True

	def printConnection(self):
		print '[RUDP Connection]'
		print '\tdestAddr:', self.destAddr
		print '\tpktId   :', self.pktId
		print '\twait    :', self.wait
		try:
			print '\taccept  :', self.accep
			print '\ttime    :', self.time
			print '\tdata    :', self.data
		except:
			print 'NOT VALID'

