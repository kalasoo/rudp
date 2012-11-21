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
class MAX_RESND_FAIL:
	def __init__(self):
		print '\ttimeout 3 times:'
#-------------------#
class ENCODE_DATA_FAIL:
	def __init__(self, dataToEncode):
		print '\tencode() fail:', dataToEncode
class DECODE_DATA_FAIL:
	def __init__(self, pktToDecode):
		print '\tdecode() fail:', pktToDecode
#-------------------#
class WRONG_PKT:
	def __init__(self, func, recvPkt):
		print '\t', func
class END_CONNECTION:
	def __init__(self, c):
		#print '\tconnnection is end'
		#c.printConnection()
		pass
