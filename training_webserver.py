import os
import orchestrator
import smash_utils

from pathlib import Path
from flask import Flask, render_template, jsonify
from smash_utils import MOVE_LIST
import datetime as dt

app = Flask(__name__, static_folder='./frontend/static', template_folder='./frontend')


CHARACTERS = [
    os.path.basename(str(c)[:-len('.png')])
    for c in sorted(Path('./frontend/static/characters').iterdir(), key=os.path.getmtime)
    if str(c).endswith('.png')
]


@app.route('/')
def homepage():
    return render_template("characters.html", characters=CHARACTERS)


@app.route('/character/<char>', methods=['GET'])
def character_select(char):
    move_list = {m: os.path.exists(smash_utils.get_macro_file(char, m)) for m in MOVE_LIST}
    return render_template('moves.html', character=char, moves=move_list)


@app.route('/<char>/<move>/record', methods=['POST'])
def start_recording_and_macro(char, move):
    # remove all recorded files for this macro
    smash_utils.ensure_directory(char)
    for file in smash_utils.list_recording_files(char, move):
        os.remove(file)
    # start recording
    start_dttm = dt.datetime.now() + dt.timedelta(seconds=3)
    orchestrator.relay_record(
        smash_utils.get_macro_file(char, move),
        start_dttm
    )
    orchestrator.recorder_record(
        smash_utils.get_recording_file(char, move, str(dt.datetime.now().timestamp())),
        start_dttm
    )
    smash_utils.wait_for_time(start_dttm)
    return '', 204


@app.route('/<char>/<move>/playback', methods=['POST'])
def start_playback(char, move):
    start_dttm = dt.datetime.now() + dt.timedelta(seconds=3)
    end_dttm = orchestrator.relay_playback(
        smash_utils.get_macro_file(char, move),
        start_dttm
    )
    orchestrator.recorder_record(
        smash_utils.get_recording_file(char, move, str(start_dttm.timestamp())),
        start_dttm,
        end_dttm
    )
    smash_utils.wait_for_time(start_dttm)
    return jsonify({'wait': (end_dttm - start_dttm).total_seconds()})


@app.route('/stop', methods=['POST'])
def stop_recording_and_macro():
    orchestrator.relay_stop()
    orchestrator.recorder_stop()
    return '', 204


if __name__ == "__main__":
    try:
        orchestrator.start_processes()
        app.run(host='0.0.0.0')
    finally:
        orchestrator.close()
