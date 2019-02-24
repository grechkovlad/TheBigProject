import unittest

from targetplatform import get_nth_bit, set_nth_bit_zero, parse_c_cmd, RAM_SIZE
from targetplatform.HackSimulator import HackSimulator


def _is_ram_clear(ram):
    for i in range(0, RAM_SIZE):
        if ram[i] != 0:
            return False
    return True


class MyTestCase(unittest.TestCase):

    def test_bit_operations(self):
        self.assertEqual(get_nth_bit(0b0101010101010101, 0), 1)
        self.assertEqual(get_nth_bit(0b0101010101010101, 1), 0)
        self.assertEqual(get_nth_bit(0b0101010101010101, 4), 1)
        self.assertEqual(get_nth_bit(0b0101010101010101, 14), 1)
        self.assertEqual(get_nth_bit(0b0101010101010101, 15), 0)

        self.assertEqual(set_nth_bit_zero(0b0101010101010101, 0), 0b0101010101010100)
        self.assertEqual(set_nth_bit_zero(0b0101010101010101, 1), 0b0101010101010101)
        self.assertEqual(set_nth_bit_zero(0b0101010101010101, 4), 0b0101010101000101)


    def test_parse_c_cmd(self):
        dest, comp, jump = parse_c_cmd(0b1110000111011001)
        self.assertEqual(dest, 0b011)
        self.assertEqual(comp, 0b000111)
        self.assertEqual(jump, 0b001)

        dest, comp, jump = parse_c_cmd(0b1111110011110110)
        self.assertEqual(dest, 0b110)
        self.assertEqual(comp, 0b1110011)
        self.assertEqual(jump, 0b110)

    def test_default_run(self):
        platform = HackSimulator([0])
        platform.run_next_cmd()
        self.assertTrue(_is_ram_clear(platform._ram))

    def test_simple_a_cmd(self):
        platform = HackSimulator([0b0101010101010100])
        self.assertEqual(platform._A, 0b0)
        platform.run_next_cmd()
        self.assertEqual(platform._A, 0b101010101010100)
        self.assertEqual(platform._D, 0b0)
        self.assertTrue(_is_ram_clear(platform._ram))

    def test_simple_c_cmd(self):
        platform = HackSimulator([0b1111000010011001])
        platform._D = 5;
        platform._A = 7;
        platform._ram[platform._A] = -1
        platform.run_next_cmd()
        self.assertEqual(platform._D, 4)
        self.assertEqual(platform._ram[platform._A], 4)
        self.assertEqual(platform._A, 7)
        self.assertEqual(platform._PC, 7)

    def test_add_program(self):
        platform = HackSimulator([0b0000000000000010,
                                  0b1110110000010000,
                                  0b0000000000000011,
                                  0b1110000010010000,
                                  0b0000000000000000,
                                  0b1110001100001000])
        platform.run()
        self.assertEqual(platform._ram[0], 5)

    def test_max_program(self):
        platform = HackSimulator([0b0000000000000000,
                                  0b1111110000010000,
                                  0b0000000000000001,
                                  0b1111010011010000,
                                  0b0000000000001010,
                                  0b1110001100000001,
                                  0b0000000000000001,
                                  0b1111110000010000,
                                  0b0000000000001100,
                                  0b1110101010000111,
                                  0b0000000000000000,
                                  0b1111110000010000,
                                  0b0000000000000010,
                                  0b1110001100001000,
                                  0b0000000000001110,
                                  0b1110101010000111])
        platform._ram[0] = 12;
        platform._ram[1] = 9;
        platform.run(20)
        self.assertEqual(platform._ram[2], 12)

    def test_mult_program(self):
        platform = HackSimulator([0b0000000000000010,
                                  0b1110101010001000,
                                  0b0000000000000000,
                                  0b1111110000010000,
                                  0b0000000000001110,
                                  0b1110001100000010,
                                  0b0000000000000001,
                                  0b1111110000010000,
                                  0b0000000000000010,
                                  0b1111000010001000,
                                  0b0000000000000000,
                                  0b1111110010001000,
                                  0b0000000000000010,
                                  0b1110101010000111,
                                  0b0000000000001110,
                                  0b1110101010000111])
        platform._ram[0] = 4
        platform._ram[1] = 5
        platform.run(50)
        self.assertEqual(platform._ram[2], 20)

    def test_rect_draw(self):
        platform = HackSimulator([0b0000000000000000,
                                  0b1111110000010000,
                                  0b0000000000010111,
                                  0b1110001100000110,
                                  0b0000000000010000,
                                  0b1110001100001000,
                                  0b0100000000000000,
                                  0b1110110000010000,
                                  0b0000000000010001,
                                  0b1110001100001000,
                                  0b0000000000010001,
                                  0b1111110000100000,
                                  0b1110111010001000,
                                  0b0000000000010001,
                                  0b1111110000010000,
                                  0b0000000000100000,
                                  0b1110000010010000,
                                  0b0000000000010001,
                                  0b1110001100001000,
                                  0b0000000000010000,
                                  0b1111110010011000,
                                  0b0000000000001010,
                                  0b1110001100000001,
                                  0b0000000000010111,
                                  0b1110101010000111
                                  ])
        platform._ram[0] = 10
        platform.run(150)
        rect_addrs = [16384, 16416, 16448, 16480, 16512, 16544, 16576, 16608, 16640, 16672]
        for addr in rect_addrs:
            self.assertEqual(platform._ram[addr], 0b1111111111111111)
        self.assertEqual(platform._ram[0], 10)
        self.assertEqual(platform._ram[17], 16704)

    def test_basic_loop(self):
        loop_prog = list(map(lambda str: int(str, 2), open('basic_loop.hack').readlines()))
        platform = HackSimulator(loop_prog)
        platform._ram[0] = 256
        platform._ram[1] = 300
        platform._ram[2] = 400
        platform._ram[400] = 5
        platform.run()
        self.assertEqual(platform._ram[256], 15)

    def test_byte_overflow(self):
        platform = HackSimulator([0b0111111111111111,
                                  0b1110110000010000,
                                  0b0000000000000000,
                                  0b1110001100001000,
                                  0b1111000010001000,
                                  0b1111110111001000,
                                  0b1111110111001000
                                  ])
        platform.run()
        self.assertEqual(platform._ram[0], 0)

        platform = HackSimulator([0b1110111010001000])
        platform.run()
        self.assertEqual(platform._ram[0], 0b1111111111111111)

        platform = HackSimulator([0b0000000000000100,
                                  0b1110111010000100,
                                  0b0000000000000000,
                                  0b1110101010000111,
                                  0b0000000000000000,
                                  0b1110111111001000
                                  ])
        platform.run()
        self.assertEqual(platform._ram[0], 1)

    """
    def test_keyboard(self):
        pong_prog = list(map(lambda str : int(str, 2), open('D:/NAND/nand2tetris/projects/06/Pong.hack').readlines()))
        platform = HackSimulator(pong_prog, True)
        platform.run()

    """


if __name__ == '__main__':
    unittest.main()
