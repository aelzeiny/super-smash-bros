from typing import Optional

import cv2
import datetime as dt

from smash_utils import wait_for_time


class WebCamRecorder:
    def __init__(self, capture_device: int = 0, width: int = 960, height: int = 720, fourcc: str = 'mp4v',
                 fps: int = 59.9999):
        self.width = width
        self.height = height
        self.fps = fps

        self.fourcc = cv2.VideoWriter_fourcc(*fourcc)
        self.start_dttm = None
        self.end_dttm = None
        self.cap = cv2.VideoCapture(capture_device)
        self.writer = None

    def start_recording(self, output_path: str, start_dttm: dt.datetime, end_dttm: Optional[dt.datetime] = None):
        self.writer = cv2.VideoWriter(output_path, self.fourcc, self.fps, (self.width, self.height))
        self.start_dttm = start_dttm
        self.end_dttm = end_dttm

    def heartbeat(self):
        if not self.cap.isOpened() or not self.writer:
            return

        wait_for_time(self.start_dttm)
        if dt.datetime.now() > self.end_dttm:
            self.reset()
            return

        ret, frame = self.cap.read()
        if not ret:
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
        pass

    def __exit__(self, *args):
        # Release everything if job is finished
        self.cap.release()
        if self.writer:
            self.writer.release()
        cv2.destroyAllWindows()
