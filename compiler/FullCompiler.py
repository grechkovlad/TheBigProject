from compiler import JackCompiler
from compiler import VmTranslator
from compiler import Assembler
from os.path import join


def compile_jack(source, target):
    """Compile Jack code from source to VM, ASM, and HACK code

    Keyword arguments:
    source - a single file or a directory with jack source code
    target - a directory for storing
    result in. target/vm, target/asm, target/hack will contain vm, asm, and hack code respectively
    """

    vm_code_dir, asm_code_dir, hack_code_dir = join(target, "vm"), join(target, "asm"), join(target, "hack")
    JackCompiler.main(source, vm_code_dir)
    VmTranslator.main(vm_code_dir, asm_code_dir)
    Assembler.main(asm_code_dir, hack_code_dir)
