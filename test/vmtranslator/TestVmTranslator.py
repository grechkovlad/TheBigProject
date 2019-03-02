import unittest
from test.vmtranslator import vm_to_hack
from targetplatform.HackSimulator import HackSimulator
from targetplatform import read_program


class MyTestCase(unittest.TestCase):
    def test_basic_test(self):
        hack_program_file = "BasicTest.hack"
        vm_to_hack("BasicTest.vm", hack_program_file)
        platform = HackSimulator(read_program(hack_program_file))
        platform._ram[0] = 256
        platform._ram[1] = 300
        platform._ram[2] = 400
        platform._ram[3] = 3000
        platform._ram[4] = 3010
        platform.run(max_ticks=600)
        self.assertEqual(platform._ram[256], 472)
        self.assertEqual(platform._ram[300], 10)
        self.assertEqual(platform._ram[401], 21)
        self.assertEqual(platform._ram[402], 22)
        self.assertEqual(platform._ram[3006], 36)
        self.assertEqual(platform._ram[3012], 42)
        self.assertEqual(platform._ram[3015], 45)
        self.assertEqual(platform._ram[11], 510)

    def test_pointer_test(self):
        hack_program_file = "PointerTest.hack"
        vm_to_hack("PointerTest.vm", hack_program_file)
        platform = HackSimulator(read_program(hack_program_file))
        platform._ram[0] = 256
        platform.run(max_ticks=450)
        self.assertEqual(platform._ram[256], 6084)
        self.assertEqual(platform._ram[3], 3030)
        self.assertEqual(platform._ram[4], 3040)
        self.assertEqual(platform._ram[3032], 32)
        self.assertEqual(platform._ram[3046], 46)

    def test_static_test(self):
        hack_program_file = "StaticTest.hack"
        vm_to_hack("StaticTest.vm", hack_program_file)
        platform = HackSimulator(read_program(hack_program_file))
        platform._ram[0] = 256
        platform.run(max_ticks=200)
        self.assertEqual(platform._ram[256], 1110)

    def test_simple_add(self):
        hack_program_file = "SimpleAdd.hack"
        vm_to_hack("SimpleAdd.vm", hack_program_file)
        platform = HackSimulator(read_program(hack_program_file))
        platform._ram[0] = 256
        platform.run(max_ticks=200)
        self.assertEqual(platform._ram[0], 257)
        self.assertEqual(platform._ram[256], 15)

    def test_stack_test(self):
        hack_program_file = "StackTest.hack"
        vm_to_hack("StackTest.vm", hack_program_file)
        platform = HackSimulator(read_program(hack_program_file))
        platform._ram[0] = 256
        platform.run(max_ticks=1000)
        self.assertEqual(platform._ram[0], 266)
        self.assertEqual(platform._ram[256], 0b1111111111111111)
        self.assertEqual(platform._ram[257], 0)
        self.assertEqual(platform._ram[258], 0)
        self.assertEqual(platform._ram[259], 0)
        self.assertEqual(platform._ram[260], 0b1111111111111111)
        self.assertEqual(platform._ram[261], 0)
        self.assertEqual(platform._ram[262], 0b1111111111111111)
        self.assertEqual(platform._ram[263], 0)
        self.assertEqual(platform._ram[264], 0)
        self.assertEqual(platform._ram[265], 0b1111111110100101)