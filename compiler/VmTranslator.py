class Context:
    class_name = None
    cmp_count = 0
    func_name = ""
    ret_count = 0


class VmCmd:
    def translate(self):
        raise NotImplementedError()


class MemoryCmd(VmCmd):
    ...


class PushCmd(MemoryCmd):
    ...


class PushRegularSegmentCmd(PushCmd):
    def translate(self):
        return self._load_value_to_D() + self._push_D_to_stack()

    def __init__(self, name, val):
        self.name = name
        self.x = val

    def _load_value_to_D(self):
        if self.x == 0:
            return ['@%s' % self.name,
                    'A = M',
                    'D = M']
        if self.x == 1:
            return ['@%s' % self.name,
                    'A = M + 1',
                    'D = M']
        return ['@' + str(self.x),
                'D = A',
                '@' + self.name,
                'D = D + M',
                'A = D',
                'D = M']

    def _push_D_to_stack(self):
        return ['@SP',
                'M = M + 1',
                'A = M - 1',
                'M = D']


class PushConstCmd(PushCmd):
    def translate(self):
        if self.x == 0:
            return ['@SP',
                    'M = M + 1',
                    'A = M - 1',
                    'M = 0']
        if self.x == 1:
            return ['@SP',
                    'M = M + 1',
                    'A = M - 1',
                    'M = 1']
        return ['@' + str(self.x),
                'D = A',
                '@SP',
                'M = M + 1',
                'A = M - 1',
                'M = D']

    def __init__(self, val):
        self.x = val


class PushFixedSegmentCmd(PushCmd):

    def __init__(self, val):
        self.x = val


class PushStaticCmd(PushFixedSegmentCmd):
    def translate(self):
        return ['@%s' % Context.class_name + '.' + str(self.x),
                'D = M',
                '@SP',
                'M = M + 1',
                'A = M - 1',
                'M = D']


class PushTempCmd(PushFixedSegmentCmd):
    def translate(self):
        return ['@%d' % (5 + self.x),
                'D = M',
                '@SP',
                'M = M + 1',
                'A = M - 1',
                'M = D']


class PushPointerCmd(PushCmd):
    def __init__(self, segment_name):
        self.name = segment_name

    def translate(self):
        return ['@%s' % self.name,
                'D = M',
                '@SP',
                'M = M + 1',
                'A = M - 1',
                'M = D']


class PopCmd(MemoryCmd):
    ...


class PopRegularSegmentCmd(PopCmd):

    def __init__(self, segment_name, val):
        self._name = segment_name
        self.x = val

    def translate(self):
        return self._store_pointer_to_r13() + self._pop_to_pointer_r13()

    def _pop_to_pointer_r13(self):
        return ['@SP',
                'AM = M - 1',
                'D = M',
                '@R13',
                'A = M',
                'M = D']

    def _store_pointer_to_r13(self):
        if self.x == 0:
            return ['@' + self._name,
                    'D = M',
                    '@R13',
                    'M = D']
        if self.x == 1:
            return ['@' + self._name,
                    'D = M + 1',
                    '@R13',
                    'M = D']
        return ['@' + str(self.x),
                'D = A',
                '@' + self._name,
                'D = D + M',
                '@R13',
                'M = D']


class PopFixedSegmentCmd(PopCmd):

    def __init__(self, val):
        self.x = val


class PopStaticCmd(PopFixedSegmentCmd):
    def translate(self):
        return ['@SP',
                'AM = M - 1',
                'D = M',
                "@%s" % Context.class_name + '.' + str(self.x),
                'M = D']


class PopTempCmd(PopFixedSegmentCmd):
    def translate(self):
        return ['@SP',
                'AM = M - 1',
                'D = M',
                "@%d" % (5 + self.x),
                'M = D']


class PopPointerCmd(PopCmd):
    def __init__(self, segment_name):
        self._name = segment_name

    def translate(self):
        return ['@SP',
                'AM = M - 1',
                'D = M',
                '@%s' % self._name,
                'M = D']


class ArithmCmd(VmCmd):
    ...


class UnaryArithmCmd(ArithmCmd):
    def translate(self):
        return ['@SP',
                'A = M - 1',
                'M = ' + self._calc_on_M()]


class NegCmd(UnaryArithmCmd):
    def _calc_on_M(self):
        return '-M'


class NotCmd(UnaryArithmCmd):
    def _calc_on_M(self):
        return '!M'


class BinaryArithmCmd(ArithmCmd):
    ...


class NonCompArithmCmd(BinaryArithmCmd):
    def __init__(self, sign):
        self._sign = sign

    def translate(self):
        res = ['@SP',
               'AM = M - 1',
               'D = M',
               'A = A - 1']
        res += ['M = M ' + self._sign + ' D']
        return res


