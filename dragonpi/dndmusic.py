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

"""Monitor the keyboard numberpad and play music for certain
key-presses."""

import logging
log = logging.getLogger(__name__)
import os
import time

from pynput import keyboard
import vlc

THIS_DIR = os.path.abspath(os.path.dirname(__file__))
MUSIC_DIR = os.path.join(THIS_DIR, 'audio/')

# Cross fade intervals, in second
FADE_TIME = 1.5
BATTLE_FADE_TIME = 0.3
VICTORY_FADE_TIME = 0.2

key_from_char = keyboard.KeyCode.from_char
key_from_vk = keyboard.KeyCode.from_vk

class MusicListener(keyboard.Listener):
    # List of key assignments: (song_file, volume, fade_time)
    key_assignments = {
        key_from_char('1'): ('battle_music_1.mp3', 100, BATTLE_FADE_TIME),
        # key_from_char('000'): ('battle_music_2.mp3', 100, FADE_TIME),
        key_from_char('4'): ('battle_music_2.mp3', 100, BATTLE_FADE_TIME),
        key_from_char('7'): ('battle_music_3.mp3', 100, BATTLE_FADE_TIME),
        key_from_char('9'): ('forest_sounds_1.mp3', 100, FADE_TIME),
        key_from_char('.'): ('town_sounds_1.mp3', 100, FADE_TIME),
        key_from_char(','): ('town_sounds_1.mp3', 100, FADE_TIME),
        key_from_char('3'): ('tavern_sounds_1.mp3', 100, FADE_TIME),
        key_from_char('6'): ('cave_sounds_1.m4a', 100, FADE_TIME),
        key_from_char('/'): ('goblins_1.opus', 100, FADE_TIME),
        # key_from_vk(65437): ('crowded_bar_1.opus', 100, FADE_TIME),
        key_from_char('*'): ('orc_grunts.m4a', 100, FADE_TIME),
        key_from_char('2'): ('holst_neptune.opus', 100, FADE_TIME),
        key_from_char('5'): ('holst_saturn.opus', 100, FADE_TIME),
        key_from_vk(65437): ('holst_saturn.opus', 100, FADE_TIME),
        key_from_char('8'): ('holst_mars.ogg', 100, FADE_TIME),
        keyboard.Key.enter: ('Stop', None, None),
        keyboard.Key.backspace: ('Pause', None, None),
        key_from_char('-'): ('VolDown', None, None),
        key_from_char('+'): ('VolUp', None, None),
        key_from_char('0'): ('victory_fanfare.m4a', 100, VICTORY_FADE_TIME),
        # key_from_char('/'): (None, None, None),
    }
    _player = None
    volume = 100
    fade_steps = 30
    min_volume = 0
    max_volume = 100
    
    def __init__(self, *args, **kwargs):
        self.instance = vlc.Instance('--input-repeat=999999', '--quiet')
        # Setup the keyboard listener
        super().__init__(on_press=self.on_press, *args, **kwargs)
   
    def stop_music(self, fade_time=FADE_TIME):
        if self._player is not None:
            log.debug('Stopping music')
            self.fade_volume(0, fade_time=fade_time)
            self._player.stop()
            # Remove the VLC media player
            del self._player
            self._player = None
    
    def fade_volume(self, target, fade_time=FADE_TIME):
        if self._player is not None:
            init_vol = self._player.audio_get_volume()
            curr_vol = init_vol
            delta_vol = target - init_vol
            # Fade in the volume
            for i in range(self.fade_steps):
                curr_vol = curr_vol + delta_vol/self.fade_steps
                log.debug("Volume set to %d", round(curr_vol))
                self._player.audio_set_volume(round(curr_vol))
                time.sleep(fade_time / self.fade_steps)
            log.debug('Faded volume from %d to %d', init_vol, round(curr_vol))
    
    def start_music(self, song_file, fade_time):
        if os.path.exists(song_file):
            log.info("Starting song: %s", song_file)
            self._player = self.instance.media_player_new(f'file://{song_file}')
            self._player.audio_set_volume(0)
            self._player.play()
            time.sleep(0.01)
            self.fade_volume(self.volume, fade_time=fade_time)
        else:
            log.error('Song file not found: %s', song_file)
    
    def toggle_pause(self):
        if self._player is not None:
            log.debug("Paused music")
            self._player.pause()
    
    def on_press(self, key):
        log.debug("Pressed key %s", key)
        (action, vol, fade_time) = self.key_assignments.get(key, (None, None, None))
        if action == "Stop":
            self.stop_music(fade_time=FADE_TIME)
        elif action == 'VolUp':
            self.change_volume(10)
        elif action == 'VolDown':
            self.change_volume(-10)
        elif action == 'Pause':
            self.toggle_pause()
        elif action is not None:
            vol_ratio = vol / 100 if vol is not None else 1
            self.volume *= vol_ratio
            song_file = os.path.join(MUSIC_DIR, action)
            self.stop_music(fade_time=fade_time)
            self.start_music(song_file, fade_time=fade_time)
    
    def change_volume(self, delta_vol):
        new_vol = self.volume + delta_vol
        old_vol = self.volume
        # Make sure the new volume is within 0 and 100
        new_vol = min(new_vol, self.max_volume)
        new_vol = max(new_vol, self.min_volume)
        # Execute the volume change
        if self.volume != new_vol:
            self.volume = new_vol
            self.fade_volume(self.volume, fade_time=0.05)
            log.debug("Changed volume from %d to %d", old_vol, new_vol)
        else:
            log.info("Volume NOT changed from %d to %d", old_vol, new_vol)
    
    def join(self, *args, **kwargs):
        log.info("D&D Music started. Waiting for keypress...")
        return super().join(*args, **kwargs)
