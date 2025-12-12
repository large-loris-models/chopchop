from functools import reduce
from core.grammar import is_nonempty, TreeGrammar
from core.parser import D, Choice, Parser, delta, image
from core.lexing.lexing import LexerSpec
from typing import Callable


class RealizabilityChecker:
    def __init__(
        self,
        constraint: Callable[[TreeGrammar], TreeGrammar],
        initial_parser: Parser,
        lexerspec: LexerSpec,
    ):
        self.constraint = constraint
        self.parser = initial_parser
        self.lexerspec = lexerspec

    def realizable(self, prefix: str, final: bool = False) -> bool:
        """
        Checks if a prefix is realizable.
        If final is True, the prefix must be a complete program.
        """
        lexes = self.lexerspec.lex(prefix, final)
        prefix_space = Choice.of(
            reduce(lambda parser, token: D(token, parser), lex, self.parser)
            for lex in lexes
        )
        if final:
            prefix_space = delta(prefix_space)

        constrained_prefix_space = self.constraint(image(prefix_space))
        return is_nonempty(constrained_prefix_space)
