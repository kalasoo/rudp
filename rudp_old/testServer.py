from rudpUserDict import *

server = rudpServer(RCV_PORT)
print '-------------------------Testing (Server)---------------------\n'
print '==> Server is created.\n'

server.start()
print '==> Server is waiting for clients.\n'
