from pymycobot.mycobot import MyCobot
from pymycobot.genre import Angle
from time import sleep

mc = MyCobot('/dev/ttyUSB0')
if mc.is_power_on() == 0:
    mc.power_on()

mc.set_gripper_ini()
mc.set_gripper_state(0, 50)

speed = 60
mc.sync_send_angles(
    [0, 0, 0, 0, 0, 0],
    speed,
).sync_send_angles(
    [11.33, 30, 45.17, 84.9, -55.81, 170.59],
    speed,
).send_angle(Angle.J2.value, 58.53, speed)

while True:
    if mc.is_in_position([11.33, 58.53, 45.17, 84.9, -55.81, 170.59], 0) == 1:
        break
    elif mc.is_in_position([11.33, 58.53, 45.17, 84.9, -55.81, 170.59], 0) == -1:
        print('is_in_position returns error')
        break

sleep(0.5)
mc.set_gripper_state(1, 50)
sleep(2)

mc.sync_send_angles(
    [0, 0, 0, 0, -80, -80],
    speed,
).sync_send_angles(
    [-32.95, 89.82, 47.37, -86.92, -86.22, -45.61],
    speed,
)

sleep(0.5)
mc.set_gripper_state(0, 50)
sleep(2)

mc.sync_send_angles(
    [0, 0, 0, 0, 0, 0],
    speed,
)
