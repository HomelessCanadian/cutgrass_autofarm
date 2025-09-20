import argparse
from bot_core import ClassI


parser = argparse.ArgumentParser()
parser.add_argument("--debug", action="store_true")
args = parser.parse_args()

bot = ClassI()
bot.run()
