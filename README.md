# Regex File Search

A Python script that searches one or more named input files for lines containing a match to a regular expression pattern. The script supports various options such as case-insensitivity, colour highlighting, and displaying surrounding context lines. Create Docker/Podman-based testing environments for a Makefile with pytest running on multiple Python versions.

## Features
- Search files or standard input using regular expressions
- Highlight matching text
- Ignore case distinctions
- Display surrounding context lines with `---` as a separator between matching blocks
- Compatible with Python 3.11+ and follows PEP8 coding guidelines

### Command-line Options
- `-c`, `--color`: Highlights matching text.
- `-i`, `--ignore-case`: Ignores case distinctions.
- `-C NUM`, `--context NUM`: Prints surrounding NUM lines of context.

## Requirements
- Python 3.12+
- Dependencies listed in `requirements.txt`:
    - `pytest`
    - `termcolor`

## Installation
1. Clone the repository:
    ```bash
    git clone https://github.com/xsedlak/PyFileGrep.git
    cd PyFileGrep
    ```
2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Testing Environment
This project includes a Docker/Podman-based testing environment to run tests for multiple Python versions (3.8 and 3.12). The testing setup uses Makefile targets to simplify the process.

### Makefile Targets
1. **Build containers**:
    ```bash
    make build
    ```
2. **Run tests**:
    ```bash
   make run
    ```
   This runs the tests inside the built containers.
3. **Clean up images**:
    ```bash
    make clean
    ```
   This removes the built Docker/Podman images.

## Custom Pytest Markers
This project uses custom pytest markers to organize tests into categories:
- `@pytest.mark.corner`: Tests for corner cases.
- `@pytest.mark.positive`: Tests for positive cases.
- `@pytest.mark.negative`: Tests for negative cases.
These markers are registered in the `pytest.ini` file to avoid warnings.
