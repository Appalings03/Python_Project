from machine import SPI, Pin
from rfm69 import RFM69
import time


FREQ		   = 434.0
ENCRYPTION_KEY = b"\x01\x02\x03\x04\x05\x06\x07\x08\x01\x02\x03\x04\x05\x06\x07\x08"
BASESTATION_ID		= 159 # ID of this node (being the base station)

spi = SPI(0, miso=Pin(4), mosi=Pin(7), sck=Pin(6), baudrate=50000, polarity=0, phase=0, firstbit=SPI.MSB)
nss = Pin( 5, Pin.OUT, value=True )
rst = Pin( 3, Pin.OUT, value=False )

rfm = RFM69( spi=spi, nss=nss, reset=rst )
rfm.frequency_mhz = FREQ

# Optionally set an encryption key (16 byte AES key). MUST match both
# on the transmitter and receiver (or be set to None to disable/the default).
rfm.encryption_key = ( ENCRYPTION_KEY )
rfm.node = BASESTATION_ID # This instance is the node 100

print( 'Freq			:', rfm.frequency_mhz )
print( 'NODE			:', rfm.node )

print("Waiting for packets...")

# Send a packet and waits for its ACK.
# Note you can only send a packet up to 60 bytes in length.
counter = 1
last_rssi	   = None # Capture the RSSI when receing ack
rfm.ack_retries = 3 # 3 attempt to receive ACK
rfm.ack_wait	= 0.5 # 500ms, time to wait for ACK 
rfm.destination = BASESTATION_ID # Send to specific node 100

while True:
	packet = rfm.receive( with_ack=True )
	# Optionally change the receive timeout from its default of 0.5 seconds:
	# packet = rfm.receive(timeout=5.0)
	# If no packet was received during the timeout then None is returned.
	if packet is None:
		# Packet has not been received
		pass
	else:
		# Received a packet!
		print( "Received (raw bytes):", packet )
		# And decode to ASCII text
		packet_text = str(packet, "ascii")
		print("Received (ASCII):", packet_text)
		# RSSI of last received message
		print("RSSI			: %3.2f" % rfm.rssi )
		# Fine sampling of RSSI. 
		# Under development: sometime hold the SPI for infinite time
		# rfm.sample_rssi()
		print("-"*40)


