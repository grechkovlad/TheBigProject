import threading

import keyboard
import numpy as np
from cvpubsubs.webcam_pub import VideoHandlerThread

from targetplatform import *


class HackSimulator:

    def __init__(self, rom, show_screen=False, fps_limit=10):
        self._ram = [0] * RAM_SIZE
        self._rom = rom
        self._D = 0
        self._A = 0
        self._PC = 0
        self._show_screen = show_screen
        self._ticks = 0
        if show_screen:
            self._screen = np.ones((SCREEN_HEIGHT, SCREEN_WIDTH))
            self._video_handler_thread = VideoHandlerThread(video_source=self._screen,
                                                            callbacks=lambda frame, cam_id: self._screen,
                                                            fps_limit=fps_limit)

    def run(self, max_ticks=None):
        if self._show_screen:
            thread = threading.Thread(target=lambda: self._video_handler_thread.display())
            thread.start()
        while self._PC < len(self._rom) and (not max_ticks or self._ticks < max_ticks):
            self.run_next_cmd()

    def run_next_cmd(self):
        if self._PC >= len(self._rom):
            raise ValueError("The program is over!")
        self._ticks = self._ticks + 1
        cmd = self._rom[self._PC]
        self._PC = self._PC + 1
        if get_nth_bit(cmd, 15) == 0:
            self._run_a_cmd(cmd)
        else:
            self._run_c_cmd(cmd)

    def _run_a_cmd(self, cmd):
        self._A = set_nth_bit_zero(cmd, 15)

    def _run_c_cmd(self, cmd):
        dest, comp, jump = parse_c_cmd(cmd)
        comp_res = self._calc_comp(comp)
        self._write_to_dest(dest, comp_res)
        self._jump(comp_res, jump)

    def _calc_comp(self, comp):
        if get_nth_bit(comp, 6) == 0:
            return comp_dict_a0[comp](self._A, self._D) & BIT_MASK_16
        m = self._get_m()
        return comp_dict_a1[set_nth_bit_zero(comp, 6)](m, self._D) & BIT_MASK_16

    def _write_to_dest(self, dest, val):
        if get_nth_bit(dest, 0) == 1:
            self._write_to_m(val)
        if get_nth_bit(dest, 1) == 1:
            self._D = val
        if get_nth_bit(dest, 2) == 1:
            self._A = val;

    def _write_to_m(self, val):
        if self._A == KEYBOARD:
            return
        if get_nth_bit(self._A, 15) == 1 or self._A >= RAM_SIZE:
            raise ValueError("Illegal address while writing to RAM: %d" % self._A)
        self._ram[self._A] = val
        if self._show_screen and SCREEN_BEGIN <= self._A <= SCREEN_END:
            self._draw_pixels_batch(self._A - SCREEN_BEGIN, self._ram[self._A])

    def _jump(self, comp_res, jump):
        if jump_dict[jump](comp_res):
            self._PC = self._A

    def _draw_pixels_batch(self, batch_num, val):
        row = batch_num >> 5
        col = batch_num & 0b11111
        for i in range(0, BITS):
            self._screen[row][(col << 4) + i] = (~get_nth_bit(val, i) & 1)

    def _get_m(self):
        if self._A != KEYBOARD:
            if self._A < 0 or self._A >= RAM_SIZE:
                raise ValueError("Illegal address while reading from RAM")
            return self._ram[self._A]
        keys_pressed = keyboard.get_hotkey_name()
        if len(keys_pressed) == 0:
            return 0
        if len(keys_pressed) == 1:
            return ord(keys_pressed)
        if keys_pressed in key_dict.keys():
            return key_dict[keys_pressed]
        return 0