class CmpCmd(BinaryArithmCmd):
    def translate(self):
        Context.cmp_count = Context.cmp_count + 1
        return ['@SP',
                'AM = M - 1',
                'D = M',
                'A = A - 1',
                'D = M - D',
                '@CMP_TRUE' + str(Context.cmp_count),
                'D;' + self._get_jump_cond(),
                '@SP',
                'A = M - 1',
                'M = 0',
                '@CMP_END' + str(Context.cmp_count),
                '0;JMP',
                '(CMP_TRUE' + str(Context.cmp_count) + ')',
                '@SP',
                'A = M - 1',
                'M = -1',
                '(CMP_END' + str(Context.cmp_count) + ')']


class LtCmd(CmpCmd):
    def _get_jump_cond(self):
        return 'JLT'


class GtCmd(CmpCmd):
    def _get_jump_cond(self):
        return 'JGT'


class EqCmd(CmpCmd):
    def _get_jump_cond(self):
        return 'JEQ'


def get_simple_label_name(str):
    return '%s$%s' % (Context.func_name, str)


def get_ret_label_name():
    return '%s$ret.%d' % (Context.func_name, Context.ret_count)


def get_function_label_name(name):
    return '%s' % name


def get_function_init_label_name(name):
    return '%s$init' % name


def get_function_end_init_label_name(name):
    return '%s$end_init' % name


class LabelCmd(VmCmd):
    def __init__(self, name):
        self.name = name

    def translate(self):
        return ['(%s)' % get_simple_label_name(self.name)]


class GotoCmd(VmCmd):
    def __init__(self, name):
        self.name = name

    def translate(self):
        return ['@%s' % get_simple_label_name(self.name),
                '0;JMP']


class IfGotoCmd(VmCmd):
    def __init__(self, name):
        self.name = name

    def translate(self):
        return ['@SP',
                'AM = M - 1',
                'D = M',
                '@%s' % get_simple_label_name(self.name),
                'D;JNE']


class CallCmd(VmCmd):
    def __init__(self, func, arg_num):
        self.func = func
        self.arg_num = arg_num

    def translate(self):
        Context.ret_count = Context.ret_count + 1
        return ['@%s' % get_ret_label_name(),
                'D = A',
                '@SP',
                'M = M + 1',
                'A = M - 1',
                'M = D',
                '@LCL',
                'D = M',
                '@SP',
                'M = M + 1',
                'A = M - 1',
                'M = D',
                '@ARG',
                'D = M',
                '@SP',
                'M = M + 1',
                'A = M - 1',
                'M = D',
                '@THIS',
                'D = M',
                '@SP',
                'M = M + 1',
                'A = M - 1',
                'M = D',
                '@THAT',
                'D = M',
                '@SP',
                'M = M + 1',
                'A = M - 1',
                'M = D',
                '@SP',
                'D = M',
                '@LCL',
                'M = D',
                '@%d' % (5 + self.arg_num),
                'D = D - A',
                '@ARG',
                'M = D',
                '@%s' % get_function_label_name(self.func),
                '0;JMP',
                '(%s)' % get_ret_label_name()]


class ReturnCmd(VmCmd):
    def translate(self):
        return ['@5',  # BEGIN: store ret address to r14
                'D = A',
                '@LCL',
                'A = M - D',
                'D = M',
                '@R14',
                'M = D',  # END
                '@SP',  # BEGIN: store return value to ARG_0
                'A = M - 1',
                'D = M',
                '@ARG',
                'A = M',
                'M = D',  # END
                'D = A + 1',  # BEGIN: set SP to ARG + 1
                '@SP',
                'M = D',  # END
                '@LCL',  # BEGIN: restore THAT
                'D = M - 1',
                '@R15',
                'AM = D',
                'D = M',
                '@THAT',
                'M = D',  # END
                '@R15',  # BEGIN: restore THIS
                'AM = M - 1',
                'D = M',
                '@THIS',
                'M = D',  # END
                '@R15',  # BEGIN: restore ARG
                'AM = M - 1',
                'D = M',
                '@ARG',
                'M = D',  # END
                '@R15',  # BEGIN: restore LCL
                'AM = M - 1',
                'D = M',
                '@LCL',
                'M = D',  # END,
                '@R14',  # BEGIN: jumping to return address,
                'A = M',
                '0;JMP']


