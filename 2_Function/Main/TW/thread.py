from threading import Thread
from typing import Any

class NewThread(Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs={}):
        # 초기화 함수, 인스턴스가 생성될 때 실행됩니다.
        # Thread 클래스의 초기화 함수를 호출하여 스레드를 설정합니다.
        Thread.__init__(self, group, target, name, args, kwargs)

    def run(self) -> None:
        # 스레드가 실행할 작업을 정의하는 함수입니다.
        # target이 None이 아닌 경우, target 함수를 args와 kwargs를 사용하여 호출하고,
        # 그 결과를 _return에 저장합니다.
        if self._target != None:
            self._return = self._target(*self._args, **self._kwargs)

    def join(self, *args: Any) -> Any:
        # 스레드가 종료될 때까지 기다리는 함수입니다.
        # 기다리는 동안 메인 스레드는 블록됩니다.
        # 기다린 후에는 _return 값을 반환합니다.
        Thread.join(self, *args)
        return self._return
