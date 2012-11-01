from rudpUser import *
from sys import argv

print '--------------------- Start of Test (Client)----------------------'
if len(argv) == 2: c = rudpClient(int(argv[1]))
else: c = rudpClient(50020)
if len(argv) == 3: dataSize = int(argv[2])
else: dataSize = 10000
data = 'o' * dataSize

if c.connect(SERVER_IP, SERVER_PORT):
        print '==> Client is created.'
        c.conn.printConnection()
        print '==> [Handshaking] Client - OK'
        print '==> [Data-Delivery] Client - Sending'
        if c.sendData(data):
                print "==> [Data-Delivery] Client - Completed"
                c.close()
                print '==> [Shutdown] Client - Disconnected'
        else: print '==> Error: fail to deliver data to Server'
else: print '==> Error: fail to connect to Server'
print '--------------------- End of Test (Client)----------------------'
