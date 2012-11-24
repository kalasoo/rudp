import gevent
from gevent.queue import Queue
from gevent import Greenlet

class Actor(gevent.Greenlet):

    def __init__(self):
        self.inbox = Queue()
        Greenlet.__init__(self)

    def receive(self, message):
        """
        Define in your subclass.
        """
        raise NotImplemented()

    def _run(self):
        self.running = True

        while self.running:
            message = self.inbox.get()
            self.receive(message)


class Pinger(Actor):
    def receive(self, message):
        print message
        pong.inbox.put('ping')
        gevent.sleep(1)

class Ponger(Actor):
    def receive(self, message):
        print message
        ping.inbox.put('pong')
        gevent.sleep(1)

ping = Pinger()
pong = Ponger()

ping.start()
pong.start()

ping.inbox.put('start')
gevent.joinall([ping, pong])