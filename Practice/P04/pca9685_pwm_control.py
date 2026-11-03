# Requires: pip3 install adafruit-circuitpython-pca9685 adafruit-blinka
#
# Wiring (matches this circuit):
#   - PCA9685 VCC  -> RPi 3.3V (pin 1)
#   - PCA9685 SDA  -> RPi GPIO2 / pin 3
#   - PCA9685 SCL  -> RPi GPIO3 / pin 5
#   - PCA9685 GND  -> RPi GND (common ground with the servo power supply)
#   - PCA9685 V+   -> external 4.8-6V supply for the servo (NOT from RPi)
#   - Servo signal (orange) -> PCA9685 channel 0, 1, ...
#   - Servo VCC (red)       -> PCA9685 V+ terminal
#   - Servo GND (brown)     -> PCA9685 GND terminal

import time

import board
import busio
from adafruit_pca9685 import PCA9685

PWM_FREQ_HZ = 50  # 20ms period, per the MG90S PWM spec


class ServoController:
    def __init__(self, pca, channel, duty_min=5.0, duty_max=10.0, change=0.1):
        self.pca = pca
        self.channel = channel
        self.duty_min = duty_min
        self.duty_max = duty_max
        self.change = change

        self.forward = True
        # Start at the midpoint; override with set_duty() if a different
        # center is needed (<- fill this using the answer for Question 3).
        self.set_duty((duty_min + duty_max) / 2)

    @staticmethod
    def _duty_percent_to_raw(duty_percent):
        duty_percent = max(0.0, min(100.0, duty_percent))
        return int(duty_percent / 100.0 * 0xFFFF)

    # Servo모터의 현재 duty(%)를 설정
    def set_duty(self, duty_percent):
        self.raw = duty_percent
        self.pca.channels[self.channel].duty_cycle = self._duty_percent_to_raw(duty_percent)

    # Servo모터의 duty를 step 단위로 증가/감소시키며 제어
    def step(self):
        if self.raw + self.change > self.duty_max or self.raw - self.change < self.duty_min:
            self.forward = not self.forward
        next_raw = self.raw + self.change if self.forward else self.raw - self.change

        self.set_duty(next_raw)

    # 현재 Servo모터의 duty를 출력
    def echo_duty(self):
        print(f"Channel{self.channel} Duty (in %):", self.raw)

    # Servo모터를 정지시킴
    def stop(self):
        self.pca.channels[self.channel].duty_cycle = 0


i2c = busio.I2C(board.SCL, board.SDA)
pca = PCA9685(i2c)
pca.frequency = PWM_FREQ_HZ

servos = [
    ServoController(pca, channel=15),
    ServoController(pca, channel=14),
]

try:
    while True:
        for servo in servos:
            servo.step()

        servos[0].echo_duty()
        time.sleep(0.1)
except KeyboardInterrupt:
    pass
finally:
    for servo in servos:
        servo.stop()
    pca.deinit()
