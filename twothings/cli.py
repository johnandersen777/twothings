import os
import hashlib
import argparse

from dffml.util.cli.arg import Arg
from dffml.util.cli.cmd import CMD

RAND_STR_DEFAULT_BITS_ENTROPY = 4096

class RandStr(CMD):
    """
    Generate a random string
    """

    arg_bits = Arg('--bits', default=RAND_STR_DEFAULT_BITS_ENTROPY, type=int, help=f"Number of bits of entropy (default: {RAND_STR_DEFAULT_BITS_ENTROPY})")

    async def run(self):
        print(hashlib.sha384(os.urandom(int(self.bits / 8))).hexdigest())


import asyncio
import curses
from curses.textpad import Textbox, rectangle

class Curses:

    def main(self, stdscr):
        raise NotImplementedError()

    def wrapped(self, func):
        def call_wrapper():
            curses.wrapper(func)
        return call_wrapper

    async def wrapper(self, func):
        await asyncio.get_event_loop().run_in_executor(None,
                self.wrapped(func))

    async def run(self):
        await self.wrapper(self.main)

class CursesEWS(Curses):

    def main(self, stdscr):
        self.window = stdscr
        # Clear screen
        stdscr.clear()

        # stdscr.border()

        # This raises ZeroDivisionError when i == 10.
        for i in range(0, 10):
            v = i-10
            stdscr.addstr(i, 0, '10 divided by {} is {}'.format(v, stdscr))

        stdscr.refresh()
        stdscr.getkey()

    async def run(self):
        cli = asyncio.create_task(self.wrapper(self.main))
        await cli

class EWSClientEmail(CMD):
    """
    Email client for EWS
    """

    async def run(self):
        await CursesEWS().run()

class Email(CMD):
    """
    Email related utilities
    """

    ewsclient = EWSClientEmail

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
    email = Email
