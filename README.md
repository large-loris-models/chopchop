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

# Description
The repository is organized as follows:

## Directories
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
