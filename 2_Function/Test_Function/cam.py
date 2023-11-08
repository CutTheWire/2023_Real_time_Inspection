import cv2
from roboflow import Roboflow
import numpy as np
import tensorflow as tf

# Roboflow API 초기화
rf = Roboflow(api_key="RTdjTlzLV7sjZLXuFTsR")
project = rf.workspace().project("nut_sh")
model = project.version(3).model

# 모델 로드
loaded_model = mo

# 비디오 캡처 객체 생성
cap = cv2.VideoCapture(0)

while True:
    # 프레임 읽기
    ret, frame = cap.read()
    if not ret:
        break

    # 이미지 전처리
    input_tensor = tf.convert_to_tensor(frame)
    input_tensor = input_tensor[tf.newaxis, ...]

    # 추론 실행
    output_dict = loaded_model(input_tensor)

    # 결과 시각화
    for i in range(output_dict['detection_scores'][0].shape[0]):
        if output_dict['detection_scores'][0][i] > 0.5:
            ymin, xmin, ymax, xmax = output_dict['detection_boxes'][0][i].numpy()
            (left, right, top, bottom) = (xmin * frame.shape[1], xmax * frame.shape[1], ymin * frame.shape[0], ymax * frame.shape[0])
            cv2.rectangle(frame, (int(left), int(top)), (int(right), int(bottom)), (0, 255, 0), 2)

    # 결과 프레임 표시
    cv2.imshow('frame', frame)
    
    # 'q' 키를 누르면 종료
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 비디오 캡처 객체 해제 및 창 닫기
cap.release()
cv2.destroyAllWindows()
