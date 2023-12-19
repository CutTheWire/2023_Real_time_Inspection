import cv2
from typing import Tuple
import numpy as np
import base64
from PIL import Image
from skimage.metrics import structural_similarity as ssim
import os
import glob
import copy

def detect_defects(frame_a: np.ndarray) -> Tuple[int, float]:
    # 'Documents/TW' 디렉토리에서 .ini 파일들을 찾습니다.
    ini_files = glob.glob(os.path.expanduser("~\\Documents\\TW\\*.ini"))

    # ssim_value를 저장할 변수를 초기화합니다.
    max_ssim_value = 0

    # .ini 파일들에 대해
    for ini_file in ini_files:
        frame = copy.deepcopy(frame_a)
        # .ini 파일을 읽습니다.
        with open(ini_file, 'r') as f:
            img_data_base64 = f.read()

        # base64 데이터를 이미지로 변환합니다.
        img_data = base64.b64decode(img_data_base64)
        nparr = np.frombuffer(img_data, np.uint8)
        img_chisqr = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
        base64_height, base64_width = img_chisqr.shape

        if len(frame.shape) == 3:
            img_height, img_width, _ = frame.shape
        elif len(frame.shape) == 2:
            img_height, img_width = frame.shape
        elif len(frame.shape) == 4:
            _, _, img_height, img_width = frame.shape

        if img_width > base64_width:
            frame = frame[:, 0:base64_width]

        elif img_height > base64_height:
            # 이미지를 base64 이미지 크기에 맞게 잘라냅니다.
            frame = frame[0:base64_height, :]

        elif img_width >= base64_width and img_height >= base64_height:
            # 이미지를 base64 이미지 크기에 맞게 잘라냅니다.
            frame = frame[0:base64_height, 0:base64_width]
        frame = cv2.resize(frame, (base64_width, base64_height))

        del img_height, img_width, base64_width, base64_height
        
        # AKAZE 디텍터 생성
        akaze = cv2.AKAZE_create()
        kp1, des1 = akaze.detectAndCompute(img_chisqr, None)
        kp2, des2 = akaze.detectAndCompute(frame, None)

        # BFMatcher 객체 생성
        bf = cv2.BFMatcher(cv2.NORM_HAMMING2, crossCheck=True)
        # 매칭
        matches = bf.match(des1, des2)
        errors = []
        # 매칭된 특징점이 있는지 확인
        if len(matches) == 0:
            errors.extend([50] * (len(kp1)))
        else:
            # 매칭 결과를 거리 기준으로 정렬
            matches = sorted(matches, key = lambda x:x.distance)
            # 매칭된 선의 개수 계산
            line_count = len(matches)
            # 매칭된 선의 길이의 합 계산
            total_length = sum([m.distance for m in matches])
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

        # 만약 현재 ssim_value가 이전까지의 최대값보다 크면, 최대값을 갱신합니다.
        if total_error > max_ssim_value:
            max_ssim_value = total_error

    # 가장 높은 ssim_value를 target_value로 설정합니다.
    target_value = max_ssim_value
    # target_value에 따라 다른 값을 반환합니다.
    if  target_value < 4000:
        return 1, target_value
    elif 4000 < target_value and target_value < 4500:
        return 2, target_value
    else:
        return 0, target_value
