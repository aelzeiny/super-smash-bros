from typing import Optional

import cv2
import datetime as dt

from smash_utils import wait_for_time


class WebCamRecorder:
    def __init__(self, capture_device: int = 0, fourcc: str = 'MJPG', fps: int = 59.9999):
        self.cap = cv2.VideoCapture(capture_device)

        self.fourcc = cv2.VideoWriter_fourcc(*fourcc)
        self.width = int(self.cap.get(3))
        self.height = int(self.cap.get(4))
        self.writer = None

        self.start_dttm = None
        self.end_dttm = None

        self.fps = fps

    def start_recording(self, output_path: str, start_dttm: dt.datetime, end_dttm: Optional[dt.datetime] = None):
        self.writer = cv2.VideoWriter(output_path, self.fourcc, self.fps, (self.width, self.height))
        self.start_dttm = start_dttm
        self.end_dttm = end_dttm

    def heartbeat(self):
        if not self.cap.isOpened() or not self.writer:
            return

        print('heartbeat1')
        wait_for_time(self.start_dttm)
        print('heartbeat2')
        if self.end_dttm and dt.datetime.now() > self.end_dttm:
            self.reset()
            return
        print('heartbeat3')

        ret, frame = self.cap.read()
        if not ret:
            return

        print('heartbeat4')
        cv2.imshow('frame', frame)
        self.writer.write(frame)
        cv2.waitKey(1)

    def reset(self):
        if self.writer:
            self.writer.release()
        self.start_dttm = None
        self.end_dttm = None
        self.writer = None

    def __enter__(self):
        pass

    def __exit__(self, *args):
        # Release everything if job is finished
        self.cap.release()
        if self.writer:
            self.writer.release()
        cv2.destroyAllWindows()
