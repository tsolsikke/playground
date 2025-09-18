import pytest
from playground import p004_type as t


def test_int_ops():
    assert t.add_int(2, 3) == 5
    assert t.sub_int(10, 4) == 6
    assert t.mul_int(6, 7) == 42
    assert t.div_int(7, 3) == 2
    assert t.mod_int(7, 3) == 1
    assert t.pow_int(2, 8) == 256
    assert t.bit_and(0b1100, 0b1010) == 0b1000
    assert t.bit_or(0b1100, 0b1010) == 0b1110
    assert t.bit_xor(0b1100, 0b1010) == 0b0110
    assert t.bit_shift_left(1, 3) == 8
    assert t.bit_shift_right(8, 3) == 1


def test_float_ops():
    assert t.add_float(0.1, 0.2) == pytest.approx(0.3)
    assert t.div_float(7.0, 2.0) == pytest.approx(3.5)
    assert t.round_float(3.14159, 2) == 3.14


def test_bool_ops():
    assert t.and_bool(True, False) is False
    assert t.or_bool(True, False) is True
    assert t.not_bool(True) is False
    assert t.is_truthy(123) is True
    assert t.is_truthy("") is False


def test_str_ops():
    assert t.concat_str("Hello", "World") == "HelloWorld"
    assert t.repeat_str("a", 3) == "aaa"
    assert t.slice_str("abcdef", 1, 4) == "bcd"
    assert t.to_upper("abc") == "ABC"
    assert t.to_lower("XYZ") == "xyz"
    assert t.contains_str("banana", "na") is True
    assert t.split_str("a b c") == ["a", "b", "c"]


def test_bytes_ops():
    b = t.str_to_bytes("ABC")
    assert isinstance(b, bytes)
    assert t.bytes_to_str(b) == "ABC"
    assert t.get_byte_value(b, 0) == 65
    assert t.bytes_concat(b"A", b"B") == b"AB"
