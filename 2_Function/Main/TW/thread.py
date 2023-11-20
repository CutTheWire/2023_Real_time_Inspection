from threading import Thread
from typing import Any

class NewThread(Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}):
        Thread.__init__(self, group, target, name, args, kwargs)

    def run(self) -> None:
        if self._target != None:
            self._return = self._target(*self._args, **self._kwargs)

    def join(self, *args: Any) -> Any:
        Thread.join(self, *args)
        return self._return

