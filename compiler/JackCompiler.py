import glob;
import os;
from sys import argv
from xml.etree.ElementTree import Element


class Token(object):
    def xml_repr(self):
        pass

    def string_repr(self):
        pass;

    def is_any_field(self):
        return False;

    def is_comma(self):
        return False;

    def is_subroutine_start(self):
        return False;

    def is_type(self):
        return False;

    def is_var(self):
        return False;

    def is_statement(self):
        return False;

    def is_let(self):
        return False;

    def is_if(self):
        return False;

    def is_do(self):
        return False;

    def is_while(self):
        return False;

    def is_return(self):
        return False;

    def is_else(self):
        return False;

    def is_opening_square(self):
        return False;

    def is_any_const(self):
        return False;

    def is_opening_round(self):
        return False;

    def is_closing_round(self):
        return False;

    def is_unary_op(self):
        return False;

    def is_dot(self):
        return False;

    def is_op(self):
        return False;

    def is_semicolon(self):
        return False;

    def is_int_const(self):
        return False

    def is_string_const(self):
        return False

    def is_keyword_const(self):
        return False


class SymbolToken(Token):
    def __init__(self, symbol):
        self.symbol = symbol;

    def xml_repr(self):
        elem = Element("symbol");
        elem.text = self.symbol;
        return elem;

    def string_repr(self):
        return self.symbol;

    def is_comma(self):
        return self.symbol == ',';

    def is_opening_square(self):
        return self.symbol == '[';

    def is_opening_round(self):
        return self.symbol == '(';

    def is_closing_round(self):
        return self.symbol == ')';

    def is_unary_op(self):
        return self.symbol in ['-', '~'];

    def is_dot(self):
        return self.symbol == '.';

    def is_op(self):
        return self.symbol in ['+', '-', '*', '/', '&', '|', '<', '>', '='];

    def is_semicolon(self):
        return self.symbol == ';';


class KeywordToken(Token):
    def __init__(self, keyword):
        self.keyword = keyword;

    def xml_repr(self):
        elem = Element("keyword");
        elem.text = self.keyword;
        return elem;

    def string_repr(self):
        return self.keyword;

    def is_any_field(self):
        return self.keyword in ["field", "static"]

    def is_subroutine_start(self):
        return self.keyword in ["constructor", "function", "method"];

    def is_type(self):
        return self.keyword in ["int", "boolean", "char"];

    def is_var(self):
        return self.keyword == "var";

    def is_statement(self):
        return self.keyword in ["let", "if", "while", "do", "return"];

    def is_let(self):
        return self.keyword == "let";

    def is_if(self):
        return self.keyword == "if";

    def is_do(self):
        return self.keyword == "do";

    def is_while(self):
        return self.keyword == "while";

    def is_return(self):
        return self.keyword == "return";

    def is_else(self):
        return self.keyword == "else";

    def is_any_const(self):
        return self.keyword in ["true", "false", "null", "this"]

    def is_keyword_const(self):
        return self.keyword in ["true", "false", "null", "this"]


class StringLiteralToken(Token):
    def __init__(self, val):
        self.val = val;

    def xml_repr(self):
        elem = Element("stringConstant");
        elem.text = self.val;
        return elem;

    def string_repr(self):
        return self.val;

    def is_any_const(self):
        return True;

    def is_string_const(self):
        return True


class IntToken(Token):
    def __init__(self, val):
        self.val = val;

    def xml_repr(self):
        elem = Element("integerConstant");
        elem.text = str(self.val);
        return elem;

    def string_repr(self):
        return str(self.val);

    def is_any_const(self):
        return True;

    def is_int_const(self):
        return True


class IdentifierToken(Token):
    def __init__(self, identifier):
        self.identifier = identifier;

    def xml_repr(self):
        elem = Element("identifier");
        elem.text = self.identifier;
        return elem;

    def string_repr(self):
        return str(self.identifier);

    def is_type(self):
        return True;


