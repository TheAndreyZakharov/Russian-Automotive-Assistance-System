import os
import cv2
import time
import numpy as np
import threading
from datetime import datetime
from collections import deque
import carla  # подключаем CARLA

class CameraBufferRecorder:
    def __init__(self, camera_keys, fps=30, buffer_seconds=60, post_seconds=60, output_dir="recordings"):
        self.fps = fps
        self.buffer_seconds = buffer_seconds
        self.post_seconds = post_seconds
        self.buffer = {key: deque(maxlen=fps * buffer_seconds) for key in camera_keys}
        self.last_frame_time = {key: None for key in camera_keys}

        # === Подключаемся к CARLA и машине
        client = carla.Client('localhost', 2000)
        client.set_timeout(10.0)
        world = client.get_world()
        vehicles = world.get_actors().filter('vehicle.*')
        self.vehicle = vehicles[0] if vehicles else None

        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.output_dir = os.path.join(base_dir, output_dir)
        self.lock = threading.Lock()
        os.makedirs(self.output_dir, exist_ok=True)

    def get_speed_kmh(self):
        try:
            if self.vehicle:
                v = self.vehicle.get_velocity()
                speed = (v.x**2 + v.y**2 + v.z**2)**0.5
                return int(speed * 3.6)
        except:
            pass
        return 0

    def add_frame(self, key, frame):
        with self.lock:
            if key in self.buffer and self.vehicle:
                velocity = self.vehicle.get_velocity()
                speed = (velocity.x**2 + velocity.y**2 + velocity.z**2)**0.5 * 3.6
                self.buffer[key].append((frame.copy(), time.time(), speed))
                self.last_frame_time[key] = time.time()


    def trigger_event_recording(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        buffer_snapshots = {}
        local_sizes = {}

        with self.lock:
            for key, frames in self.buffer.items():
                if not frames:
                    continue
                buffer_snapshots[key] = list(frames)
                frame_sample = frames[0][0]  # достаём сам frame из tuple
                h, w = frame_sample.shape[:2]
                local_sizes[key] = (w, h)

        def stop_local_recording():
            post_frames = {k: [] for k in buffer_snapshots}
            start_time = time.time()

            while time.time() - start_time < self.post_seconds:
                with self.lock:
                    for key in post_frames:
                        if self.buffer[key]:
                            frame, ts, speed = self.buffer[key][-1]
                            post_frames[key].append((frame.copy(), ts, speed))
                time.sleep(1 / self.fps)

            with self.lock:
                for key, before_frames in buffer_snapshots.items():
                    after_frames = post_frames[key]
                    all_frames = before_frames + after_frames
                    total_frames = len(all_frames)
                    forced_fps = max(1, total_frames / (self.buffer_seconds + self.post_seconds))

                    w, h = local_sizes[key]
                    out_path = os.path.join(self.output_dir, f"{timestamp}_{key}.mp4")
                    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                    writer = cv2.VideoWriter(out_path, fourcc, forced_fps, (w, h))

                    for frame, ts, speed in all_frames:
                        if frame.shape[:2] != (h, w):
                            frame = cv2.resize(frame, (w, h))

                        dt = datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
                        overlay_text = f"{dt}  |  {int(speed)} km/h"

                        # Мелкий шрифт
                        font_scale = 0.4
                        thickness = 1
                        color = (255, 255, 255)

                        text_size, _ = cv2.getTextSize(overlay_text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)
                        text_x = w - text_size[0] - 10
                        text_y = 15

                        cv2.putText(frame, overlay_text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness, cv2.LINE_AA)

                        writer.write(frame)

                    writer.release()

        threading.Thread(target=stop_local_recording, daemon=True).start()
