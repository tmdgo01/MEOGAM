import RPi.GPIO as GPIO
import time
from flask import Flask

app = Flask(__name__)

# 스테퍼 모터 핀 설정
IN1 = 6  # 스테퍼 모터 IN1
IN2 = 13 # 스테퍼 모터 IN2
IN3 = 19 # 스테퍼 모터 IN3
IN4 = 26 # 스테퍼 모터 IN4

# 서보 모터 핀 설정
servoPin = 21  # 서보 모터 핀

# 워터 펌프 핀 설정
IN11 = 17  # 워터 펌프 IN11
IN22 = 27  # 워터 펌프 IN22

# 팬 모터 핀 설정
DIR_PIN = 20  # 팬 모터 방향 핀
STEP_PIN = 16 # 팬 모터 스텝 핀

# 초기 설정
Steps = 0 # 스테퍼 모터의 현재 스텝 위치
Direction = 0 # 스테퍼 모터의 회전 방향
number_steps = 512  # 스테퍼 모터의 회전 단계 수 (2048/4)

# 딜레이 설정
DELAY = 0.001 # 팬 모터 속도 제어를 위한 딜레이

# 팬 모터의 각도 제한 설정
MIN_ANGLE = 0   # 최소 각도
MAX_ANGLE = 180 # 최대 각도

def setup():
    # GPIO 설정
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(IN1, GPIO.OUT)  # 스테퍼 모터 IN1 핀 출력 설정
    GPIO.setup(IN2, GPIO.OUT)  # 스테퍼 모터 IN2 핀 출력 설정
    GPIO.setup(IN3, GPIO.OUT)  # 스테퍼 모터 IN3 핀 출력 설정
    GPIO.setup(IN4, GPIO.OUT)  # 스테퍼 모터 IN4 핀 출력 설정

    GPIO.setup(servoPin, GPIO.OUT)  # 서보 모터 핀 출력 설정
    GPIO.output(servoPin, GPIO.LOW) # 서보 모터 초기 출력값 설정

    GPIO.setup(IN11, GPIO.OUT)  # 워터 펌프 IN11 핀 출력 설정
    GPIO.setup(IN22, GPIO.OUT)  # 워터 펌프 IN22 핀 출력 설정
    
    GPIO.setup(DIR_PIN, GPIO.OUT)  # 팬 모터 방향 핀 출력 설정
    GPIO.setup(STEP_PIN, GPIO.OUT) # 팬 모터 스텝 핀 출력 설정

    # 서보 모터 PWM 설정
    global servo
    servo = GPIO.PWM(servoPin, 50)  # 50Hz 주기로 PWM 설정
    servo.start(0)  # 초기 PWM 듀티 사이클 0으로 시작 (서보 모터 0도 위치)

def stepper(nbStep):
    # 스테퍼 모터 제어 함수
    global Steps
    global Direction

    if nbStep >= 0:
        Direction = 1 # 양수이면 시계방향
    else:
        Direction = 0 # 음수이면 반시계방향
        nbStep = -nbStep

    # 스테퍼 모터를 원하는 단계 수만큼 회전
    for _ in range(int(nbStep * 8)):
        if Steps == 0:
            GPIO.output(IN1, GPIO.HIGH)
            GPIO.output(IN2, GPIO.LOW)
            GPIO.output(IN3, GPIO.LOW)
            GPIO.output(IN4, GPIO.LOW)
        elif Steps == 1:
            GPIO.output(IN1, GPIO.HIGH)
            GPIO.output(IN2, GPIO.HIGH)
            GPIO.output(IN3, GPIO.LOW)
            GPIO.output(IN4, GPIO.LOW)
        elif Steps == 2:
            GPIO.output(IN1, GPIO.LOW)
            GPIO.output(IN2, GPIO.HIGH)
            GPIO.output(IN3, GPIO.LOW)
            GPIO.output(IN4, GPIO.LOW)
        elif Steps == 3:
            GPIO.output(IN1, GPIO.LOW)
            GPIO.output(IN2, GPIO.HIGH)
            GPIO.output(IN3, GPIO.HIGH)
            GPIO.output(IN4, GPIO.LOW)
        elif Steps == 4:
            GPIO.output(IN1, GPIO.LOW)
            GPIO.output(IN2, GPIO.LOW)
            GPIO.output(IN3, GPIO.HIGH)
            GPIO.output(IN4, GPIO.LOW)
        elif Steps == 5:
            GPIO.output(IN1, GPIO.LOW)
            GPIO.output(IN2, GPIO.LOW)
            GPIO.output(IN3, GPIO.HIGH)
            GPIO.output(IN4, GPIO.HIGH)
        elif Steps == 6:
            GPIO.output(IN1, GPIO.LOW)
            GPIO.output(IN2, GPIO.LOW)
            GPIO.output(IN3, GPIO.LOW)
            GPIO.output(IN4, GPIO.HIGH)
        elif Steps == 7:
            GPIO.output(IN1, GPIO.HIGH)
            GPIO.output(IN2, GPIO.LOW)
            GPIO.output(IN3, GPIO.LOW)
            GPIO.output(IN4, GPIO.HIGH)
        else:
            GPIO.output(IN1, GPIO.LOW)
            GPIO.output(IN2, GPIO.LOW)
            GPIO.output(IN3, GPIO.LOW)
            GPIO.output(IN4, GPIO.LOW)

        time.sleep(0.001)

        # 모터 회전 방향에 따라 스텝 증가 또는 감소
        if Direction == 1:
            Steps += 1
        else:
            Steps -= 1

        # 스텝이 범위를 초과하면 0 또는 7로 순환
        if Steps > 7:
            Steps = 0
        elif Steps < 0:
            Steps = 7

