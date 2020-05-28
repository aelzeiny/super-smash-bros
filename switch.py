import sdl2
import sdl2.ext
import struct
import binascii
import serial
import datetime as dt
import pickle

from smash_utils import wait_for_time
from collections import namedtuple


class ControllerStateTime (namedtuple('ControllerStateTime', ('message', 'delta'))):
    """
    Serializable object responsible for recording a particular input at a particular timestamp
    """
    def formatted_message(self):
        return binascii.hexlify(self.message) + b'\n'

    def serialize(self):
        return binascii.hexlify(pickle.dumps(self))

    @staticmethod
    def deserialize(self):
        return pickle.loads(binascii.unhexlify(self))


class SwitchRelay:
    def __init__(self, controller_id: int, **kwargs):
        self.ser = serial.Serial(**kwargs)

        sdl2.SDL_Init(sdl2.SDL_INIT_GAMECONTROLLER)
        self.controller = sdl2.SDL_GameControllerOpen(int(controller_id))
        try:
            print('Using "{:s}" for input.'.format(
                sdl2.SDL_JoystickName(sdl2.SDL_GameControllerGetJoystick(self.controller)).decode('utf8')
            ))
        except AttributeError:
            print(f'Using controller {controller_id} for input.')

        self.input_stack = []
        self.recording = None
        self.start_dttm = None
        self.prev_msg_stamp = None

    def __enter__(self):
        pass

    def __exit__(self, *args):
        self.ser.close()
        if self.recording:
            self.recording.flush()
            self.recording.close()

    def heartbeat(self):
        msg_stamp = next(self.input_stack)
        # This this input has aleady been entered, then don't spam the stack
        if self.prev_msg_stamp and msg_stamp.message == self.prev_msg_stamp.message:
            return

        # Wait for the correct amount of time to pass before performing an input
        wait_for_time(self.start_dttm + dt.timedelta(seconds=msg_stamp.delta))
        self.ser.write(msg_stamp.formatted_message())

        # record result if needed
        if self.recording is not None:
            self.recording.write(msg_stamp.serialize() + b'\n')

        self.prev_msg_stamp = msg_stamp

    def playback_recording(self, path: str, start_dttm: dt.datetime):
        self.start_dttm = start_dttm
        wait_for_time(start_dttm)

        playback_iter = self.replay_states(path)
        self.input_stack = playback_iter

    def start_recording(self, path: str, start_dttm: dt.datetime):
        self.start_dttm = start_dttm
        wait_for_time(start_dttm)

        live = self.controller_states()
        self.recording = open(path)
        self.input_stack = live

    def controller_states(self):
        cls = self.__class__
        controller = self.controller
        while True:
            elaped_time = dt.datetime.now().timestamp() - self.start_dttm
            buttons = sum((
                sdl2.SDL_GameControllerGetButton(controller, b) << n for n, b in enumerate(cls.buttonmapping)
            ))
            buttons |= (
                           abs(sdl2.SDL_GameControllerGetAxis(controller,  sdl2.SDL_CONTROLLER_AXIS_TRIGGERLEFT)) >
                           cls.trigger_deadzone
                       ) << 6
            buttons |= (
                            abs(sdl2.SDL_GameControllerGetAxis(controller, sdl2.SDL_CONTROLLER_AXIS_TRIGGERRIGHT)) >
                            cls.trigger_deadzone
                       ) << 7

            hat = cls.hatcodes[
                sum([sdl2.SDL_GameControllerGetButton(controller, b) << n for n, b in enumerate(cls.hatmapping)])
            ]

            rawaxis = [
                sdl2.SDL_GameControllerGetAxis(controller, n) for n in cls.axismapping
            ]
            axis = [((0 if abs(x) < cls.axis_deadzone else x) >> 8) + 128 for x in rawaxis]

            rawbytes = struct.pack('>BHBBBB', hat, buttons, *axis)
            message_stamp = ControllerStateTime(rawbytes, elaped_time)
            yield message_stamp

    @staticmethod
    def replay_states(filename):
        with open(filename, 'rb') as replay:
            for line in replay.readlines():
                # remove new-line character at end of line, and feed it into deserializer
                yield ControllerStateTime.deserialize(line[:-1])


    buttonmapping = [
        sdl2.SDL_CONTROLLER_BUTTON_X,  # Y
        sdl2.SDL_CONTROLLER_BUTTON_A,  # B
        sdl2.SDL_CONTROLLER_BUTTON_B,  # A
        sdl2.SDL_CONTROLLER_BUTTON_Y,  # X
        sdl2.SDL_CONTROLLER_BUTTON_LEFTSHOULDER,  # L
        sdl2.SDL_CONTROLLER_BUTTON_RIGHTSHOULDER,  # R
        sdl2.SDL_CONTROLLER_BUTTON_INVALID,  # ZL
        sdl2.SDL_CONTROLLER_BUTTON_INVALID,  # ZR
        sdl2.SDL_CONTROLLER_BUTTON_BACK,  # SELECT
        sdl2.SDL_CONTROLLER_BUTTON_START,  # START
        sdl2.SDL_CONTROLLER_BUTTON_LEFTSTICK,  # LCLICK
        sdl2.SDL_CONTROLLER_BUTTON_RIGHTSTICK,  # RCLICK
        sdl2.SDL_CONTROLLER_BUTTON_GUIDE,  # HOME
        sdl2.SDL_CONTROLLER_BUTTON_INVALID,  # CAPTURE
    ]

    axismapping = [
        sdl2.SDL_CONTROLLER_AXIS_LEFTX,  # LX
        sdl2.SDL_CONTROLLER_AXIS_LEFTY,  # LY
        sdl2.SDL_CONTROLLER_AXIS_RIGHTX,  # RX
        sdl2.SDL_CONTROLLER_AXIS_RIGHTY,  # RY
    ]

    hatmapping = [
        sdl2.SDL_CONTROLLER_BUTTON_DPAD_UP,  # UP
        sdl2.SDL_CONTROLLER_BUTTON_DPAD_RIGHT,  # RIGHT
        sdl2.SDL_CONTROLLER_BUTTON_DPAD_DOWN,  # DOWN
        sdl2.SDL_CONTROLLER_BUTTON_DPAD_LEFT,  # LEFT
    ]

    hatcodes = [8, 0, 2, 1, 4, 8, 3, 8, 6, 7, 8, 8, 5, 8, 8]

    axis_deadzone = 1000
    trigger_deadzone = 0

    @classmethod
    def get_macro_duration(cls, input_macro_path):
        return sum([state.delta for state in cls.replay_states(input_macro_path)])
