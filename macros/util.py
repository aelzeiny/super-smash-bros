import os
import subprocess as sp
DEVNULL = open(os.devnull, 'wb')


def move_list():
    return [
        'fair', 'bair', 'dair', 'uair', 'nair',
        'ftilt', 'dtilt', 'utilt', 'jab',
        'fsmash', 'dsmash', 'usmash',
        'sb', 'ub', 'db', 'nb',
        'walk', 'run', 'dash-attack', 'grab',
        'whoa', 'ledge', 'shield', 'roll'
    ]


def get_characters():
    return [
        "MARIO",
        "DONKEY KONG",
        "LINK",
        "SAMUS",
        "DARK SAMUS",
        "YOSHI",
        "KIRBY",
        "FOX",
        "PIKACHU",
        "LUIGI",
        "NESS",
        "CAPTAIN",
        "FALCON",
        "JIGGLYPUFF",
        "PEACH",
        "DAISY",
        "BOWSER",
        "ICE CLIMBERS",
        "SHEIK",
        "ZELDA",
        "DR. MARIO",
        "PICHU",
        "FALCO",
        "MARTH",
        "LUCINA",
        "YOUNG LINK",
        "GANONDORF",
        "MEWTWO",
        "ROY",
        "CHROM",
        "MR. GAME",
        "& WATCH",
        "META KNIGHT",
        "PIT",
        "DARK PIT",
        "ZERO SUIT SAMUS",
        "WARIO",
        "SNAKE",
        "IKE",
        "POKÉMON",
        "TRAINER",
        "DIDDY KONG",
        "LUCAS",
        "SONIC",
        "KING DEDEDE",
        "OLIMAR",
        "LUCARIO",
        "R.O.B.",
        "TOON LINK",
        "WOLF",
        "VILLAGER",
        "MEGA MAN",
        "Wii Fit TRAINER",
        "ROSALINA & LUMA",
        "LITTLE MAC",
        "GRENINJA",
        "Mii FIGHTER",
        "PALUTENA",
        "PAC-MAN",
        "ROBIN",
        "SHULK",
        "BOWSER JR.",
        "DUCK HUNT",
        "RYU",
        "KEN",
        "CLOUD",
        "CORRIN",
        "BAYONETTA",
        "INKLING",
        "RIDLEY",
        "SIMON",
        "RICHTER",
        "KING K. ROOL",
        "ISABELLE",
        "INCINEROAR",
        "PIRANHA PLANT",
        "JOKER",
        "HERO",
        "BANJO & KAZOOIE"
    ]


def subprocess_call(cmd, logger='bar', errorprint=True):
    """ Executes the given subprocess command.

    Set logger to None or a custom Proglog logger to avoid printings.

    NOTE: SEE MOVIEPY library!
    """
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
            print('Moviepy - Command returned an error')
        raise IOError(err.decode('utf8'))
    else:
        print('Command successful')


    del proc