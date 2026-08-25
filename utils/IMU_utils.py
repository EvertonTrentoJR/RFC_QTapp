import serial
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from collections import deque

# ============================================================
# CONFIGURATION
# ============================================================

PORT = "COM12"
BAUDRATE = 115200

# Number of samples visible on screen
WINDOW = 500

# ============================================================
# SERIAL
# ============================================================

ser = serial.Serial(
    PORT,
    BAUDRATE,
    timeout=0.1
)

# Remove old data from serial buffer
ser.reset_input_buffer()

print(f"Connected to {PORT} @ {BAUDRATE} baud")


# ============================================================
# DATA
# ============================================================

names = [
    "Ax", "Ay", "Az",
    "Gx", "Gy", "Gz",
    "Mx", "My", "Mz",
    "Qi", "Qj", "Qk", "Qr"
]

data = {
    name: deque(maxlen=WINDOW)
    for name in names
}

samples = deque(maxlen=WINDOW)

sample_number = 0


# ============================================================
# FIGURE
# ============================================================

plt.ion()

fig, ax = plt.subplots(
    4,
    1,
    figsize=(12, 10),
    sharex=True
)

fig.suptitle("BNO085 Real-Time IMU Data")


# ------------------------------------------------------------
# Accelerometer
# ------------------------------------------------------------

line_ax, = ax[0].plot([], [], label="Ax")
line_ay, = ax[0].plot([], [], label="Ay")
line_az, = ax[0].plot([], [], label="Az")

ax[0].set_ylabel("m/s²")
ax[0].set_title("Accelerometer")
ax[0].legend()
ax[0].grid()


# ------------------------------------------------------------
# Gyroscope
# ------------------------------------------------------------

line_gx, = ax[1].plot([], [], label="Gx")
line_gy, = ax[1].plot([], [], label="Gy")
line_gz, = ax[1].plot([], [], label="Gz")

ax[1].set_ylabel("rad/s")
ax[1].set_title("Gyroscope")
ax[1].legend()
ax[1].grid()


# ------------------------------------------------------------
# Magnetometer
# ------------------------------------------------------------

line_mx, = ax[2].plot([], [], label="Mx")
line_my, = ax[2].plot([], [], label="My")
line_mz, = ax[2].plot([], [], label="Mz")

ax[2].set_ylabel("µT")
ax[2].set_title("Magnetometer")
ax[2].legend()
ax[2].grid()


# ------------------------------------------------------------
# Quaternion
# ------------------------------------------------------------

line_qi, = ax[3].plot([], [], label="Qi")
line_qj, = ax[3].plot([], [], label="Qj")
line_qk, = ax[3].plot([], [], label="Qk")
line_qr, = ax[3].plot([], [], label="Qr")

ax[3].set_ylabel("Quaternion")
ax[3].set_xlabel("Sample")
ax[3].set_title("Rotation Vector")
ax[3].legend()
ax[3].grid()


plt.tight_layout()


# ============================================================
# REAL-TIME LOOP
# ============================================================

try:

    while plt.fignum_exists(fig.number):

        # ----------------------------------------------------
        # Read serial
        # ----------------------------------------------------

        while ser.in_waiting:

            try:

                line = ser.readline().decode(
                    "utf-8",
                    errors="ignore"
                ).strip()

                values = line.split(",")

                # Arduino packet must contain exactly 13 values
                if len(values) != 13:
                    continue

                values = [float(v) for v in values]

                # Store values
                for name, value in zip(names, values):
                    data[name].append(value)

                samples.append(sample_number)

                sample_number += 1

            except ValueError:
                # Ignore header / malformed lines
                continue


        # ----------------------------------------------------
        # Update plots
        # ----------------------------------------------------

        if len(samples) > 0:

            x = list(samples)

            # Accelerometer

            line_ax.set_data(x, data["Ax"])
            line_ay.set_data(x, data["Ay"])
            line_az.set_data(x, data["Az"])


            # Gyroscope

            line_gx.set_data(x, data["Gx"])
            line_gy.set_data(x, data["Gy"])
            line_gz.set_data(x, data["Gz"])


            # Magnetometer

            line_mx.set_data(x, data["Mx"])
            line_my.set_data(x, data["My"])
            line_mz.set_data(x, data["Mz"])


            # Quaternion

            line_qi.set_data(x, data["Qi"])
            line_qj.set_data(x, data["Qj"])
            line_qk.set_data(x, data["Qk"])
            line_qr.set_data(x, data["Qr"])


            # ------------------------------------------------
            # Automatic axis limits
            # ------------------------------------------------

            for axis in ax:

                axis.relim()
                axis.autoscale_view()


        # ----------------------------------------------------
        # Refresh
        # ----------------------------------------------------

        fig.canvas.draw_idle()
        fig.canvas.flush_events()

        plt.pause(0.01)


except KeyboardInterrupt:

    print("\nStopped by user.")


finally:

    ser.close()

    print("Serial port closed.")