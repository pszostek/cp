#!/usr/bin/env python
import sys

# Store results here
class CppName:
    def __init__(self, head, template, tail):
        self.head = head
        self.template = template
        self.tail = tail
        self.pointer = ''
    def setpointer(self, s):
        self.pointer = s
    def inspect(self, level=0):
        if type(self.head) is str:
            print("\t"*level + str(self.head))
        else:
            self.head.inspect(level)

        if self.template is not None:
            print("\t"*level + "<")
            for templ in self.template:
                templ.inspect(level)
            print("\t"*level + ">")

        if self.tail is not None:
            if type(self.tail) is str:
                print("\t" * (level+1) + str(self.tail))
            else:
                self.tail.inspect(level+1)

        if type(self.head) is not str and self.pointer != '':
            if type(self.pointer) is str:
                print("\t" * level + self.pointer)
            else:
                self.pointer.inspect(level)

# Lexer
tokens = (
    'LPAREN', 'RPAREN', 'NAME', 'DCOLON', 'COMMA',  'LCOMP', 'RCOMP', 'TIDE'
   )

t_LPAREN = r'\('
t_RPAREN = r'\)'
t_DCOLON = r'::'
t_COMMA = r','

operators = r'operator\+\+|operator--|operator>>|operator<<'
t_NAME = r'(' + operators + r'|[a-zA-Z_~\*&][a-zA-Z0-9_  \*&]*)'

t_LCOMP = r'<'
t_RCOMP = r'>'
t_TIDE = r'~'


def t_error(t):
    print("Illegal character {0}".format(t.value[0]))

t_ignore = " \t"

# Parser

precedence = (
        ('right', 'DCOLON'),
        ('left', 'LCOMP')

        )

def p_template_list(t):
    """templatelist : type COMMA templatelist"""
    t[0] = [t[1]] + t[3]

def p_template_list_single(t):
    """templatelist : type"""
    t[0] = [t[1]]

def p_template(t):
    """template : LCOMP templatelist RCOMP"""
    t[0] = t[2] 

# Why is this rule needed? Because we might have something like
# a<int, bool>* const& ..
# The NAME will catch any pointers, const, etc after the template definition
def p_type_templ_pointer(t):
    """type : type template NAME"""
    t[0] = CppName(t[1], t[2], None)
    t[0].setpointer(t[3])

def p_type_templ(t):
    """type : type template"""
    t[0] = CppName(t[1], t[2], None)

def p_type(t):
    """type : NAME"""
    t[0] = CppName(t[1], None, None)

def p_type_type(t):
    """type : type DCOLON type"""
    t[0] = CppName(t[1], None, t[3])

def p_master(t):
    """master : type"""
    t[0] = t[1]

def p_error(t):
    print("Syntax error at {0}".format(t.value))

def main():
    import ply.lex as lex
    import ply.yacc as yacc
    lex.lex()
    yacc.yacc(start="master")
    #a = yacc.parse("std::_Rb_tree<std::basic_string<char, std::char_traits<char>, std::allocator<char> >, std::basic_string<char, std::char_traits<char>, std::allocator<char> >, std::_Identity<     std::basic_string<char, std::char_traits<char>, std::allocator<char> > >, std::less<std::basic_string<char, std::char_traits<char>, std::allocator<char> > >, std::allocator<std::basic_string<char, std::char_traits<char>, std::alloca     tor<char> > > >::_M_insert_<std::basic_string<char, std::char_traits<char>, std::allocator<char> > const&>")
    #a.inspect()
    #exit(1)

    while True:
        line = raw_input()
        print("Got " + line)
        try:
            a = yacc.parse(line)
            a.inspect()
        except:
            print("Could not parse " + line)

if __name__ == "__main__":
    main()

