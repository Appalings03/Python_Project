import serial
import math
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# === COM PORT CONFIGURATION ===
SERIAL_PORT = 'COM11'
BAUD_RATE = 115200

ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0)

# === STORAGE ===
temperature = []
pressure = []
altitude = []
humidity = []
time_values = []

ax_values = []
ay_values = []
az_values = []
anorm_values = []
P0 = 1013.25   # sea level pressure
# ==== Temperature function ====
def temperature_function():
	axT.clear()
	axT.plot(time_values, temperature, color="red")
	axT.set_title("Temperature")
	axT.set_xlabel("Time (sec)", loc="right")
	axT.set_ylabel("Temperature (°C)")
	axT.grid(True)

# ==== Pressure function ====
def pressure_function():
	axP.clear()
	axP.plot(time_values, pressure, color="blue", label="Pressure")
	axP.set_title("Pressure")
	axP.set_xlabel("Time (sec)", loc="right")
	axP.set_ylabel("Pressure (hPa)")
	axP.grid(True)
	axP.legend(loc="upper left")

	# display altitude as text in the corner
	if len(altitude) > 0:
		axP.text(
			0.98, 0.95,
			f"Altitude: {altitude[-1]:.1f} m",
			transform=axP.transAxes,
			ha="right",
			va="top",
			fontsize=12,
			bbox=dict(facecolor="white", alpha=0.8)
		)  
# ==== Humidity function ====
def humidity_function():
	axH.clear()
	axH.plot(time_values, humidity, color="green")
	axH.set_title("Humidity")
	axH.set_xlabel("Time (sec)", loc="right")
	axH.set_ylabel("Humidity (%)")
	axH.grid(True)

# ==== Acceleration function ====
def acceleration_function():
	axA.clear()
	axA.plot(time_values, ax_values, color="orange", label="Ax")
	axA.plot(time_values, ay_values, color="purple", label="Ay")
	axA.plot(time_values, az_values, color="brown", label="Az")
	axA.plot(time_values, anorm_values, color="black", linewidth=2, label="|A|")
	axA.set_title("Accelerations")
	axA.set_xlabel("Time (sec)", loc="right")
	axA.set_ylabel("Acceleration (m/s²)")
	axA.grid(True)
	axA.legend(loc="center right")

# =============================
# SENSOR VALUES EXTRACTION
# =============================
def extract_values(line):
	try:
		if "T=" not in line or "Ax=" not in line or "t=" not in line:
			return None

		t = float(line.split("t=")[1].split("s")[0])
		temp = float(line.split("T=")[1].split("°C")[0])
		pres = float(line.split("P=")[1].split("hPa")[0])
		hum = float(line.split("H=")[1].split("%")[0])
		ax = float(line.split("Ax=")[1].split("m/s²")[0])
		ay = float(line.split("Ay=")[1].split("m/s²")[0])
		az = float(line.split("Az=")[1].split("m/s²")[0])

		return t, temp, pres, hum, ax, ay, az

	except:
		return None

# =========================
# FIGURES
# =========================
fig, (axT, axP, axH, axA) = plt.subplots(4, 1, figsize=(11, 11))
plt.tight_layout(pad=3.0)

# =========================
# UPDATE
# =========================
def update(frame):
	while ser.in_waiting:
		line = ser.readline().decode('utf-8', errors='ignore').strip()
		values = extract_values(line)

		if values is None:
			continue

		t, temp, pres, hum, ax, ay, az = values
		# altitude calculation
		h = 44330 * (1 - (pres / P0) ** 0.1903)
		
		time_values.append(t)
		temperature.append(temp)
		pressure.append(pres)
		altitude.append(h)
		humidity.append(hum)

		ax_values.append(ax)
		ay_values.append(ay)
		az_values.append(az)

		anorm = math.sqrt(ax**2 + ay**2 + az**2)
		anorm_values.append(anorm)
		  
		
	# function calls
	temperature_function()
	pressure_function()
	humidity_function()
	acceleration_function()

ani = FuncAnimation(fig, update, interval=200, cache_frame_data=False)

plt.show()
