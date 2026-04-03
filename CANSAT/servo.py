from machine import Pin, PWM 
import time

# Initialize the servo on pin GP15
servo = PWM(Pin(15))
servo.freq(50) #Standard servo frequency (50Hz)

# Convert an angle into duty cycle
def set_angle(angle):
	# angle (0-180) into duty (roughly 500 to 2500 µs)
	duty = int(2000 + (angle / 180) * 6000)
	servo.duty_u16(duty)

while True:
	# Aller à 0°
	set_angle(0)
	print ("going to 0°")
	time.sleep(1)

	# Aller à 180°
	set_angle(180)
	print ("going to 180°")
	time.sleep(1) 