def setAngle(angle): # 서보 모터의 각도 설정 함수
    duty = angle / 18 + 2
    GPIO.output(servoPin, True)
    servo.ChangeDutyCycle(duty)
    time.sleep(1)
    GPIO.output(servoPin, False)
    servo.ChangeDutyCycle(0)
    
def setFanAngle(angle): # 팬 모터의 각도 설정 함수
    angle = max(MIN_ANGLE, min(MAX_ANGLE, angle)) # 각도를 최소 및 최대 각도 사이로 제한

    # 필요한 스텝 수 계산
    total_steps = int(angle * 200 / 180)  # 200 스텝/회전 기준

    # 모터 방향 설정
    if total_steps >= 0:
        GPIO.output(DIR_PIN, GPIO.LOW)  # 시계방향 회전
    else:
        GPIO.output(DIR_PIN, GPIO.HIGH) # 반시계방향 회전
        
    start_time = time.time()

    # 주어진 시간 동안 팬 모터를 회전
    while time.time() - start_time < 13:
        GPIO.output(STEP_PIN, GPIO.HIGH)
        time.sleep(DELAY)
        GPIO.output(STEP_PIN, GPIO.LOW)
        time.sleep(DELAY)

def destroy():
    # GPIO 설정 초기화
    GPIO.cleanup()

@app.route('/IN')
def insert_shampoo():
    # 샴푸를 투입하는 함수
    setAngle(180) # 서보 모터를 180도 회전
    time.sleep(4)
    setAngle(0) # 서보 모터를 0도로 되돌림
    time.sleep(1)
    servo.stop() # 서보 모터 정지
    return "<h1> INSERT SHAMPOO </h1>"

@app.route('/Shampoo')
def shampoo():
    # 샴푸를 일정 횟수 투입하는 함수
    for _ in range(3):
        stepper(number_steps // 4)  # 스테퍼 모터 1/4 회전
        time.sleep(1)
        stepper(-number_steps // 4) # 반대 방향으로 1/4 회전
        time.sleep(1)
    return "<h1> SHAMPOO </h1>"

@app.route('/Water')
def insert_water():
    # 물 투입
    GPIO.output(IN11, GPIO.HIGH) # 워터 펌프 가동
    GPIO.output(IN22, GPIO.LOW)
    print("Pump is ON")
    time.sleep(20)  # 20초 동안 펌프 가동
    GPIO.output(IN11, GPIO.LOW) # 펌프 중지
    GPIO.output(IN22, GPIO.LOW)
    # GPIO.cleanup()
    print("Pump is OFF")
    return "<h1> WATER STOP </h1>"

@app.route('/Shake')
def shake_shampoo():
    # 팬 모터를 이용해 샴푸를 섞는 함수
    setFanAngle(180) # 팬 모터를 180도 회전
    time.sleep(8)
    print("SHAKE")
    return "<h1> MAKE SHAMPOO_WATER </h1>"

@app.route('/Start')
def meogam_all():
    # 전체 프로세스를 실행하는 함수
    insert_shampoo()
    shake_shampoo()
    insert_water()
    shampoo()
    insert_water() 
    return "<h1> MEOGAM ALL </h1>"

if __name__ == '__main__':
    setup() # 초기 설정
    app.run(host="0.0.0.0", port=8080) # Flask 서버 실행