class FunctionCmd(VmCmd):
    def __init__(self, name, var_num):
        self.name = name
        self.var_num = var_num

    def translate(self):
        Context.func_name = self.name
        return ['(%s)' % get_function_label_name(self.name),
                '@%d' % self.var_num,
                'D = A',
                '(%s)' % get_function_init_label_name(self.name),
                '@%s' % get_function_end_init_label_name(self.name),
                'D;JEQ',
                '@SP',
                'A = M',
                'M = 0',
                '@SP',
                'M = M + 1',
                'D = D - 1',
                '@%s' % get_function_init_label_name(self.name),
                '0;JMP',
                '(%s)' % get_function_end_init_label_name(self.name)]


def is_empty(line):
    if line.startswith('//'):
        return True
    else:
        return line.strip() == ''


def parse_one_word(line):
    if line == 'return':
        return ReturnCmd()
    if line == 'add':
        return NonCompArithmCmd('+')
    if line == 'sub':
        return NonCompArithmCmd('-')
    if line == 'eq':
        return EqCmd()
    if line == 'gt':
        return GtCmd()
    if line == 'lt':
        return LtCmd()
    if line == 'and':
        return NonCompArithmCmd('&')
    if line == 'or':
        return NonCompArithmCmd('|')
    if line == 'neg':
        return NegCmd()
    if line == 'not':
        return NotCmd()
    raise ValueError("Can't parse %s" % line)


def parse_three_words(w1, w2, val):
    if w1 == 'push':
        if w2 == 'local':
            return PushRegularSegmentCmd("LCL", val)
        if w2 == 'argument':
            return PushRegularSegmentCmd("ARG", val)
        if w2 == 'this':
            return PushRegularSegmentCmd("THIS", val)
        if w2 == 'that':
            return PushRegularSegmentCmd("THAT", val)
        if w2 == 'constant':
            return PushConstCmd(val)
        if w2 == 'static':
            return PushStaticCmd(val)
        if w2 == 'temp':
            return PushTempCmd(val)
        if w2 == 'pointer':
            if val == 0:
                return PushPointerCmd("THIS")
            if val == 1:
                return PushPointerCmd("THAT")
    if w1 == 'pop':
        if w2 == 'local':
            return PopRegularSegmentCmd("LCL", val)
        if w2 == 'argument':
            return PopRegularSegmentCmd("ARG", val)
        if w2 == 'this':
            return PopRegularSegmentCmd("THIS", val)
        if w2 == 'that':
            return PopRegularSegmentCmd("THAT", val)
        if w2 == 'static':
            return PopStaticCmd(val)
        if w2 == 'temp':
            return PopTempCmd(val)
        if w2 == 'pointer':
            if val == 0:
                return PopPointerCmd("THIS")
            if val == 1:
                return PopPointerCmd("THAT")
    if w1 == 'call':
        return CallCmd(w2, val)
    if w1 == 'function':
        return FunctionCmd(w2, val)
    raise ValueError("Can't parse %s %s %d" % (w1, w2, val))


def parse_branch(w1, w2):
    if w1 == 'label':
        return LabelCmd(w2)
    if w1 == 'goto':
        return GotoCmd(w2)
    if w1 == 'if-goto':
        return IfGotoCmd(w2)
    raise ValueError("Can't parse branch %s %s" % (w1, w2))


def parse_line(line):
    if line.find('//') >= 0:
        line = line[:line.find('//')]
    parts = line.split()
    if len(parts) == 1:
        return parse_one_word(parts[0])
    if len(parts) == 3:
        return parse_three_words(parts[0], parts[1], int(parts[2]))
    if len(parts) == 2:
        return parse_branch(parts[0], parts[1])
    raise ValueError("Can't parse line %s" % line)


def translate_lines(lines):
    vm_program = map(parse_line, filter(lambda line: not is_empty(line), lines))
    import itertools
    return itertools.chain.from_iterable(map(lambda cmd: cmd.translate(), vm_program))


def translate_file(path):
    _, Context.class_name = parse_path(path)
    with open(path, 'r') as sourceFile:
        lines = sourceFile.readlines()
        return translate_lines(lines)


def parse_path(path):
    import os
    path_list = path.split(os.sep)
    className = path_list[-1].split('.')[0]
    return path_list[:-1], className


def main(source, target):
    import os
    from pathlib import Path
    os.makedirs(Path(target).parent, exist_ok=True)
    if not os.path.isdir(source):
        with open(target, 'w') as outfile:
            outfile.write("\n".join(translate_file(source)))
        return
    vm_files = map(lambda filename: os.path.join(source, filename),
                   filter(lambda filename: filename.endswith('.vm'), os.listdir(source)))
    full_program = ['@256',
                    'D = A',
                    '@SP',
                    'M = D']
    full_program += list(translate_lines(['call Sys.init 0']))
    for vm_file in vm_files:
        full_program += list(translate_file(vm_file))
    with open(target, 'w') as outfile:
        outfile.write("\n".join(full_program))
