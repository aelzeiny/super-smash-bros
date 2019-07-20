import os
import cv2

from smashbros_controller import ControllerManager, reset_practice
from screen_manager import start_screencap, overlay, adjust_video
import util
import sys
import bridge
import time
import sdl2


def get_path(character, move):
    char_name = ''.join(c for c in character.lower() if c.isalnum())
    return f'/home/awkii/macros/{char_name}/{move.lower()}'


class CliList:
    def __init__(self, arr):
        self.list = arr
        self.index = 0
        self.first_render = True

    def increment(self):
        self.index = (self.index + 1) % len(self.list)

    def decrement(self):
        self.index = (self.index - 1) if self.index > 0 else len(self.list) - 1

    def render(self):
        if not self.first_render:
            self.delete_lines(len(self.list))

        for idx, m in enumerate(self.list):
            formatting = ''
            if idx == self.index:
                formatting = '\u001b[47m\u001b[30m'
            print(formatting + f'{idx}: {m}' + '\u001b[0m')
        self.first_render = False

    @staticmethod
    def delete_lines(count):
        # Draw the progress bars
        sys.stdout.write(u"\u001b[1000D")  # Move left
        sys.stdout.write('\033[K')
        sys.stdout.write(u"\u001b[" + str(count) + "A")  # Move up


class CliController:
    MAX_BUFFER = 3  # Hold time for buttons in terms of seconds

    def __init__(self, controller_id='0'):
        sdl2.SDL_Init(sdl2.SDL_INIT_GAMECONTROLLER)
        self.controller = bridge.get_controller(controller_id)
        self.last_input = []
        self.buffer = 0

    def get_input(self):
        while True:
            for e in sdl2.ext.get_events():
                if e.type == sdl2.SDL_CONTROLLERBUTTONDOWN:
                    return e.jbutton.button
            time.sleep(0.05)

    @staticmethod
    def choose_from_list(arr):
        controller = CliController()
        cli = CliList(arr)
        cli.render()
        while True:
            msg = controller.get_input()
            if sdl2.SDL_CONTROLLER_BUTTON_DPAD_DOWN == msg:
                cli.increment()
            elif sdl2.SDL_CONTROLLER_BUTTON_DPAD_UP == msg:
                cli.decrement()
            elif sdl2.SDL_CONTROLLER_BUTTON_START == msg or sdl2.SDL_CONTROLLER_BUTTON_B == msg:
                return cli.index
            cli.render()


class BackException(Exception):
    pass


def controller_and_video(controller, video_savepath):
    def should_kill_callback():
        return not controller.thread.is_alive()

    print('starting controller')
    controller_start = controller.start()

    print('starting screencap')
    screen_start = start_screencap(video_savepath, should_kill_callback)

    print('joining threads')
    controller.stop()
    adjust_video(video_savepath, controller_start.value - screen_start)
    cv2.destroyWindow(video_savepath)
    cv2.waitKey(1)


def record(character, move):
    filename = get_path(character, move)
    controller = ControllerManager(filename)
    controller.with_controller()
    controller_and_video(controller, filename)


def playback(character, move):
    filename = get_path(character, move)

    for i in range(2):
        print('TRY #' + str(i + 1))
        controller = ControllerManager()
        controller.with_action(reset_practice().play())
        controller.with_playback(filename)
        screen_filename = filename + str(i + 1)

        controller_and_video(controller, screen_filename)

    overlay(filename + '1', filename + '2')


def main():
    characters = util.get_characters()
    for idx, c in enumerate(characters):
        print(f'{idx}: {c}')
    character_idx = int(input('Select Character: '))
    selected_character = characters[character_idx]
    print(selected_character)
    character_dir = get_path(selected_character, '')
    is_running = True
    while is_running:
        try:
            try:
                curr_moves = set([c[:-4] for c in os.listdir(character_dir) if c.endswith('.map')])
            except FileNotFoundError:
                os.mkdir(character_dir)
                curr_moves = []
            moves = [m + '*' if m in curr_moves else m for m in util.move_list()]
            move_idx = CliController.choose_from_list(moves)
            selected_move = moves[move_idx].rstrip('*')
            print('\n', moves[move_idx])
            playback_idx = CliController.choose_from_list(['record', 'playback', 'back'])
            print('\n', playback_idx)
            if playback_idx == 0:
                record(selected_character, selected_move)
                time.sleep(1)
            elif playback_idx == 1:
                playback(selected_character, selected_move)
                time.sleep(1)
            else:
                raise BackException
        except BackException:
            pass


if __name__ == '__main__':
    main()
