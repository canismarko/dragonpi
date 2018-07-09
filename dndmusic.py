#!/usr/bin/env python3

"""Monitor the keyboard numberpad and play music for certain
key-presses."""

import logging
log = logging.getLogger(__name__)
import os
import time

from pynput import keyboard
import vlc

MUSIC_DIR = os.path.abspath(os.path.dirname(__file__))
# MUSIC_DIR = '/home/mwolf/src/dndmusic/'


class Player():
    key_assignments = {
        keyboard.KeyCode.from_char('0'): os.path.join(MUSIC_DIR, 'battle_music_1.mp3'),
        keyboard.KeyCode.from_char('000'): os.path.join(MUSIC_DIR, 'battle_music_2.mp3'),
        keyboard.KeyCode.from_char('.'): os.path.join(MUSIC_DIR, 'battle_music_3.mp3'),
        keyboard.KeyCode.from_char(','): os.path.join(MUSIC_DIR, 'battle_music_3.mp3'),
        keyboard.KeyCode.from_char('1'): os.path.join(MUSIC_DIR, 'forest_sounds_1.mp3'),
        keyboard.KeyCode.from_char('2'): os.path.join(MUSIC_DIR, 'town_sounds_1.mp3'),
        keyboard.KeyCode.from_char('3'): os.path.join(MUSIC_DIR, 'tavern_sounds_1.mp3'),
        keyboard.KeyCode.from_char('4'): os.path.join(MUSIC_DIR, 'cave_sounds_1.m4a'),
        keyboard.KeyCode.from_char('5'): os.path.join(MUSIC_DIR, 'crowded_bar_1.opus'),
        keyboard.KeyCode.from_vk(65437): None,
        keyboard.KeyCode.from_char('6'): os.path.join(MUSIC_DIR, 'orc_grunts.m4a'),
        keyboard.KeyCode.from_char('7'): os.path.join(MUSIC_DIR, 'holst_neptune.opus'),
        keyboard.KeyCode.from_char('8'): os.path.join(MUSIC_DIR, 'holst_saturn.opus'),
        keyboard.KeyCode.from_char('9'): os.path.join(MUSIC_DIR, 'holst_mars.ogg'),
        keyboard.Key.enter: 'Stop',
        keyboard.Key.backspace: 'Pause',
        keyboard.KeyCode.from_char('-'): 'VolDown',
        keyboard.KeyCode.from_char('+'): 'VolUp',
        keyboard.KeyCode.from_char('*'): os.path.join(MUSIC_DIR, 'victory_fanfare.m4a'),
        keyboard.KeyCode.from_char('/'): None,
    }
    _player = None
    volume = 100
    fade_steps = 30
    min_volume = 0
    max_volume = 100
    
    def __init__(self):
        self.instance = vlc.Instance('--input-repeat=999999', '--quiet')
   
    def stop_music(self):
        if self._player is not None:
            log.debug('Stopping music')
            self.fade_volume(0)
            self._player.stop()
            # Remove the VLC media player
            del self._player
            self._player = None
    
    def fade_volume(self, target, fade_time=1.5):
        if self._player is not None:
            init_vol = self._player.audio_get_volume()
            curr_vol = init_vol
            delta_vol = target - init_vol
            # Fade in the volume
            for i in range(self.fade_steps):
                curr_vol = curr_vol + delta_vol/self.fade_steps
                self._player.audio_set_volume(round(curr_vol))
                time.sleep(fade_time / self.fade_steps)
            log.debug('Faded volume from %d to %d', init_vol, round(curr_vol))
    
    def start_music(self, song_file):
        if os.path.exists(song_file):
            log.info("Starting song: %s", song_file)
            self._player = self.instance.media_player_new(f'file://{song_file}')
            self._player.audio_set_volume(0)
            self._player.play()
            time.sleep(0.1)
            self.fade_volume(self.volume)
        else:
            log.error('Song file not found: %s', song_file)
    
    def toggle_pause(self):
        if self._player is not None:
            log.debug("Paused music")
            self._player.pause()
    
    def on_press(self, key):
        log.debug("Pressed key %s", key)
        action = self.key_assignments.get(key, None)
        if action == "Stop":
            self.stop_music()
        elif action == 'VolUp':
            self.change_volume(10)
        elif action == 'VolDown':
            self.change_volume(-10)
        elif action == 'Pause':
            self.toggle_pause()
        elif action is not None:
            self.stop_music()
            self.start_music(action)
    
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

def monitor_keypresses():
    player = Player()
    listener = keyboard.Listener(on_press=player.on_press)
    with listener:
        log.info("D&D Music started. Waiting for keypress...")
        listener.join()

def main():
    monitor_keypresses()

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()
