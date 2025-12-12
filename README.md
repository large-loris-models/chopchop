# ChopChop
A programmable constrained decoder for semantic properties (e.g., type safety, program equivalence up to rewrite, simple static analyses).
Users encode semantic constraints as pruners over AST-like "program spaces". ChopChop then automatically constrains the sampling of autoregressive LLMs to produce constraint-satisfying output. 
A comprehensive overview appears in [our paper](https://doi.org/10.1145/3776708).

# Installation
### Requirements
- Python 3.12+.
- To run the TypeScript case study, the typescript compiler `tsc` must be installed (`npm install -g typescript`).
### Instructions
1. Clone the repository:
```bash
git clone https://github.com/timothytmzhou/chopchop.git
cd chopchop
```

2. Verify your Python version by running
```bash
python3 --version
```
If this shows a version <3.12, explicitly call the next step with the version you have (e.g. `python3.12` instead of `python3`).

3. Make and activate a fresh virtual environment (see previous step):
```bash
python3 -m venv chopchop
source chopchop/bin/activate
```

4. Install dependencies:
```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

5. Verify installation suceeded by running:
```bash
python -m pytest
```
the tests may take 1-2 minutes to pass.

# Usage
ChopChop requires a grammar, abstract syntax, and zero or more pruner(s).
Grammars are written in the following Lark-like format:
```
<!-- Definitions of terminals. -->
NUM: /[0-9]+/
WS: /\s+/

<!-- Nonterminals and their productions. -->
start: expr ";"
expr: expr "+" num {Add} 
    | num
num: NUM {Num}

<!-- Ignore whitespace -->
%ignore WS
```
Each annotation in braces gives the name of the AST node to be constructed when the production rule fires.


Abstract syntax is specified by subclassing `Application`, a generic superclass for internal AST nodes.
For example, the Add node in the grammar above can be written as
```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Add(Application):
    left: TreeGrammar
    right: TreeGrammar
```

At runtime, a cyclic graph representing the set of possible ASTs is constructed.
We expose these graphs to users as `TreeGrammar` objects, which they should think of as infinite AST-like trees that have special `Union` and `EmptySet` nodes to represent a union of sets of ASTs and the empty set of ASTs respectively. 
To manipulate these objects, users write pruners, which are functions that map `TreeGrammar`s to `TreeGrammar`s by removing undesirable programs.
For example, 
```python
from core.grammar import TreeGrammar, Union, EmptySet, Token

@rewrite
def sum_of_evens(t: TreeGrammar) -> TreeGrammar:
  """Remove ASTs that contain even integers."""
    match t:
        case Union(children):
            return Union.of(sum_of_evens(c) for c in children)
        case Num(arg):
            token = as_tree(arg)
            match token:
                case Token(is_complete=True, prefix=prefix) if int(prefix) % 2 == 1:
                    return EmptySet()
                case _:
                    return t
        case Add(left, right):
            return Add(sum_of_evens(left), sum_of_evens(right))
        case _:
            return EmptySet()
```
Note that the pruner does not explicitly worry about cycles. 
The `@rewrite` annotation lifts the pruner to our cyclic datastructures.
However, users should avoid writing pruners where the set of distinct recursive invocations will not reach a fixpoint if run on a cyclic graph, e.g., by passing around a counter.

Finally, a user bundles the information into a realizability checker which can be used to constrain LLM calls.
```python
# Grammar & Abstract Syntax
grammar_source = files(__package__).joinpath("my_grammar.lark").read_text()
ast_constructors: list[type[Application]] = [Add, Num]

# Extract grammatical information
start_lexer_spec, start_grammar = parse_attribute_grammar(
    ast_constructors, grammar_source, "start"
).build_parser()

# Build RealizabilityChecker
checker = RealizabilityChecker(
    sum_of_evens,
    start_grammar,
    start_lexer_spec,
)

# Set up LLM and run it on a prompt
model_config = ModelConfig(model_id='codellama/CodeLlama-7b-Instruct-hf')
model_runner = LanguageModelRunner(model_config=model_config)
out = runner.run(
  Config(), "Write a sum of your favorite integers.", realizability_checker=checker
)
```

More complex examples can be found in `experiments/egraph` and `experiments/typescript`.

# Repository Organization
The repository is organized into the following directories:

- **`core`**  
  Implements the backend of the tool (constructing and manipulating prefix spaces).

- **`llm`**  
  Provides functionality for running LLMs and interfacing an LLM with a realizability checker.

- **`experiments`**  
  Split into two subdirectories for benchmarks:
  - `experiments/egraph`
  - `experiments/typescript`

  Each of these directories contains:
  - A realizability checker definition
    - A `.lark` file describing the concrete syntax.  
    - A `.py` file describing the abstract syntax.  
    - Another Python file defining a pruner.  
    - For `egraph` benchmarks, rewrite rules are included in an `.egglog` file.
  - A `scripts` subdirectory  
    Contains scripts to run experiments.
  - a `paper_data` subdirectory  
    Contains the raw data used in the paper.

- **`demo`**  
  Contains code for running a small web demo, allowing users to check realizability of various prefixes.  
  A publicly available version is hosted at [chop.streamlit.app](https://chop.streamlit.app).
  Users can provide prefixes and check realizability with respect to a checker: by default, there is a basic example with an egraph-based checker.
  There is also a custom option to define your own checker.
