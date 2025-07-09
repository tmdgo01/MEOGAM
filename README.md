# 혼자 머리를 감기 힘든 사람을 위한 머리 세척 기계
Flask와 Raspberry Pi를 이용하여 앱-하드웨어 제작

| 번호   | 액추에이터 종류         | 개수     | 설명          |
| ---- | ---------------- | ------ | ----------- |
| 1    | Stepper Motor | 1    | 머리 감기     |
| 2    | Servo Motor    | 1    | 샴푸 기울이기   |
| 3    | DC Motor        | 1  | 샴푸/물 혼합     |
| 4    | WaterPump         | 1   | 물 공급       |
| 5    | SZH-MDBL-002(Motor driver)    | 1    | WaterPump, Dc Motor     |

![MEOGAM](https://github.com/user-attachments/assets/21651fcf-cf58-4c41-b203-98f6103e7011)

## Raspberry Pin Settings

<!-- [31] GPIO 6   → 스텝퍼 IN1
[33] GPIO 13  → 스텝퍼 IN2  
[35] GPIO 19  → 스텝퍼 IN3  
[37] GPIO 26  → 스텝퍼 IN4  

[40] GPIO 21  → 서보 모터 PWM  

[11] GPIO 17  → 릴레이 IN1 (펌프)  
[13] GPIO 27  → 릴레이 IN2 (펌프)  

[38] GPIO 20  → 팬 모터 DIR  
[36] GPIO 16  → 팬 모터 STEP --!>

![그림1](https://github.com/user-attachments/assets/412a64bb-d6ea-4341-b1d8-84915bfdd43e)


