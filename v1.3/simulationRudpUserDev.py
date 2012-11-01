#-------------------------------------#
#   2012 - 2013 Final Year Project    #
#   NeP2P                             #
#   Task1.1: RUDP Server-N:Clients    #
#   YIN  MING  : IE / 5, CUHK         #
#   YING XUHANG: IE / 4, CUHK         #
#-------------------------------------#
#   Client & Server Dev Module        #
#-------------------------------------#

from rudp import *
from time import sleep, time
from threading import Timer
from random import random
from os import stat
from math import ceil
from json import dumps as jsonEncode
from sys import stdout

SERVER_IP = '127.0.0.1' # Local Host
#SERVER_IP = '137.189.97.35'  # lab.neP2P.com
#SERVER_IP = '54.248.144.148' # AWS Ubuntu Server
SERVER_PORT = RCV_PORT
MAX_PKT_SIZE = 1000 #  MAX_PKT_SIZE = MAX_DATA - 4 = 1000
MAX_BLOCK_SIZE = 1000000
TIME_CHECK_PERIOD = 3
strTime = time()

def checkTimeOut(conns):
	conNum = len(conns)
	curTime   = time()
	print '\nOnline C:', conNum, 'time:', curTime - strTime , 'sec'
	while True:
		if conNum == 0: break
		if curTime - conns[0].time > END_WAIT:
			conns.pop(0)
			stdout.write('x ')
			stdout.flush()
			#newprint '\tConnection:', conns.pop(0).destAddr, 'is closed'
		conNum -= 1
	t = Timer(TIME_CHECK_PERIOD, checkTimeOut, [conns])
	t.daemon = True
	t.start()

class rudpServer:
	def __init__(self, srcPort):
		self.skt = socket(AF_INET, SOCK_DGRAM) #UDP
		self.skt.bind(('', srcPort)) #used for recv
		self.conns = []
		self.strTime = time()
		
	def __del__(self):
		self.skt.close()

	def start(self):
		checkTimeOut(self.conns)
		while True:
			recvData, addr = self.skt.recvfrom(MAX_DATA)
			try:
				recvPkt = decode(recvData)
				#print recvPkt	## For debugging
				try:
					c = [c for c in self.conns if c.destAddr == addr][0]
					sendPkt = rudpProcessSwitch[recvPkt['pktType']](recvPkt, c)
					self.conns.remove(c)
					self.conns.append(c)
				except IndexError:
					if recvPkt['pktType'] == SYN:
						self.conns.append( rudpConnection(addr, False) )
						c = self.conns[-1]
						sendPkt = rudpProcessSwitch[SYN](recvPkt, c)
						#print 'New Connection - {}'.format(str(len(self.conns)))
						#, [c.destAddr for c in self.conns]
					else: continue
			except: continue
			else:
				self.skt.sendto(encode(sendPkt), c.destAddr)
				if sendPkt['pktType'] == FIN_ACK: 
					self.conns.remove(c)
					stdout.write('o ')
					stdout.flush()
					#print 'Close Connection: ', c.destAddr
					#print '\tRemaining Connections', [c.destAddr for c in self.conns]
				#print sendPkt	## For debugging

class logClient:
	def __init__(self, srcAddr, desAddr, logAddr):
		self.logAddr   = logAddr
		self.srcAddr   = srcAddr
		self.desAddr   = desAddr

		self.pktSend   = 0
		self.pktReSend = 0
		self.pktRecv   = 0
		self.bytSend   = 0
		self.bytReSend = 0
		
		self.strTimePt = 0
		self.endTimePt = 0
		self.special   = []
		self.status    = False

	def printLog(self):
		print self.srcAddr, '<=>', self.desAddr
		print '\tstrTimePt :', self.strTimePt
		print '\tendTimePt :', self.endTimePt
		print '\tlogAddr   :', self.logAddr
		print '\tpktSend   :', self.pktSend
		print '\tpktReSend :', self.pktReSend
		print '\tpktRecv   :', self.pktRecv
		print '\tbytSend   :', self.bytSend
		print '\tbytReSend :', self.bytReSend
		for s in self.special:
			print '\tSpecial Event:', s
		print 'status: [', self.status, ']'

	#def printShortLong(self):
         #       print 'Client at {}:'.format(self.srcAddr)
          #      pss
                #print 'time={}'.format((self.endTime-self.))

	def convertDic(self):
		dic = {
			'srcAddr'  : self.srcAddr,
			'desAddr'  : self.desAddr,
			'pktSend'  : self.pktSend,
			'pktReSend': self.pktReSend,
			'pktRecv'  : self.pktRecv,
			'bytSend'  : self.pktSend,
			'bytReSend': self.bytReSend,
			'strTimePt': self.strTimePt,
			'endTimePt': self.endTimePt,
			'special'  : self.special,
			'status'   : self.status
		}
		return dic

	def sendLog(self, skt):
		#self.printLog()
		skt.sendto(jsonEncode(self.convertDic()), self.logAddr)

