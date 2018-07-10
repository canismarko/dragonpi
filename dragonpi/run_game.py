#!/usr/bin/env python3

import logging
log = logging.getLogger(__name__)
import argparse

from .dndmusic import MusicListener

def parse_args():
    """Parse the command-line arguments and return the options."""
    parser = argparse.ArgumentParser(description="Launch the DragonPi D&D game helper.")
    # Add command-line arguments
    parser.add_argument('-d', '--debug', action='store_true', help="Spit out verbose logging")
    # Parse the actual command line arguments
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    # Prepare logging if requested
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    # Load the listener for doing music keypresses
    with MusicListener() as music:
        music.join()


if __name__ == "__main__":
    main()
