import os
import cv2
import numpy as np
from datetime import datetime

class save:
    def __init__(self, program: str, function: str) -> None:
        self.program = program
        self.function = function
        # Documents(문서) 폴더 경로
        self.documents_folder = os.path.join(os.path.expanduser("~"))
        self.main_folder = os.path.join(self.documents_folder, "TW")
        self.sub_folder = os.path.join(self.main_folder, self.program)
        self.date_folder = os.path.join(self.sub_folder, datetime.today().strftime('%y%m%d'))
    
    def nut_image_save(self, frame: np.ndarray) -> str:
        # 폴더가 이미 존재하는지 확인 후 생성
        for f in [self.main_folder, self.sub_folder, self.date_folder]:
            if not os.path.exists(f):
                os.mkdir(f)
        
        # 이미지를 읽어옴
        filename = f"{datetime.today().strftime('%H%M%S')}_{self.function}.jpg"
        photo_path = os.path.join(self.date_folder, filename)
        
        # 이미지를 저장
        cv2.imwrite(photo_path, frame)
        return photo_path
    
