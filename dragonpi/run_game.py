#!/usr/bin/env python3

import logging
log = logging.getLogger(__name__)
import argparse
from threading import Thread

from dragonpi.dndmusic import MusicListener
from dragonpi.lcdmenu import LCDMenu, AudioOutput, Greeting

def parse_args():
    """Parse the command-line arguments and return the options."""
    parser = argparse.ArgumentParser(description="Launch the DragonPi D&D game helper.")
    # Add command-line arguments
    parser.add_argument('-d', '--debug', action='store_true', help="Spit out verbose logging")
    # Parse the actual command line arguments
    args = parser.parse_args()
    return args


def start_music():
    # Load the listener for doing music keypresses
    with MusicListener() as music:
        music.join()


def start_lcd():
    lcdmenu = LCDMenu()
    entries = [Greeting(), AudioOutput()]
    lcdmenu.add_entries(*entries)
    lcdmenu.join()


def main():
    args = parse_args()
    # Prepare logging if requested
    if args.debug:
        logging.basicConfig(level=logging.INFO)
    # Start the music handler
    music_thread = Thread(target=start_music)
    music_thread.start()
    # Start the LCD menu
    lcd_thread = Thread(target=start_lcd)
    lcd_thread.start()


if __name__ == "__main__":
    main()
