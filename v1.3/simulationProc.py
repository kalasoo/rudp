from random import random, expovariate, gauss
from time import sleep, time
import subprocess
from threading import Timer
from os import getcwd

#-------------------#
# Configuration     #
#-------------------#
MEAN_INT_ARRIVAL = 5	# inver-arrival time between two clients
MEAN_JOB_SIZE = 15000	# average of data length = 15000 bytes, 15 packets if MAX_PKT_SIZE = 1000
STD_JOB_SIZE = 5000	# standard deviation of data length = 5000 bytes
BASE_PORT = 50020	# Port range: [BASE_PORT, BASE_PORT + MAX_PORT]
MAX_PORT = 1000 	# Max clients supported: MAX_PORT
REFRESH_PERIOD = 3	
BASE_PATH = getcwd()


class Generator:
	def __init__(self):
		pass
	def getNextClient(self):	# return the waiting time for parent process to generate next client
		return expovariate(MEAN_INT_ARRIVAL)

	def getNextJobSize(self):
		return int(abs(gauss(MEAN_JOB_SIZE, STD_JOB_SIZE)))
		
class Counter:
	def __init__(self):
		self.min_interArrivalTime = float('inf')
		self.max_interArrivalTime = -1
		self.avg_interArrivalTime = 0
		self.num_client = 0
		self.min_jobSize = float('inf')
		self.max_jobSize = -1
		self.avg_jobSize = 0
		self.startTime = time()
	
	def update_InterArrivalTime(self, interArrivalTime):
		if interArrivalTime < self.min_interArrivalTime: self.min_interArrivalTime = interArrivalTime
		if interArrivalTime > self.max_interArrivalTime: self.max_interArrivalTime = interArrivalTime
		self.avg_interArrivalTime = (self.avg_interArrivalTime * (self.num_client - 1) + interArrivalTime) / self.num_client
	
	def update_ClientNum(self):
		self.num_client += 1
	
	def update_JobSize(self, jobSize):
		if jobSize < self.min_jobSize: self.min_jobSize = jobSize
		if jobSize > self.max_jobSize: self.max_jobSize = jobSize
		self.avg_jobSize = (self.avg_jobSize * (self.num_client - 1) + jobSize) / self.num_client
		
	def printCounter(self):
		info = 'Total C:{0}({1}/sec), '.format(self.num_client, int(self.num_client/(time() - self.startTime)*1000)/float(1000))
		info += 'InterArrival: {0}/{1}/{2}(min,max,avg), '.format(int(self.min_interArrivalTime*1000)/float(1000), int(self.max_interArrivalTime*100)/float(100), int(self.avg_interArrivalTime*100)/float(100))
		info += 'JobSize: {0}/{1}/{2}(min,max,avg)'.format(self.min_jobSize, self.max_jobSize, self.avg_jobSize)
		print info
		pass

class SysState:
	def __init__(self):
		self.list_client = []
		self.dict_port = dict()	# 'PortNum' = 1 (free) or 0 (used)
		for i in xrange(BASE_PORT, BASE_PORT + MAX_PORT, 1): self.dict_port[str(i)] = 1
		self.dict_info = dict()	# 'pid' = PortNum

	def getFreePort(self):
		tmp_list_port = sorted(self.dict_port.items(), key = lambda dict_port:dict_port[1], reverse = True)
		if tmp_list_port[0][1] == 0: return False	# Check the availability status of the 1st port
		else: return tmp_list_port[0][0]
		
	def addClient(self, proc_client):
		self.list_client.append(proc_client)	

	def usePort(self, portNum):
		self.dict_port[str(portNum)] = 0
		
	def addPidPortPair(self, pid, portNum):
		self.dict_info[str(pid)] = portNum
		
	def freePort(self):
		tmp_list_client = []
		for iClient in self.list_client:
			if iClient.poll() is not None: 
				self.dict_port[str(self.dict_info.get(str(iClient.pid)))] = 1
			else: tmp_list_client.append(iClient)
		self.list_client = tmp_list_client
		
	def getClientNum(self):
		return len(self.list_client)

def refreshTimeOut(counter, state):
	counter.printCounter()
	state.freePort()
	Timer(REFRESH_PERIOD, refreshTimeOut, [counter, state]).start()

class Simulator:
	def __init__(self):
		self.generator = Generator()
		self.sys_state = SysState()
		self.counter = Counter()

	def start(self):
		# Main program starts here
		# start Timer
		Timer(REFRESH_PERIOD, refreshTimeOut, [self.counter, self.sys_state]).start()
		
		while True:
			timestamp = time()
			next_interArrivalTime = self.generator.getNextClient()
			next_port = self.sys_state.getFreePort()
			if next_port:
				next_jobSize = self.generator.getNextJobSize()
				cmd = "python {0}/simulationClient.py {1} {2}".format(BASE_PATH, next_port, next_jobSize)
				proc_client = subprocess.Popen([cmd], shell = True)
				self.sys_state.addClient(proc_client)
				self.sys_state.usePort(next_port)
				self.sys_state.addPidPortPair(proc_client.pid, next_port)
				
				self.counter.update_ClientNum()
				self.counter.update_InterArrivalTime(next_interArrivalTime)
				self.counter.update_JobSize(next_jobSize)
			sleep(next_interArrivalTime)
				
s = Simulator()
s.start()
