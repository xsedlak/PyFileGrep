import pytest
from RegexFileSearch import search_pattern

# Helper function to capture output
def capture_output(capsys, file_path, pattern, ignore_case=False, context=0, color=False):
    with open(file_path, 'r') as file:
        search_pattern(file, pattern, ignore_case, context, color)
    return capsys.readouterr().out

# Helper function for streaming input
def capture_stream_output(capsys, stream_data, pattern, ignore_case=False, context=0, color=False):
    from io import StringIO
    stream = StringIO(stream_data)
    search_pattern(stream, pattern, ignore_case, context, color)
    return capsys.readouterr().out

# Positive cases
@pytest.mark.positive
def test_find_existing_user(capsys):
    output = capture_output(capsys, "/etc/passwd", "root")
    assert "root:" in output

@pytest.mark.positive
def test_find_existing_group(capsys):
    output = capture_output(capsys, "/etc/group", "sudo")
    assert "sudo:" in output

@pytest.mark.positive
def test_case_sensitive_search(capsys):
    output = capture_output(capsys, "/etc/passwd", "Root")
    assert output == ""  # Should not find "Root" (with capital R)

@pytest.mark.positive
def test_case_insensitive_search(capsys):
    output = capture_output(capsys, "/etc/passwd", "Root", ignore_case=True)
    assert "root:" in output

# Negative cases
@pytest.mark.negative
def test_nonexistent_user(capsys):
    output = capture_output(capsys, "/etc/passwd", "nonexistentuser")
    assert output == ""

@pytest.mark.negative
def test_nonexistent_group(capsys):
    output = capture_output(capsys, "/etc/group", "nonexistentgroup")
    assert output == ""

# Corner cases
@pytest.mark.corner
def test_special_characters(capsys):
    output = capture_output(capsys, "/etc/passwd", r"\$")
    assert "" in output  # Searches for lines containing $

@pytest.mark.corner
def test_long_pattern(capsys):
    long_pattern = "x" * 1000
    output = capture_output(capsys, "/etc/passwd", long_pattern)
    assert output == ""

@pytest.mark.corner
def test_context_lines(capsys):
    output = capture_output(capsys, "/etc/passwd", "root", context=2)
    assert len(output.split("\n")) > 3  # Should contain more than 3 lines

# Test for uppercase letters in /etc/passwd (if they exist)
@pytest.mark.positive
def test_uppercase_in_passwd(capsys):
    # Capture all lines containing uppercase letters
    output = capture_output(capsys, "/etc/passwd", "[A-Z]")
    assert len(output.split("\n")) > 1 # Should contain more than 1 line

# TC's for streaming/big input files
# Positive cases
@pytest.mark.positive
def test_large_file_positive(tmp_path, capsys):
    # Create a large temporary file
    large_file = tmp_path / "large_file.txt"
    with open(large_file, "w") as f:
        for i in range(1_000_000):  # 1 million lines
            f.write(f"line {i}\n")
        f.write("target_line\n")  # Add a target line to match

    output = capture_output(capsys, file_path=str(large_file), pattern="target_line")
    assert "target_line" in output


@pytest.mark.positive
def test_streamed_input_positive(capsys):
    # Simulate streamed input
    stream_data = "line1\nline2\ntarget_line\nline4\n"
    output = capture_stream_output(capsys, stream_data, "target_line")
    assert "target_line" in output

# Negative cases
@pytest.mark.negative
def test_large_file_no_match(tmp_path, capsys):
    # Create a large temporary file with no matching lines
    large_file = tmp_path / "large_file_no_match.txt"
    with open(large_file, "w") as f:
        for i in range(1_000_000):  # 1 million lines
            f.write(f"line {i}\n")

    output = capture_output(capsys, file_path=str(large_file), pattern="nonexistent_pattern")
    assert output == ""

@pytest.mark.negative
def test_streamed_input_no_match(capsys):
    # Simulate streamed input with no matching lines
    stream_data = "line1\nline2\nline3\nline4\n"
    output = capture_stream_output(capsys, stream_data, "nonexistent_pattern")
    assert output == ""

# Corner cases
@pytest.mark.corner
def test_large_file_special_characters(tmp_path, capsys):
    # Create a large temporary file with special characters
    large_file = tmp_path / "large_file_special_chars.txt"
    with open(large_file, "w") as f:
        for i in range(1_000):
            f.write(f"line {i} $pecial_char$\n")

    output = capture_output(capsys, file_path=str(large_file), pattern=r"\$pecial_char\$")
    assert "$pecial_char$" in output

@pytest.mark.corner
def test_streamed_input_special_characters(capsys):
    # Simulate streamed input with special characters
    stream_data = "line1\nline2 $pecial_char$\nline3\n"
    output = capture_stream_output(capsys, stream_data, r"\$pecial_char\$")
    assert "$pecial_char$" in output

@pytest.mark.corner
def test_large_file_long_pattern(tmp_path, capsys):
    # Create a large temporary file and search for a long pattern
    large_file = tmp_path / "large_file_long_pattern.txt"
    long_pattern = "x" * 1000  # Very long pattern to match

    with open(large_file, "w") as f:
        for i in range(1_000):
            f.write(f"line {i}\n")
        f.write(long_pattern + "\n")

    output = capture_output(capsys, file_path=str(large_file), pattern=long_pattern)

    assert long_pattern in output

@pytest.mark.corner
def test_streamed_input_long_pattern(capsys):
    # Simulate streamed input with a long pattern to match
    long_pattern = "x" * 1000  # Very long pattern to match
    stream_data = f"line1\n{long_pattern}\nline3\n"

    output = capture_stream_output(capsys, stream_data, long_pattern)
    assert long_pattern in output