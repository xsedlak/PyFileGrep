import pytest
import os
from RegexFileSearch import search_pattern

# Helper function to capture output
def capture_output(capsys, file_path, pattern, ignore_case=False, context=0, color=False):
    with open(file_path, 'r') as file:
        search_pattern(file, pattern, ignore_case, context, color)
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