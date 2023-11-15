import serial
import time

class Ardu:
    def __init__(self, port: str) -> None:
        self.arduino = serial.Serial(port, 9600)
        time.sleep(2)

    def move(self, arg: int) -> None:
        arg = str(arg)
        if arg in ["1", "0"]:
            self.arduino.write(arg.encode())
            time.sleep(1)
    
    def __del__(self):
        self.arduino.close()
        
# #TEST
# if __name__ == "__main__":
#     Ar = Ardu("COM4")
#     for i in  [0,1,0,1,0,1,0,1,0,1,0,1]:
#         Ar.move(i)