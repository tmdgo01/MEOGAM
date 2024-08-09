import RPi.GPIO as GPIO
import time
from flask import Flask

app = Flask(__name__)

IN1 = 6  # stepper motor
IN2 = 13
IN3 = 19
IN4 = 26

servoPin = 21  # ServoMotor

IN11 = 17  # WaterPump
IN22 = 27

DIR_PIN = 20 # FanMotor
STEP_PIN = 16

Steps = 0
Direction = 0
number_steps = 512  # = 2048/4

DELAY = 0.001 # contorol FanMotor Speed

MIN_ANGLE = 0 # Fan angle limits
MAX_ANGLE = 180

def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(IN1, GPIO.OUT)  # stepper motor
    GPIO.setup(IN2, GPIO.OUT)
    GPIO.setup(IN3, GPIO.OUT)
    GPIO.setup(IN4, GPIO.OUT)

    GPIO.setup(servoPin, GPIO.OUT)  # servo motor
    GPIO.output(servoPin, GPIO.LOW)

    GPIO.setup(IN11, GPIO.OUT)  # water pump
    GPIO.setup(IN22, GPIO.OUT)
    
    GPIO.setup(DIR_PIN, GPIO.OUT) # FanMotor
    GPIO.setup(STEP_PIN, GPIO.OUT)

    global servo
    servo = GPIO.PWM(servoPin, 50)  # 50 Hz (20 ms PWM period)
    servo.start(0)  # Starts PWM with duty cycle of 0 (servo at 0 degrees)


def stepper(nbStep):
    global Steps
    global Direction

    if nbStep >= 0:
        Direction = 1
    else:
        Direction = 0
        nbStep = -nbStep

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

        if Direction == 1:
            Steps += 1
        else:
            Steps -= 1

        if Steps > 7:
            Steps = 0
        elif Steps < 0:
            Steps = 7


def setAngle(angle): # StepperMotor Angle
    duty = angle / 18 + 2
    GPIO.output(servoPin, True)
    servo.ChangeDutyCycle(duty)
    time.sleep(1)
    GPIO.output(servoPin, False)
    servo.ChangeDutyCycle(0)
    
def setFanAngle(angle): # FanMotor Angle
    angle = max(MIN_ANGLE, min(MAX_ANGLE, angle))

    # Calculate the number of steps required
    total_steps = int(angle * 200 / 180)  # Assuming 200 steps per revolution

    # Set the motor direction
    if total_steps >= 0:
        GPIO.output(DIR_PIN, GPIO.LOW)  # Rotate clockwise
    else:
        GPIO.output(DIR_PIN, GPIO.HIGH)  # Rotate counter-clockwise
        
    start_time = time.time()

    while time.time() - start_time < 13:
        GPIO.output(STEP_PIN, GPIO.HIGH)
        time.sleep(DELAY)
        GPIO.output(STEP_PIN, GPIO.LOW)
        time.sleep(DELAY)


def destroy():
    GPIO.cleanup()


@app.route('/IN')
def insert_shampoo():
    setAngle(180)
    time.sleep(4)
    setAngle(0)
    time.sleep(1)
    servo.stop()
    return "<h1> INSERT SHAMPOO </h1>"


@app.route('/Shampoo')
def shampoo():
    for _ in range(3):
        stepper(number_steps // 4)
        time.sleep(1)
        stepper(-number_steps // 4)
        time.sleep(1)
    return "<h1> SHAMPOO </h1>"

@app.route('/Water')
def insert_water():
    GPIO.output(IN11, GPIO.HIGH)
    GPIO.output(IN22, GPIO.LOW)
    print("Pump is ON")
    time.sleep(20)  # Run the pump
    GPIO.output(IN11, GPIO.LOW)
    GPIO.output(IN22, GPIO.LOW)
    # GPIO.cleanup()
    print("Pump is OFF")
    return "<h1> WATER STOP </h1>"

@app.route('/Shake')
def shake_shampoo():
    setFanAngle(180)
    time.sleep(8)
    print("SHAKE")
    return "<h1> MAKE SHAMPOO_WATER </h1>"

@app.route('/Start')
def meogam_all():
    insert_shampoo()
    shake_shampoo()
    insert_water()
    shampoo()
    insert_water() # OUT
    return "<h1> MEOGAM ALL </h1>"


if __name__ == '__main__':
    setup()
    app.run(host="0.0.0.0", port=8080)

