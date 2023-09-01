# core parsing logic

from base64 import b64decode, b64encode
from typing import List, Union, Dict

from constants import *
from util import fmt, Encodable

# TODO: str or repr?


class Minigame(Encodable):
    def __init__(self, raw: str):
        self.raw = raw
        self.fields = {
            'not': 'implemented'
        }

    def encode(self):
        return ' '.join(list(map(fmt, self.fields.values())))


class FarmMinigame(Minigame):
    def __init__(self, raw: str):
        super().__init__(raw)

        space_split = raw.split(' ')
        general_split = space_split[0].split(':')

        seeds_str = space_split[1]
        seeds = dict()
        for i, name in enumerate(SEEDS):
            seeds[name] = seeds_str[i] == '1'

        plot_split = space_split[2].split(':')
        plot = list(map(int, plot_split[:-1]))
        plot_plants = plot[::2]
        plot_ages = plot[1::2]
        plot = list(zip(plot_plants, plot_ages))

        self.fields = {
            'general': {
                'timeNextTick': int(general_split[0]),
                'soil': int(general_split[1]),
                'timeNextSoilChange': int(general_split[2]),
                'frozen': int(general_split[3]),
                'harvested': int(general_split[4]),
                'harvestedAllTime': int(general_split[5]),
                'gardenOpen': int(general_split[6]),
                'convertTimes': int(general_split[7]),
                'timeNextFreeze': int(general_split[8]),
            },
            'seeds': seeds,
            'plot': plot,
        }

    def encode(self):
        # flatten plot list first
        plot_flat = []
        for seed, age in self.fields['plot']:
            plot_flat.append(seed)
            plot_flat.append(age)

        return ' '.join([                                             # VVV dumb idiot
            ':'.join(list(map(fmt, self.fields['general'].values()))) + ':',
            ''.join(['1' if value else '0' for value in self.fields['seeds'].values()]),
            ':'.join(list(map(fmt, plot_flat))),
        ])


class Stock(Encodable):
    def __init__(self, raw: str):
        self.raw = raw
        split = raw.split(':')
        self.fields = {
            'valueCents': int(split[0]),
            'mode': int(split[1]),
            'd': int(split[2]),
            'dur': int(split[3]),
            'amount': int(split[4]),
            'hidden': int(split[5]),
            'boughtThisTick': int(split[6]),
            'valueLastBuyCents': int(split[7]),
        }

    def encode(self):
        return ':'.join(list(map(fmt, self.fields.values())))


class BankMinigame(Minigame):
    def __init__(self, raw: str):
        super().__init__(raw)

        space_split = raw.split(' ')
        general_split = space_split[0].split(':')
        stocks_split = space_split[1].split('!')

        self.fields = {
            'general': {
                'officeLevel': int(general_split[0]),
                'brokers': int(general_split[1]),
                'lines': int(general_split[2]),
                'profits': float(general_split[3]),
                'darkColor': int(general_split[4]),
            },
            'stocks': dict(zip(STOCK_SYMBOLS, list(map(Stock, stocks_split[:-1])))),
            'stockMarketOpen': int(space_split[2]),
        }

    def encode(self):
        return ' '.join([
            ':'.join(list(map(fmt, self.fields['general'].values()))),
            '!'.join(list(map(fmt, self.fields['stocks'].values()))) + '!',
            fmt(self.fields['stockMarketOpen']),
        ])


class TempleMinigame(Minigame):
    def __init__(self, raw: str):
        super().__init__(raw)

        space_split = raw.split(' ')

        self.fields = {
            'chosen': list(map(int, space_split[0].split('/'))),
            'swaps': int(space_split[1]),
            'timeSwapped': int(space_split[2]),
            'pantheonOpen': int(space_split[3]),
        }

    def encode(self):
        return ' '.join([
            '/'.join(list(map(fmt, self.fields['chosen']))),
            fmt(self.fields['swaps']),
            fmt(self.fields['timeSwapped']),
            fmt(self.fields['pantheonOpen']),
        ])


