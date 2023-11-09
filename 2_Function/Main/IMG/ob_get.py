import cv2
import numpy as np
import datetime

class object_get:
    def __init__(self) -> None:
        self.last_counted_time = None

    def get(self, frame, height, width):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 75, 255, cv2.THRESH_BINARY)

        horizontal_line_y = height // 2
        min_contour_size = 100000

        contours, _ = cv2.findContours(binary, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        contours = list(filter(lambda cnt: cv2.contourArea(cnt) >= min_contour_size, contours))

        if contours:  # contours 리스트가 비어있지 않은 경우에만 실행
            contour = max(contours, key=cv2.contourArea)  # 가장 큰 윤곽선 선택
            hull = cv2.convexHull(contour)
            cv2.drawContours(frame, [hull], -1, (0, 255, 0), 3)
            min_y = np.min(hull[:, :, 1])

            if min_y <= horizontal_line_y and min_y >= horizontal_line_y - 65:
                current_time = datetime.datetime.now()

                # 마지막으로 카운트된 시간이 없거나, 마지막으로 카운트된 시간으로부터 0.5초 이상 경과한 경우에만 카운트합니다.
                if self.last_counted_time is None or (current_time - self.last_counted_time).total_seconds() > 0.30:
                    self.last_counted_time = current_time
                    x, y, w, h = cv2.boundingRect(contour)
                    return frame, (x,y,w,h)

        cv2.line(frame, (0, horizontal_line_y), (width, horizontal_line_y), (0, 0, 255), 2)

        return frame, 0