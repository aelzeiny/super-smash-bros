import os

import cv2
import threading
import datetime as dt

from util import subprocess_call


def adjust_video(filename, adj_secs):
    if not filename.endswith('.avi'):
        filename += '.avi'
    if adj_secs < 0:
        lengthen_video(filename, -adj_secs)
    elif adj_secs > 0:
        trim_video(filename, adj_secs)


def trim_video(filename, trim_secs):
    print(f'Trimming Video {trim_secs} secs')
    subprocess_call(f"ffmpeg -y -i '{filename}' -ss {trim_secs} -vcodec copy -acodec copy '{filename}'")


def lengthen_video(filename, trim_secs):
    file, ext = os.path.splitext(filename)
    dir = os.path.dirname(os.path.abspath(filename))
    blank_path = os.path.join(dir, 'blank' + ext)
    copy_path = os.path.join(dir, 'copy' + ext)
    print(f'Extending Video {trim_secs} secs')
    print('Cloning some frames')
    subprocess_call(f"ffmpeg -y -ss 0 -i '{filename}' -c copy -t {trim_secs} '{blank_path}'")
    print('Adding blank frames to original')
    subprocess_call(f'ffmpeg -y -i "concat:{blank_path}|{filename}" -c copy {copy_path}')
    os.rename(copy_path, filename)
    os.remove(blank_path)


def overlay(filename_a, filename_b):
    cap_a = cv2.VideoCapture(filename_a + '.avi')
    cap_b = cv2.VideoCapture(filename_b + '.avi')

    while cap_a.isOpened() and cap_b.isOpened():
        ret_a, frame_a = cap_a.read()
        ret_b, frame_b = cap_b.read()
        if not ret_a or not ret_b:
            break
        added = cv2.addWeighted(frame_a, 0.5, frame_b, 0.5, 0)
        cv2.imshow('frame', added)
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

    cap_a.release()
    cap_b.release()


def start_screencap(output_filename, should_kill_callback, width=1024, height=768, fps=60):
    # Create a VideoCapture object
    cap = cv2.VideoCapture(0)
    if width:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    if height:
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    if fps:
        cap.set(cv2.CAP_PROP_FPS, fps)

    # Default resolutions of the frame are obtained.The default resolutions are system dependent.
    # We convert the resolutions from float to integer.
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    # Define the codec and create VideoWriter object.The output is stored in 'outpy.avi' file.
    out = cv2.VideoWriter(f'{output_filename}.avi',
                          cv2.VideoWriter_fourcc(*'MJPG'),
                          int(cap.get(cv2.CAP_PROP_FPS)),
                          (frame_width, frame_height))

    start_dttm = None

    while True:
        ret, frame = cap.read()
        if ret:
            if not start_dttm:
                start_dttm = dt.datetime.now().timestamp()
            # Write the frame into the file 'output.avi'
            out.write(frame)
            # Display the resulting frame
            cv2.imshow('frame', frame)
            # Press Q on keyboard to stop recording
            if cv2.waitKey(1) & 0xFF == ord('q') or should_kill_callback():
                break
        # Break the loop
        else:
            break

            # When everything done, release the video capture and video write objects
    cap.release()
    out.release()
    return start_dttm


class ScreenManagerAsync:
    def __init__(self, width=None, height=None, fps=None):
        # Create a VideoCapture object
        self.cap = VideoCaptureAsync(width=width, height=height, fps=fps)
        self.out = None

    def start(self):
        self.cap.start()

    def close(self):
        # When everything done, release the video capture and video write objects
        self.cap.stop()
        if self.out:
            self.out.release()
        # Closes all the frames
        cv2.destroyAllWindows()

    def update(self, message):
        ret, frame = self.cap.read()
        if not ret:
            raise ValueError(ret)
        if self.out:
            self.out.write(frame)
        fps = self.cap.get(cv2.CAP_PROP_FPS)
        cv2.putText(
            frame,
            f'{fps} - {message}',
            (0, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=1,
            color=(0, 0, 255),
            thickness=3
        )
        if self.out:
            self.out.write(frame)
        # Display the resulting frame
        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            return

    def record(self, filename):
        # Define the codec and create VideoWriter object.The output is stored in 'outpy.avi' file.
        self.out = cv2.VideoWriter(
            f'{filename}.mp4',
            cv2.VideoWriter_fourcc('m', 'p', '4', 'v'),
            10,
            (
                int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            )
        )


class VideoCaptureAsync:
    def __init__(self, src=0, fps=None, width=None, height=None):
        self.src = src
        self.cap = cv2.VideoCapture(self.src)
        if width and height:
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        if fps:
            self.cap.set(cv2.CAP_PROP_FPS, fps)
        self.grabbed, self.frame = self.cap.read()
        self.started = False
        self.read_lock = threading.Lock()

    def set(self, var1, var2):
        self.cap.set(var1, var2)

    def get(self, var1):
        return self.cap.get(var1)

    def start(self):
        if self.started:
            print('[!] Asynchroneous video capturing has already been started.')
            return None
        self.started = True
        self.thread = threading.Thread(target=self.update, args=())
        self.thread.start()
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