class WizardMinigame(Minigame):
    def __init__(self, raw: str):
        super().__init__(raw)

        space_split = raw.split(' ')

        self.fields = {
            'magic': float(space_split[0]),
            'spells': int(space_split[1]),
            'spellsAllTime': int(space_split[2]),
            'grimoireOpen': int(space_split[3]),
        }

    def encode(self):
        return ' '.join(list(map(fmt, self.fields.values())))


MINIGAME_CONFIG: List[Union[None, type]] = [None for _ in BUILDINGS]
MINIGAME_CONFIG[2] = FarmMinigame
MINIGAME_CONFIG[5] = BankMinigame
MINIGAME_CONFIG[6] = TempleMinigame
MINIGAME_CONFIG[7] = WizardMinigame


class Building(Encodable):
    def __init__(self, raw: str, idx: int):
        split = raw.split(',')
        minigame = split[4]
        if minigame:
            minigame = MINIGAME_CONFIG[idx](minigame)

        self.fields = {
            'count': int(split[0]),
            'countTotal': int(split[1]),
            'cookiesTotal': int(split[2]),
            'level': int(split[3]),
            'minigame': minigame,
            'muted': int(split[5]),
            'countHighest': int(split[6]),
        }

    def encode(self):
        return ','.join(list(map(fmt, self.fields.values())))


class Buff(Encodable):
    def __init__(self, raw: str):
        split = raw.split(',')

        if len(split) >= 5:
            data = int(split[4])
        else:
            data = None

        self.fields: Dict[str, Union[int, float, None, str]] = {
            'buffId': int(split[0]),
            'framesTotal': int(split[1]),
            'framesLeft': int(split[2]),
            'multiplier': float(split[3]),
            'data': data,
        }

    def encode(self):
        copy = self.fields.copy()
        copy['multiplier'] = str(self.fields['multiplier'])

        fields_list = list(copy.values())
        if fields_list[-1] is None:
            fields_list.pop()

        return ','.join(list(map(fmt, fields_list)))


class Block(Encodable):
    # parse the raw string
    def __init__(self, raw: str):
        self.raw = raw

    # construct the string for rebuilding the save file
    def encode(self):
        if hasattr(self, 'fields') and isinstance(self.fields, dict):
            return ';'.join(list(map(fmt, self.fields.values())))
        else:
            return self.raw


class EmptyBlock(Block):
    def __init__(self, raw: str):
        super().__init__(raw)
        if raw:
            raise 'non-empty string passed into EmptyBlock'

        self.fields = dict()

    def encode(self):
        return ''


class UnknownBlock(Block):
    def __init__(self, raw: str):
        super().__init__(raw)


class VersionBlock(Block):
    def __init__(self, raw: str):
        super().__init__(raw)
        self.version = raw

    def encode(self):
        return self.version


class GeneralBlock(Block):
    def __init__(self, raw: str):
        super().__init__(raw)
        split = raw.split(';')
        self.fields = {
            'timeAscended': int(split[0]),
            'timeStarted': int(split[1]),  # guessing
            'timeSaved': int(split[2]),
            'name': split[3],
            'RandomizerSeed': split[4],
            'appearance': split[5],
        }


class OptionsBlock(Block):
    def __init__(self, raw: str):
        super().__init__(raw)
        self.options = dict()
        for i, name in enumerate(OPTIONS):
            self.options[name] = raw[i] == '1'

        for name in ['Short numbers', 'Scary stuff']:
            self.options[name] = not self.options[name]

    def encode(self):
        copy = self.options.copy()

        for name in ['Short numbers', 'Scary stuff']:
            copy[name] = not self.options[name]

        return ''.join(['1' if value else '0' for value in copy.values()])


