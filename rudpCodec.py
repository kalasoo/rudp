#-------------------------------------#
#   2012 - 2013 Final Year Project    #
#   NeP2P                             #
#   Task1: RUDP (Reliable UDP)        #
#   YIN  MING  : IE / 5, CUHK         #
#   YING XUHANG: IE / 4, CUHK         #
#-------------------------------------#
#   rudpCodec module                  #
#-------------------------------------#

from struct import *

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
SYN       = 0x40000000
ACK       = 0x20000000
FIN       = 0x10000000
DAT       = 0x08000000
SYN_ACK   = 0x04000000
ACK_DAT   = 0x02000000
FIN_ACK   = 0x01000000
MAX_PKTID = 0xffffff

#-------------------#
# Protocol codec    #
#-------------------#
def encode(pktType, pktId, data): #pktId can be either ACK # or SEQ #
    if pktId <= MAX_PKTID:
        header = pktType | pktId
        return pack('i', header) + data
    else:
        print 'encode() - pktId overbound'
        return False

def decode(bitStr):
    if len(bitStr) < 4:
        print 'decode() - data < 4 Bytes'
        return False, False, ''
    header  = unpack('i', bitStr[:4])[0]
    pktType = header & 0x7f000000
    pktId   = header & 0x00ffffff
    return pktType, pktId, bitStr[4:]