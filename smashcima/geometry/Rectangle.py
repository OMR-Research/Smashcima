from .Point import Point
from math import ceil, floor


class Rectangle:
    def __init__(self, x: float, y: float, width: float, height: float):
        assert width >= 0 and height >= 0, "Rectangle cannot have negative size"
        self.x = float(x)
        self.y = float(y)
        self.width = float(width)
        self.height = float(height)
    
    @property
    def left(self) -> float:
        return self.x

    @property
    def top(self) -> float:
        return self.y
    
    @property
    def right(self) -> float:
        return self.x + self.width
    
    @property
    def bottom(self) -> float:
        return self.y + self.height
    
    def __repr__(self):
        return f"Rectangle({self.x}, {self.y}, {self.width}, {self.height})"
    
    @property
    def center(self) -> Point:
        """The center point"""
        return Point(
            self.x + self.width / 2,
            self.y + self.height / 2
        )
    
    @property
    def top_left_corner(self) -> Point:
        """Top left corner point"""
        return Point(self.left, self.top)
    
    @property
    def top_right_corner(self) -> Point:
        """Top right corner point"""
        return Point(self.right, self.top)
    
    @property
    def bottom_left_corner(self) -> Point:
        """Bottom left corner point"""
        return Point(self.left, self.bottom)
    
    @property
    def bottom_right_corner(self) -> Point:
        """Bottom right corner point"""
        return Point(self.right, self.bottom)
    
    @property
    def has_no_area(self) -> bool:
        """Returns true if either of the two dimensions are zero"""
        return self.width == 0 or self.height == 0

    def snap_grow(self) -> "Rectangle":
        """Returns a copy of the rectangle with its size "ceiled" to the
        integer grid. That is, it grows so that it has integer position and size"""
        top = floor(self.top)
        bottom = ceil(self.bottom)
        left = floor(self.left)
        right = ceil(self.right)
        return Rectangle(
            x=left,
            y=top,
            width=right-left,
            height=bottom-top
        )
    
    def snap_shrink(self) -> "Rectangle":
        """Returns a copy of the rectangle with its size "floored to the
        integer grid. That is, it shrinks so that is has integer position and size"""
        top = ceil(self.top)
        bottom = floor(self.bottom)
        left = ceil(self.left)
        right = floor(self.right)
        return Rectangle(
            x=left,
            y=top,
            width=right-left,
            height=bottom-top
        )
    
    def dilate(self, distange: float) -> "Rectangle":
        """Return a rectangle that has grown on all sides uniformly
        by the given distance"""
        top = self.top - distange
        bottom = self.bottom + distange
        left = self.left - distange
        right = self.right + distange
        return Rectangle(
            x=left,
            y=top,
            width=right-left,
            height=bottom-top
        )
    
    def intersect_with(self, other: "Rectangle") -> "Rectangle":
        """Returns the rectangle of the intersection of two rectangles.
        Returns a 0-sized rectangle if the two rectangles don't overlap."""
        left = max(self.left, other.left)
        right = min(self.right, other.right)
        width = max(0, right - left)

        top = max(self.top, other.top)
        bottom = min(self.bottom, other.bottom)
        height = max(0, bottom - top)

        return Rectangle(
            x=left,
            y=top,
            width=width,
            height=height
        )
    
    def relativize_to(self, viewport: "Rectangle") -> "Rectangle":
        """Returns this rectangle with relative coodrinates to the viewport
        
        Relative coordinates vary between [0, 0] and [1, 1] within the viewport,
        but can get outside the bounds if this rectangle is not completely
        within the viewport. Use intersect_with() for clamping.
        """
        return Rectangle(
            x=(self.x - viewport.x) / viewport.width,
            y=(self.y - viewport.y) / viewport.height,
            width=self.width / viewport.width,
            height=self.height / viewport.height
        )
    
    def absolutize_to(self, viewport: "Rectangle") -> "Rectangle":
        """Return rectangle with absolute coordinates given a viewport

        Relative coordinates vary between [0, 0] and [1, 1] within the viewport,
        if `self` is relativized to these coordinates, use this method to
        convert this rectangle's coordinates back to absolute numbers.
        """
        return Rectangle(
            x=viewport.x + self.x * viewport.width,
            y=viewport.y + self.y * viewport.height,
            width=viewport.width * self.width,
            height=viewport.height * self.height
        )
