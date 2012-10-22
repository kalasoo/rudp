from rudpUser import *
from sys import argv

print '---------------------Testing (Client)----------------------\n'
c1 = rudpClient(int(argv[1]))
print '==> Client is created.'
c1.conn.printConnection()

data1 = 'A wiki enables communities to write documents collaboratively, using a simple markup language and a web browser. A single page in a wiki website is referred to as a "wiki page", while the entire collection of pages, which are usually well interconnected by hyperlinks, is "the wiki". A wiki is essentially a database for creating, browsing, and searching through information. A wiki allows for non-linear, evolving, complex and networked text, argument and interaction.'


if c1.connect(SERVER_IP, SERVER_PORT):
	print '\n==> [Handshaking] Client  - OK\n'
	print '==> [Data-Delivery] Client  is sending data to Server\n'
	if c1.sendData(data1): print "OKOKOK"
	else: print "FALSE" 
else: print '\n==> [Handshaking] Client  - Failure\n'

print '---------------------END (Client)----------------------\n'