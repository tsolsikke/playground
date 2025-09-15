# py/src/playground/p003_io.py

import csv
import sys
from typing import Iterable, List, Sequence, TextIO, Optional


def _stdout(stream: Optional[TextIO]) -> TextIO:
    return stream if stream is not None else sys.stdout


def _stdin(stream: Optional[TextIO]) -> TextIO:
    return stream if stream is not None else sys.stdin


def read_line(stream: Optional[TextIO] = None) -> str:
    """
    1行読み込み（末尾の改行は除去）。EOFのときは空文字を返す。
    """
    s = _stdin(stream)
    line = s.readline()
    if line == "":
        return ""
    return line.rstrip("\n")


def write_line(s: str, stream: Optional[TextIO] = None, *, flush: bool = False) -> None:
    """
    1行書き込み（末尾に改行を付ける）。必要なら flush。
    """
    out = _stdout(stream)
    out.write(s)
    out.write("\n")
    if flush:
        out.flush()


def print_flush(*args, sep: str = " ", end: str = "\n", stream: Optional[TextIO] = None) -> None:
    """
    print の薄いラッパ：即時 flush を保証。
    """
    out = _stdout(stream)
    out.write(sep.join(map(str, args)) + end)
    out.flush()


def read_ints_from_line(line: str) -> List[int]:
    """
    空白区切りの整数列を1行から読み取る。
    空要素は無視。整数化できないトークンがあれば ValueError。
    """
    tokens = [t for t in line.strip().split() if t != ""]
    ints: List[int] = []
    for t in tokens:
        try:
            ints.append(int(t, 10))
        except Exception as e:
            raise ValueError(f"invalid int token: {t!r}") from e
    return ints


def read_ints(stream: Optional[TextIO] = None) -> List[int]:
    """
    ストリームから1行読み取り、空白区切りの整数配列にして返す。
    EOFなら空配列。
    """
    line = read_line(stream)
    if line == "":
        return []
    return read_ints_from_line(line)


def echo_stream(src: TextIO, dst: Optional[TextIO] = None, *, count_bytes: bool = False) -> int:
    """
    入力ストリームをそのまま出力へコピー。
    戻り値はデフォルトで「文字数」。count_bytes=True のときは UTF-8 バイト数。
    ※テキストIO想定。バイナリは対象外。
    """
    out = _stdout(dst)
    total_chars = 0
    total_bytes = 0
    while True:
        chunk = src.read(8192)
        if chunk == "":
            break
        out.write(chunk)
        total_chars += len(chunk)
        if count_bytes:
            total_bytes += len(chunk.encode("utf-8"))
    return total_bytes if count_bytes else total_chars


def read_csv_rows(
    stream: TextIO,
    *,
    delimiter: str = ",",
    quotechar: str = '"',
    skip_empty: bool = True,
) -> List[List[str]]:
    """
    CSVを全行読み込み、2次元配列にして返す（ヘッダ有無は問わない）。
    """
    # TextIO を前提とする。csv は newline='' が望ましいが、外部から渡されるためここでは制御しない。
    reader = csv.reader(stream, delimiter=delimiter, quotechar=quotechar)
    rows: List[List[str]] = []
    for row in reader:
        if skip_empty and (len(row) == 0 or (len(row) == 1 and row[0] == "")):
            continue
        rows.append(row)
    return rows


def write_lines(lines: Sequence[str], stream: Optional[TextIO] = None, *, flush: bool = False) -> None:
    """
    シーケンスの各要素を1行ずつ書き出す（末尾に改行付与）。
    """
    out = _stdout(stream)
    for s in lines:
        out.write(s)
        out.write("\n")
    if flush:
        out.flush()


def read_all(stream: Optional[TextIO] = None) -> str:
    """
    ストリームの中身を全て読み取り文字列で返す。
    """
    s = _stdin(stream)
    return s.read()


def to_string_lines(values: Iterable[object]) -> List[str]:
    """
    任意オブジェクト列を str に変換した行配列へ。
    """
    return [str(v) for v in values]


def cli_sum(stdin: Optional[TextIO] = None, stdout: Optional[TextIO] = None) -> int:
    """
    1行の整数列を読み取り、合計値を出力して終了。戻り値は合計値。
    入力例: "10 20 30" -> 出力: "60"
    """
    ins = _stdin(stdin)
    outs = _stdout(stdout)
    ints = read_ints(ins)
    total = sum(ints)
    print_flush(str(total), stream=outs)
    return total