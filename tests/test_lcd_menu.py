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


from unittest import mock, TestCase

from dragonpi.lcdmenu import LCDMenu, MenuItem


class TestLCDMenu(TestCase):
    def test_item_interaction(self):
        lcd = mock.MagicMock()
        menu = LCDMenu(lcd=lcd)
        item1 = mock.MagicMock()
        # Add the items
        menu.add_entries(item1)
        # Check that item1 is manipulated first
        menu.select_pressed()
        item1.select.assert_called()
        # Select the left or right item
        menu.right_pressed()
        item1.move_right.assert_called()
        menu.left_pressed()
        item1.move_left.assert_called()
    
    def test_switch_menus(self):
        lcd = mock.MagicMock()
        menu = LCDMenu(lcd=lcd)
        item1 = mock.MagicMock()
        item1.name = "Item 1"
        item2 = mock.MagicMock()
        item2.name = "Item 2"
        item3 = mock.MagicMock()
        item3.name = "Item 3"
        menu.add_entries(item1, item2, item3)
        # Press down button
        self.assertIs(menu.active_item(), item1)
        menu.down_pressed()
        self.assertIs(menu.active_item(), item2)
        menu.down_pressed()
        menu.down_pressed()
        self.assertIs(menu.active_item(), item1)
        # Press up button
        menu.up_pressed()
        self.assertIs(menu.active_item(), item3)
    
    def test_refresh_text(self):
        lcd = mock.MagicMock()
        menu = LCDMenu(lcd=lcd)
        item1 = mock.MagicMock()
        item1.name = "Item 1"
        item1.active_text = mock.MagicMock(return_value="Option 1")
        menu.add_entries(item1)
        # Check that the correct text is set to the LCD
        menu.refresh_text()
        lcd.clear.assert_called()
        lcd.message.assert_called_with('Item 1\nOption 1')
