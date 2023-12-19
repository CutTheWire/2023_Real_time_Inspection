import cv2
import numpy as np
import math
import matplotlib.pyplot as plt

# 이미지 파일 경로
img1 = cv2.imread("C:\\Users\\sjmbe\\TW\\NUT\\231108\\1-1\\105003_SUA502M.jpg", cv2.IMREAD_GRAYSCALE)
img2 = cv2.imread("C:\\Users\\sjmbe\\TW\\NUT\\231108\\1-1\\105742_SUA502M.jpg", cv2.IMREAD_GRAYSCALE)

# AKAZE 디텍터 생성
akaze = cv2.AKAZE_create()

# 키 포인트 검출 및 디스크립터 계산
kp1, des1 = akaze.detectAndCompute(img1, None)
kp2, des2 = akaze.detectAndCompute(img2, None)

# BFMatcher 객체 생성
bf = cv2.BFMatcher(cv2.NORM_HAMMING2, crossCheck=True)

# 매칭
matches = bf.match(des1, des2)

# 매칭된 특징점이 있는지 확인
if len(matches) == 0:
    print("No matching points found")
else:
    # 매칭 결과를 거리 기준으로 정렬
    matches = sorted(matches, key = lambda x:x.distance)
    # 매칭된 선의 개수 계산
    line_count = len(matches)
    # 매칭된 선의 길이의 합 계산
    total_length = sum([m.distance for m in matches])
    # 매칭 결과 그리기
    result = cv2.drawMatches(img1, kp1, img2, kp2, matches[:50], None, flags=2)
    # 결과 이미지와 오차 그래프를 같은 창에 출력
    fig, axs = plt.subplots(2, 1, figsize=(10, 10))
    # 매칭된 선의 길이 저장
    lengths = [m.distance for m in matches]
    # 기준 이미지의 매칭 선 길이의 평균
    avg_length_img1 = total_length / line_count
    # 비교 이미지의 매칭 선 길이와 기준 이미지의 선 길이와의 오차 계산
    errors = [abs(l - avg_length_img1) for l in lengths]
    # 기준 이미지의 매칭 선 수가 비교 이미지의 선 수보다 많은 경우, 부족한 선 수만큼 오차를 50으로 할당하여 errors 리스트에 추가
    if len(kp1) > len(kp2):
        errors.extend([50] * (len(kp1) - len(kp2)))
    # 오차값 합계 계산
    total_error = sum(errors)
    print("Score: ", total_error)
    # 결과 이미지 출력
    axs[1].imshow(cv2.cvtColor(result, cv2.COLOR_BGR2RGB))
    # 오차를 그래프로 표시
    axs[0].plot(errors)
    axs[0].set_title('Error of Matching Line Lengths')
    axs[0].set_xlabel('Matched Line Index')
    axs[0].set_ylabel('Error')

    plt.tight_layout()
    plt.show()
