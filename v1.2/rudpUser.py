#-------------------------------------#
#   2012 - 2013 Final Year Project    #
#   NeP2P                             #
#   Task1.1: RUDP Server-N:Clients    #
#   YIN  MING  : IE / 5, CUHK         #
#   YING XUHANG: IE / 4, CUHK         #
#-------------------------------------#
#   Server module                     #
#-------------------------------------#

from rudp import *
from time import sleep
from random import random

SERVER_IP = '127.0.0.1'
SERVER_PORT = RCV_PORT
MAX_PKT_SIZE = 100  #  MAX_PKT_SIZE = MAX_DATA - 4
MAX_BLOCK_SIZE = 1000

class rudpServer:
	def __init__(self, srcPort):
		self.skt = socket(AF_INET, SOCK_DGRAM) #UDP
		self.skt.bind(('', srcPort)) #used for recv
		self.conns = []
		
	def __del__(self):
		self.skt.close()

	def start(self):
		while True:
			recvData, addr = self.skt.recvfrom(MAX_DATA)
			try:
				recvPkt = decode(recvData)
				#print recvPkt	## For debugging
				try:
					c = [c for c in self.conns if c.destAddr == addr][0]
					sendPkt = rudpProcessSwitch[recvPkt['pktType']](recvPkt, c)
				except IndexError:
					if recvPkt['pktType'] == SYN:
						self.conns.append( rudpConnection(addr, False) )
						c = self.conns[-1]
						sendPkt = rudpProcessSwitch[SYN](recvPkt, c)
						print 'New Connection - {}'.format(str(len(self.conns)))
						#, [c.destAddr for c in self.conns]
					else: continue
			except: continue
			else:
				self.skt.sendto(encode(sendPkt), c.destAddr)
				if sendPkt['pktType'] == FIN_ACK: 
					self.conns.remove(c)
					print 'Close Connection: ', c.destAddr
					#print '\tRemaining Connections', [c.destAddr for c in self.conns]
				#print sendPkt	## For debugging

class rudpClient:
	def __init__(self, srcPort):
		self.skt = socket(AF_INET, SOCK_DGRAM) #UDP
		self.skt.bind(('', srcPort)) #used for recv
		self.conn = rudpConnection(None, True)

	def connect(self, destIP = SERVER_IP, destPort = SERVER_PORT):
		self.conn.destAddr = (destIP, destPort)
		
		self.skt.settimeout(RTO)
		for i in xrange(MAX_RESND):
			try: 
				self.skt.sendto(encode(rudpPacket(SYN, self.conn.pktId)), self.conn.destAddr)
				print rudpPacket(SYN, self.conn.pktId) 	## For debugging
				
				while True:
					recvData, addr = self.skt.recvfrom(MAX_DATA)
					try: 
						recvPkt = decode(recvData)
						sendPkt = rudpProcessSwitch[recvPkt['pktType']](recvPkt, self.conn)
						return True
					except WRONG_PKT, KeyError: continue
			except timeout: continue
			except Exception as e : 
				print e.message
				print '[Handshaking] unexpected error occurs\n' ## For debugging
				return False
		raise MAX_RESND_FAIL()
	
	def sendData(self, data):
		# Compute total size of data and prepare data packets to be sent
		total_pkt = len(data)/MAX_PKT_SIZE + 1 + int(random()*10)
		data_pkt = range(total_pkt)
		for i in xrange(0, total_pkt, 1):
			data_pkt[i] = data[i*MAX_PKT_SIZE : (i+1)*MAX_PKT_SIZE-1]
			
		# [HandShaking] - Done
		# [Data-Delivery]
		sendPkt = rudpPacket(DAT, self.conn.pktId)
		for i in xrange(0, len(data_pkt), 1):
			sendPkt['data'] = data_pkt[i]
			for j in xrange(MAX_RESND):
				try:		
					self.skt.sendto(encode(sendPkt), self.conn.destAddr)
					print "send: ", sendPkt ## For debugging
					while True:
						recvData, addr = self.skt.recvfrom(MAX_DATA)
						try: 
							recvPkt = decode(recvData)
							sendPkt = rudpProcessSwitch[recvPkt['pktType']](recvPkt, self.conn)
							#sleep(1)
							break
						except WRONG_PKT, KeyError: continue
				except timeout: 
					if j == MAX_RESND - 1: raise MAX_RESND_FAIL()
					else: continue
				except Exception as e: 
					print e.message
					return False
				break
		
		# [Shutdown]
		sendPkt = rudpPacket(FIN, self.conn.pktId);
		for i in xrange(MAX_RESND):
			try:
				self.skt.sendto(encode(sendPkt), self.conn.destAddr)
				self.conn.wait = FIN_ACK
				while True:
					recvData, addr = self.skt.recvfrom(MAX_DATA)
					try: 
						recvPkt = decode(recvData)
						rudpProcessSwitch[recvPkt['pktType']](recvPkt, self.conn)
					except WRONG_PKT, KeyError: continue
					except END_CONNECTION:
						# close the connection
						return True
			except timeout: continue
			except Exception as e: 
				print e.message
				return False
		raise MAX_RESND_FAIL()
		
		
	def sendFile(self, filepath):
		# Read form file block by block
		# Block size is the size of data that can be sent by calling sendData() every time		
		pass
		
						
			

