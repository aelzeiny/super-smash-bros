from switch import SwitchRelay
import datetime as dt
from multiprocessing import Queue, Process
from typing import Optional, Tuple
from smash_utils import read_relay_config


relay_q: Optional[Queue] = None
recorder_q: Optional[Queue] = None
relay_process: Optional[Process] = None
recorder_process: Optional[Process] = None


QUIT = 0
RECORD = 1
PLAYBACK = 2
STOP = 3


def start_processes():
    global relay_process, relay_q, recorder_process, recorder_q

    def _start_process(func) -> Tuple[Process, Queue]:
        queue = Queue()
        process = Process(target=func, args=(queue,))
        return process, queue

    relay_process, relay_q = _start_process(start_relay_process)
    recorder_process, recorder_q = _start_process(start_recorder_process)


def close():
    relay_q.put(dict(
        command=QUIT
    ))
    recorder_q.put(dict(
        command=QUIT
    ))
    relay_process.join()
    recorder_process.join()


def start_relay_process(queue):
    relay_config = read_relay_config()
    # relay = SwitchRelay(
    #     bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE,
    #     stopbits=serial.STOPBITS_ONE, timeout=None, **relay_config
    # )

    while True:
        if not queue.empty():
            cmd = queue.get_nowait()
            print('>>>', cmd)
            if cmd['command'] == QUIT:
                break
            elif cmd['command'] == RECORD:
                start_dttm = dt.datetime.fromtimestamp(cmd['start_dttm'])
                # relay.start_recording(cmd['path'], start_dttm)
            elif cmd['command'] == PLAYBACK:
                start_dttm = dt.datetime.fromtimestamp(cmd['start_dttm'])
                # relay.playback_recording(cmd['path'], start_dttm)
            elif cmd['command'] == STOP:
                pass
                # relay.reset()

        # relay.heartbeat()


def start_recorder_process(queue):
    while True:
        if not queue.empty():
            cmd = queue.get_nowait()
            print('>>>', cmd)
            if cmd['command'] == QUIT:
                break


# region RELAY ACTIONS
def relay_record(output_macro_path: str, start_dttm: dt.datetime):
    relay_q.put(dict(
        command=RECORD,
        start_dttm=start_dttm,
        path=output_macro_path
    ))


def relay_playback(input_macro_path: str, start_dttm: dt.datetime) -> dt.datetime:
    """Starts controller playback & returns the end_dttm of playback"""
    duration = SwitchRelay.get_macro_duration(input_macro_path)
    relay_q.put(dict(
        command=PLAYBACK,
        path=input_macro_path,
        start_dttm=start_dttm
    ))
    return start_dttm + dt.timedelta(seconds=duration)


def relay_stop():
    relay_q.put(dict(
        command=STOP
    ))
# endregion


# region RECORDER ACTIONS
def recorder_record(output_macro_path: str, start_dttm: dt.datetime, end_dttm: Optional[dt.datetime] = None):
    recorder_q.put(dict(
        command=RECORD,
        path=output_macro_path,
        start_dttm=start_dttm,
    ))


def recorder_stop():
    recorder_q.put(dict(
        command=STOP
    ))
# endregion
