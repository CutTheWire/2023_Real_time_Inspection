import serial.tools.list_ports
import time
from typing import Union

class Usb:
    def __init__(self) -> None:
        # 초기화 함수, 인스턴스가 생성될 때 실행됩니다.
        # 아두이노가 연결된 포트를 찾습니다.
        self.port = "COM1"

    def get(self) -> Union[str, None]:
        # 아두이노가 연결된 포트를 반환하는 함수입니다.
        ports = serial.tools.list_ports.comports()
        for self.port, desc, _ in sorted(ports):
            if "Arduino" in desc:
                return self.port
        return self.port

class Ardu(Usb):
    def __init__(self) -> None:
        # 초기화 함수, 인스턴스가 생성될 때 실행됩니다.
        # 아두이노와 시리얼 통신을 설정하고, 통신 준비를 위해 잠시 대기합니다.
        super().__init__()
        self.port = super().get()
        self.arduino = None  # 아두이노와의 연결을 저장하는 변수입니다.
        try:
            self.arduino = serial.Serial(self.port, 9600)
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(2)
        
    def move(self, arg: int) -> None:
        # 아두이노에 명령을 전송하는 함수입니다.
        # arg를 문자열로 변환한 후, 이를 아두이노에 전송합니다.
        # 아두이노가 명령을 처리할 시간을 주기 위해 잠시 대기합니다.
        arg = str(arg)
        if arg in ["1", "0", "2"]:
            self.arduino.write(arg.encode())
            time.sleep(0.5)
    
    def __del__(self) -> None:
        # 소멸자 함수, 인스턴스가 소멸될 때 실행됩니다.
        # 아두이노와의 시리얼 통신을 종료합니다.
        self.arduino.close()

# TEST
if __name__ == "__main__":
    # 테스트 코드입니다.
    # 아두이노와 통신하는 Ardu 클래스의 인스턴스를 생성하고,
    # 0, 1, 2를 번갈아 가며 아두이노에 전송합니다.
    Ar = Ardu()
    for i in  [0,1,0,1,1,2,0,1,0,1,0,1,0,1]:
        Ar.move(i)
