import serial.tools.list_ports
import time
from typing import Union

class Usb:
    def __init__(self) -> None:
        self.port = "COM1"

    def get(self) -> Union[str, None]:
        ports = serial.tools.list_ports.comports()
        for self.port, desc, _ in sorted(ports):
            if "Arduino" in desc:
                return self.port
        return self.port

class Ardu(Usb):
    def __init__(self) -> None:
        super().__init__()
        self.port = super().get()
        self.arduino = None  # 이 부분을 추가해주세요.
        try:
            self.arduino = serial.Serial(self.port, 9600)
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(2)
        
    def move(self, arg: int) -> None:
        arg = str(arg)
        if arg in ["1", "0", "2"]:
            self.arduino.write(arg.encode())
            time.sleep(0.5)
    
    def __del__(self) -> None:
        self.arduino.close()