class Tokenizer():
    def __init__(self, text):
        self.currentToken = None;
        self.text = text;
        self.i = 0;
        self.advance();

    def has_more_tokens(self):
        return not (self.currentToken is None);

    def advance(self):
        self._skip_bullshit();
        if self.i >= len(self.text):
            self.currentToken = None;
            return;
        if self.text[self.i] in ['(', ')', '[', ']', '{', '}', '.', ',', ';', '+', '-', '*', '/', '&', '|', '<', '>',
                                 '=', '~']:
            self.currentToken = SymbolToken(self.text[self.i]);
            self.i = self.i + 1;
            return;
        keywords = ["class", "constructor", "function", "method", "field", "static", "var", "int", "char", "boolean",
                    "void", "true", "false", "null", "this", "let", "do", "if", "else", "while", "return"];
        for keyword in keywords:
            if self._at_keyword(keyword):
                self.currentToken = KeywordToken(keyword);
                self.i = self.i + len(keyword);
                return;
        if self.text[self.i] == '"':
            pos = self.text.find('"', self.i + 1);
            self.currentToken = StringLiteralToken(self.text[self.i + 1: pos]);
            self.i = pos + 1;
            return;
        if self._is_digit_at(self.i):
            pos = self.i;
            while self._is_digit_at(pos + 1):
                pos = pos + 1;
            self.currentToken = IntToken(int(self.text[self.i:pos + 1]));
            self.i = pos + 1;
            return;
        pos = self.i;
        while self._is_digit_at(pos + 1) or self._is_letter_at(pos + 1) or self._is_underscore_at(pos + 1):
            pos = pos + 1;
        self.currentToken = IdentifierToken(self.text[self.i: pos + 1]);
        self.i = pos + 1;

    def _skip_bullshit(self):
        while (True):
            if self.i >= len(self.text):
                return;
            if self.text[self.i:self.i + 1].isspace():
                self.i = self.i + 1;
                continue;
            if self._at_string("//"):
                self.i = self.text.find("\n", self.i) + 1;
                continue;
            if self._at_string("/**"):
                self.i = self.text.find("*/", self.i) + 2;
                continue;
            return;

    def _is_digit_at(self, pos):
        if pos >= len(self.text):
            return False;
        return '0' <= self.text[pos] <= '9';

    def _at_keyword(self, str):
        if not self._at_string(str):
            return False
        if self._is_digit_at(self.i + len(str)) or self._is_letter_at(self.i + len(str)) or self._is_underscore_at(self.i + len(str)):
            return False
        return True

    def _at_string(self, str):
        if self.i >= len(self.text) - len(str) + 1:
            return False;
        return self.text[self.i:self.i + len(str)] == str;

    def _is_letter_at(self, pos):
        if pos >= len(self.text):
            return False;
        if 'a' <= self.text[pos] <= 'z':
            return True;
        if 'A' <= self.text[pos] <= 'Z':
            return True;
        return False;

    def _is_underscore_at(self, pos):
        if pos >= len(self.text):
            return False;
        return self.text[pos] == '_';


class CompilerContext(object):
    def __init__(self, className):
        self.className = className
        self.statics = {};
        self.fields = {};
        self.args = {};
        self.locals = {};
        self.whileCount = 0
        self.ifCount = 0
        self.invocationArgsCount = 0

    def updateWithField(self, isStatic, type, name):
        if "field" == isStatic:
            table = self.fields;
        else:
            table = self.statics;
        index = len(table);
        table[name] = (type, index)

    def updateWithLocal(self, type, name):
        index = len(self.locals)
        self.locals[name] = (type, index)

    def updateWithArg(self, type, name):
        index = len(self.args)
        self.args[name] = (type, index)

    def clearSubroutineLevel(self):
        self.args = {}
        self.locals = {}

    def is_class(self, symbol):
        return not (symbol in self.statics or symbol in self.fields or symbol in self.args or symbol in self.locals)

    def get_symbol_info(self, symbol):
        if symbol in self.locals:
            return "local", self.locals[symbol][0], self.locals[symbol][1]
        if symbol in self.args:
            return "arg", self.args[symbol][0], self.args[symbol][1]
        if symbol in self.fields:
            return "field", self.fields[symbol][0], self.fields[symbol][1]
        if symbol in self.statics:
            return "static", self.statics[symbol][0], self.statics[symbol][1]


def compileVarNameWithComma(tokenizer, classLevel, isStatic, type, context):
    tokenizer.advance()
    name = tokenizer.currentToken.string_repr()
    if classLevel:
        context.updateWithField(isStatic, type, name)
    else:
        context.updateWithLocal(type, name)
    tokenizer.advance()


def compileVarNamesListTail(tokenizer, classLevel, isStatic, type, context):
    while tokenizer.currentToken.is_comma():
        compileVarNameWithComma(tokenizer, classLevel, isStatic, type, context)


