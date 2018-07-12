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

class DummyLCD():
    """A mocked LCD Plate that is used if no LCD is available."""
    def clear(self, *args, **kwargs):
        log.debug('Dummy logger cleared')
    
    def message(self, s, *args, **kwargs):
        log.debug('Dummy logger message: %s', s)


class LCDMenu():
    _active_item_idx = 0
    _menu_items = []
    
    def __init__(self, lcd=None):
        # Get default LCD display
        if lcd is None:
            try:
                from .Adafruit_CharLCD import Adafruit_CharLCDPlate
                lcd = Adafruit_CharLCDPlate()
            except RuntimeError:
                log.warning('Could not load Adafruit_CharLCDPlate')
                warnings.warn("Could not load ADafruit_CharLCDPlate", RuntimeWarning)
                lcd = DummyLCD()
        self.lcd = lcd
        # Create an empty array to hold new menu items
        self._menu_items = []
    
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
        buttons = ((self.lcd.SELECT, self.select_pressed),
                   (self.lcd.LEFT, self.left_pressed),
                   (self.lcd.RIGHT, self.right_pressed),
                   (self.lcd.UP, self.up_pressed),
                   (self.lcd.DOWN, self.down_pressed),)
        while True:
            # Check status of each button
            for button in buttons:
                if self.lcd.is_pressed(button[0]):
                    button[1]()
                    # Wait for the button to be released
                    while self.lcd.is_pressed(button[0]):
                        pass
    
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
        self.active_item().move_left()
        self.refresh_text()
    
    def right_pressed(self):
        """Respond when the "Right" button is pressed."""
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
        raise NotImplementedError()


class Greeting(MenuItem):
    pass


class AudioOutput(MenuItem):
    pass
