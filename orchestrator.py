from pathlib import Path

import sdl2
import serial

from switch import SwitchRelay
import os
import datetime as dt
import json as json_util
from multiprocessing import Pipe, Process

from smash_utils import CHARACTERS, MOVE_LIST, ConsoleList
from webcam_recorder import WebCamRecorder


def get_macro_file(character: str, move: str) -> str:
    return f'./macros/{character}/{move}.macro'


def get_recording_file(character: str, move: str, tag=0) -> str:
    return f'./macros/{character}/{move}_{str(tag).zfill(2)}.mp4'


def select_menu_with_controller(desc, arr):
    console_list = ConsoleList(desc, arr)
    console_list.display()

    while True:
        for event in sdl2.ext.get_events():
            if event.type == sdl2.SDL_CONTROLLERBUTTONDOWN:
                if event.jbutton.button == sdl2.SDL_CONTROLLER_BUTTON_DPAD_DOWN:
                    console_list.set_index(max(0, console_list.idx - 1))
                elif event.jbutton.button == sdl2.SDL_CONTROLLER_BUTTON_DPAD_UP:
                    console_list.set_index(max(len(arr) - 1, console_list.idx + 1))
                elif event.jbutton.button == sdl2.SDL_CONTROLLER_BUTTON_B:
                    return arr[console_list.idx]
                console_list.display()


def select_character():
    return select_menu_with_controller('Select Character: ', CHARACTERS)


def select_move():
    return select_menu_with_controller('Select Move: ', MOVE_LIST)


def select_should_record(character, move):
    if not os.path.exists(get_macro_file(character, move)):
        return True
    response = select_menu_with_controller('Overwrite or play: ', ('Record', 'Playback'))
    return response == 'Record'


def read_relay_config():
    config_path = str(Path(__file__).parent() / 'config.json')
    return json_util.loads(config_path)


QUIT = 0
RECORD = 1
PLAYBACK = 2
STOP = 3


def start_relay_process(pipe):
    relay_config = read_relay_config()
    relay = SwitchRelay(
        bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE, timeout=None, **relay_config
    )
    while True:
        json = pipe.recv()
        if json['command'] == QUIT:
            break
        elif json['command'] == RECORD:
            start_dttm = dt.datetime.fromtimestamp(json['start_dttm'])
            relay.start_recording(json['path'], start_dttm)
        elif json['command'] == PLAYBACK:
            start_dttm = dt.datetime.fromtimestamp(json['start_dttm'])
            relay.playback_recording(json['path'], start_dttm)
        elif json['command'] == STOP:
            relay.reset()
        relay.heartbeat()


def start_recorder_process(pipe):
    recorder = WebCamRecorder()
    while True:
        json = pipe.recv()
        recorder.heatbeat()


if __name__ == '__main__':
    controller_parent_conn, controller_child_conn = Pipe()
    controller_process = Process(target=start_relay_process, args=(controller_child_conn, ))

    recorder_parent_conn, recorder_child_conn = Pipe()
    recorder_process = Process(target=start_recorder_process, args=(recorder_child_conn, ))

    controller_process.start()
    recorder_process.start()

    character_str = select_character()
    move_str = select_move(character_str)
    should_record = select_should_record()
    start_dttm = dt.datetime.now() + dt.timedelta(seconds=3)
    if should_record:
        controller_parent_conn.send(dict(
            command=RECORD,
            start_dttm=start_dttm,
            path=get_macro_file(character_str, move_str)
        ))
        recorder_parent_conn.send(dict(
            command=RECORD,
            start_dttm=start_dttm,
            path=get_recording_file(character_str, move_str, tag=0)
        ))
    else:
        controller_parent_conn.send(dict(
            command=PLAYBACK,
            start_dttm=start_dttm,
            path=get_macro_file(character_str, move_str)
        ))
        recorder_parent_conn.send(dict(
            command=RECORD,
            start_dttm=start_dttm,
            path=get_recording_file(character_str, move_str, tag=1)
        ))
        is_done = controller_parent_conn.recv()
        recorder_parent_conn.send(dict(
            command=STOP
        ))
