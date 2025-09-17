from typing import List
"""
プリミティブ型 (004_type.py)

Python の基本的な型 (int, float, bool, str, bytes) に関する
基本的な操作を関数化したサンプル集。
"""


# ========= int 関連 =========
def add_int(a: int, b: int) -> int:
    return a + b


def sub_int(a: int, b: int) -> int:
    return a - b


def mul_int(a: int, b: int) -> int:
    return a * b


def div_int(a: int, b: int) -> int:
    """整数除算（C言語の / と違い、小数点以下切り捨て）"""
    return a // b


def mod_int(a: int, b: int) -> int:
    return a % b


def pow_int(a: int, b: int) -> int:
    return a**b


def bit_and(a: int, b: int) -> int:
    return a & b


def bit_or(a: int, b: int) -> int:
    return a | b


def bit_xor(a: int, b: int) -> int:
    return a ^ b


def bit_shift_left(a: int, n: int) -> int:
    return a << n


def bit_shift_right(a: int, n: int) -> int:
    return a >> n


# ========= float 関連 =========
def add_float(a: float, b: float) -> float:
    return a + b


def div_float(a: float, b: float) -> float:
    return a / b


def round_float(x: float, ndigits: int = 0) -> float:
    return round(x, ndigits)


# ========= bool 関連 =========
def and_bool(a: bool, b: bool) -> bool:
    return a and b


def or_bool(a: bool, b: bool) -> bool:
    return a or b


def not_bool(a: bool) -> bool:
    return not a


def is_truthy(x: object) -> bool:
    """Pythonのtruthy/falsy評価を返す"""
    return bool(x)


# ========= str 関連 =========
def concat_str(a: str, b: str) -> str:
    return a + b


def repeat_str(s: str, n: int) -> str:
    return s * n


def slice_str(s: str, start: int, end: int) -> str:
    return s[start:end]


def to_upper(s: str) -> str:
    return s.upper()


def to_lower(s: str) -> str:
    return s.lower()


def contains_str(s: str, sub: str) -> bool:
    return sub in s


def split_str(s: str, sep: str = " ") -> List[str]:
    return s.split(sep)


# ========= bytes 関連 =========
def str_to_bytes(s: str, encoding: str = "utf-8") -> bytes:
    return s.encode(encoding)


def bytes_to_str(b: bytes, encoding: str = "utf-8") -> str:
    return b.decode(encoding)


def get_byte_value(b: bytes, index: int) -> int:
    """b[index] を数値として返す"""
    return b[index]


def bytes_concat(a: bytes, b: bytes) -> bytes:
    return a + b
