
# -*- coding: cp1252 -*-
import threading
import time


class MyTimer:
    def __init__(self, tempo, target, args= [], kwargs={}):
        self._target = target
        self._args = args
        self._kwargs = kwargs
        self._tempo = tempo

    def _run(self):
        self._timer = threading.Timer(self._tempo, self._run)
        self._timer.start()
        self._target(*self._args, **self._kwargs)
        
    def start(self):
        self._timer = threading.Timer(self._tempo, self._run)
        self._timer.start()

    def stop(self):
        self._timer.cancel()


def affiche(unstr):
    print unstr, time.clock()

a = MyTimer(1.0, affiche, ["MyTimer"])
a.start()
time.sleep(5.5)
print u"Timer arrêté"
a.stop()
time.sleep(2.0)
print u"Timer relancé"
a.start()
