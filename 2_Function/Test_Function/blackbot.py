from PIL import Image
import os

# 이미지 파일이 들어있는 폴더 경로
image_folder = "C:/Users/sjmbe/TW/NUT/231108/0"

# 결과를 저장할 텍스트 파일 경로
output_file = "C:/Users/sjmbe/TW/NUT/231108/0.txt"

# 검은 픽셀 수를 세는 함수
def count_black_pixels(image_path):
    img = Image.open(image_path)
    img = img.convert('L')  # 흑백 이미지로 변환
    black_pixels = img.histogram()[0]  # 히스토그램에서 검은 픽셀 수 가져오기
    return black_pixels

# 이미지 폴더 내의 모든 이미지 파일에 대해 검은 픽셀 수를 세고 결과를 텍스트 파일에 저장
with open(output_file, 'w') as f:
    for filename in os.listdir(image_folder):
        if filename.endswith('.jpg') or filename.endswith('.png'):  # 이미지 파일 확장자 확인
            image_path = os.path.join(image_folder, filename)
            black_pixels = count_black_pixels(image_path)
            f.write(f'{filename}: {black_pixels} 검은 픽셀\n')

print(f'검은 픽셀 수가 {output_file} 파일에 저장되었습니다.')
