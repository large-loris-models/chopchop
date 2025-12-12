from core.lexing.lexing import LexerSpec
from core.lexing.token import Token
import regex as re


def test_partial_lex_abc():
    lspec = LexerSpec(frozenset({
        Token("a", re.compile("a")),
        Token("b", re.compile("b")),
        Token("c", re.compile("c"))
    }), re.compile(""))
    assert lspec.partial_lex("abc") == {
        (Token("a", re.compile("a"), "a", True),
         Token("b", re.compile("b"), "b", True),
         Token("c", re.compile("c"), "c", False))}

    assert lspec.partial_lex("") == {()}
    assert lspec.partial_lex("d") == set()


def test_partial_lex_ignore():
    lspec = LexerSpec(frozenset({
        Token("a", re.compile("a")),
        Token("b", re.compile("b")),
        Token("c", re.compile("c"))
    }), re.compile("\\s+"))
    assert lspec.partial_lex("a b   c") == {
        (Token("a", re.compile("a"), "a", True),
         Token("b", re.compile("b"), "b", True),
         Token("c", re.compile("c"), "c", False))}

    assert lspec.partial_lex("    ") == {()}


def test_partial_lex_disjoint():
    lspec = LexerSpec(frozenset({
        Token("a", re.compile("a+")),
        Token("b", re.compile("b+")),
    }), re.compile(""))
    assert lspec.partial_lex("aaaa") == {
        (Token("a", re.compile("a+"), "aaaa", False),)}

    assert lspec.partial_lex("aaabaabb") == {
        (Token("a", re.compile("a+"), "aaa", True),
         Token("b", re.compile("b+"), "b", True),
         Token("a", re.compile("a+"), "aa", True),
         Token("b", re.compile("b+"), "bb", False))}

    assert lspec.partial_lex("") == {()}


def test_partial_lex_nonsingleton():
    lspec = LexerSpec(frozenset({
        Token("print", re.compile(r'print\$')),
        Token("lpar", re.compile("\\(")),
        Token("rpar", re.compile("\\)")),
        Token("var", re.compile("[a-z]+")),
        Token("dot", re.compile("\\.")),
        Token("caps", re.compile("tocaps"))
    }), re.compile("\\s+"))
    assert lspec.partial_lex("print$( foo.tocap") == {
        (Token("print", re.compile(r'print\$'), "print$", True),
         Token("lpar", re.compile("\\("), "(", True),
         Token("var", re.compile("[a-z]+"), "foo", True),
         Token("dot", re.compile("\\."), ".", True),
         Token("caps", re.compile("tocaps"), "tocap", False)),
        (Token("print", re.compile(r'print\$'), "print$", True),
         Token("lpar", re.compile("\\("), "(", True),
         Token("var", re.compile("[a-z]+"), "foo", True),
         Token("dot", re.compile("\\."), ".", True),
         Token("var", re.compile("[a-z]+"), "tocap", False))
    }

    assert lspec.partial_lex("  ))( zip prin") == {
        (Token("rpar", re.compile("\\)"), ")", True),
         Token("rpar", re.compile("\\)"), ")", True),
         Token("lpar", re.compile("\\("), "(", True),
         Token("var", re.compile("[a-z]+"), "zip", True),
         Token("print", re.compile(r'print\$'), "prin", False)),
        (Token("rpar", re.compile("\\)"), ")", True),
         Token("rpar", re.compile("\\)"), ")", True),
         Token("lpar", re.compile("\\("), "(", True),
         Token("var", re.compile("[a-z]+"), "zip", True),
         Token("var", re.compile("[a-z]+"), "prin", False))
    }

    assert lspec.partial_lex("  ))( zip prin ") == {
        (Token("rpar", re.compile("\\)"), ")", True),
         Token("rpar", re.compile("\\)"), ")", True),
         Token("lpar", re.compile("\\("), "(", True),
         Token("var", re.compile("[a-z]+"), "zip", True),
         Token("var", re.compile("[a-z]+"), "prin", True))
    }


def test_partial_lex_finalize():
    lspec = LexerSpec(frozenset({
        Token("print", re.compile("print$")),
        Token("var", re.compile("[a-z]+"))
    }), re.compile("\\s+"))
    assert lspec.partial_lex("a p") == {
        (Token("var", re.compile("[a-z]+"), "a", True),
         Token("var", re.compile("[a-z]+"), "p", False)),
        (Token("var", re.compile("[a-z]+"), "a", True),
         Token("print", re.compile("print$"), "p", False))
    }

    assert lspec.lex("a p") == {
        (Token("var", re.compile("[a-z]+"), "a", True),
         Token("var", re.compile("[a-z]+"), "p", True))
    }
