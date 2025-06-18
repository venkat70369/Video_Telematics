import time
import math
import keyboard
import threading
import datetime
from multiprocessing.connection import Client

# Simulated Vehicle Publisher Code (Publisher)
class SimulatedVehicle:
    def __init__(self, x=0, y=0, velocity=0):
        self.x = x
        self.y = y
        self.velocity = velocity
        self.angle = 0  # Direction in degrees
        self.crash = False
        self.timestamp = (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def key_event(self, event, acceleration=0.5, deceleration=-0.5, dt=0.1):
        if event.event_type == keyboard.KEY_DOWN:
            if event.name == 'w':
                self.velocity += acceleration * dt
            elif event.name == 's':
                self.velocity += deceleration * dt
            elif event.name == 'b':
                self.crash = True

        if event.name in ('w', 's'):
            dx = self.velocity * math.cos(math.radians(self.angle)) * dt
            dy = self.velocity * math.sin(math.radians(self.angle)) * dt
            self.x += dx
            self.y += dy


class Publisher:
    def __init__(self):
        self.vehicle = SimulatedVehicle()

    def start_publishing(self):
        keyboard.hook(self.vehicle.key_event)
        address = r'\\.\pipe\vehicle_data_pipe'  # Same named pipe path
        conn = Client(address, authkey=b'secret')
        try:
            while True:
                dx = self.vehicle.velocity * math.cos(math.radians(self.vehicle.angle)) * 0.1
                dy = self.vehicle.velocity * math.sin(math.radians(self.vehicle.angle)) * 0.1
                self.vehicle.x += dx
                self.vehicle.y += dy

                print(f"Location: ({self.vehicle.x:.2f}, {self.vehicle.y:.2f}), Speed: {self.vehicle.velocity:.2f} m/s")

                if self.vehicle.crash:
                    # Notice the extra parentheses creating a tuple
                    conn.send((f"Location: ({self.vehicle.x:.2f}, {self.vehicle.y:.2f}), Speed: {self.vehicle.velocity:.2f} m/s",self.vehicle.timestamp))
                    reply = conn.recv()
                    print("Received from server:", reply)
                    print("🚨 Incident detected!")  # Removed call to subscriber
                    self.vehicle.crash = False  # reset after handling

                time.sleep(0.1)

        except KeyboardInterrupt:
            print("Exiting simulation.")
            time.sleep(0.1)


def main():
    publisher = Publisher()
    publisher_thread = threading.Thread(target=publisher.start_publishing())
    publisher_thread.daemon = True
    publisher_thread.start()


    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Main loop interrupted. Exiting...")

if __name__ == "__main__":
    main()
