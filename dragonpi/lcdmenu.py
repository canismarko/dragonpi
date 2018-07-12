# This file is part of DragonPi.
# 
# DragonPi is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# DragonPi is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with DragonPi.  If not, see <https://www.gnu.org/licenses/>.

"""Framework for using the Adafruit character LCD plate for a menu.

A series of ``MenuItem`` instances are to be added to an LCDMenu()
instance, building up the menu in pieces.

"""

import logging
log = logging.getLogger(__name__)
import warnings
import contextlib
import time
from subprocess import call, check_output
import re
import os

CHECKMARK = '\x01'

def int_from_hex_string(s):
    d = int.from_bytes(bytes('\x01', encoding='utf8'), byteorder='big')
    return d


class DummyLCD():
    """A mocked LCD Plate that is used if no LCD is available."""
    def clear(self, *args, **kwargs):
        log.debug('Dummy logger cleared')
    
    def message(self, s, *args, **kwargs):
        log.debug('Dummy logger message: %s', s)


class LCDMenu():
    _active_item_idx = 0
    _menu_items = []
    #CharLCDplatebuttonnames.
    SELECT = 0
    RIGHT = 1
    DOWN = 2
    UP = 3
    LEFT = 4
    # CharLCDPlate Colors
    WHITE = (1.0, 1.0, 1.0)
    RED = (1.0, 0.0, 0.0)
    
    def __init__(self, lcd=None):
        # Get default LCD display
        if lcd is None:
            try:
                from .Adafruit_CharLCD import Adafruit_CharLCDPlate, SELECT
                lcd = Adafruit_CharLCDPlate()
            except RuntimeError:
                log.warning('Could not load Adafruit_CharLCDPlate')
                warnings.warn("Could not load ADafruit_CharLCDPlate", RuntimeWarning)
                lcd = DummyLCD()
        self.lcd = lcd
        self.init_lcd()
        # Create an empty array to hold new menu items
        self._menu_items = []

    def init_lcd(self):
        self.lcd.set_color(*self.WHITE)
        # Set custom characters
        print(int_from_hex_string(CHECKMARK))
        self.lcd.create_char(int_from_hex_string(CHECKMARK),
                             [0,1,3,22,28,8,0,0])
        
    
    def add_entries(self, *entries):
        """Add menu item entries to the list of menu options.
        
        Parameters
        ----------
        *entries
          Any number of new menu items to be added to the menu.
        
        """
        self._menu_items.extend(entries)
    
    def join(self):
        """Monitor the LCD menu for button presses."""
        self.refresh_text()
        buttons = ((self.SELECT, self.select_pressed),
                   (self.LEFT, self.left_pressed),
                   (self.RIGHT, self.right_pressed),
                   (self.UP, self.up_pressed),
                   (self.DOWN, self.down_pressed),)
        while True:
            # Check status of each button
            for button in buttons:
                if self.lcd.is_pressed(button[0]):
                    button[1]()
                    # Wait for the button to be released
                    while self.lcd.is_pressed(button[0]):
                        pass

    @contextlib.contextmanager
    def press_button(self):
        try:
            yield
        except NotImplementedError:
            self.lcd.set_color(*self.RED)
            time.sleep(0.3)
            self.lcd.set_color(*self.WHITE)
    
    def refresh_text(self):
        """Update the display text from the current menu item."""
        self.lcd.clear()
        # Set the new text
        item = self.active_item()
        self.lcd.message(f'{item.name}\n{item.active_text()}')
    
    def active_item(self):
        return self._menu_items[self._active_item_idx]
    
    def select_pressed(self):
        """Respond when the "Select" button is pressed."""
        self.active_item().select()
        self.refresh_text()
    
    def left_pressed(self):
        """Respond when the "Left" button is pressed."""
        with self.press_button():
            self.active_item().move_left()
        self.refresh_text()
    
    def right_pressed(self):
        """Respond when the "Right" button is pressed."""
        with self.press_button():
            self.active_item().move_right()
        self.refresh_text()
    
    def down_pressed(self):
        """Respond when the "Down" button is pressed."""
        # Cycle around the list of menu items
        new_idx = (self._active_item_idx + 1) % len(self._menu_items)
        self._active_item_idx = new_idx
        self.refresh_text()
    
    def up_pressed(self):
        """Respond when the "Up" button is pressed."""
        # Cycle around the list of menu items
        new_idx = (self._active_item_idx - 1) % len(self._menu_items)
        self._active_item_idx = new_idx
        self.refresh_text()


class MenuItem():
    name = "Menu Item:"
    def select(self):
        """Action to take if the select button is pressed."""
        raise NotImplementedError()
    
    def move_right(self):
        """Action to take when the "right" button is pressed."""
        raise NotImplementedError()
    
    def move_left(self):
        """Action to take when the "left" button is pressed."""
        raise NotImplementedError()
    
    def active_text(self):
        """Text based on the current active item."""
        return f"[{self.name} text]"


class Greeting(MenuItem):
    @property
    def name(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        version = open(os.path.join(base_dir, '..', 'VERSION')).read()
        return f"DragonPi v{version}"
    
    def active_text(self):
        return "Up/Dn for menu"


class AudioOutput(MenuItem):
    name = "Audio Output"
    highlight_idx = 0
    source_names = ['Auto', 'Analog 1/4"', 'HDMI']
    curr_val_re = re.compile(': values=(\d+)')
    
    def active_text(self):
        txt = self.source_names[self.highlight_idx]
        # Add a checkmark if currently selected
        if self.highlight_idx == self.active_idx:
            txt = f'{CHECKMARK} {self.highlight_idx}:{txt}'
        else:
            txt = f'  {self.highlight_idx}:{txt}'
        return txt

    def move_right(self):
        # Show the next item in the list
        new_idx = (self.highlight_idx + 1) % len(self.source_names)
        self.highlight_idx = new_idx

    def move_left(self):
        # Show the previous item in the list
        new_idx = (self.highlight_idx - 1) % len(self.source_names)
        self.highlight_idx = new_idx

    @property
    def active_idx(self):
        output = check_output(['amixer', 'cget', 'numid=3'])
        output = output.decode('ascii')
        # Search the output for the necessary value
        curr_match = self.curr_val_re.search(output)
        idx = int(curr_match.group(1)) if curr_match else 0
        return idx

    def select(self):
        new_idx = self.highlight_idx
        # Update the active item
        call(['amixer', 'cset', 'numid=3', str(new_idx)])
