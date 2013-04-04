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
from time import time, localtime, strftime
from Queue import Queue
from Queue import Empty as QEmpty
from collections import OrderedDict as oDict
#-------------------#
# RUDP Constants    #
#-------------------#
MAX_DATA  = 10244
MAX_RESND = 3
RTO       = 1 		# The retransmission time period
SDR_PORT  = 50007
RCV_PORT  = 50008	# 50000-50010
MAX_PKTID = 0xffffff
MAX_CONN  = 1000
ACK_LMT   = 100
DAT = 0x40000000
ACK = 0x20000000
REL = 0x01000000
#-------------------#
# RUDP MODE         #
#-------------------#
RUDP_DEBUG = False
RUDP_LOG   = False
RUDP_STAT  = True
STAT_PKTS  = 10
class Logger():
	def __init__(self, f = None):
		self.initTime = time();
		if f:
			self.f = f
		else:
			self.f = open('rudp_log_' + str(int(time())) + '.txt', 'a')
		self.logWriteLine( 'NEW_SOCKET', strftime("%a, %d %b %Y %H:%M:%S +0000", localtime()) )
	def __del__(self):
		self.logWriteLine( 'END_SOCKET', strftime("%a, %d %b %Y %H:%M:%S +0000", localtime()) )
		self.f.close()
	def logWriteLine(self, option, *data):
		data = [str(time() - self.initTime), option] + list(data)
		self.f.write( ' '.join(str(i) for i in data) + '\n' )

class Recorder():
	def __init__(self, pkt_period = STAT_PKTS):
		self.lastTime = time()
		self.perStat  = {}  # addr  => [sendpkt_num, sendbyte_num, recvpkt_num, recvbyte_num, retransmit_num]
		self.ttlStat  = {}	# addr  => [sendpkt_num, sendbyte_num, recvpkt_num, recvbyte_num, retransmit_num]
		self.timeStat = []  # index => [timestamp, perStat]
		self.ttlTime  = 0
		self.period   = pkt_period if pkt_period else STAT_PKTS
		self.onperiod = 0
	def updateSend(self, addr, length):
		if addr not in self.perStat:
			self.perStat[addr] = [0, 0, 0, 0, 0]
		self.perStat[addr][0] += 1
		if length >= 0:
			self.perStat[addr][1] += length
		self.onperiod += 1
		if self.onperiod == self.period:
			self.updateOnTime()
			self.onperiod = 0
	def updateRecv(self, addr, length):
		if addr not in self.perStat:
			self.perStat[addr] = [0, 0, 0, 0, 0]
		self.perStat[addr][2] += 1
		if length >= 0:
			self.perStat[addr][3] += length
		self.onperiod += 1
		if self.onperiod == self.period:
			self.updateOnTime()
			self.onperiod = 0
	def updateLoss(self, addr):
		self.perStat[addr][4] += 1
	def updateOnTime(self):
		self.timeStat.append([time() - self.lastTime, self.perStat])
		self.lastTime = time()
		for addr, value in self.perStat.iteritems():
			if addr in self.ttlStat:
				self.ttlStat[addr] = [sum(a) for a in zip(self.ttlStat[addr], value)]
			else:
				self.ttlStat[addr] = value
		self.perStat = {}
		self.printPeriod()
	def printPeriod(self):
		print str(self.timeStat[-1])
	def printTTL(self):
		print str(self.timeStat)
		print str(self.ttlStat)

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
		return rudpPacket(header & 0x7e000000, header & 0x00ffffff, header & REL, bitStr[4:])

#-------------------#
# DataStructure     #
#-------------------#
class ListDict():
	def __init__(self):
	#addr   => a ref to an element in the list 
		self.dict = dict()
	#index  => [addr, value]
		self.list = list()
	#length of dict & list
		self.len  = 0

	def __getitem__(self, addr):
		ref = self.dict[addr]
		if self.list[-1] != ref:
			self.list.remove(ref)
			self.list.append(ref)
		return ref

	def resetItem(self, addr, value):
		ref = self.dict[addr]
		if self.list[-1] != ref:
			self.list.remove(ref)
			self.list.append(ref)
		ref[1] = value

	def newItem(self, addr, value):
		if self.len == MAX_CONN:
		#remove the first one in the ListDict
			del self.dict[self.list[0][0]]
			self.list.pop(0)
		else:
			self.len += 1
	#add new item
		ref = [addr, value]
		self.list.append(ref)
		self.dict[addr] = ref

	def __delitem__(self, addr):
		self.list.remove( self.dict[addr] )
		del self.dict[addr]
		self.len -= 1

