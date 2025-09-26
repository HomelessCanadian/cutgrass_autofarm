# cgfarm.py
# repos/cutgrass_autofarm/cgfarm.py

import argparse
from bot_core import ClassI
from bot_utils import now

parser = argparse.ArgumentParser()
parser.add_argument("--debug", action="store_true", help="Enable debug logging")
parser.add_argument("--game", type=str, default="cg", help="Game mode (cg, cc, etc.)")
parser.add_argument("--afk", action="store_true", help="Run in AFK-only mode")
args = parser.parse_args()

print(f"{now()} 🎮 Launching CGfarm with game='{args.game}' afk_only={args.afk}")
bot = ClassI(game=args.game, afk_only=args.afk)
bot.run()