def compileClassVarDecl(tokenizer, context):
    isStatic = tokenizer.currentToken.string_repr()
    tokenizer.advance()
    type = tokenizer.currentToken.string_repr()
    tokenizer.advance()
    name = tokenizer.currentToken.string_repr()
    context.updateWithField(isStatic, type, name)
    tokenizer.advance()
    compileVarNamesListTail(tokenizer, True, isStatic, type, context)
    tokenizer.advance()


def compileClassVarDecls(tokenizer, context):
    while tokenizer.currentToken.is_any_field():
        compileClassVarDecl(tokenizer, context);


def compileParam(tokenizer, context):
    type = tokenizer.currentToken.string_repr()
    tokenizer.advance()
    name = tokenizer.currentToken.string_repr()
    context.updateWithArg(type, name)
    tokenizer.advance();


def compileParamWithComma(tokenizer, context):
    tokenizer.advance();
    type = tokenizer.currentToken.string_repr()
    tokenizer.advance();
    name = tokenizer.currentToken.string_repr()
    context.updateWithArg(type, name)
    tokenizer.advance();


def compileParamListTail(tokenizer, context):
    while tokenizer.currentToken.is_comma():
        compileParamWithComma(tokenizer, context)


def compileParamList(tokenizer, context):
    if tokenizer.currentToken.is_type():
        compileParam(tokenizer, context);
    if tokenizer.currentToken.is_comma():
        compileParamListTail(tokenizer, context)


def compileLocalVarDecl(tokenizer, context):
    tokenizer.advance();
    type = tokenizer.currentToken.string_repr();
    tokenizer.advance();
    name = tokenizer.currentToken.string_repr();
    context.updateWithLocal(type, name)
    tokenizer.advance();
    compileVarNamesListTail(tokenizer, False, type, name, context)
    tokenizer.advance();


def compileLocalVarDecls(tokenizer, context):
    while tokenizer.currentToken.is_var():
        compileLocalVarDecl(tokenizer, context);


def compileExprList(tokenizer, context):
    context.invocationArgsCount = 0
    isFirst = True;
    vmCode = []
    while not tokenizer.currentToken.is_closing_round():
        context.invocationArgsCount = context.invocationArgsCount + 1
        if not isFirst:
            tokenizer.advance();
        vmCode.extend(compileExpr(tokenizer, context))
        isFirst = False;
    return vmCode;


def compileSymbolRValue(kind, index):
    dict = {
        "local": "push local %d",
        "static": "push static %d",
        "arg": "push argument %d",
        "field": "push this %d"
    }
    return dict[kind] % index


def compileSymbolLValue(kind, index):
    dict = {
        "local": "pop local %d",
        "static": "pop static %d",
        "arg": "pop argument %d",
        "field": "pop this %d"
    }
    return dict[kind] % index


def compileSubroutineCall(firstToken, tokenizer, context):
    if tokenizer.currentToken.is_opening_round():
        vmCode = ["push pointer 0"]
        tokenizer.advance();
        explicitArgsVmCode = compileExprList(tokenizer, context)
        vmCode.extend(explicitArgsVmCode)
        vmCode.append("call %s.%s %d" % (context.className, firstToken.string_repr(), context.invocationArgsCount + 1))
        tokenizer.advance();
        return vmCode;
    receiver = firstToken.string_repr()
    tokenizer.advance();
    name = tokenizer.currentToken.string_repr()
    tokenizer.advance();
    tokenizer.advance();
    explicitArgsVmCode = compileExprList(tokenizer, context)
    tokenizer.advance();
    if context.is_class(receiver):
        vmCode = explicitArgsVmCode;
        vmCode.append("call %s.%s %d" % (receiver, name, context.invocationArgsCount))
        return vmCode
    kind, type, index = context.get_symbol_info(receiver)
    vmCode = [compileSymbolRValue(kind, index)]
    vmCode.extend(explicitArgsVmCode)
    vmCode.append("call %s.%s %d" % (type, name, context.invocationArgsCount + 1))
    return vmCode


def compileStringConst(str):
    vmCode = ["push constant %d" % len(str), "call String.new 1"]
    for chr in str:
        vmCode.extend(["push constant %d" % ord(chr), "call String.appendChar 2"])
    return vmCode



def compileKeywordConst(keyword):
    vmCodeDict = {
        "null": ["push constant 0"],
        "false": ["push constant 0"],
        "true": ["push constant 0", "not"],
        "this": ["push pointer 0"]
    }
    return vmCodeDict[keyword]


def compileUnaryOp(unaryOp):
    vmCodeDict = {
        "-": "neg",
        "~": "not"
    }
    return vmCodeDict[unaryOp]


