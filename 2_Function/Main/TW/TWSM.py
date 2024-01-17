import platform
import wmi
from typing import Union, Any

class TW:
    def __init__(self) -> None:
        self.result = ["178BFBFF00800F82B45629E1", "BFEBFBFF000906A3C425D006","BFEBFBFF00030678D2FA040C", "BFEBFBFF00040651B6168272"]
        self._cpu_info = None
        self._LogicalDisk = None

    def __eq__(self, other: Union['TW', str]) -> bool:
        # 동등성을 검사하는 함수입니다.
        # other가 TW 클래스의 인스턴스이면, other의 result가 self의 result에 모두 포함되어 있는지 검사합니다.
        # other가 문자열이면, other가 self의 result에 포함되어 있는지 검사합니다.
        # 그 외의 경우에는 False를 반환합니다.
        if isinstance(other, TW):
            return all(item in self.result for item in other.result)
        elif isinstance(other, str):
            return other in self.result
        else:
            return False
        
    def __call__(self) -> Union[bool, Exception, int]:
        # 인스턴스를 함수처럼 호출할 수 있게 해주는 함수입니다.
        # 현재 운영체제가 Windows인 경우, cpu_info와 LogicalDisk를 합쳐 self와 동등한지 검사합니다.
        # 그렇지 않은 경우에는 2를 반환합니다.
        if platform.system() == 'Windows':
            try:
                result = self.cpu_info + self.LogicalDisk
                return self == result
            except:
                return 3
        else:
            return 2
        
    @property
    def cpu_info(self) -> str:
        # CPU 정보를 반환하는 프로퍼티입니다.
        # 현재 시스템의 CPU 정보를 출력합니다.
        # CPU 정보가 없는 경우에는 "0000000000000000"을 반환합니다.
        c = wmi.WMI()
        processors = c.Win32_Processor()
        if processors:
            return processors[0].ProcessorId
        else:
            return  "0000000000000000"
        
    @property
    def LogicalDisk(self) -> str:
        # 논리 디스크 정보를 반환하는 프로퍼티입니다.
        # 현재 시스템의 C 드라이브 논리 디스크 정보를 반환합니다.
        # 논리 디스크 정보가 없는 경우에는 "00000000"을 반환합니다.
        drive = "C"
        c = wmi.WMI()
        logical_disks = c.Win32_LogicalDisk(DeviceID=drive + ":")
        if logical_disks:
            return  logical_disks[0].VolumeSerialNumber
        else:
            return  "00000000"
