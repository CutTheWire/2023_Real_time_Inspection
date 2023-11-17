import platform
import wmi
from typing import Union, Any

class TW:
    def __init__(self) -> None:
        self.result = ["178BFBFF00800F82B45629E1", "BFEBFBFF000906A3C425D006", "BFEBFBFF00040651B6168272"]
        self._cpu_info = None
        self._LogicalDisk = None

    def __eq__(self, other: Union['TW', str]) -> bool:
        if isinstance(other, TW):
            return all(item in self.result for item in other.result)
        elif isinstance(other, str):
            return other in self.result
        else:
            return False
        
    def __call__(self) -> Union[bool, Exception, int]:
        if platform.system() == 'Windows':
            try:
                result = self.cpu_info + self.LogicalDisk
                return self == result
            except Exception as e:
                return e
        else:
            return 2
        
    @property
    def cpu_info(self) -> str:
        c = wmi.WMI()
        processors = c.Win32_Processor()
        if processors:
            return processors[0].ProcessorId
        else:
            return  "0000000000000000"
        
    @property
    def LogicalDisk(self) -> str:
        drive = "C"
        c = wmi.WMI()
        logical_disks = c.Win32_LogicalDisk(DeviceID=drive + ":")
        if logical_disks:
            return  logical_disks[0].VolumeSerialNumber
        else:
            return  "00000000"
