def get_nth_bit(val, nth):
    if (val & (1 << nth)) == 0:
        return 0
    return 1


def set_nth_bit_zero(val, nth):
    return val & (~(1 << nth))


comp_dict_a0 = {
    0b101010: lambda a, d: 0,
    0b111111: lambda a, d: 1,
    0b111010: lambda a, d: -1,
    0b001100: lambda a, d: d,
    0b110000: lambda a, d: a,
    0b001101: lambda a, d: ~d,
    0b110001: lambda a, d: ~a,
    0b001111: lambda a, d: -d,
    0b110011: lambda a, d: -a,
    0b011111: lambda a, d: d + 1,
    0b110111: lambda a, d: a + 1,
    0b001110: lambda a, d: d - 1,
    0b110010: lambda a, d: a - 1,
    0b000010: lambda a, d: d + a,
    0b010011: lambda a, d: d - a,
    0b000111: lambda a, d: a - d,
    0b000000: lambda a, d: d & a,
    0b010101: lambda a, d: d | a
}

comp_dict_a1 = {
    0b110000: lambda m, d: m,
    0b110001: lambda m, d: ~m,
    0b110011: lambda m, d: -m,
    0b110111: lambda m, d: m + 1,
    0b110010: lambda m, d: m - 1,
    0b000010: lambda m, d: d + m,
    0b010011: lambda m, d: d - m,
    0b000111: lambda m, d: m - d,
    0b000000: lambda m, d: d & m,
    0b010101: lambda m, d: d | m
}

jump_dict = {
    0b000: lambda val: False,
    0b001: lambda val: val != 0 and get_nth_bit(val, BITS - 1) == 0,
    0b010: lambda val: val == 0,
    0b011: lambda val: get_nth_bit(val, BITS - 1) == 0,
    0b100: lambda val: get_nth_bit(val, BITS - 1) == 1,
    0b101: lambda val: val != 0,
    0b110: lambda val: val == 0 or get_nth_bit(val, BITS - 1) == 1,
    0b111: lambda val: True
}

key_dict = {
    'enter': 128,
    'backspace': 129,
    'left': 130,
    'up': 131,
    'right': 132,
    'down': 133,
    'home': 134,
    'end': 135,
    'page up': 136,
    'page down': 137,
    'insert': 138,
    'delete': 139,
    'esc': 140,
    'f1': 141,
    'f2': 142,
    'f3': 143,
    'f4': 144,
    'f5': 145,
    'f6': 146,
    'f7': 147,
    'f8': 148,
    'f9': 149,
    'f10': 150,
    'f11': 151,
    'f12': 152
}


def parse_c_cmd(cmd):
    return (cmd & 0b0000000000111000) >> 3, (cmd & 0b0001111111000000) >> 6, (cmd & 0b0000000000000111)


RAM_SIZE = 24577
ROM_SIZE = pow(2, 15)
BITS = 16
SCREEN_BEGIN = 16384
SCREEN_END = 24575
KEYBOARD = 24576
BIT_MASK_16 = 0b1111111111111111
SCREEN_HEIGHT = 256
SCREEN_WIDTH = 512
