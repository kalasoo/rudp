import subprocess
import sys
import os
from sys import argv
from time import sleep
from random import random

def test_start():
	BASE_PORT = int(argv[1])
	total_num = int(argv[2])
	for i in xrange(0, total_num, 1):
		cpid = os.fork()
		if (cpid == 0):
			theproc = subprocess.Popen(["python ~/Dropbox/FYP/Task1.1/rudp/test-client.py {}".format(BASE_PORT + i)], shell = True)
			try: 
				sleep(int(random()*2))
				theproc.communicate()
		    		theproc.kill()
		    	except Exception as e:
		    		print e.message
		    		return False
			return True
	return True

test_start()
