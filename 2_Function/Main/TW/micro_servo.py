import serial.tools.list_ports
import time
from typing import Union

class Usb:
    def __init__(self) -> None:
        # 초기화 함수, 인스턴스가 생성될 때 실행됩니다.
        # 아두이노가 연결된 포트를 찾습니다.
        self.port = None

    def get(self) -> Union[str, None]:
        # 아두이노가 연결된 포트를 반환하는 함수입니다.
        ports = serial.tools.list_ports.comports()
        
        for port_get, desc, _ in sorted(ports):
            if "Arduino" in desc or "CH340" in desc:
                self.port = port_get
                return self.port
        return None

class Ardu(Usb):
    def __init__(self) -> None:
        self.__init__ = super()
        self.port = self.get()
        self.arduino = None  # 이 부분을 추가해주세요.
        self.defl = "0"
        try:
            self.arduino = serial.Serial(self.port, 9600)
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(2)

    def check(self) -> bool:
        # 아두이노가 연결되어 있는지 확인하는 함수입니다.
        if self.arduino is not None:
            try:
                # 테스트 쓰기를 시도하여 포트가 열려 있는지 확인합니다.
                self.arduino.write(''.encode())
                return True
            except serial.SerialException:
                # 쓰기 실패 시, 포트가 닫혀 있음을 나타냅니다.
                return False
        else:
            # arduino 객체가 None이면, 아두이노가 연결되어 있지 않음을 나타냅니다.
            return False
        
    def move(self, arg: int) -> None:
        # 아두이노에 명령을 전송하는 함수입니다.
        # arg를 문자열로 변환한 후, 이를 아두이노에 전송합니다.
        # 아두이노가 명령을 처리할 시간을 주기 위해 잠시 대기합니다.
        arg = str(arg)
        if arg in ["1", "0", "2"]:
            try:
                self.arduino.write(arg.encode())
            except:
                self.arduino.write(self.defl.encode())
            time.sleep(0.5)
    
    def __del__(self) -> None:
        # 소멸자 함수, 인스턴스가 소멸될 때 실행됩니다.
        # 아두이노와의 시리얼 통신을 종료합니다.
        self.arduino.close()

# TEST
# if __name__ == "__main__":
#     # 테스트 코드입니다.
#     # 아두이노와 통신하는 Ardu 클래스의 인스턴스를 생성하고,
#     # 0, 1, 2를 번갈아 가며 아두이노에 전송합니다.
#     Ar = Ardu()
#     for i in  [0,1,0,1,1,2,0,1,0,1,0,1,0,1]:
#         Ar.move(i)
