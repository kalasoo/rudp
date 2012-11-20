from rudpDumbUser import *
from sys import argv

print '--------------------- Start of Test (Client)----------------------'
if len(argv) == 2: c = rudpClient(int(argv[1]))
else: c = rudpDumbSender(50020)
if len(argv) == 3: dataSize = int(argv[2])
else: dataSize = 10000
data = 'o' * dataSize
print '==> [Data-Delivery] Sender - Sending'
c.sendData(data)
print '--------------------- End of Test (Client)----------------------'
