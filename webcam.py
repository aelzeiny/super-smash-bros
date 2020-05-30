from typing import Optional

import cv2
import threading
import datetime as dt
import time

from smash_utils import wait_for_time


class WebCamRecorder:
    def __init__(self, capture_device: int = 0, fourcc: str = 'MJPG', width: int = 640, height: int = 480,
                 fps: int = 60):
        self.cap = VideoCaptureAsync(capture_device, width=width, height=height, fps=fps)

        self.fourcc = cv2.VideoWriter_fourcc(*fourcc)
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.fps = fps

        self.writer = None
        self.start_dttm = None
        self.end_dttm = None

    def start_recording(self, output_path: str, start_dttm: dt.datetime, end_dttm: Optional[dt.datetime] = None):
        self.writer = cv2.VideoWriter(output_path, self.fourcc, self.fps, (self.width, self.height))
        self.start_dttm = start_dttm
        self.end_dttm = end_dttm

    def heartbeat(self):
        if not self.cap.isOpened():
            return

        ret, frame = self.cap.read()
        if not ret:
            return

        cv2.imshow('frame', frame)

        if self.writer:
            wait_for_time(self.start_dttm)
            if self.end_dttm and dt.datetime.now() > self.end_dttm:
                self.reset()
                return

            self.writer.write(frame)

        cv2.waitKey(1)

    def reset(self):
        if self.writer:
            self.writer.release()
        self.start_dttm = None
        self.end_dttm = None
        self.writer = None

    def __enter__(self):
        self.cap.start()

    def __exit__(self, *args):
        # Release everything if job is finished
        self.cap.stop()
        self.cap.cap.release()
        if self.writer:
            self.writer.release()
        cv2.destroyAllWindows()


class VideoCaptureAsync:
    """
    SOURCE A: https://github.com/gilbertfrancois/video-capture-async
    SOURCE B: https://github.com/alievk/avatarify/
    """
    WARMUP_TIMEOUT = 10.0

    def __init__(self, src=0, width=640, height=480, fps=60):
        self.src = src

        self.cap = cv2.VideoCapture(self.src)
        if not self.cap.isOpened():
            raise RuntimeError("Cannot open camera")

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.cap.set(cv2.CAP_PROP_FPS, fps)
        self.grabbed, self.frame = self.cap.read()
        self.started = False
        self.read_lock = threading.Lock()
        self.thread = None

    def set(self, var1, var2):
        self.cap.set(var1, var2)

    def get(self, var):
        return self.cap.get(var)

    def isOpened(self):  # noqa
        return self.cap.isOpened()

    def start(self):
        if self.started:
            print('[!] Asynchronous video capturing has already been started.')
            return None
        self.started = True
        self.thread = threading.Thread(target=self.update, args=(), daemon=True)
        self.thread.start()

        # (warmup) wait for the first successfully grabbed frame
        warmup_start_time = time.time()
        while not self.grabbed:
            warmup_elapsed_time = (time.time() - warmup_start_time)
            if warmup_elapsed_time > self.__class__.WARMUP_TIMEOUT:
                raise RuntimeError(
                    "Failed to succesfully grab frame from the camera "
                    f"(timeout={self.__class__.WARMUP_TIMEOUT}s). Try to restart."
                )

            time.sleep(0.5)

        return self

    def update(self):
        while self.started:
            grabbed, frame = self.cap.read()
            with self.read_lock:
                self.grabbed = grabbed
                self.frame = frame

    def read(self):
        with self.read_lock:
            frame = self.frame.copy()
            grabbed = self.grabbed
        return grabbed, frame

    def stop(self):
        self.started = False
        self.thread.join()

    def __exit__(self, exec_type, exc_value, traceback):
        self.cap.release()
