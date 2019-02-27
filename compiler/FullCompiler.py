from compiler import JackCompiler
from compiler import VmTranslator
from compiler import Assembler
from os.path import join
from os.path import isfile
from os.path import splitext
from os.path import basename


def compile_jack(source, target):
    """Compile Jack code from source to VM, ASM, and HACK code

    Keyword arguments:
    source - a single file or a directory with jack source code
    target - a directory for storing
    result in. target/vm, target/asm, target/hack will contain vm, asm, and hack code respectively
    """

    project_name = splitext(basename(source))[0] if isfile(source) else basename(source)
    vm_code_dir, asm_code_dir, hack_code_dir = join(target, "vm"), join(target, "asm"), join(target, "hack")
    asm_file = join(asm_code_dir, project_name + ".asm")
    JackCompiler.main(source, vm_code_dir)
    VmTranslator.main(vm_code_dir, asm_file)
    Assembler.main(asm_file, join(hack_code_dir, project_name + ".hack"))
