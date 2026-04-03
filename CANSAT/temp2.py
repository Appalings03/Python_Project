# Mean read the TMP36 analog temperature
#   sensor wired to ADC0 (GP26)
#
from machine import ADC, Pin
import time

# Deactivate PowerSafe (lower ripple)
Pin( 23, Pin.OUT, value=True )

adc = ADC(Pin(26))

while True:
	value = 0
	for i in range(10):
		value += adc.read_u16()
	value /= 10
	mv = 3300.0 * value / 65535
	temp = (mv-500)/10
	print( 'Temp: %5.2f °C, Voltage: %4i mV' % (temp,mv) )
	time.sleep(0.100 )

