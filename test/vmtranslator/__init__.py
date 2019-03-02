
def vm_to_hack(source, target):
    from compiler import VmTranslator, Assembler
    from os.path import exists
    from os import remove
    temp_asm_file = "temp.asm"
    if exists(temp_asm_file):
        remove(temp_asm_file)
    VmTranslator.main(source, temp_asm_file)
    Assembler.main(temp_asm_file, target)
    if exists(temp_asm_file):
        remove(temp_asm_file)