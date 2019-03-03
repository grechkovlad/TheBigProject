import unittest
from test.vmtranslator import vm_to_hack
from targetplatform.HackSimulator import HackSimulator
from targetplatform import read_program


class VmTranslatorTestCase(unittest.TestCase):
    def _get_platform_to_run(self):
        hack_program_file = self._get_test_name() + ".hack"
        vm_to_hack(self._get_vm_source_path(), hack_program_file)
        platform = HackSimulator(read_program(hack_program_file))
        return platform

    def tearDown(self):
        from os.path import exists
        from os import remove
        if exists(self._get_test_name() + ".hack"):
            remove(self._get_test_name() + ".hack")


class VmTranslatorSingleFileTestCase(VmTranslatorTestCase):
    def _get_vm_source_path(self):
        return self._get_test_name() + ".vm"


class VmTranslatorDirectoryTestCase(VmTranslatorTestCase):
    def _get_vm_source_path(self):
        return self._get_test_name()


class BasicTestCase(VmTranslatorSingleFileTestCase):
    def _get_test_name(self):
        return "BasicTest"

    def test_case(self):
        platform = self._get_platform_to_run()
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


class PointerTestCase(VmTranslatorSingleFileTestCase):
    def _get_test_name(self):
        return "PointerTest"

    def test_case(self):
        platform = self._get_platform_to_run()
        platform._ram[0] = 256
        platform.run(max_ticks=450)
        self.assertEqual(platform._ram[256], 6084)
        self.assertEqual(platform._ram[3], 3030)
        self.assertEqual(platform._ram[4], 3040)
        self.assertEqual(platform._ram[3032], 32)
        self.assertEqual(platform._ram[3046], 46)


class StaticTestCase(VmTranslatorSingleFileTestCase):
    def _get_test_name(self):
        return "StaticTest"

    def test_case(self):
        platform = self._get_platform_to_run()
        platform._ram[0] = 256
        platform.run(max_ticks=200)
        self.assertEqual(platform._ram[256], 1110)


class SimpleAddTestCase(VmTranslatorSingleFileTestCase):
    def _get_test_name(self):
        return "SimpleAdd"

    def test_case(self):
        platform = self._get_platform_to_run()
        platform._ram[0] = 256
        platform.run(max_ticks=200)
        self.assertEqual(platform._ram[0], 257)
        self.assertEqual(platform._ram[256], 15)


class StackTestCase(VmTranslatorSingleFileTestCase):
    def _get_test_name(self):
        return "StackTest"

    def test_case(self):
        platform = self._get_platform_to_run()
        platform._ram[0] = 256
        platform.run(max_ticks=1000)
        self.assertEqual(platform._ram[0], 266)
        self.assertEqual(platform._ram[256], 0b1111111111111111)
        self.assertEqual(platform._ram[257], 0)
        self.assertEqual(platform._ram[258], 0)
        self.assertEqual(platform._ram[259], 0)
        self.assertNotEqual(platform._ram[260], 0)
        self.assertEqual(platform._ram[261], 0)
        self.assertNotEqual(platform._ram[262], 0)
        self.assertEqual(platform._ram[263], 0)
        self.assertEqual(platform._ram[264], 0)
        self.assertEqual(platform._ram[265], 0b1111111110100101)


class BasicLoopTestCase(VmTranslatorSingleFileTestCase):
    def _get_test_name(self):
        return "BasicLoop"

    def test_case(self):
        platform = self._get_platform_to_run()
        platform._ram[0] = 256
        platform._ram[1] = 300
        platform._ram[2] = 400
        platform._ram[400] = 3
        platform.run(max_ticks=600)
        self.assertEqual(platform._ram[0], 257)
        self.assertEqual(platform._ram[256], 6)


class FibonacciTestCase(VmTranslatorSingleFileTestCase):
    def _get_test_name(self):
        return "FibonacciSeries"

    def test_case(self):
        platform = self._get_platform_to_run()
        platform._ram[0] = 256
        platform._ram[1] = 300
        platform._ram[2] = 400
        platform._ram[400] = 6
        platform._ram[401] = 3000
        platform.run(max_ticks=1100)
        self.assertEqual(platform._ram[3000], 0)
        self.assertEqual(platform._ram[3001], 1)
        self.assertEqual(platform._ram[3002], 1)
        self.assertEqual(platform._ram[3003], 2)
        self.assertEqual(platform._ram[3004], 3)
        self.assertEqual(platform._ram[3005], 5)


