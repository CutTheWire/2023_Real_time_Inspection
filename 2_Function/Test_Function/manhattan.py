import cv2
import numpy as np

# 이미지 불러오기
img1 = cv2.imread('nut (1).jpg', -1)
img2 = cv2.imread('nut (2).jpg', -1)
imgs = [img1, img2]
mask_imgs = []

for img in imgs:
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # 이진화를 수행합니다. 밝기가 150 이상인 픽셀을 하얀색(255)으로 설정합니다.
    _, thresh = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY)
    # 윤곽선을 찾기
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # 초기 마스크 생성
    mask = np.zeros_like(img1)
    # 윤곽선 부분만 마스크에 그리기
    for contour in contours:
        # 윤곽선의 넓이 계산
        area = cv2.contourArea(contour)
        
        # 일정 넓이 이상인 경우에만 마스크에 그리기
        if area > 10000:  # 원하는 넓이 값으로 변경
            cv2.drawContours(mask, [contour], -1, (255, 255, 255), thickness=cv2.FILLED)

        # 원본 이미지에 마스크를 적용하여 윤곽선 부분만 출력
        src = cv2.bitwise_and(img, mask)

    # 결과 이미지를 표시
    mask_imgs.append(src)

# 이미지의 차이 계산 (절대 값)
difference = cv2.absdiff(mask_imgs[0], mask_imgs[1])

# 이미지의 차이를 그레이스케일로 변환
gray = cv2.cvtColor(difference, cv2.COLOR_BGR2GRAY)

# 이진화
_, binary = cv2.threshold(gray, 30, 255, cv2.THRESH_BINARY)

# 이진 이미지에서 흰색 픽셀(차이가 있는 픽셀)의 좌표 찾기
white_pixels = np.where(binary == 255)

# 맨하탄 거리 계산
manhattan_distance = np.sum(np.abs(white_pixels[0] - white_pixels[1]))

print("맨하탄 거리:", manhattan_distance)
