import sys

sourcePath = sys.argv[1]


def is_garbage(line):
    return (not without_comment(line)) or (without_comment(line).isspace());


def remove_garbage(program_param):
    return map(lambda line: line.strip(), filter(lambda line: not is_garbage(line), program_param));


def without_comment(line):
    if line.find('//') >= 0:
        return line[0: line.find('//')].strip();
    else:
        return line.strip();


def remove_inline_comments(program):
    return map(lambda line: without_comment(line), program);


def remove_labels_defs(program):
    return filter(lambda line: not is_label_definition(line), program);


with open(sourcePath, 'r') as sourceFile:
    program = sourceFile.readlines();


def is_label_definition(line):
    return line[0] == '(' and line[-1] == ')';


def get_label_name(line):
    return line[1:-1];


def set_predefined_symbols(symbol_table):
    for i in range(16):
        symbol_table['R' + str(i)] = str(i);
    symbol_table['SCREEN'] = '16384';
    symbol_table['KBD'] = '24576';
    symbol_table['SP'] = '0';
    symbol_table['LCL'] = '1';
    symbol_table['ARG'] = '2';
    symbol_table['THIS'] = '3';
    symbol_table['THAT'] = '4';


def collect_labels(program, symbol_table):
    current_op = 0;
    for line in program:
        if (is_label_definition(line)):
            symbol_table[get_label_name(line)] = current_op;
        else:
            current_op = current_op + 1;


def is_a_instr(line):
    return line[0] == '@';


def resolve_a_instr(line, symbol_table, current_addr):
    value = line[1:];
    if value.isdigit():
        return (line, current_addr);
    if value in symbol_table:
        return '@' + str(symbol_table[value]), current_addr;
    symbol_table[value] = current_addr;
    return '@' + str(current_addr), current_addr + 1;


def resolve_one_line(line, symbol_table, current_addr):
    if not is_a_instr(line):
        return line, current_addr;
    else:
        return resolve_a_instr(line, symbol_table, current_addr);


def resolve_symbols(program, symbol_table):
    current_addr = 16;
    for line in program:
        resolved_line, current_addr = resolve_one_line(line, symbol_table, current_addr);
        yield resolved_line;


def a_to_binary(a_instr):
    if int(a_instr[1:]) > 32767:
        raise ValueError("Program is too large!")
    return '{0:016b}'.format(int(a_instr[1:]))


def get_parts_of_c(c_instr):
    c_instr = c_instr.replace(" ", "")
    dest = '';
    jump = '';
    comp_l = 0;
    comp_r = len(c_instr);
    if c_instr.find('=') >= 0:
        comp_l = c_instr.find('=') + 1;
        dest = c_instr[:c_instr.find('=')];
    if c_instr.find(';') >= 0:
        comp_r = c_instr.find(';');
        jump = c_instr[c_instr.find(';') + 1:];
    comp = c_instr[comp_l:comp_r];
    return dest, comp, jump;


def jump_to_binary(jump):
    return {
        '': '000',
        'JGT': '001',
        'JEQ': '010',
        'JGE': '011',
        'JLT': '100',
        'JNE': '101',
        'JLE': '110',
        'JMP': '111'
    }[jump];


def dest_to_binary(dest):
    res = ['0', '0', '0'];
    if dest.find('A') >= 0:
        res[0] = '1';
    if dest.find('M') >= 0:
        res[2] = '1';
    if dest.find('D') >= 0:
        res[1] = '1';
    return ''.join(res);


def comp_to_binary(comp):
    return {
        '0': '0101010',
        '1': '0111111',
        '-1': '0111010',
        'D': '0001100',
        'A': '0110000',
        '!D': '0001101',
        '!A': '0110001',
        '-D': '0001111',
        '-A': '0110011',
        'D+1': '0011111',
        "A+1": '0110111',
        'D-1': '0001110',
        'A-1': '0110010',
        'D+A': '0000010',
        'D-A': '0010011',
        'A-D': '0000111',
        'D&A': '0000000',
        'D|A': '0010101',
        'M': '1110000',
        '!M': '1110001',
        '-M': '1110011',
        'M+1': '1110111',
        'M-1': '1110010',
        'D+M': '1000010',
        'D-M': '1010011',
        'M-D': '1000111',
        'D&M': '1000000',
        'M&D': '1000000',
        'D|M': '1010101',
        'M|D': '1010101',
        'M+D': '1000010'
    }[comp];


def c_to_binary(c_instr):
    dest, comp, jump = get_parts_of_c(c_instr);
    return '111' + comp_to_binary(comp) + dest_to_binary(dest) + jump_to_binary(jump);


def line_to_binary(line):
    if is_a_instr(line):
        return a_to_binary(line);
    else:
        return c_to_binary(line);


def to_binary(program):
    return map(lambda line: line_to_binary(line), program);


sensible_symbols = list(remove_inline_comments(remove_garbage(program)));
symbol_table = {};
set_predefined_symbols(symbol_table);
collect_labels(sensible_symbols, symbol_table);
resolved = resolve_symbols(remove_labels_defs(sensible_symbols), symbol_table);
binary = to_binary(resolved);

with open('res.hack', 'w') as out_file:
    out_file.write('\n'.join(binary))
