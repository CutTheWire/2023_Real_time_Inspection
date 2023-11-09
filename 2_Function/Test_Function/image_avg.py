import cv2
import numpy as np
import os
import base64

# 이미지 디렉토리 설정
img_dir = "C:\\Users\\sjmbe\\TW\\NUT\\231109"

# 이미지 파일들을 모두 불러옵니다.
img_files = [f for f in os.listdir(img_dir) if os.path.isfile(os.path.join(img_dir, f))]

# 첫 번째 이미지의 크기를 확인합니다.
first_img = cv2.imread(os.path.join(img_dir, img_files[0]), cv2.IMREAD_GRAYSCALE)
height, width = first_img.shape

# 픽셀값의 합을 저장할 배열을 초기화합니다.
pixel_sum = np.zeros((height, width), np.float32)

# 각 이미지에 대해
for img_file in img_files:
    # 이미지를 불러옵니다.
    img = cv2.imread(os.path.join(img_dir, img_file), cv2.IMREAD_GRAYSCALE)

    # 모든 이미지를 첫 번째 이미지와 같은 크기로 조정합니다.
    img_resized = cv2.resize(img, (width, height))

    # 픽셀값을 더합니다.
    pixel_sum += img_resized

# 이미지의 개수로 나눠 평균을 구합니다.
avg_img = (pixel_sum / len(img_files)).astype(np.uint8)
(_ ,aavg_img)= cv2.threshold(avg_img, 150, 255, cv2.THRESH_BINARY)

cv2.imshow("",aavg_img)
cv2.waitKey(0)
cv2.destroyAllWindows()
# 이미지를 base64 데이터로 변환합니다.
_, buffer = cv2.imencode('.png', avg_img)
img_base64 = base64.b64encode(buffer)

# base64 데이터를 텍스트 파일로 저장합니다.
with open('C:\\Users\\sjmbe\\TW\\NUT\\1_avg_img_base64.txt', 'w') as f:
    f.write(img_base64.decode())
