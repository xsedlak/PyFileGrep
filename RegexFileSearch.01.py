import argparse
import re
import sys
import os
from typing import TextIO
from termcolor import colored

class FileProcessor:
    def __init__(self, pattern: str, ignore_case: bool, context: int, color: bool):
        self.pattern = pattern
        self.ignore_case = ignore_case
        self.context = context
        self.color = color
        self.regex = self._compile_regex()

    def _compile_regex(self):
        flags = re.IGNORECASE if self.ignore_case else 0
        try:
            return re.compile(self.pattern, flags)
        except re.error as e:
            raise ValueError(f"Invalid regular expression: {e}") from e

    def process(self, file: TextIO):
        context_before = []
        line_number = 0
        last_match_end = 0

        while True:
            line = file.readline()
            if not line:
                break

            line_number += 1
            line_content = line.rstrip('\n')

            if self.regex.search(line_content):
                self._print_context_separator(line_number, last_match_end)
                self._print_context_before(context_before, file.name)
                self._print_matching_line(line_number, line_content, file.name)
                last_match_end = self._print_context_after(file, line_number)
                context_before = []
            else:
                self._update_context_buffer(context_before, line_number, line_content)

    def _print_context_separator(self, current_line: int, last_match_end: int):
        if last_match_end > 0 and current_line - last_match_end > 1:
            print(colored("---", 'yellow'))

    def _print_context_before(self, context_buffer: list, filename: str):
        if self.context > 0 and context_buffer:
            for ctx_line in context_buffer[-self.context :]:
                self._print_line(filename, *ctx_line)

    def _print_matching_line(self, line_num: int, content: str, filename: str):
        highlighted = self.regex.sub(
            lambda m: colored(m.group(0), 'red', attrs=['bold']),
            content
        ) if self.color else content
        self._print_line(filename, line_num, highlighted, is_match=True)

    def _print_context_after(self, file: TextIO, start_line: int) -> int:
        context_lines = []
        current_line = start_line
        for _ in range(self.context):
            line = file.readline()
            if not line:
                break
            current_line += 1
            self._print_line(file.name, current_line, line.rstrip('\n'))
        return current_line

    def _update_context_buffer(self, buffer: list, line_num: int, content: str):
        if self.context > 0:
            buffer.append((line_num, content))
            if len(buffer) > self.context * 2:
                buffer.pop(0)

    def _print_line(self, filename: str, line_num: int, content: str, is_match: bool = False):
        prefix = colored(f"{filename}[{line_num}]", 'cyan') if self.color else f"{filename}[{line_num}]"
        print(f"{prefix}{content}")

def main():
    parser = argparse.ArgumentParser(
        description="Advanced file search with regex and context",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="Examples:\n"
               "  Search in file:  ./RegexFileSearch.py error log.txt\n"
               "  Stream input:     cat log.txt | ./RegexFileSearch.py error -\n"
               "  Case-insensitive: ./RegexFileSearch.py -i WARN *.log"
    )

    parser.add_argument("pattern", help="Regex pattern to search for")
    parser.add_argument("files", nargs="*", default=["-"],
                        help="Files to process (use '-' for stdin)")
    parser.add_argument("-i", "--ignore-case", action="store_true",
                        help="Case-insensitive search")
    parser.add_argument("-c", "--color", action="store_true",
                        help="Enable colored output")
    parser.add_argument("-C", "--context", type=int, default=0,
                        help="Number of context lines to show")

    # Print help if no arguments are provided
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    # Check if help argument is present and exit after printing help
    if '-h' in sys.argv or '--help' in sys.argv:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()


    try:
        processor = FileProcessor(
            pattern=args.pattern,
            ignore_case=args.ignore_case,
            context=args.context,
            color=args.color
        )

        for filename in args.files:
            try:
                if filename == "-":
                    processor.process(sys.stdin)
                else:
                    validate_file(filename)
                    with open(filename, 'r', buffering=1) as file:
                        processor.process(file)
            except (FileNotFoundError, PermissionError, IsADirectoryError) as e:
                handle_file_error(filename, e)

    except KeyboardInterrupt:
        print(colored("\n[ERROR] Search interrupted by user", 'yellow'), file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(colored(f"[ERROR] {e}", 'red'), file=sys.stderr)
        sys.exit(1)

def validate_file(path: str):
    if not os.path.exists(path):
        raise FileNotFoundError(f"File '{path}' does not exist")
    if not os.path.isfile(path):
        raise IsADirectoryError(f"'{path}' is a directory")
    if not os.access(path, os.R_OK):
        raise PermissionError(f"No read access for '{path}'")

def handle_file_error(filename: str, error: Exception):
    error_type = {
        FileNotFoundError: "File not found",
        IsADirectoryError: "Is a directory",
        PermissionError: "Permission denied"
    }.get(type(error), "File error")

    print(colored(f"[ERROR] {error_type}: {filename}", 'red'), file=sys.stderr)
    sys.exit(1)

if __name__ == "__main__":
    main()