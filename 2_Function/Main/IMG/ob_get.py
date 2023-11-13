import cv2
from typing import Tuple, Union
import numpy as np
import datetime
import cv2
from typing import Tuple, Union
import numpy as np
import datetime

class object_get:
    def __init__(self) -> None:
        self.last_counted_time = None
        self.min_contour_size = 10000
        self.sub_line_y = 150
        self.sub_line_x = 400

    def get(self, frame: np.ndarray, width: int, height: int) -> Union[Tuple[np.ndarray, int], Tuple[np.ndarray, tuple]]:
        horizontal_line_y = height // 2
        # frame의 일부를 선택하여 gray와 binary 생성
        gray = cv2.cvtColor(frame[(horizontal_line_y-self.sub_line_y):, self.sub_line_x:-self.sub_line_x], cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 75, 255, cv2.THRESH_BINARY)

        contours, _ = cv2.findContours(binary, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        del gray, binary
        contours = list(filter(lambda cnt: cv2.contourArea(cnt) >= self.min_contour_size, contours))
        
        # 수직선 그리기
        cv2.line(frame, (self.sub_line_x, horizontal_line_y- self.sub_line_y), (self.sub_line_x, height), (255, 255, 255), 2)  # 왼쪽 수직선
        cv2.line(frame, (width - self.sub_line_x, horizontal_line_y- self.sub_line_y), (width - self.sub_line_x, height), (255, 255, 255), 2)  # 오른쪽 수직선
        
        # 수평선 그리기
        cv2.line(frame, (0, horizontal_line_y), (width, horizontal_line_y), (0, 0, 255), 2)
        cv2.line(frame, (0, horizontal_line_y - self.sub_line_y), (width, horizontal_line_y - self.sub_line_y), (0, 255, 255), 2)

        if contours:  # contours 리스트가 비어있지 않은 경우에만 실행
            contour = max(contours, key=cv2.contourArea)  # 가장 큰 윤곽선 선택
            hull = cv2.convexHull(contour)
            del contours, contour
            # frame 전체에 대해 윤곽선 그리기
            cv2.drawContours(frame[horizontal_line_y-self.sub_line_y:, self.sub_line_x:-self.sub_line_x], [hull], -1, (0, 255, 0), 3)
            min_y = np.min(hull[:, :, 1]) + horizontal_line_y - self.sub_line_y  # 슬라이싱으로 잘린 부분만큼 y축 위치를 보정
            if min_y <= horizontal_line_y and min_y >= horizontal_line_y - self.sub_line_y:
                current_time = datetime.datetime.now()

                if self.last_counted_time is None or (current_time - self.last_counted_time).total_seconds() > 0.55:
                    self.last_counted_time = current_time
                    del current_time
                    x, y, w, h = cv2.boundingRect(hull)
                    # bounding box 좌표 조정
                    x += self.sub_line_x
                    y += horizontal_line_y - self.sub_line_y  # bounding box의 y축 위치도 보정
                    return frame, (x, y, w, h)
        return frame, 0
