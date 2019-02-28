import unittest
from compiler import Assembler
from os import remove
from os.path import exists


class TestAssembler(unittest.TestCase):
    def test_max(self):
        if exists('Max.hack'):
            remove('Max.hack')
        Assembler.main('Max.asm', 'Max.hack')
        actual = list(open('Max.hack').readlines())
        expected = list(open('Max_etalon.hack').readlines())
        self.assertEqual(actual, expected)

    def test_pong(self):
        if exists('Pong.hack'):
            remove('Pong.hack')
        Assembler.main('Pong.asm', 'Pong.hack')
        actual = list(open('Pong.hack').readlines())
        expected = list(open('Pong_etalon.hack').readlines())
        self.assertEqual(actual, expected)