class SimpleFunctionTestCase(VmTranslatorSingleFileTestCase):
    def _get_test_name(self):
        return "SimpleFunction"

    def test_case(self):
        platform = self._get_platform_to_run()
        platform._ram[0] = 317
        platform._ram[1] = 317
        platform._ram[2] = 310
        platform._ram[3] = 3000
        platform._ram[4] = 4000
        platform._ram[310] = 1234
        platform._ram[311] = 37
        platform._ram[312] = 1000
        platform._ram[313] = 305
        platform._ram[314] = 300
        platform._ram[315] = 3010
        platform._ram[316] = 4010
        platform.run(max_ticks=300)
        self.assertEqual(platform._ram[0], 311)
        self.assertEqual(platform._ram[1], 305)
        self.assertEqual(platform._ram[2], 300)
        self.assertEqual(platform._ram[3], 3010)
        self.assertEqual(platform._ram[4], 4010)
        self.assertEqual(platform._ram[310], 1196)


class NestedCallTestCase(VmTranslatorDirectoryTestCase):
    def _get_test_name(self):
        return "NestedCall"

    def test_case(self):
        platform = self._get_platform_to_run()
        platform._ram[0] = 261
        platform._ram[1] = 261
        platform._ram[2] = 256
        platform._ram[3] = 0b1111111111111101
        platform._ram[4] = 0b1111111111111100
        platform._ram[5] = 0b1111111111111111
        platform._ram[6] = 0b1111111111111111
        platform._ram[256] = 1234
        platform._ram[257] = 0b1111111111111111
        platform._ram[258] = 0b1111111111111110
        platform._ram[259] = 0b1111111111111101
        platform._ram[260] = 0b1111111111111100
        platform._ram[261] = 0b1111111111111111
        platform._ram[262] = 0b1111111111111111
        platform._ram[263] = 0b1111111111111111
        platform._ram[264] = 0b1111111111111111
        platform._ram[265] = 0b1111111111111111
        platform._ram[266] = 0b1111111111111111
        platform._ram[267] = 0b1111111111111111
        platform._ram[268] = 0b1111111111111111
        platform._ram[269] = 0b1111111111111111
        platform._ram[270] = 0b1111111111111111
        platform._ram[271] = 0b1111111111111111
        platform._ram[272] = 0b1111111111111111
        platform._ram[273] = 0b1111111111111111
        platform._ram[274] = 0b1111111111111111
        platform._ram[275] = 0b1111111111111111
        platform._ram[276] = 0b1111111111111111
        platform._ram[277] = 0b1111111111111111
        platform._ram[278] = 0b1111111111111111
        platform._ram[279] = 0b1111111111111111
        platform._ram[280] = 0b1111111111111111
        platform._ram[281] = 0b1111111111111111
        platform._ram[282] = 0b1111111111111111
        platform._ram[283] = 0b1111111111111111
        platform._ram[284] = 0b1111111111111111
        platform._ram[285] = 0b1111111111111111
        platform._ram[286] = 0b1111111111111111
        platform._ram[287] = 0b1111111111111111
        platform._ram[288] = 0b1111111111111111
        platform._ram[289] = 0b1111111111111111
        platform._ram[290] = 0b1111111111111111
        platform._ram[291] = 0b1111111111111111
        platform._ram[292] = 0b1111111111111111
        platform._ram[293] = 0b1111111111111111
        platform._ram[294] = 0b1111111111111111
        platform._ram[295] = 0b1111111111111111
        platform._ram[296] = 0b1111111111111111
        platform._ram[297] = 0b1111111111111111
        platform._ram[298] = 0b1111111111111111
        platform._ram[299] = 0b1111111111111111
        platform.run(max_ticks=4000)
        self.assertEqual(platform._ram[0], 261)
        self.assertEqual(platform._ram[1], 261)
        self.assertEqual(platform._ram[2], 256)
        self.assertEqual(platform._ram[3], 4000)
        self.assertEqual(platform._ram[4], 5000)
        self.assertEqual(platform._ram[5], 135)
        self.assertEqual(platform._ram[6], 246)


class StaticHard(VmTranslatorDirectoryTestCase):
    def _get_test_name(self):
        return "StaticTest"

    def test_case(self):
        platform = self._get_platform_to_run()
        platform._ram[0] = 256
        platform.run(max_ticks=2500)
        self.assertEqual(platform._ram[0], 263)
        self.assertEqual(platform._ram[261], 0b1111111111111110)
        self.assertEqual(platform._ram[262], 8)


class FibonacciHardTestCase(VmTranslatorDirectoryTestCase):
    def _get_test_name(self):
        return "FibonacciElement"

    def test_case(self):
        platform = self._get_platform_to_run()
        platform.run(max_ticks=6000)
        self.assertEqual(platform._ram[0], 262)
        self.assertEqual(platform._ram[261], 3)
