import os
import hashlib
import argparse

from dffml.util.cli.arg import Arg
from dffml.util.cli.cmd import CMD

from twothings.calendar.sync import CalendarSync

RAND_STR_DEFAULT_BITS_ENTROPY = 4096

class RandStr(CMD):
    """
    Generate a random string
    """

    arg_bits = Arg('--bits', default=RAND_STR_DEFAULT_BITS_ENTROPY, type=int, help=f"Number of bits of entropy (default: {RAND_STR_DEFAULT_BITS_ENTROPY})")

    async def run(self):
        print(hashlib.sha384(os.urandom(int(self.bits / 8))).hexdigest())

class CalSync(CMD):

    async def run(self):
        CalendarSync().calendar_sync_ews_to_google()

class HexBits(CMD):

    arg_hex = Arg("hex")

    async def run(self):
        # 360ef0
        length = len(self.hex) * 4
        bits = []
        print("|", end="")
        for bit in range(0, length - 1):
            print(" %02d |" % (bit,), end="")
        print(" %02d |" % (length - 1,))
        for byte in map(lambda c: int("0x0" + c, 16), self.hex[::-1]):
            bits += list(map(lambda bit: 1 if byte & (1 << bit) else 0, range(0, 4)))
        print("|  " + " |  ".join(map(str, bits)), end=" |\n")

class CLI(CMD):
    '''
     __   __                                _                      _
     \\ \\ / /__  _   _  __      ____ _ _ __ | |_   _ __ ___   ___  | |_ ___
      \\ V / _ \\| | | | \\ \\ /\\ / / _` | '_ \\| __| | '_ ` _ \\ / _ \\ | __/ _ \\
       | | (_) | |_| |  \\ V  V / (_| | | | | |_  | | | | | |  __/ | || (_) |
       |_|\\___/ \\__,_|   \\_/\\_/ \\__,_|_| |_|\\__| |_| |_| |_|\\___|  \\__\\___/

				     _
				    ( )
				     H
				     H
				    _H_
				 .-'-.-'-.
				/         \\
			       |           |
			       |   .-------'._
			       |  / /  '.' '. \\
			       |  \\ \\ @   @ / /
			       |   '---------'
			       |    _______|
			       |  .'-+-+-+|
			       |  '.-+-+-+|
			       |    """""" |
			       '-.__   __.-'
				    """

	  _         _                   _   _     _                ___
       __| | ___   | |___      _____   | |_| |__ (_)_ __   __ _ __|__ \\
      / _` |/ _ \\  | __\\ \\ /\\ / / _ \\  | __| '_ \\| | '_ \\ / _` / __|/ /
     | (_| | (_) | | |_ \\ V  V / (_) | | |_| | | | | | | | (_| \\__ \\_|
      \\__,_|\\___/   \\__| \\_/\\_/ \\___/   \\__|_| |_|_|_| |_|\\__, |___(_)
							  |___/
    '''

    CLI_FORMATTER_CLASS = argparse.RawDescriptionHelpFormatter

    randstr = RandStr
    calsync = CalSync
    hexbits = HexBits
