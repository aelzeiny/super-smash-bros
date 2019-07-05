import cv2
import threading


class ScreenManager:
    def __init__(self):
        # Create a VideoCapture object
        self.cap = VideoCaptureAsync()
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
        # Display the resulting frame
        cv2.imshow('frame', frame)
        cv2.waitKey(1) & 0xFF

    def record(self, filename):
        # Define the codec and create VideoWriter object.The output is stored in 'outpy.avi' file.
        self.out = cv2.VideoWriter(
            f'{filename}.mp4',
            cv2.VideoWriter_fourcc('m', 'p', '4', 'v'),
            10,
            (self.cap.get(cv2.CAP_PROP_FRAME_WIDTH), cv2.CAP_PROP_FRAME_HEIGH)
        )


class VideoCaptureAsync:
    def __init__(self, src=0, width=None, height=None):
        self.src = src
        self.cap = cv2.VideoCapture(self.src)
        if width and height:
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
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