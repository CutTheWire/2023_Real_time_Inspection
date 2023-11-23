'''
해당 코드는 Arduino IDE에서 arduino UNO에 업로드하는 코드로
실제 pyinstaller로 EXE 파일을 만들 경우 파이썬 코드에선 모듈로써 사용되지 않는 코드입니다.

확인용 파일로 보시길 추천합니다.

'''
#include<Servo.h> // 서보 모터 제어를 위한 라이브러리를 포함합니다.

Servo myservo; // 서보 객체를 생성합니다.
int servoPin = 12; // 서보 모터가 연결된 핀 번호를 지정합니다.
int centerPos = 90;  // 중앙 위치를 지정합니다.
int moveDegree = 39;  // 움직일 각도를 지정합니다.

void setup()
{
  myservo.attach(servoPin); // 서보 객체를 서보 핀에 연결합니다.
  Serial.begin(9600);  // 시리얼 통신을 시작합니다. 통신 속도는 9600 bps입니다.
  myservo.write(centerPos);  // 처음에 서보 모터를 중앙 위치로 설정합니다.
}

void loop()
{
  if (Serial.available()) {  // 시리얼 통신으로 데이터가 들어올 경우에만 실행합니다.
    char ch = Serial.read(); // 들어온 데이터를 읽어옵니다.
    if (ch == '1') {  // '1'이라는 신호가 들어올 경우
      myservo.write(centerPos - moveDegree);  // 중앙 위치에서 왼쪽으로 moveDegree 만큼 이동시킵니다.
    } else if (ch == '0' or '2') {  // '0', '2'이라는 신호가 들어올 경우
      myservo.write(centerPos + moveDegree+10);  // 중앙 위치에서 오른쪽으로 moveDegree+10 만큼 이동시킵니다.
    }
  }
}
