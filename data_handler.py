# data_handler.py

import cv2
import threading
import sys
import time
import os
from multiprocessing.connection import Listener, Client
import subprocess

class DataHandler:
    def __init__(self, data_pipe=r'\\.\pipe\vehicle_data_pipe', incident_pipe=r'\\.\pipe\mypipe_incident'):
        self.data_pipe = data_pipe
        self.incident_pipe = incident_pipe
        self.log_file = "vehicle_log.txt"
        self.continuous_video = "continuous_video.mp4"
        self.cap = cv2.VideoCapture(0)
        self.lock = threading.Lock()
        self.fps = 20.0
        self.resolution = (640, 480)

        if not self.cap.isOpened():
            print("❌ Could not open camera.")
            self.cap = None

    def start_livestream_and_record(self):
        if self.cap is None:
            return

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(self.continuous_video, fourcc, self.fps, self.resolution)

        while True:
            with self.lock:
                ret, frame = self.cap.read()
            if not ret:
                print("❌ Failed to capture frame.")
                break

            out.write(frame)
            cv2.imshow("Live Feed", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        out.release()
        self.cap.release()
        cv2.destroyAllWindows()

    def listen_for_vehicle_data(self):
        listener = Listener(self.data_pipe, authkey=b'secret')
        print("🚦 DataHandler listening for vehicle data...")

        while True:
            conn = listener.accept()
            msg = conn.recv()
            print("📥 Received:", msg)

            with open(self.log_file, 'a') as f:
                f.write(str(msg) + "\n")

            if isinstance(msg, tuple) and len(msg) == 2:
                info_str, timestamp = msg
                if "Speed" in info_str and "Location" in info_str:
                    print("🚨 Incident detected!")

                    try:
                        # Launch EventHandler
                        event_script_path = r"C:\Users\agilk\AppData\Roaming\JetBrains\PyCharmCE2025.1\scratches\event_handler.py"
                        subprocess.Popen([sys.executable, event_script_path],
                                         creationflags=subprocess.CREATE_NEW_CONSOLE)

                        # Try to connect to EventHandler pipe with retry
                        start_time = time.time()
                        timeout = 10  # seconds

                        while True:
                            try:
                                forward_conn = Client(self.incident_pipe, authkey=b'secret')
                                break
                            except (ConnectionRefusedError, FileNotFoundError):
                                if time.time() - start_time > timeout:
                                    raise TimeoutError("❌ EventHandler pipe not ready in time.")
                                time.sleep(0.2)

                        # Send timestamp
                        forward_conn.send(float(timestamp))
                        response = forward_conn.recv()
                        print("📬 EventHandler replied:", response)
                        forward_conn.close()

                    except Exception as e:
                        print("❌ Failed to communicate with EventHandler:", e)

            conn.close()

    def run(self):
        threading.Thread(target=self.start_livestream_and_record, daemon=True).start()
        self.listen_for_vehicle_data()

if __name__ == "__main__":
    handler = DataHandler()
    handler.run()
