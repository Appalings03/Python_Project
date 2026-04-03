import math
import time
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# === STORAGE ===
temperature = []
pressure = []
altitude = []
humidity = []
time_values = []

start_time = time.time()
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

# =========================
# FIGURES
# =========================
fig, (axT, axP, axH) = plt.subplots(3, 1, figsize=(11, 10))
plt.tight_layout(pad=3.0)

# =========================
# UPDATE
# =========================
def update(frame):
	t = time.time() - start_time   # real elapsed time
	value = math.sin(t)			# defined function
	
	# Simulate pressure around 1013 hPa
	p = 1013 + value * 10

	# altitude calculation
	h = 44330 * (1 - (p / P0) ** 0.1903)

	time_values.append(t)
	temperature.append(value)
	pressure.append(p)
	altitude.append(h)
	humidity.append(value)

	# function calls
	temperature_function()
	pressure_function()
	humidity_function()

ani = FuncAnimation(fig, update, interval=100, cache_frame_data=False)

plt.show()
