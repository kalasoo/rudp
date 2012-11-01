from socket import *
from json import loads as jsonDecode
from threading import Timer

LOG_PORT = 49999	# this port is used to get logging information from every client

class Logger:
	def __init__(self):
		# bind a socket
		self.skt = socket(AF_INET, SOCK_DGRAM)
		self.skt.bind(('', LOG_PORT))
		
		# Open a logging file
		self.logfile = open('log.txt', 'w')
		# write reporter starting time into logfile
		self.cNum = 0
		self.cSus = 0
		self.cFai = 0
		
	def __del__(self):
		self.skt.close()
		close(self.logfile)
		pass
		
	def checkLog(self):
		if self.cNum: 
			info = 'Total: {0}, '.format(self.cNum)
			info += 'Success: {0}({1}%), '.format(self.cSus, int((float(self.cSus)/float(self.cNum))*10000)/float(10000))
			info += 'Fail: {0}({1}%), '.format(self.cFai, int((float(self.cFai)/float(self.cNum))*10000)/float(10000))
			print info
		t = Timer(3, self.checkLog)
		t.daemon = True
		t.start()

	def start(self):
		self.checkLog()
		while True:
			data, addr = self.skt.recvfrom(1000)
			logTmp = jsonDecode(data)
			self.cNum += 1
			if logTmp['status']: self.cSus += 1
			else: self.cFai += 1

	def log(self, record):
		# write a record into the logfile
		pass

	def generate(self):
		# generate simulation report
		pass
		
l = Logger()
l.start()
