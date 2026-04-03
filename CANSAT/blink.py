from machine import Pin, PWM
import time

led = PWM( Pin(25 ))
led.freq(1000)

def gamma( pc ):
	return pow(pc/100,2.2)*100

while True:
	for i in range( 0, 100, 5 ):
		pwm_val = int(gamma(i)*65534/100)
		led.duty_u16( pwm_val )
		print( pwm_val )
		time.sleep_ms( 20 )
	for i in range( 0, 100, 5 ):
		pwm_val = int(gamma(100-i)*65534/100)
		led.duty_u16( pwm_val )
		print( pwm_val )
		time.sleep_ms( 20 )
