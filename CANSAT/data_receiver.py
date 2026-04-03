from machine import SPI, Pin
from rfm69 import RFM69
import time
import sys

# ==============================
# RFM69 CONFIGURATION
# ==============================
spi = SPI(
	0, miso=Pin(4), mosi=Pin(7), sck=Pin(6),
	baudrate=50000, polarity=0, phase=0, firstbit=SPI.MSB
)

nss = Pin(5, Pin.OUT, value=True)
rst = Pin(3, Pin.OUT, value=False)

rfm = RFM69(spi=spi, nss=nss, reset=rst)
rfm.frequency_mhz = 434.0
rfm.encryption_key = (
	b"\x01\x02\x03\x04\x05\x06\x07\x08"
	b"\x01\x02\x03\x04\x05\x06\x07\x08"
)

print("Receiver ready!")
print("=== Dynamic display ===")

# ==============================
# MONITORING VARIABLES
# ==============================
last_line_length = 0
last_packet_time = time.time()
timeout_sec = 10  # alert after 10 seconds without packet

# ==============================
# MAIN LOOP
# ==============================
while True:
	packet = rfm.receive()
	current_time = time.time()

	if packet:
		try:
			# decoding
			data_str = packet.decode("utf-8").strip()
			values = data_str.split(",")

			# check that all values are present
			if len(values) != 7:
				continue

			# data extraction
			t_em, temp, pres, hum, ax, ay, az = map(float, values)

			# dynamic line for display
			line = (
				"t={:.2f}s | T={:.2f}°C | P={:.2f}hPa | H={:.2f}% || "
				"Ax={:.3f}m/s² Ay={:.3f}m/s² Az={:.3f}m/s²"
			).format(t_em, temp, pres, hum, ax, ay, az)

			# clear previous characters if the line becomes shorter
			clear_line = line + " " * max(0, last_line_length - len(line))
			sys.stdout.write("\r" + clear_line)

			last_line_length = len(line)
			last_packet_time = current_time

		except Exception:
			continue

	else:
		# no packet received: check timeout
		if current_time - last_packet_time > timeout_sec:
			msg = "Telemetry lost after 10 seconds"
			clear_line = msg + " " * max(0, last_line_length - len(msg))
			sys.stdout.write("\r" + clear_line)
			last_line_length = len(msg)

	# small delay to avoid CPU overload
	time.sleep(0.05)
