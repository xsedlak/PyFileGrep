import argparse
import re
import sys
import os
from typing import TextIO
from termcolor import colored

def search_pattern(file: TextIO, pattern: str, ignore_case: bool, context: int, color: bool) -> None:
    flags = re.IGNORECASE if ignore_case else 0
    try:
        regex = re.compile(pattern, flags)
    except re.error as e:
        print(colored(f"Error in regular expression: {e}", 'red'), file=sys.stderr)
        return

    # Read all lines from the file
    lines = file.readlines()

    for i, line in enumerate(lines):
        if regex.search(line):
            # Determine the range of lines to print (including context)
            start, end = max(0, i - context), min(len(lines), i + context + 1)
            # Print separator if not the first match
            if i > 0 and start > 0:
                print(colored("---", 'yellow'))
            # Print lines (with or without highlighting)
            for j in range(start, end):
                output = f"{file.name}[{j + 1}]{lines[j].strip()}"
                if j == i:
                    if color:
                        output = regex.sub(lambda m: colored(m.group(0), 'green'), output)
                    print(colored(output, 'cyan'))
                else:
                    print(output)

def main() -> None:
    # Set up command line argument parser
    parser = argparse.ArgumentParser(description="Search for lines matching a pattern in files.")
    parser.add_argument("pattern", help="The regular expression pattern to search for.")
    parser.add_argument("files", nargs="+", help="Files to search.")
    parser.add_argument("-i", "--ignore-case", action="store_true", help="Ignore case distinctions.")
    parser.add_argument("-c", "--color", action="store_true", help="Highlight matching text.")
    parser.add_argument("-C", "--context", type=int, default=0, help="Number of context lines to include.")

    # Print help if no arguments are provided
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()

    try:
        for file_name in args.files:
            # Check if file exists
            if not os.path.exists(file_name):
                raise FileNotFoundError(f"File {file_name} not found!")
            # Check if it's a file and not a directory
            if not os.path.isfile(file_name):
                raise IsADirectoryError(f"{file_name} is a directory, not a file!")

            try:
                with open(file_name, 'r') as file:
                    search_pattern(file, args.pattern, args.ignore_case, args.context, args.color)
            except IOError as e:
                print(f"[ERROR] Reading file {file_name}: {e}", file=sys.stderr)
    except FileNotFoundError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)
    except IsADirectoryError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n[ERROR] Search interrupted by user!", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