class StatsBlock(Block):
    def __init__(self, raw: str):
        super().__init__(raw)
        split = raw.split(';')
        self.fields = {
            'cookies': float(split[0]),
            'cookiesAllTime': float(split[1]),
            'clicks': int(split[2]),
            'clicksGolden': int(split[3]),
            'cookiesHandmade': float(split[4]),
            'goldenCookiesMissed': int(split[5]),
            'backgroundType': int(split[6]),
            'milkType': int(split[7]),
            'cookiesPast': float(split[8]),
            'grandmatriarchsStatus': int(split[9]),
            'timesPledged': int(split[10]),
            'framesLeftPledge': int(split[11]),
            'researchUpgradeId': int(split[12]),
            'researchFramesLeft': int(split[13]),
            'ascensions': int(split[14]),
            'clicksGoldenAllTime': int(split[15]),
            'cookiesWrinklers': float(split[16]),
            'wrinklersPopped': int(split[17]),
            'santaLevel': int(split[18]),
            'reindeerClicked': int(split[19]),
            'framesLeftSeason': int(split[20]),
            'seasonSwitcherUses': int(split[21]),
            'unknown14/empty': split[22],
            'cookiesWrinklersCurrent': float(split[23]),
            'wrinklersCurrent': int(split[24]),
            'prestigeLevel': float(split[25]),
            'heavenlyChips': float(split[26]),
            'heavenlyChipsSpent': float(split[27]),
            'heavenlyCookies': float(split[28]),
            'ascensionMode': int(split[29]),
            'permanentUpgrade0': int(split[30]),
            'permanentUpgrade1': int(split[31]),
            'permanentUpgrade2': int(split[32]),
            'permanentUpgrade3': int(split[33]),
            'permanentUpgrade4': int(split[34]),
            'dragonLevel': int(split[35]),
            'dragonAura': int(split[36]),
            'dragonAura2': int(split[37]),
            'chimeType': int(split[38]),
            'volume': int(split[39]),
            'wrinklersShiny': int(split[40]),
            'cookiesWrinklersShiny': float(split[41]),
            'sugarLumps': int(split[42]),
            'sugarLumpsAllTime': int(split[43]),
            'timeLastSugarLump': int(split[44]),
            'timeLastSugarLumpRefill': int(split[45]),
            'sugarLumpType': int(split[46]),
            'vault': split[47],
            'heralds': int(split[48]),
            'goldenCookieFortune': int(split[49]),
            'cpsFortune': int(split[50]),
            'cpsHighestThisAscension': float(split[51]),
            'volumeMusic': int(split[52]),
            'cookiesSent': float(split[53]),
            'cookiesReceived': float(split[54]),
        }


class BuildingsBlock(Block):
    def __init__(self, raw: str):
        super().__init__(raw)
        split = raw.split(';')

        self.buildings = dict()
        for i, b in enumerate(split[:-1]):
            self.buildings[BUILDINGS[i]] = Building(b, i)

    def encode(self):
        return ';'.join(list(map(fmt, self.buildings.values()))) + ';'


class AchievementsBlock(Block):
    def __init__(self, raw: str):
        super().__init__(raw)
        self.unlocked = dict()
        for i, name in enumerate(ACHIEVEMENTS):
            self.unlocked[name] = raw[i] == '1'

    def encode(self):
        return ''.join(['1' if value else '0' for value in self.unlocked.values()])


class BuffsBlock(Block):
    def __init__(self, raw: str):
        super().__init__(raw)
        split = raw.split(';')

        self.buffs = list(map(Buff, split[:-1]))

    def encode(self):
        if not self.buffs:
            return ''
        return ';'.join(list(map(fmt, self.buffs))) + ';'


BLOCKS_CONFIG = [
    VersionBlock,
    EmptyBlock,  # this block is actually empty on purpose "just in case we need some more stuff here"
    GeneralBlock,
    OptionsBlock,
    StatsBlock,
    BuildingsBlock,
    UnknownBlock,  # upgrades (i don't want to do this)
    AchievementsBlock,
    BuffsBlock,
    UnknownBlock,  # mod data
]


class Save:
    def __init__(self, raw_export_str: str) -> None:
        decoded = self.decode_from_raw(raw_export_str)
        self.blocks: List[Block] = []
        block_split = decoded.split('|')
        for data, cls in zip(block_split, BLOCKS_CONFIG):
            self.blocks.append(cls(data))

    def encode_and_b64(self) -> str:
        encoded = b64encode(self.encode().encode('utf-8')).decode('utf-8')
        return encoded.replace('=', '%3D') + '%21END%21'

    @classmethod
    def decode_from_raw(cls, raw_export_str: str) -> str:
        prepared = raw_export_str.replace('%21END%21', '').replace('%3D', '=')
        return b64decode(prepared).decode('utf-8')

    def encode(self):
        return '|'.join(list(map(fmt, self.blocks)))
