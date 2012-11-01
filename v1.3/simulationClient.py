from simulationRudpUserDev import *
from sys import argv

c = rudpClient(int(argv[1]))
if len(argv) == 3: dataSize = int(argv[2])
else: dataSize = 10000
data = 'o' * dataSize

if c.connect(SERVER_IP, SERVER_PORT):
        if c.sendData(data):
                c.close()
        else: print '==> Error: fail to deliver data to Server'
else: print '==> Error: fail to connect to Server'