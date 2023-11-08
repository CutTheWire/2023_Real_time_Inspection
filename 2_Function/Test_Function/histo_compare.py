import cv2
import numpy as np
import matplotlib.pyplot as plt

img1 = cv2.imread('nut (1).jpg', -1)
img2 = cv2.imread('nut (2).jpg', -1)
img3 = cv2.imread('nut (3).jpg', -1)
img4 = cv2.imread('nut (4).jpg', -1)
img5 = cv2.imread('nut (5).jpg', -1)
img6 = cv2.imread('nut (6).jpg', -1)
img7 = cv2.imread('nut (7).jpg', -1)

imgs = [img1, img2, img3, img4, img5, img6, img7]
hists = []

def image_mask(src):
    # 그레이스케일 이미지로 변환
    gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)

    # 이진화를 수행합니다. 밝기가 150 이상인 픽셀을 하얀색(255)으로 설정합니다.
    _, thresh = cv2.threshold(gray, 130, 255, cv2.THRESH_BINARY)

    # 윤곽선을 찾기
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 초기 마스크 생성
    mask = np.zeros_like(img)

    # 윤곽선 부분만 마스크에 그리기
    for contour in contours:
        # 윤곽선의 넓이 계산
        area = cv2.contourArea(contour)
        
        # 일정 넓이 이상인 경우에만 마스크에 그리기
        if area > 10000:  # 원하는 넓이 값으로 변경
            cv2.drawContours(mask, [contour], -1, (255, 255, 255), thickness=cv2.FILLED)

    # 원본 이미지에 마스크를 적용하여 윤곽선 부분만 출력
    src = cv2.bitwise_and(img, mask)

    # R, G, B 채널 추출
    b_channel, g_channel, r_channel = cv2.split(src)

    # R, G, B 값 중 하나라도 140 이상인 픽셀을 마스크로 설정
    mask = (r_channel >= 142) | (g_channel >= 142) | (b_channel >= 142)

    # 마스크를 이용하여 이미지 필터링
    filtered_image = src.copy()
    filtered_image[~mask] = [0, 0, 0]  # R 값이 150 미만인 픽셀을 검은색으로 설정

    # 윤곽선 그리기
    contours, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    # 윤곽선 부분만 마스크에 그리기
    for contour in contours:
        # 윤곽선의 넓이 계산
        area = cv2.contourArea(contour)
        
        # 일정 넓이 이상인 경우에만 마스크에 그리기
        if area > 200:  # 원하는 넓이 값으로 변경
            # 윤곽선을 원본 이미지에 그리기
            cv2.drawContours(filtered_image, [contour], -1, (0, 0, 255), thickness=2)

    return filtered_image

for i, img in enumerate(imgs):
    img = image_mask(img)
    plt.subplot(len(imgs)//2, len(imgs) - len(imgs)//2, i + 1)
    if i == 0:
        plt.title('main')
    else:
        plt.title('img%d' % (i + 1))
    plt.axis('off')
    plt.imshow(img, cmap='gray')  # Use cmap='gray' for grayscale images
    # ---① 각 이미지의 히스토그램 계산
    hist = cv2.calcHist([img], [0], None, [256], [0, 256])
    # ---② 0~1로 정규화
    cv2.normalize(hist, hist, 0, 1, cv2.NORM_MINMAX)
    hists.append(hist)

query = hists[0]
methods = {'CORREL': cv2.HISTCMP_CORREL, 'CHISQR': cv2.HISTCMP_CHISQR,
            'INTERSECT': cv2.HISTCMP_INTERSECT, 'BHATTACHARYYA': cv2.HISTCMP_BHATTACHARYYA}

# 결과를 저장할 리스트 생성
results = []

for j, (name, flag) in enumerate(methods.items()):
    row = []  # 각 메서드 결과를 저장할 행
    row.append(name)  # 메서드 이름 추가
    for i, (hist, img) in enumerate(zip(hists, imgs)):
        ret = cv2.compareHist(query, hist, flag)
        if flag == cv2.HISTCMP_INTERSECT:
            ret = ret / np.sum(query)
        ret = round(ret*100,4)

        row.append(ret)
    results.append(row)

# 표로 결과 시각화
table_data = np.array(results)
column_labels = ['Method'] + ['img%d' % (i + 1) for i in range(len(imgs))]

plt.figure(figsize=(10, 10))
plt.axis('off')
table = plt.table(cellText=table_data, colLabels=column_labels, cellLoc='center', loc='center')
# 폰트 크기 설정
table.auto_set_font_size(False)
table.set_fontsize(12)  # 원하는 폰트 크기로 설정

cell_height = 0.05
table.scale(1, 2)  # 첫 번째 매개변수는 폭, 두 번째 매개변수는 높이 비율
for i, key in enumerate(table.get_celld().keys()):
    cell = table.get_celld()[key]
    if key[0] == 0:
        cell.set_height(cell_height * 2)  # 첫 번째 행의 셀 높이를 두 배로 조정


plt.show()
