import os
import cv2
import tensorflow as tf
from roboflow import Roboflow
import tempfile

# GPU를 사용할 수 있는지 확인하고 활성화
if tf.config.list_physical_devices('GPU'):
    physical_devices = tf.config.list_physical_devices('GPU')
    for device in physical_devices:
        tf.config.set_visible_devices(device, 'GPU')
        tf.config.experimental.set_memory_growth(device, True)
        print(f"gpu : {device}")
        try:
            tf.config.set_logical_device_configuration(
                device,
                [tf.config.LogicalDeviceConfiguration(memory_limit=3072)])
        except RuntimeError as e:
            # 프로그램 시작시에 가상 장치가 설정되어야만 합니다
            print(e)
    print("GPU 사용 중")
else:
    print("CPU 사용 중")

# Roboflow API 초기화
rf = Roboflow(api_key="RTdjTlzLV7sjZLXuFTsR")
project = rf.workspace().project("nut_sh")
model = project.version(3).model

def filter_low_similarity(predictions, threshold):
    filtered_predictions = {'predictions': []}
    for prediction in predictions['predictions']:
        if prediction['confidence'] >= threshold:
            filtered_predictions['predictions'].append(prediction)
    return filtered_predictions

def catch(frame):
    # 이미지를 파일로 저장
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmpfile:
        tmpfile_name = tmpfile.name
        cv2.imwrite(tmpfile_name, frame)

        # YOLOv8 모델로 이미지 파일에서 객체 인식 (GPU 사용)
        with tf.device("/GPU:0"):
            predictions = model.predict(tmpfile_name, confidence=40, overlap=30).json()

    # 임시 파일 삭제
    os.remove(tmpfile_name)

    # 유사도가 70% 이상인 예측만 필터링
    filtered_predictions = filter_low_similarity(predictions, 0.8)

    for prediction in filtered_predictions['predictions']:
        x, y, width, height = int(prediction['x']), int(prediction['y']), int(prediction['width']), int(prediction['height'])
        label = prediction['class']

        # 객체 주변에 경계 상자 그리기
        pt1 = (x - width//2, y - height//2)
        pt2 = (x + width//2, y + height//2)
        cv2.rectangle(frame, pt1, pt2, (0, 255, 0), 2)

        # 객체 레이블과 정확도 표시
        label_text = f"{label.upper()}"  # 레이블과 정확도 텍스트 생성
        cv2.putText(frame, label_text, (pt1[0], pt1[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 2)

    return frame
