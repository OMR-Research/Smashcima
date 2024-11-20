import math
from typing import Iterator


class Vector2:
    """Mathematical 2D vector"""

    def __init__(self, x: float, y: float):
        self.x = float(x)
        self.y = float(y)
    
    @property
    def left(self) -> float:
        return self.x

    @property
    def top(self) -> float:
        return self.y

    @property
    def magnitude_squared(self) -> float:
        return self.x * self.x + self.y * self.y
    
    @property
    def magnitude(self) -> float:
        return math.sqrt(self.magnitude_squared)
    
    def __repr__(self):
        return f"Vector2({self.x}, {self.y})"

    def __add__(self, other):
        if isinstance(other, Vector2):
            return Vector2(self.x + other.x, self.y + other.y)
        else:
            raise ValueError("Vectors can only be added with other vectors")
    
    def __sub__(self, other):
        if isinstance(other, Vector2):
            return Vector2(self.x - other.x, self.y - other.y)
        else:
            raise ValueError("Vectors can only be subtracted from other vectors")
    
    def __neg__(self):
        return Vector2(-self.x, -self.y)

    def __mul__(self, other):
        if isinstance(other, float) or isinstance(other, int):
            return Vector2(self.x * other, self.y * other)
        else:
            raise ValueError("Vectors can only be multiplied by scalars")
    
    def __truediv__(self, other):
        if isinstance(other, float) or isinstance(other, int):
            return Vector2(self.x / other, self.y / other)
        else:
            raise ValueError("Vectors can only be divided by scalars")
    
    def __iter__(self) -> Iterator[float]:
        yield self.x
        yield self.y

    def rotate90degCC(self) -> "Vector2":
        """Returns a 90deg rotated version of the vector counter clockwise"""
        return Vector2(self.y, -self.x)

    def rotate90degCW(self) -> "Vector2":
        """Returns a 90deg rotated version of the vector clockwise"""
        return Vector2(-self.y, self.x)

    def normalize(self) -> "Vector2":
        """Returns the vector normalized to unit length"""
        m = self.magnitude
        if m == 0:
            raise Exception("Zero vector cannot be normalized")
        return self / m
