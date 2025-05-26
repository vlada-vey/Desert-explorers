rom machine import Pin, PWM, I2C
from ble_uart_peripheral import *
import uasyncio as asio
from time import sleep, sleep_ms
from tcs34725 import *
from MX1508 import *
import time
import utime

# Инициализация моторов
motor1 = MX1508(25, 33)  # Левый мотор
motor2 = MX1508(26, 27)  # Правый мотор

# --- Настройки сервопривода ---
SERVO_PIN = 18
SERVO_FREQ = 50
SERVO_MIN_DUTY = 2000
SERVO_MAX_DUTY = 9000
SERVO_RANGE = SERVO_MAX_DUTY - SERVO_MIN_DUTY
servo = PWM(Pin(SERVO_PIN), freq=SERVO_FREQ)
current_angle = 90  # Начальное положение сервы

# --- Функции движения ---
def stop():
    motor1.stop()
    motor2.stop()

def forward(speed=500):
    motor1.forward(speed)
    motor2.forward(speed)

def backward(speed=500):
    motor1.reverse(speed)
    motor2.reverse(speed)

def turn_right(speed=500):
    motor1.forward(speed)
    motor2.reverse(speed)

def turn_left(speed=500):
    motor1.reverse(speed)
    motor2.forward(speed)

# --- Управление сервоприводом ---
def set_servo_angle(angle):
    global current_angle
    if 0 <= angle <= 180:
        duty = int(SERVO_MIN_DUTY + (angle / 180) * SERVO_RANGE)
        servo.duty_u16(duty)
        current_angle = angle
        print(f"Серва: {angle}°")
    else:
        print("Ошибка: Угол должен быть 0-180")

def move_up():
    global current_angle
    new_angle = current_angle + 15
    if new_angle > 180:
        new_angle = 180
    set_servo_angle(new_angle)

def move_down():
    global current_angle
    new_angle = current_angle - 15
    if new_angle < 0:
        new_angle = 0
    set_servo_angle(new_angle)

# --- Bluetooth обработчик ---
cmd = ''
state = False

def on_rx():
    global cmd, state
    uart_in = uart.read()
    try:
        uart_str = uart_in.decode().strip()
        print("UART IN:", uart_str)

        # Управление движением
        if uart_str == '!B516':    # Вперед
            forward()
        elif uart_str == '!B615':  # Назад
            backward()
        elif uart_str == '!B714':  # Вправо
            turn_right()
        elif uart_str == '!B813':  # Влево
            turn_left()
        elif uart_str.startswith('!SA'):  # Абсолютный угол
            try:
                angle = int(uart_str[3:])
                set_servo_angle(angle)
            except ValueError:
                print("Ошибка угла сервы")
        elif uart_str == '!UP':    # +15°
            move_up()
        elif uart_str == '!DOWN':  # -15°
            move_down()
        elif uart_str in ('!B507', '!B606', '!B804', '!B705', '!B309'):
            stop()

        cmd = uart_str
        state = True

    except UnicodeDecodeError:
        print("Ошибка декодирования")

# --- BLE инициализация ---
ble = bluetooth.BLE()
uart = BLEUART(ble, name="RobotControl")
uart.irq(handler=on_rx)

# --- Асинхронная задача ---
async def execute(int_ms):
    while True:
        await asio.sleep_ms(int_ms)

print("Система активирована")
loop = asio.get_event_loop()
loop.create_task(execute(0))
loop.run_forever()
