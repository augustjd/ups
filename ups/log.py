import sys
import logging
import random

import colorama
colorama.init(autoreset=True)


def dim(s):
    return colorama.Style.DIM + s + colorama.Style.NORMAL


def normal(s):
    return colorama.Style.NORMAL + s


def bright(s):
    return colorama.Style.BRIGHT + s + colorama.Style.NORMAL


def magenta(s):
    return color(colorama.Fore.MAGENTA, s)


def yellow(s):
    return color(colorama.Fore.YELLOW, s)


def blue(s):
    return color(colorama.Fore.BLUE, s)


def green(s):
    return color(colorama.Fore.GREEN, s)


def color(color, s):
    return color + s + colorama.Fore.RESET


ALL_COLORS = [
    colorama.Fore.RED,
    colorama.Fore.YELLOW,
    colorama.Fore.GREEN,
    colorama.Fore.CYAN,
    colorama.Fore.BLUE,
    colorama.Fore.MAGENTA,
    colorama.Fore.LIGHTRED_EX,
    colorama.Fore.LIGHTYELLOW_EX,
    colorama.Fore.LIGHTGREEN_EX,
    colorama.Fore.LIGHTCYAN_EX,
    colorama.Fore.LIGHTBLUE_EX,
    colorama.Fore.LIGHTMAGENTA_EX,
]


def random_color(key=None):
    random.seed(key)
    return random.choice(ALL_COLORS)


LOG_FORMAT = (dim('%(asctime)s ') +
              '%(levelname)8s ' +
              '%(message)s')


COLORS = {
    'WARNING': colorama.Fore.YELLOW,
    'INFO': colorama.Fore.BLUE,
    'DEBUG': colorama.Fore.WHITE,
    'CRITICAL': colorama.Fore.YELLOW,
    'ERROR': colorama.Fore.RED
}


class ColoredFormatter(logging.Formatter):
    def __init__(self, msg, use_color=True):
        logging.Formatter.__init__(self, msg)
        self.use_color = use_color

    def format(self, record):
        levelname = record.levelname

        if self.use_color and levelname in COLORS:
            record.levelname = COLORS[levelname] + '[{: <7s}]'.format(levelname) + colorama.Fore.RESET

        return logging.Formatter.format(self, record)


formatter = ColoredFormatter(LOG_FORMAT)
logging.basicConfig()

stdout_handler = logging.StreamHandler(stream=sys.stdout)
stdout_handler.setLevel(logging.INFO)
stdout_handler.setFormatter(formatter)

log = logging.getLogger('ups')
log.addHandler(stdout_handler)
log.propagate = False
