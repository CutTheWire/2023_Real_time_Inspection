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

class Ardu:
    def __init__(self) -> None:
        self.port = Usb().get()
        self.arduino = None  # 이 부분을 추가해주세요.
        self.defl = "0"
        try:
            self.arduino = serial.Serial(self.port, 9600)
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(2)
        
    def move(self, arg: int) -> None:
        arg = str(arg)
        if arg in ["1", "0", "2"]:
            try:
                self.arduino.write(arg.encode())
            except:
                self.arduino.write(self.defl.encode())
            time.sleep(0.5)
    
    def __del__(self) -> None:
        self.arduino.close()

# TEST
if __name__ == "__main__":
    Ar = Ardu()
    for i in  [0,1,0,1,1,2,0,1,0,1,0,1,0,1]:
        Ar.move(i)