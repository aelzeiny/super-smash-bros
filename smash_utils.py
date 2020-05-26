import os
import subprocess as sp
import colorama
DEVNULL = open(os.devnull, 'wb')


CHARACTERS = [
    'Mario', 'Luigi', 'Peach', 'Bowser', 'Dr. Mario', 'Rosalina & Luma', 'Bowser Jr.', 'Yoshi',
    'Donkey Kong', 'Diddy Kong', 'Link', 'Zelda', 'Samus', 'Sheik', 'Young Link', 'Ganondorf',
    'Toon Link', 'Zero Suit Samus', 'Kirby', 'Meta Knight', 'King Dedede', 'Fox', 'Falco', 'Wolf',
    'Jigglypuff', 'Pichu', 'Mewtwo', 'Pokémon Trainer', 'Greninja', 'Captain Falcon', 'Ness',
    'Lucas', 'Ice Climbers', 'Marth', 'Roy', 'Lucinaε', 'Robin', 'Corrin', 'Mr. Game & Watch', 'Pit',
    'Palutena', 'Dark Pitε', 'Olimar', 'R.O.B.', 'Villager', 'Wii Fit Trainer', 'Little Mac', 'Shulk',
    'Duck Hunt', 'Sonic', 'Mega Man', 'Pac-Man', 'Ryu', 'Cloud', 'Bayonetta', 'Mii Brawler SSBU.png',
    'Mii Swordfighter', 'Mii Gunner', 'King K. Rool', 'Ridley', 'Dark Samusε', 'Incineroar', 'Chromε',
    'Inkling', 'Kenε', 'Simon', 'Richter', 'Lucario', 'Ike', 'Wario', 'Snake', 'Mii Brawler', 'Daisyε',
    'Isabelle', 'Piranha Plant (DLC)', 'Byleth (DLC)', 'ARMS character (DLC)', 'Hero (DLC)',
    'Banjo & Kazooie (DLC)', 'Terry (DLC)', 'Joker (DLC)'
]


MOVE_LIST = [
    'fair', 'bair', 'dair', 'uair', 'nair',
    'ftilt', 'dtilt', 'utilt', 'jab',
    'fsmash', 'dsmash', 'usmash',
    'sb', 'ub', 'db', 'nb',
    'walk', 'run', 'dash-attack', 'grab',
    'whoa', 'ledge', 'shield', 'roll'
]


def subprocess_call(cmd: str, errorprint=True):
    """ Executes the given subprocess command. """
    print(f'Running:\n>>> "+ {cmd}')

    popen_params = {"stdout": DEVNULL,
                    "stderr": sp.PIPE,
                    "stdin": DEVNULL}

    if os.name == "nt":
        popen_params["creationflags"] = 0x08000000

    proc = sp.Popen(cmd, shell=True, **popen_params)

    out, err = proc.communicate()  # proc.wait()
    proc.stderr.close()

    if proc.returncode:
        if errorprint:
            print('Command returned an error')
        raise IOError(err.decode('utf8'))
    else:
        print('Command successful')

    del proc


CURSOR_UP_ONE = '\x1b[1A'
ERASE_LINE = '\x1b[2K'


class ConsoleList:
    def __init__(self, description: str, elements: list):
        self.description = description
        self.elements = elements
        self.idx = 0
        colorama.init()

    def set_index(self, idx):
        self.idx = idx

    def display(self):
        print(colorama.ansi.clear_screen())
        print(self.description)
        for idx, el in self.elements:
            if idx == self.idx:
                print(colorama.Fore.CYAN)
                print(f'>> {el}')
                print(colorama.Style.RESET_ALL)
            else:
                print(el)
