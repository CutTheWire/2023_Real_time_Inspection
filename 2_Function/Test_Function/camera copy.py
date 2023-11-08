import cv2
import torch


# 카메라 열기 (일반적으로 0은 내장 웹캠을 가리킴)
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()

    if not ret:
        break

    # 프레임을 화면에 표시
    cv2.imshow('Object Detection', frame)

    # 'q' 키를 누를 때까지 화면 업데이트 대기
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 카메라 종료
cap.release()
cv2.destroyAllWindows()
