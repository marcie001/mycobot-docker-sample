from pymycobot.mycobot import MyCobot
from pymycobot.genre import Angle
from time import sleep

mc = MyCobot('/dev/ttyUSB0')
if mc.is_power_on() == 0:
    mc.power_on()

mc.send_angles([0, 0, 0, 0, 0, 0], 50)
sleep(5)
mc.send_angles([1.84, -24.39, -22.81, 1.71, -2.19, 0.03], 30)
