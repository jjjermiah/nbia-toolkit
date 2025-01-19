import pytest

from nbiatoolkit.fs.byte_size import ByteSize


def test_bytesize_initialization():
    """Test initialization of ByteSize."""
    b = ByteSize(1024)
    assert b.bytes == 1024
    assert int(b) == 1024


def test_readable_metric():
    """Test readable metric representation."""
    b = ByteSize(1500)
    suffix, value = b.readable_metric
    assert suffix == "KB"
    assert value == 1.5


def test_readable_binary():
    """Test readable binary representation."""
    b = ByteSize(2048)
    suffix, value = b.readable_binary
    assert suffix == "KiB"
    assert value == 2.0


def test_dynamic_attributes():
    """Test dynamic attribute access for different units."""
    b = ByteSize(1048576)  # 1 MiB
    assert b.kilobytes == 1048.576
    assert b.megabytes == 1.048576
    assert b.gigabytes == 0.001048576
    assert b.kibibytes == 1024
    assert b.mebibytes == 1
    assert b.gibibytes == 0.0009765625


def test_invalid_attribute():
    """Test access to an invalid attribute."""
    b = ByteSize(1024)
    with pytest.raises(AttributeError):
        _ = b.invalid_attribute


def test_str_representation():
    """Test string representation of ByteSize."""
    b = ByteSize(2048)
    assert str(b) == "2.00 KiB"


def test_repr_representation():
    """Test repr representation of ByteSize."""
    b = ByteSize(2048)
    assert repr(b) == "ByteSize(2048)"


def test_format_representation():
    """Test formatted string representation of ByteSize."""
    b = ByteSize(2048)
    assert format(b, ".1f") == "2.0 KiB"

    tb = ByteSize(1_000_000_000_000)

    assert format(tb, ".1f") == ""



def test_addition():
    """Test addition of two ByteSize instances."""
    b1 = ByteSize(1024)
    b2 = ByteSize(2048)
    assert b1 + b2 == ByteSize(3072)


def test_subtraction():
    """Test subtraction of two ByteSize instances."""
    b1 = ByteSize(2048)
    b2 = ByteSize(1024)
    assert b1 - b2 == ByteSize(1024)


def test_multiplication():
    """Test multiplication of ByteSize by an integer."""
    b = ByteSize(1024)
    assert b * 2 == ByteSize(2048)


def test_truedivision():
    """Test true division of ByteSize by an integer."""
    b = ByteSize(2048)
    assert b / 2 == ByteSize(1024)


def test_floordivision():
    """Test floor division of ByteSize by an integer."""
    b = ByteSize(2048)
    assert b // 2 == ByteSize(1024)


def test_large_value():
    """Test ByteSize with a large value."""
    b = ByteSize(10**12)
    suffix, value = b.readable_metric
    assert suffix == "TB"
    assert value == 1.0


def test_small_value():
    """Test ByteSize with a small value."""
    b = ByteSize(1)
    suffix, value = b.readable_binary
    assert suffix == "B"
    assert value == 1.0


def test_zero_value():
    """Test ByteSize with a zero value."""
    b = ByteSize(0)
    suffix, value = b.readable_binary
    assert suffix == "B"
    assert value == 0.0