class rudpClient:
	def __init__(self, srcPort, logAddr = ('127.0.0.1', 49999)):
		self.skt = socket(AF_INET, SOCK_DGRAM) #UDP
		self.skt.bind(('', srcPort)) #used for recv
		self.log = logClient(self.skt.getsockname(), None, logAddr)
	
	def __del__(self):
		self.skt.close()

	def connect(self, destIP = SERVER_IP, destPort = SERVER_PORT):
		self.conn = rudpConnection(None, True)
		self.conn.destAddr = (destIP, destPort)

		self.log.desAddr = self.conn.destAddr
		self.log.strTimePt = time()
		isReSend = False

		self.skt.settimeout(RTO)
		for i in xrange(MAX_RESND):
			try:
				if isReSend:
					dataSent = self.skt.sendto(encode(rudpPacket(SYN, self.conn.pktId)), self.conn.destAddr)
					self.log.bytSend += dataSent
					self.log.bytReSend += dataSent
					self.log.pktSend += 1
					self.log.pktReSend += 1
				else:
					self.log.bytSend += self.skt.sendto(encode(rudpPacket(SYN, self.conn.pktId)), self.conn.destAddr)
					self.log.pktSend += 1
				#print rudpPacket(SYN, self.conn.pktId) 	## For debugging
				
				while True:
					recvData, addr = self.skt.recvfrom(MAX_DATA)
					self.log.pktRecv += 1
					try: 
						recvPkt = decode(recvData)
						sendPkt = rudpProcessSwitch[recvPkt['pktType']](recvPkt, self.conn)
						return True
					except WRONG_PKT:
						self.log.special.append('Wrong packet')
						continue
					except KeyError:
						self.log.special.append('Invalid packet type')
						continue
			except timeout:
				self.log.special.append('Timeout in connect()')
				isReSend = True
				continue
			except Exception as e : 
				print e.message
				print '[Handshaking] unexpected error occurs\n' ## For debugging
				return False
		self.log.special.append('Resend 3 times')
		raise MAX_RESND_FAIL()
	
	def sendData(self, data):
		# Compute total size of data and prepare data packets to be sent
		total_pkt = int(ceil(len(data)/float(MAX_PKT_SIZE))) # + int(random()*10)
		data_pkt = range(total_pkt)
		for i in xrange(0, total_pkt, 1):
			data_pkt[i] = data[i*MAX_PKT_SIZE : (i+1)*MAX_PKT_SIZE]
			
		# [HandShaking] - Done
		# [Data-Delivery]
		sendPkt = rudpPacket(DAT, self.conn.pktId)
		for i in xrange(0, len(data_pkt), 1):

			isReSend = False
			
			#sleep(1)

			sendPkt['data'] = data_pkt[i]
			for j in xrange(MAX_RESND):
				try:
					if isReSend:
						dataSent = self.skt.sendto(encode(sendPkt), self.conn.destAddr)
						self.log.bytSend += dataSent
						self.log.bytReSend += dataSent
						self.log.pktSend += 1
						self.log.pktReSend += 1
					else:
						self.log.bytSend += self.skt.sendto(encode(sendPkt), self.conn.destAddr)
						self.log.pktSend += 1
					#print "send:  'pktType':{}, 'pktId':{}, 'data':{} bytes".format(sendPkt['pktType'], sendPkt['pktId'], len(sendPkt['data'])) ## For debugging
					while True:
						recvData, addr = self.skt.recvfrom(MAX_DATA)
						self.log.pktRecv += 1
						try: 
							recvPkt = decode(recvData)
							sendPkt = rudpProcessSwitch[recvPkt['pktType']](recvPkt, self.conn)
							#sleep(1)
							break
						except WRONG_PKT:
							self.log.special.append('Wrong packet')
							continue
						except KeyError:
							self.log.special.append('Invalid packet type')
							continue
				except timeout: 
					if j == MAX_RESND - 1: 
						self.log.special.append('Resend 3 times')
						raise MAX_RESND_FAIL()
					else:
						self.log.special.append('Timeout in sendData()')
						isReSend = True
						continue
				except Exception as e: 
					print e.message
					return False
				break
		return True
		
	def close(self):
		# [Shutdown]
		isReSend = False

		sendPkt = rudpPacket(FIN, self.conn.pktId);
		for i in xrange(MAX_RESND):
			try:
				if isReSend:
					dataSent = self.skt.sendto(encode(sendPkt), self.conn.destAddr)
					self.log.bytSend += dataSent
					self.log.bytReSend += dataSent
					self.log.pktSend += 1
					self.log.pktReSend += 1
				else:
					self.log.bytSend += self.skt.sendto(encode(sendPkt), self.conn.destAddr)
					self.log.pktSend += 1

				self.conn.wait = FIN_ACK
				while True:
					recvData, addr = self.skt.recvfrom(MAX_DATA)
					try: 
						recvPkt = decode(recvData)
						rudpProcessSwitch[recvPkt['pktType']](recvPkt, self.conn)
					except WRONG_PKT:
						self.log.special.append('Wrong packet')
						continue
					except KeyError:
						self.log.special.append('Invalid packet type')
						continue
					except END_CONNECTION:
						# close the connection
						self.log.endTimePt = time()
						self.log.status = True
						self.log.sendLog(self.skt)
						del self.conn
						return True
			except timeout:
				self.log.special.append('Timeout in close()')
				isReSend = True
				continue
			except Exception as e: 
				print e.message
				return False
		self.log.special.append('Resend 3 times')
		self.log.sendLog(self.skt)
		raise MAX_RESND_FAIL()
		
	
		
	def sendFile(self, filepath):
		# Read form file block by block
		# Block size is the size of data that can be sent by calling sendData() every time
		
		fileSize = stat(filepath).st_size
		numOfBlocks = int(ceil(fileSize / float(MAX_BLOCK_SIZE)))

		infile = open(filepath, 'r')
		infile.seek(0)

		for i in xrange(0, numOfBlocks, 1):
			try:
				dataBlock = infile.read(MAX_BLOCK_SIZE)
				if self.sendData(dataBlock): continue
			except Exception as e:
				print e.message
				return False
		infile.close()
		return True
