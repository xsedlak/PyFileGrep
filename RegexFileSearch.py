import argparse
import re
import sys
from typing import TextIO
from termcolor import colored

def search_pattern(file: TextIO, pattern: str, ignore_case: bool, context: int, color: bool) -> None:
    """
    Search for a regex pattern in a file or stream and print matching lines with optional context.
    """
    flags = re.IGNORECASE if ignore_case else 0
    try:
        regex = re.compile(pattern, flags)
    except re.error as e:
        print(colored(f"[ERROR] Invalid regular expression: {e}", 'red'), file=sys.stderr)
        return

    # Sliding window for context lines
    context_buffer = []
    line_number = 0

    try:
        for line in file:
            line_number += 1
            line = line.rstrip()  # Remove trailing newline characters

            if regex.search(line):
                # Print context lines before the match
                if context_buffer:
                    print(colored("---", 'yellow'))
                    for buffered_line in context_buffer:
                        print(buffered_line)

                # Print the matching line with optional highlighting
                if color:
                    highlighted_line = regex.sub(lambda m: f"\033[91m{m.group(0)}\033[0m", line)
                    print(f"{getattr(file, 'name', '<stream>')}[{line_number}]{highlighted_line}")
                else:
                    print(f"{getattr(file, 'name', '<stream>')}[{line_number}]{line}")

                # Clear the context buffer after printing
                context_buffer.clear()

                # Add upcoming context lines to the buffer
                for _ in range(context):
                    try:
                        next_line = next(file).rstrip()
                        line_number += 1
                        context_buffer.append(f"{getattr(file, 'name', '<stream>')}[{line_number}]{next_line}")
                    except StopIteration:
                        break

            else:
                # Maintain a rolling buffer of context lines
                if context > 0:
                    if len(context_buffer) >= context:
                        context_buffer.pop(0)
                    context_buffer.append(f"{getattr(file, 'name', '<stream>')}[{line_number}]{line}")

    except Exception as e:
        print(colored(f"[ERROR] An error occurred while processing the file: {e}", 'red'), file=sys.stderr)


def main() -> None:
    """
    Main function to parse arguments and handle input/output.
    """
    parser = argparse.ArgumentParser(description="Search for lines matching a pattern in files or streams.")
    parser.add_argument("pattern", help="The regular expression pattern to search for.")
    parser.add_argument("files", nargs="*", default=["-"], help="Files to search (default: standard input).")
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
            try:
                if file_name == "-":
                    # Process standard input (streamed data)
                    search_pattern(sys.stdin, args.pattern, args.ignore_case, args.context, args.color)
                else:
                    # Open file with efficient buffering for large files
                    with open(file_name, "r", encoding="ascii") as file:
                        search_pattern(file, args.pattern, args.ignore_case, args.context, args.color)
            except FileNotFoundError:
                print(colored(f"[ERROR] File not found: {file_name}", 'red'), file=sys.stderr)
            except IsADirectoryError:
                print(colored(f"[ERROR] {file_name} is a directory, not a file!", 'red'), file=sys.stderr)
            except IOError as e:
                print(colored(f"[ERROR] Error reading file {file_name}: {e}", 'red'), file=sys.stderr)
    except KeyboardInterrupt:
        print(colored("\n[ERROR] Search interrupted by user!", 'yellow'), file=sys.stderr)


if __name__ == "__main__":
    main()
