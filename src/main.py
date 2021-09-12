from pymycobot.mycobot import MyCobot
from pymycobot.genre import Angle
from time import sleep

mc = MyCobot('/dev/ttyUSB0')
if mc.is_power_on() == 0:
    mc.power_on()

mc.send_angles([0, 0, 0, 0, 0, 0], 50)
sleep(5)
mc.send_coords([-275.4, -64.6, 199.8, -0.7, 0.0, -15.7], 50, 0)
