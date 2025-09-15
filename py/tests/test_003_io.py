# py/tests/test_003_io.py

import io
import sys

import pytest

from playground import p003_io as io3


def test_read_write_line_roundtrip():
    buf = io.StringIO()
    io3.write_line("hello", stream=buf)
    io3.write_line("world", stream=buf)
    buf.seek(0)

    assert io3.read_line(buf) == "hello"
    assert io3.read_line(buf) == "world"
    assert io3.read_line(buf) == ""  # EOF


def test_print_flush_writes_and_flushes(capsys):
    io3.print_flush("a", 1, "c")
    captured = capsys.readouterr()
    assert captured.out == "a 1 c\n"  # デフォルト sep=" ", end="\n"


def test_read_ints_from_line_valid():
    assert io3.read_ints_from_line("1 2 3") == [1, 2, 3]
    assert io3.read_ints_from_line("  -10   0  42 ") == [-10, 0, 42]


def test_read_ints_from_line_invalid():
    with pytest.raises(ValueError):
        io3.read_ints_from_line("1 two 3")


def test_read_ints_from_stream():
    src = io.StringIO("10 20 30\n")
    assert io3.read_ints(src) == [10, 20, 30]

    src = io.StringIO("")  # EOF
    assert io3.read_ints(src) == []


def test_echo_stream_counts_chars_by_default():
    src = io.StringIO("abc\ndef\n")
    dst = io.StringIO()
    n = io3.echo_stream(src, dst)  # 文字数を返す
    assert n == len("abc\ndef\n")
    assert dst.getvalue() == "abc\ndef\n"


def test_echo_stream_counts_bytes_when_requested():
    s = "åßç\n"  # マルチバイト混在
    src = io.StringIO(s)
    dst = io.StringIO()
    n = io3.echo_stream(src, dst, count_bytes=True)  # バイト数でカウント
    assert n == len(s.encode("utf-8"))
    assert dst.getvalue() == s


def test_read_csv_rows_basic():
    content = "a,b,c\n1,2,3\nx,,z\n\n"
    src = io.StringIO(content)
    rows = io3.read_csv_rows(src)
    assert rows == [["a", "b", "c"], ["1", "2", "3"], ["x", "", "z"]]


def test_write_lines_and_read_all_back():
    dst = io.StringIO()
    io3.write_lines(["alpha", "beta", "gamma"], stream=dst)
    assert dst.getvalue().splitlines() == ["alpha", "beta", "gamma"]


def test_cli_sum_example(capsys):
    src = io.StringIO("10 20 30\n")
    total = io3.cli_sum(stdin=src, stdout=sys.stdout)
    assert total == 60
    captured = capsys.readouterr()
    assert captured.out.strip() == "60"