def compileTerm(tokenizer, context):
    if tokenizer.currentToken.is_any_const():
        if tokenizer.currentToken.is_int_const():
            vmCode = ["push constant %s" % tokenizer.currentToken.string_repr()]
        if tokenizer.currentToken.is_string_const():
            vmCode = compileStringConst(tokenizer.currentToken.string_repr())
        if tokenizer.currentToken.is_keyword_const():
            vmCode = compileKeywordConst(tokenizer.currentToken.string_repr())
        tokenizer.advance()
        return vmCode
    if tokenizer.currentToken.is_opening_round():
        tokenizer.advance();
        exprVmCode = compileExpr(tokenizer, context)
        tokenizer.advance();
        return exprVmCode;
    if tokenizer.currentToken.is_unary_op():
        unaryOp = tokenizer.currentToken.string_repr()
        tokenizer.advance();
        termVmCode = compileTerm(tokenizer, context)
        vmCode = termVmCode
        vmCode.append(compileUnaryOp(unaryOp))
        return vmCode
    firstToken = tokenizer.currentToken;
    tokenizer.advance();
    if tokenizer.currentToken.is_opening_round() or tokenizer.currentToken.is_dot():
        return compileSubroutineCall(firstToken, tokenizer, context)
    if tokenizer.currentToken.is_opening_square():  # TODO
        kind, _, index = context.get_symbol_info(firstToken.string_repr())
        vmCode = [compileSymbolRValue(kind, index)]
        tokenizer.advance();
        indexVmCode = compileExpr(tokenizer, context)
        vmCode.extend(indexVmCode)
        vmCode.extend(["add", "pop pointer 1", "push that 0"])
        tokenizer.advance();
        return vmCode;
    kind, _, index = context.get_symbol_info(firstToken.string_repr())
    return [compileSymbolRValue(kind, index)]


def compileBinaryOp(op):
    opDict = {
        '+': "add",
        '-': "sub",
        '&': "and",
        '|': "or",
        '<': "lt",
        '>': "gt",
        "=": "eq",
        "*": "call Math.multiply 2",
        "/": "call Math.divide 2"
    }
    return opDict[op]


def compileExpr(tokenizer, context):
    vmCode = compileTerm(tokenizer, context)
    while tokenizer.currentToken.is_op():
        op = tokenizer.currentToken.string_repr()
        tokenizer.advance();
        nextTermVmCode = compileTerm(tokenizer, context)
        vmCode.extend(nextTermVmCode)
        vmCode.append(compileBinaryOp(op))
    return vmCode;


def compileLet(tokenizer, context):
    tokenizer.advance();
    lValue = tokenizer.currentToken.string_repr()
    tokenizer.advance();
    if tokenizer.currentToken.is_opening_square():
        kind, _, index = context.get_symbol_info(lValue)
        vmCode = [compileSymbolRValue(kind, index)]
        tokenizer.advance()
        indexVmCode = compileExpr(tokenizer, context)
        vmCode.extend(indexVmCode)
        vmCode.append("add")
        tokenizer.advance()
        tokenizer.advance()
        rValue = compileExpr(tokenizer, context)
        vmCode.extend(rValue)
        vmCode.extend(["pop temp 0", "pop pointer 1", "push temp 0", "pop that 0"])
        tokenizer.advance()
        return vmCode
    tokenizer.advance();
    rValue = compileExpr(tokenizer, context)
    tokenizer.advance();
    vmCode = rValue
    kind, _, index = context.get_symbol_info(lValue)
    vmCode.append(compileSymbolLValue(kind, index))
    return vmCode;


def compileIf(tokenizer, context): # TODO check and fix
    tokenizer.advance();
    tokenizer.advance();
    condVmCode = compileExpr(tokenizer, context)
    tokenizer.advance();
    tokenizer.advance();
    statementsVmCode = compileStatements(tokenizer, context)
    tokenizer.advance();
    vmCode = condVmCode
    vmCode.append("not")
    ifLabelNum = context.ifCount;
    context.ifCount = context.ifCount + 1
    vmCode.append("if-goto IF_NOT_%d" % ifLabelNum)
    vmCode.extend(statementsVmCode)
    vmCode.append("goto IF_END_%d" % ifLabelNum)
    vmCode.append("label IF_NOT_%d" % ifLabelNum)
    if tokenizer.currentToken.is_else():
        tokenizer.advance();
        tokenizer.advance();
        elseStatementsVmCode = compileStatements(tokenizer, context)
        tokenizer.advance();
        vmCode.extend(elseStatementsVmCode)
    vmCode.append("label IF_END_%d" % ifLabelNum)
    return vmCode