#-------------------#
# RUDP Socket       #
#-------------------#
class rudpSocket(object):
	def __init__(self, srcPort):
	#UDP socket
		self.skt  = socket(AF_INET, SOCK_DGRAM) #UDP
		self.skt.bind(('', srcPort)) 			#used for recv
	#receivers, senders and ACK waiting list
		self.expId 		= ListDict()			#destAddr => a list of acceptable pktId
		self.nextId 	= ListDict()			#destAddr => lastPktId
		self.notACKed 	= oDict()				#(pktId, destAddr) => [timestamp, resendNum, sendPkt]
	#packet Buffer
		self.datPkts   = Queue()
	#coroutine
		spawn(self.recvLoop)
		spawn(self.ackLoop)
		sleep(0)
	#failed Connections
		self.failed = []
	#write log
		if RUDP_LOG:
			self.log = Logger()
	#stat
		if RUDP_STAT:
			self.rec = Recorder()

	def __del__(self):
		self.skt.close()
		if RUDP_LOG:
			del self.log
		if RUDP_STAT:
			self.rec.printTTL()
		

	def recvLoop(self):
		while True:
			data, addr = self.skt.recvfrom(MAX_DATA)
			recvPkt = decode(data)
		#type
			if recvPkt['type'] == DAT: self.proDAT(recvPkt, addr)
			elif recvPkt['type'] == ACK: self.proACK(recvPkt, addr)
			#except Exception as e:
			#	print e.message
			sleep(0)

	def ackLoop(self):
		while True:
			curTime	= time()
			timeToWait = 0
		#pop from left: key = (pktId, destAddr) => value = (timestamp, resendNum, sendPkt)
			for key, triple in self.notACKed.iteritems():
				if curTime - triple[0] < RTO:
					timeToWait = triple[0] + RTO - curTime 
					break
				else:
					triple[0] = curTime
				#update resendNum
					#print 'timeout', key[1][0], triple[2]['id']
					triple[1] += 1
					if RUDP_LOG:
						self.log.logWriteLine('LOSS', key[1], key[0])
					if RUDP_STAT:
						self.rec.updateLoss(key[1])
					if triple[1] == 3: 
						if RUDP_LOG:
							self.log.logWriteLine('CON_FAIL', key[1])
					#remove from notAcked
						del self.notACKed[key]
					#remove from nextId
						try: 
							del self.nextId[key[1]]
						#send MAX_PKTID to receiver
							self.skt.sendto( encode(rudpPacket(DAT, MAX_PKTID, True, '')), key[1] ) 
						except KeyError: continue 
					#raise exception
						self.failed.append(key[1])
					else:
					#put this to the end
						self.notACKed[key] = self.notACKed.pop(key)
					#resendPkt
						self.skt.sendto( encode(triple[2]), key[1] )
			#print 'ackLoop end', timeToWait
			sleep(timeToWait)

	def proDAT(self, recvPkt, addr):
	#not rel
		if not recvPkt['rel']: self.datPkts.put((recvPkt, addr))
	#rel
		else:
			isReturn = True
			try:
			#id, expIdList
				pktId, expIdList = recvPkt['id'], self.expId[addr][1]
			except KeyError:
				pktId = recvPkt['id']
			#initiate + replacement
				if pktId == 0:
					self.expId.newItem(addr, [1])
					if RUDP_LOG:
						self.log.logWriteLine('NEW_RECEIVER', addr)
				else: return
			else:
				try:
				#reset
					if pktId == 0: self.expId.resetItem(addr, [1])
				#normal	
					elif pktId == expIdList[-1]: expIdList[-1] += 1
				#lost packets received
					else: expIdList.remove(pktId) # => ValueError
				except ValueError as e:
					#print e.message
				#shutdown
					if pktId == MAX_PKTID: del self.expId[addr]
				#packet loss
					elif pktId > expIdList[-1]:
						expIdList.extend( range(expIdList[-1] + 1, pktId) )
						expIdList.append( pktId + 1 )
				#duplicate packets
					else: isReturn = False
		#ACK Packet
			if pktId == MAX_PKTID: pktId = 0
			else: pktId += 1
			sendPkt = rudpPacket(ACK, pktId)
			self.skt.sendto( encode(sendPkt), addr )
			if isReturn: self.datPkts.put((recvPkt, addr))


	def proACK(self, recvPkt, addr):
		try:
			#print (recvPkt['id'], addr), 'ACK received'
			#print recvPkt['id'], addr
			del self.notACKed[(recvPkt['id'], addr)]
			if RUDP_LOG:
				self.log.logWriteLine('ACK', addr, recvPkt['id'])
		except KeyError:
			#print 'proACK Fail' 
			return 

	def sendto(self, string, destAddr, isReliable = False): #destAddr = (destIP, destPort)
		if len(string) > MAX_DATA: return None
	#not reliable
		if not isReliable: return self.skt.sendto( encode(rudpPacket(DAT, 0, isReliable, string)), destAddr )
	#reliable
		try:
			nextId = self.nextId[destAddr][1]
		except KeyError:
			if RUDP_LOG:
				self.log.logWriteLine('NEW_SENDER', destAddr)
			self.nextId.newItem(destAddr, 0)
			nextId = 0
	#pkt
		sendPkt = rudpPacket(DAT, nextId, isReliable, string)
	#send pkt
		if RUDP_LOG:
			self.log.logWriteLine('SEND', destAddr, len(sendPkt['data']))
		if RUDP_STAT:
			self.rec.updateSend(destAddr, len(sendPkt['data']))
		ret = self.skt.sendto( encode(sendPkt), destAddr )
		nextId += 1
		if nextId > MAX_PKTID: nextId = 0
		self.nextId[destAddr][1] = nextId
	#ACK oDict
		#print 'Looking forward ACK'
		self.notACKed[(nextId, destAddr)] = [time(), 0, sendPkt]
		return ret

	def recvfrom(self, isBlocking = True):
		while True:
			try:
				recvPkt, addr = self.datPkts.get_nowait() #Non-blocking
				if RUDP_LOG:
					self.log.logWriteLine('RECV', addr, len(recvPkt['data']))
				if RUDP_STAT:
					self.rec.updateRecv(addr, len(recvPkt['data']))
				break
			except QEmpty:
				#print 'no data'
				if not isBlocking: raise NO_RECV_DATA()
				sleep(0.01)
		return recvPkt['data'], addr
