from typing import Tuple, List
import bisect


class Skyline:
    """Stacks boxes by dropping them from the top, building a skyline and
    determining for each next box where to place it."""
    def __init__(self, ground_level: float = 0):
        self.pins: List[Tuple[float, float]] = [
            (float("-Inf"), ground_level)
        ]
        """Going from left to right, a pin is a point (X, Y) that defines
        the new level ground of the skyline from that point to the left
        until the next pin is hit."""

    def drop_box(
        self,
        minimum: float,
        maximum: float,
        thickness: float
    ) -> float:
        """Minimum and maximum are the sideways bounds of the box and
        thickness is the "height" of the box falling from the top.
        Returned value is the top-position of the placed box."""
        assert minimum < maximum
        assert thickness > 0

        start_index = bisect.bisect_left(self.pins, minimum, key=lambda p: p[0])
        end_index = bisect.bisect_left(self.pins, maximum, key=lambda p: p[0])

        tallest_level = max(p[1] for p in self.pins[start_index-1:end_index])
        new_top = tallest_level + thickness

        new_pins = self.pins[:start_index] + [
            (minimum, new_top),
            (maximum, self.pins[end_index-1][1])
        ] + self.pins[end_index:]

        self.pins = new_pins
        self.compress_pins()
        return new_top
    
    def overlay_box(
        self,
        minimum: float,
        maximum: float,
        level: float
    ):
        """Places a box on the ground and updates the skyline appropriately"""
        assert minimum < maximum

        start_index = bisect.bisect_left(self.pins, minimum, key=lambda p: p[0])
        end_index = bisect.bisect_left(self.pins, maximum, key=lambda p: p[0])

        new_pins = self.pins[:start_index]

        if new_pins[-1][1] <= level:
            new_pins.append((minimum, level))

        for i in range(start_index, end_index):
            pin = self.pins[i]
            if pin[1] > level:
                new_pins.append(pin)
            else:
                new_pins.append((pin[0], level))
        
        new_pins.append(
            (maximum, self.pins[end_index-1][1])
        )
        
        new_pins += self.pins[end_index:]

        self.pins = new_pins
        self.compress_pins()
    
    def compress_pins(self):
        new_pins = [self.pins[0]]

        for pin in self.pins[1:]:
            last_position, last_level = new_pins[-1]
            
            # same level, skip
            if last_level == pin[1]:
                continue

            # same position, remove last
            if last_position == pin[0]:
                new_pins.pop()
            
            new_pins.append(pin)

        self.pins = new_pins


# .venv/bin/python3 -m smashcima.synthesis.layout.column.Skyline
if __name__ == "__main__":
    # drop boxes
    s = Skyline()
    assert s.drop_box(0, 2, thickness=1) == 1
    assert s.pins[1:] == [(0, 1), (2, 0)]

    #
    #OO
    ###########

    assert s.drop_box(1, 4, thickness=1) == 2
    assert s.pins[1:] == [(0, 1), (1, 2), (4, 0)]

    # OOO
    #OOxx
    ###########

    assert s.drop_box(0, 2, thickness=1) == 3
    assert s.pins[1:] == [(0, 3), (2, 2), (4, 0)]

    #OO
    #xOOO
    #OOxx
    ###########

    # overlay boxes
    s = Skyline()
    s.overlay_box(0, 2, level=1)
    assert s.pins[1:] == [(0, 1), (2, 0)]

    #
    #OO
    ###########

    s.overlay_box(1, 4, level=2)
    assert s.pins[1:] == [(0, 1), (1, 2), (4, 0)]

    # OOO
    #xOOO
    ###########

    s.overlay_box(2, 6, level=1)
    assert s.pins[1:] == [(0, 1), (1, 2), (4, 1), (6, 0)]

    # xxx
    #xxOOOO
    ###########

    s.overlay_box(0, 6, level=2)
    assert s.pins[1:] == [(0, 2), (6, 0)]

    #OOOOOO
    #OOOOOO
    ###########
