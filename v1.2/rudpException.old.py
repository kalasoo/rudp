#-------------------------------------#
#   2012 - 2013 Final Year Project    #
#   NeP2P                             #
#   Task1: RUDP (Reliable UDP)        #
#   YIN  MING  : IE / 5, CUHK         #
#   YING XUHANG: IE / 4, CUHK         #
#-------------------------------------#
#   rudpException module              #
#-------------------------------------#

#-------------------#
# Exceptions        #
#-------------------#
class RTO_TIME_OUT(Exception): pass
class END_TIME_OUT(Exception): pass
class MAX_RESND_FAIL():
	def __init__(self):
		print 'timeout 3 times:'
#-------------------#
class BIND_FAIL(): 
	def __init__(self, portNum):
		print 'bind() fail:', portNum
#-------------------#
class SEND_FAIL(): 
	def __init__(self):
		print 'send() fail:'
class SENDTO_FAIL(SEND_FAIL): 
	def __init__(self, length):
		SEND_FAIL.__init__(self)
		print '\tsendto() fail:', length
class ENCODE_DATA_FAIL(SEND_FAIL):
	def __init__(self, dataToEncode):
		SEND_FAIL.__init__(self)
		print '\tencode() fail:', dataToEncode
#-------------------#
class RECV_FAIL():
	def __init__(self):
		print 'recv() fail:'
class RECVFROM_FAIL(RECV_FAIL):
	def __init__(self):
		RECV_FAIL.__init__(self)
		print '\trecvfrom() fail'
class DECODE_DATA_FAIL(RECV_FAIL):
	def __init__(self, dataToDecode):
		RECV_FAIL.__init__(self)
		print '\tdecode() fail:', dataToDecode 
class WRONG_DESTADDR(RECV_FAIL):
	def __init__(self, wDestAddr):
		RECV_FAIL.__init__(self)
		print '\twrong destAddr:', wDestAddr 
class WRONG_TYPE(RECV_FAIL):
	def __init__(self, wType):
		RECV_FAIL.__init__(self)
		print '\twrong type:', wType
class WRONG_PKTID(RECV_FAIL):
	def __init__(self, wPktId):
		RECV_FAIL.__init__(self)
		print '\twrong pktId:', wPktId