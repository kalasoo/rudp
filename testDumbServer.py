from rudpDumbUser import *
from sys import stdout

print '-------------------------Testing (Dumb Receiver)---------------------\n'
r = rudpDumbReceiver(SERVER_PORT)
print '==> Receiver is running.\n'
while True:
	data = r.receive()
	if data: 	stdout.write('o ')
	else:		stdout.write('x ')
	stdout.flush()