def compileDo(tokenizer, context):
    tokenizer.advance()
    firstToken = tokenizer.currentToken
    tokenizer.advance()
    vmCode = compileSubroutineCall(firstToken, tokenizer, context)
    vmCode.append("pop temp 0")
    tokenizer.advance()
    return vmCode


def compileWhile(tokenizer, context):
    tokenizer.advance();
    tokenizer.advance();
    condVmCode = compileExpr(tokenizer, context)
    tokenizer.advance();
    tokenizer.advance();
    statementsVmCode = compileStatements(tokenizer, context)
    tokenizer.advance();
    vmCode = ["label WHILE_START_%d" % context.whileCount]
    vmCode.extend(condVmCode)
    vmCode.append("not")
    vmCode.append("if-goto WHILE_END_%d" % context.whileCount)
    vmCode.extend(statementsVmCode)
    vmCode.append("goto WHILE_START_%d" % context.whileCount)
    vmCode.append("label WHILE_END_%d" % context.whileCount)
    context.whileCount = context.whileCount + 1
    return vmCode;


def compileReturn(tokenizer, context):
    tokenizer.advance();
    if not tokenizer.currentToken.is_semicolon():
        exprVmCode = compileExpr(tokenizer, context)
        vmCode = exprVmCode
    else:
        vmCode = ["push constant 0"]
    tokenizer.advance();
    vmCode.append("return")
    return vmCode


def compileStatement(tokenizer, context):
    if tokenizer.currentToken.is_let():
        return compileLet(tokenizer, context);
    if tokenizer.currentToken.is_if():
        return compileIf(tokenizer, context);
    if tokenizer.currentToken.is_do():
        return compileDo(tokenizer, context);
    if tokenizer.currentToken.is_while():
        return compileWhile(tokenizer, context);
    if tokenizer.currentToken.is_return():
        return compileReturn(tokenizer, context);


def compileStatements(tokenizer, context):
    vmCode = []
    while tokenizer.currentToken.is_statement():
        vmCode.extend(compileStatement(tokenizer, context));
    return vmCode;


def compileSubroutineBody(tokenizer, context):
    tokenizer.advance();
    compileLocalVarDecls(tokenizer, context);
    vmCode = compileStatements(tokenizer, context);
    tokenizer.advance();
    return vmCode;


def compileSubroutineDecl(tokenizer, context):
    context.clearSubroutineLevel()
    subroutineType = tokenizer.currentToken.string_repr();
    if "method" == subroutineType:
        context.updateWithArg("this", context.className)
    tokenizer.advance();
    returnType = tokenizer.currentToken.string_repr();
    tokenizer.advance();
    name = tokenizer.currentToken.string_repr();
    tokenizer.advance();
    tokenizer.advance();
    compileParamList(tokenizer, context)
    tokenizer.advance();
    bodyVmCode = compileSubroutineBody(tokenizer, context)
    res = ["function %s.%s %d" % (context.className, name, len(context.locals))]
    if "method" == subroutineType:
        res.extend(["push argument 0", "pop pointer 0"])
    if "constructor" == subroutineType:
        res.extend(["push constant %d" % len(context.fields), "call Memory.alloc 1", "pop pointer 0"])
    res.extend(bodyVmCode)
    return res;


def compileSubroutineDecls(tokenizer, context):
    decls = []
    while tokenizer.currentToken.is_subroutine_start():
        decls.extend(compileSubroutineDecl(tokenizer, context))
    return decls


def compileClass(tokenizer):
    tokenizer.advance();
    context = CompilerContext(tokenizer.currentToken.string_repr())
    tokenizer.advance();
    tokenizer.advance();
    compileClassVarDecls(tokenizer, context);
    return compileSubroutineDecls(tokenizer, context);


def compileProgramm(file):
    tokenizer = Tokenizer(file);
    return compileClass(tokenizer);


def writeResult(file, dir, result):
    className = os.path.splitext(os.path.basename(file))[0];
    with open(os.path.join(dir, className + ".vm"), "w") as out:
        out.write("\n".join(result));


def compileFile(file, dir):
    content = open(file, 'r').read();
    vmCode = compileProgramm(content);
    writeResult(file, dir, vmCode);


def main(source, target):
    if os.path.isfile(source):
        files = [source];
    else:
        files = glob.glob("%s/*.jack" % source);
    os.makedirs(target, exist_ok=True)
    for file in files:
        compileFile(file, target);