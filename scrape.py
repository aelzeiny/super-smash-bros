"""
Scrapes from Smash WIKI URL: https://www.ssbwiki.com/Super_Smash_Bros._Ultimate
Run this JS code in the console first:
```JS
let all_links = Array.from($('.wikitable tr td'))
const big_dict = {};
for (let i = 0 ; i < all_links.length; i++) {
    let el = all_links[i];
    let imgs = el.getElementsByTagName('img');
    if (imgs.length > 0)
        big_dict[el.innerText] = Array.from(imgs)[0].getAttribute('src')
    if (el.innerText.includes('Terry'))
        break
}
JSON.stringify(big_dict);
```
"""

import json
import os

import requests
import shutil
from multiprocessing import Pool


all_characters = json.loads("{\"\\nMario\\n\":\"/images/thumb/4/44/Mario_SSBU.png/100px-Mario_SSBU.png\",\"\\nLuigi\\n\":\"/images/thumb/b/bb/Luigi_SSBU.png/91px-Luigi_SSBU.png\",\"\\nPeach\\n\":\"/images/thumb/7/74/Peach_SSBU.png/89px-Peach_SSBU.png\",\"\\nBowser\\n\":\"/images/thumb/4/49/Bowser_SSBU.png/100px-Bowser_SSBU.png\",\"\\nDr. Mario\\n\":\"/images/thumb/3/3f/Dr._Mario_SSBU.png/100px-Dr._Mario_SSBU.png\",\"\\nRosalina & Luma\\n\":\"/images/thumb/1/16/Rosalina_%26_Luma_SSBU.png/100px-Rosalina_%26_Luma_SSBU.png\",\"\\nBowser Jr.\\n\":\"/images/thumb/2/2b/Bowser_Jr._SSBU.png/100px-Bowser_Jr._SSBU.png\",\"\\nYoshi\\n\":\"/images/thumb/8/8d/Yoshi_SSBU.png/100px-Yoshi_SSBU.png\",\"\\nDonkey Kong\\n\":\"/images/thumb/c/c9/Donkey_Kong_SSBU.png/100px-Donkey_Kong_SSBU.png\",\"\\nDiddy Kong\\n\":\"/images/thumb/a/a7/Diddy_Kong_SSBU.png/96px-Diddy_Kong_SSBU.png\",\"\\nLink\\n\":\"/images/thumb/8/84/Link_SSBU.png/100px-Link_SSBU.png\",\"\\nZelda\\n\":\"/images/thumb/c/c8/Zelda_SSBU.png/100px-Zelda_SSBU.png\",\"\\nSheik\\n\":\"/images/thumb/0/00/Sheik_SSBU.png/100px-Sheik_SSBU.png\",\"\\nYoung Link\\n\":\"/images/thumb/8/8a/Young_Link_SSBU.png/100px-Young_Link_SSBU.png\",\"\\nGanondorf\\n\":\"/images/thumb/9/91/Ganondorf_SSBU.png/99px-Ganondorf_SSBU.png\",\"\\nToon Link\\n\":\"/images/thumb/5/56/Toon_Link_SSBU.png/95px-Toon_Link_SSBU.png\",\"\\nSamus\\n\":\"/images/thumb/0/03/Samus_SSBU.png/100px-Samus_SSBU.png\",\"\\nZero Suit Samus\\n\":\"/images/thumb/f/f0/Zero_Suit_Samus_SSBU.png/100px-Zero_Suit_Samus_SSBU.png\",\"\\nKirby\\n\":\"/images/thumb/0/07/Kirby_SSBU.png/100px-Kirby_SSBU.png\",\"\\nMeta Knight\\n\":\"/images/thumb/0/00/Meta_Knight_SSBU.png/100px-Meta_Knight_SSBU.png\",\"\\nKing Dedede\\n\":\"/images/thumb/f/f5/King_Dedede_SSBU.png/100px-King_Dedede_SSBU.png\",\"\\nFox\\n\":\"/images/thumb/2/2f/Fox_SSBU.png/100px-Fox_SSBU.png\",\"\\nFalco\\n\":\"/images/thumb/8/80/Falco_SSBU.png/100px-Falco_SSBU.png\",\"\\nWolf\\n\":\"/images/thumb/8/8a/Wolf_SSBU.png/100px-Wolf_SSBU.png\",\"\\nPikachu\\n\":\"/images/thumb/9/93/Pikachu_SSBU.png/100px-Pikachu_SSBU.png\",\"\\nJigglypuff\\n\":\"/images/thumb/6/6a/Jigglypuff_SSBU.png/100px-Jigglypuff_SSBU.png\",\"\\nPichu\\n\":\"/images/thumb/c/c1/Pichu_SSBU.png/100px-Pichu_SSBU.png\",\"\\nMewtwo\\n\":\"/images/thumb/d/de/Mewtwo_SSBU.png/99px-Mewtwo_SSBU.png\",\"\\nPokémon Trainer (Squirtle, Ivysaur, Charizard)\\n\":\"/images/thumb/2/28/Pok%C3%A9mon_Trainer_%28solo%29_SSBU.png/100px-Pok%C3%A9mon_Trainer_%28solo%29_SSBU.png\",\"\\nLucario\\n\":\"/images/thumb/0/08/Lucario_SSBU.png/100px-Lucario_SSBU.png\",\"\\nGreninja\\n\":\"/images/thumb/d/da/Greninja_SSBU.png/100px-Greninja_SSBU.png\",\"\\nCaptain Falcon\\n\":\"/images/thumb/d/da/Captain_Falcon_SSBU.png/100px-Captain_Falcon_SSBU.png\",\"\\nNess\\n\":\"/images/thumb/8/82/Ness_SSBU.png/100px-Ness_SSBU.png\",\"\\nLucas\\n\":\"/images/thumb/8/81/Lucas_SSBU.png/100px-Lucas_SSBU.png\",\"\\nIce Climbers\\n\":\"/images/thumb/1/12/Ice_Climbers_SSBU.png/100px-Ice_Climbers_SSBU.png\",\"\\nMarth\\n\":\"/images/thumb/e/e9/Marth_SSBU.png/100px-Marth_SSBU.png\",\"\\nRoy\\n\":\"/images/thumb/9/9d/Roy_SSBU.png/100px-Roy_SSBU.png\",\"\\nIke\\n\":\"/images/thumb/8/86/Ike_SSBU.png/100px-Ike_SSBU.png\",\"\\nLucinaε\\n\":\"/images/thumb/d/dc/Lucina_SSBU.png/100px-Lucina_SSBU.png\",\"\\nRobin\\n\":\"/images/thumb/8/82/Robin_SSBU.png/100px-Robin_SSBU.png\",\"\\nCorrin\\n\":\"/images/thumb/c/c4/Corrin_SSBU.png/100px-Corrin_SSBU.png\",\"\\nMr. Game & Watch\\n\":\"/images/thumb/c/cb/Mr._Game_%26_Watch_SSBU.png/100px-Mr._Game_%26_Watch_SSBU.png\",\"\\nPit\\n\":\"/images/thumb/3/38/Pit_SSBU.png/100px-Pit_SSBU.png\",\"\\nPalutena\\n\":\"/images/thumb/6/6b/Palutena_SSBU.png/95px-Palutena_SSBU.png\",\"\\nDark Pitε\\n\":\"/images/thumb/0/09/Dark_Pit_SSBU.png/95px-Dark_Pit_SSBU.png\",\"\\nWario\\n\":\"/images/thumb/0/04/Wario_SSBU.png/100px-Wario_SSBU.png\",\"\\nOlimar\\n\":\"/images/thumb/b/b3/Olimar_SSBU.png/100px-Olimar_SSBU.png\",\"\\nR.O.B.\\n\":\"/images/thumb/6/60/R.O.B._SSBU.png/100px-R.O.B._SSBU.png\",\"\\nVillager\\n\":\"/images/thumb/a/ac/Villager_SSBU.png/100px-Villager_SSBU.png\",\"\\nWii Fit Trainer\\n\":\"/images/thumb/f/ff/Wii_Fit_Trainer_SSBU.png/100px-Wii_Fit_Trainer_SSBU.png\",\"\\nLittle Mac\\n\":\"/images/thumb/5/53/Little_Mac_SSBU.png/100px-Little_Mac_SSBU.png\",\"\\nShulk\\n\":\"/images/thumb/0/0f/Shulk_SSBU.png/100px-Shulk_SSBU.png\",\"\\nDuck Hunt\\n\":\"/images/thumb/d/d8/Duck_Hunt_SSBU.png/100px-Duck_Hunt_SSBU.png\",\"\\nSnake\\n\":\"/images/thumb/0/02/Snake_SSBU.png/82px-Snake_SSBU.png\",\"\\nSonic\\n\":\"/images/thumb/b/ba/Sonic_SSBU.png/100px-Sonic_SSBU.png\",\"\\nMega Man\\n\":\"/images/thumb/4/46/Mega_Man_SSBU.png/100px-Mega_Man_SSBU.png\",\"\\nPac-Man\\n\":\"/images/thumb/0/03/Pac-Man_SSBU.png/100px-Pac-Man_SSBU.png\",\"\\nRyu\\n\":\"/images/thumb/6/61/Ryu_SSBU.png/100px-Ryu_SSBU.png\",\"\\nCloud\\n\":\"/images/thumb/b/b3/Cloud_SSBU.png/100px-Cloud_SSBU.png\",\"\\nBayonetta\\n\":\"/images/thumb/7/7c/Bayonetta_SSBU.png/100px-Bayonetta_SSBU.png\",\"\\nMii Brawler\\n\":\"/images/thumb/e/e4/Mii_Brawler_SSBU.png/100px-Mii_Brawler_SSBU.png\",\"\\nMii Swordfighter\\n\":\"/images/thumb/f/fa/Mii_Swordfighter_SSBU.png/100px-Mii_Swordfighter_SSBU.png\",\"\\nMii Gunner\\n\":\"/images/thumb/e/e5/Mii_Gunner_SSBU.png/100px-Mii_Gunner_SSBU.png\",\"\\nDaisyε\\n\":\"/images/thumb/2/21/Daisy_SSBU.png/100px-Daisy_SSBU.png\",\"\\nPiranha Plant (DLC)\\n\":\"/images/thumb/f/f0/Piranha_Plant_SSBU.png/100px-Piranha_Plant_SSBU.png\",\"\\nKing K. Rool\\n\":\"/images/thumb/b/b6/King_K._Rool_SSBU.png/100px-King_K._Rool_SSBU.png\",\"\\nRidley\\n\":\"/images/thumb/2/27/Ridley_SSBU.png/100px-Ridley_SSBU.png\",\"\\nDark Samusε\\n\":\"/images/thumb/a/a6/Dark_Samus_SSBU.png/100px-Dark_Samus_SSBU.png\",\"\\nIncineroar\\n\":\"/images/thumb/c/c4/Incineroar_SSBU.png/100px-Incineroar_SSBU.png\",\"\\nChromε\\n\":\"/images/thumb/5/57/Chrom_SSBU.png/85px-Chrom_SSBU.png\",\"\\nByleth (DLC)\\n\":\"/images/thumb/3/3d/Byleth_SSBU.png/100px-Byleth_SSBU.png\",\"\\nIsabelle\\n\":\"/images/thumb/2/2b/Isabelle_SSBU.png/100px-Isabelle_SSBU.png\",\"\\nInkling\\n\":\"/images/thumb/2/2e/Inkling_SSBU.png/100px-Inkling_SSBU.png\",\"\\nARMS character (DLC)\\n\":\"/images/e/e3/None.png\",\"\\nKenε\\n\":\"/images/thumb/f/f6/Ken_SSBU.png/100px-Ken_SSBU.png\",\"\\nSimon\\n\":\"/images/thumb/9/95/Simon_SSBU.png/100px-Simon_SSBU.png\",\"\\nRichterε\\n\":\"/images/thumb/c/c2/Richter_SSBU.png/100px-Richter_SSBU.png\",\"\\nJoker (DLC)\\n\":\"/images/thumb/5/5c/Joker_SSBU.png/100px-Joker_SSBU.png\",\"\\nHero (DLC)\\n\":\"/images/thumb/0/07/Hero_SSBU.png/100px-Hero_SSBU.png\",\"\\nBanjo & Kazooie (DLC)\\n\":\"/images/thumb/9/97/Banjo_%26_Kazooie_SSBU.png/100px-Banjo_%26_Kazooie_SSBU.png\",\"\\nTerry (DLC)\\n\":\"/images/thumb/f/f5/Terry_SSBU.png/100px-Terry_SSBU.png\"}")
all_characters = {k.strip(' \n'): all_characters[k] for k in all_characters}


def download_file(url, local_filename):
    print('downloading: ', url)
    with requests.get(url, stream=True) as r:
        with open(local_filename, 'wb') as f:
            shutil.copyfileobj(r.raw, f)

    return local_filename


star_map = [
    (
        f'https://www.ssbwiki.com/{all_characters[k]}',
        f'./frontend/static/characters/{k}.png'
    )
    for k in all_characters
]

if not os.path.exists('./frontend/static/characters'):
    os.mkdir('./frontend/static/characters')

for url, dest in star_map:
    download_file(url, dest)

# with Pool(1) as pool:
#     pool.starmap(download_file, [
#         (
#             f'https://www.ssbwiki.com/{all_characters[k]}',
#             f'./frontend/static/characters/{k}.png'
#         )
#         for k in all_characters
#     ])
