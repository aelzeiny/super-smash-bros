import datetime as dt
from smashbros_controller import ControllerManager, reset_practice
from screen_manager import start_screencap, overlay, trim_video, lengthen_video, adjust_video
import util
import sys
import bridge
import time
import sdl2


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
        start = dt.datetime.now().timestamp()
        while True:
            sdl2.ext.get_events()
            delta = dt.datetime.now().timestamp() - start
            curr_input = [b for b in bridge.buttonmapping + bridge.hatmapping
                          if sdl2.SDL_GameControllerGetButton(self.controller, b)]
            if not curr_input:
                self.buffer = 0
                continue
            if self.last_input != curr_input:
                self.buffer = 0
            if self.buffer > self.__class__.MAX_BUFFER:
                self.buffer = 0
                return curr_input
            self.buffer += delta
            self.last_input = curr_input
            time.sleep(0.005)

    def choose_from_list(self, arr):
        cli = CliList(arr)
        cli.render()
        while True:
            msg = self.get_input()
            if sdl2.SDL_CONTROLLER_BUTTON_DPAD_DOWN in msg:
                cli.increment()
            elif sdl2.SDL_CONTROLLER_BUTTON_DPAD_UP in msg:
                cli.decrement()
            elif sdl2.SDL_CONTROLLER_BUTTON_START in msg or sdl2.SDL_CONTROLLER_BUTTON_B:
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


def record(character, move):
    filename = f'/home/awkii/macros/{character}/{move}'
    controller = ControllerManager(filename)
    controller.with_controller()
    controller_and_video(controller, filename)


def playback(character, move):
    filename = f'/home/awkii/macros/{character}/{move}'

    for i in range(2):
        print('TRY #' + str(i + 1))
        controller = ControllerManager()
        controller.with_action(reset_practice().play())
        controller.with_playback(filename)
        screen_filename = filename + str(i + 1)

        controller_and_video(controller, screen_filename)

    overlay(filename + '1', filename + '2')


def main():
    record('test', 'sample')
    playback('test', 'sample')
    # overlay('/home/awkii/macros/test/sample1', '/home/awkii/macros/test/sample2')
    # lengthen_video('/home/awkii/macros/test/utilt.avi', 3.5)
    # characters = constants.get_characters()
    # for idx, c in enumerate(characters):
    #     print(f'{idx}: {c}')
    # character_idx = int(input('Select Character: '))
    # print(characters[character_idx])
    # controller = CliController()
    # moves = constants.move_list()
    # is_running = True
    # while is_running:
    #     try:
    #         move_idx = controller.choose_from_list(moves)
    #         print('\n', moves[move_idx])
    #         playback_idx = controller.choose_from_list(['record', 'playback', 'back'])
    #         print('\n', playback_idx)
    #         if playback_idx == 0:
    #             record(characters[character_idx], moves[move_idx])
    #         elif playback_idx == 1:
    #             playback(characters[character_idx], moves[move_idx])
    #         else:
    #             raise BackException
    #     except BackException:
    #         pass


if __name__ == '__main__':
    main()
