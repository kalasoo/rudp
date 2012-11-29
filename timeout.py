import gevent
from gevent import spawn
from random import randint
from time import time

def f1(t):
    print 'f1 sleep', t, time()
    gevent.sleep(2)
    print 'f1 wakeup', t, time()

i = 0
while True:
    r = randint(0,1)
    if r == 0: 
        gevent.sleep(1)
        print time()
    else: 
        spawn(f1, i)
        i+=1