import pigpio
import time


class ServoController:
    # MG90S 데이터시트 기준 전기적 펄스폭 한계 (us)
    DATASHEET_PULSE_MIN = 500
    DATASHEET_PULSE_MAX = 2400

    def __init__(self, pi, pin, pulse_min=600, pulse_max=2400, change=30):
        self.pi = pi
        self.pin = pin
        self.change = change

        self.set_pulse_range(pulse_min, pulse_max)
        self.forward = True
        self.set_pulse((self.pulse_min + self.pulse_max) // 2)

    # Servo모터의 pulsewidth 범위를 설정 (단위: us)
    def set_pulse_range(self, pulse_min, pulse_max):
        if pulse_min >= pulse_max:
            raise ValueError("pulse_min은 pulse_max보다 작아야 합니다.")
        if pulse_min < self.DATASHEET_PULSE_MIN or pulse_max > self.DATASHEET_PULSE_MAX:
            raise ValueError(
                f"펄스폭은 데이터시트 한계({self.DATASHEET_PULSE_MIN}~"
                f"{self.DATASHEET_PULSE_MAX}us) 안에서만 설정할 수 있습니다."
            )
        self.pulse_min = pulse_min
        self.pulse_max = pulse_max

    # Servo모터의 현재 pulsewidth를 설정 (단위: us)
    def set_pulse(self, pulsewidth):
        self.raw = pulsewidth
        self.pi.set_servo_pulsewidth(self.pin, self.raw)

    # Servo모터의 pulsewidth를 step 단위로 증가/감소시키며 제어
    def step(self):
        if self.raw + self.change > self.pulse_max or self.raw - self.change < self.pulse_min:
            self.forward = not self.forward
        next_raw = self.raw + self.change if self.forward else self.raw - self.change

        self.set_pulse(next_raw)

    # 현재 Servo모터의 pulsewidth를 출력
    def echo_pulse(self):
        print(f"GPIO{self.pin} Pulsewidth (us):", self.raw)

    # Servo모터를 정지시키고 GPIO핀을 초기화
    def stop(self):
        self.set_pulse(0)  # 신호 끄기


pi = pigpio.pi()
if not pi.connected:
    print("pigpiod에 연결할 수 없습니다. 'sudo pigpiod'로 데몬을 먼저 실행하세요.")
    exit()

servos = [
    ServoController(pi, pin=17),
    ServoController(pi, pin=27),
]

# Set one servo's pulse range to demonstrate the feature
# servos[0].set_pulse_range(1000, 1500)

try:
    while True:
        for servo in servos:
            servo.step()

        servos[0].echo_pulse()
        time.sleep(0.1)
except KeyboardInterrupt:
    pass
finally:
    for servo in servos:
        servo.stop()
    pi.stop()
