from __future__ import annotations

from functools import lru_cache
from types import MappingProxyType
from typing import ClassVar


class ByteSize(int):
    """
    A class that represents a size in bytes and provides readable
    representations in both metric (KB, MB, ...) and binary (KiB, MiB, ...) units.
    """

    _METRIC_BASE: ClassVar[int] = 1000
    _BINARY_BASE: ClassVar[int] = 1024
    _metric_suffixes: ClassVar[tuple[str, ...]] = ("KB", "MB", "GB", "TB")
    _binary_suffixes: ClassVar[tuple[str, ...]] = ("KiB", "MiB", "GiB", "TiB")

    _unit_map: ClassVar[MappingProxyType] = MappingProxyType(
        {
            "B": 1,
            "kilobytes": _METRIC_BASE,
            "KB": _METRIC_BASE,
            "megabytes": _METRIC_BASE**2,
            "MB": _METRIC_BASE**2,
            "gigabytes": _METRIC_BASE**3,
            "GB": _METRIC_BASE**3,
            "terabytes": _METRIC_BASE**4,
            "TB": _METRIC_BASE**4,
            "kibibytes": _BINARY_BASE,
            "KiB": _BINARY_BASE,
            "mebibytes": _BINARY_BASE**2,
            "MiB": _BINARY_BASE**2,
            "gibibytes": _BINARY_BASE**3,
            "GiB": _BINARY_BASE**3,
            "tebibytes": _BINARY_BASE**4,
            "TiB": _BINARY_BASE**4,
        }
    )

    def __new__(cls, value: int) -> ByteSize:
        """Create a new instance of the ByteSize class."""
        instance = super().__new__(cls, value)
        return instance

    def __init__(self, value: int) -> None:
        """Initialize the ByteSize instance."""
        self.bytes = self.B = int(value)
        super().__init__()

    @lru_cache(maxsize=None)
    def _get_readable(self, base: int, suffixes: list[str]) -> tuple[str, float]:
        """
        Determine the most appropriate readable representation for the given base.

        Parameters
        ----------
        base : int
            The base to use for calculations (e.g., 1000 for metric or 1024 for binary).
        suffixes : list[str]
            The list of suffixes corresponding to the units.

        Returns
        -------
        tuple[str, float]
                A tuple of the unit suffix and the scaled value.
        """
        value = self.bytes
        for i, suffix in enumerate(suffixes):
            unit_value = value / (base**i)
            if unit_value < base or i == len(suffixes) - 1:
                return suffix, unit_value
        # Fallback (logically unreachable)
        return suffixes[0], value

    @property
    def readable_metric(self) -> tuple[str, float]:
        """Get the most appropriate metric (base-1000) representation."""
        return self._get_readable(self._METRIC_BASE, self._metric_suffixes)

    @property
    def readable_binary(self) -> tuple[str, float]:
        """Get the most appropriate binary (base-1024) representation."""
        return self._get_readable(self._BINARY_BASE, self._binary_suffixes)

    def apparent_size(self, block_size: int) -> ByteSize:
        """
        Calculate the apparent size of this ByteSize value based on block size.

        Parameters
        ----------
        block_size : int
            The size of a single block in bytes.

        Returns
        -------
        ByteSize
            The apparent size in bytes, accounting for block allocation.
        """
        if block_size <= 0:
            raise ValueError("Block size must be greater than 0.")
        blocks = (self.bytes + block_size - 1) // block_size
        return ByteSize(blocks * block_size)

    def __getattr__(self, name: str) -> float:
        """
        Dynamically compute the value for kilobytes, megabytes, gigabytes, terabytes,
        and their binary counterparts.

        Parameters
        ----------
        name : str
            The name of the attribute being accessed.

        Returns
        -------
        float
            The computed value for the requested attribute.

        Raises
        ------
        AttributeError
            If the requested attribute is not recognized.
        """
        if name in self._unit_map:
            base = self._unit_map[name]
            return self.bytes / base
        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{name}'"
        )

    def __str__(self) -> str:
        """Return a formatted string representation of the ByteSize instance."""
        return self.__format__(".2f")

    def __repr__(self) -> str:
        """Return the official string representation of the ByteSize instance."""
        # return f"{self.__class__.__name__}({int(self)})"
        # returns the name and the value of the instance, but also the best possibble representation in human readable format
        return_str = f"{self.__class__.__name__}({int(self)})"
        return_str += f" = {self:.2f}"
        return return_str

    def __format__(self, format_spec: str) -> str:
        """Return a formatted string based on the specified format."""
        if ":" in format_spec:
            format_spec, suffix = format_spec.split(":")
            if suffix in self._unit_map:
                base = self._unit_map[suffix]
                val = self.bytes / base
                return f"{val:{format_spec}} {suffix}"
            else:
                raise ValueError(f"Unknown unit: {suffix}")
        elif format_spec in self._unit_map:
            base = self._unit_map[format_spec]
            val = self.bytes / base
            if format_spec == "B":
                return f"{val:.0f} {format_spec}"
            return f"{val:.2f} {format_spec}"
        else:
            suffix, val = self.readable_binary
            return f"{val:{format_spec}} {suffix}"

    def __sub__(self, other: int | ByteSize) -> ByteSize:
        """Subtract another ByteSize or int from this ByteSize."""
        return self.__class__(super().__sub__(other))

    def __add__(self, other: int | ByteSize) -> ByteSize:
        """Add another ByteSize or int to this ByteSize."""
        return self.__class__(super().__add__(other))

    def __mul__(self, other: int | ByteSize) -> ByteSize:
        """Multiply this ByteSize by another ByteSize or int."""
        return self.__class__(super().__mul__(other))

    def __truediv__(self, other: int | ByteSize) -> ByteSize:
        """Divide this ByteSize by another ByteSize or int."""
        return self.__class__(int(super().__truediv__(other)))

    def __floordiv__(self, other: int | ByteSize) -> ByteSize:
        """Perform floor division on this ByteSize."""
        return self.__class__(super().__floordiv__(other))


if __name__ == "__main__":
    size = ByteSize(10_737_418_240) + 123  # 10 GiB in bytes + 123 bytes

    # Binary (default)
    print(f"{size:.2f}")  # Output: "10.00 GiB"
    print(f"{size:.2f:GB}")  # Output: "10.74 GB"
    print(f"{size:.2f:KiB}")  # Output: "10485760.00 KiB"
    print(f"{size:KiB}")  # Output: "10485760.00 KiB"

    print(repr(size))  # Output: "ByteSize(10737418240) = 10.00 GiB"

    # apparant sizes for different block sizes
    size = ByteSize(1_024 * 2 + 123)
    # print the bare size
    print(f"Size: {size:B}")
    print(f"Apparent size with 512 block size: {size.apparent_size(512):B}")
    print(f"Apparent size with 1024 block size: {size.apparent_size(1024):B}")
    print(f"Apparent size with 4096 block size: {size.apparent_size(4096):B}")
    print(f"Apparent size with 8192 block size: {size.apparent_size(8192):B}")
    print(f"Apparent size with 16384 block size: {size.apparent_size(16384):B}")
