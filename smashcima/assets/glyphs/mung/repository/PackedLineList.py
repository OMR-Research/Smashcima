import bisect
import random
from typing import List

from .PackedLineGlyph import PackedLineGlyph


class PackedLineList:
    """Holds a list of lines glyphs optimized for their length-based sampling"""
    def __init__(self, lines: List[PackedLineGlyph]):
        assert all(isinstance(pg, PackedLineGlyph) for pg in lines), \
            "Items must be packed line glyphs"
        
        lines.sort(key=lambda pg: pg.line_length)

        self.lines = lines
        """The list of packed line glyphs, sorted by length ascending"""

        self.line_lengths = [pg.line_length for pg in lines]
        """The list of corresponding line lengths (for sampling)"""
    
    def pick_line(
        self,
        target_length: float,
        rng: random.Random,
        percentile_spread=0.1
    ) -> PackedLineGlyph:
        center = bisect.bisect_left(
            self.line_lengths,
            target_length,
            0,
            len(self.lines)
        )
        target_items = max(int(len(self.lines) * percentile_spread), 2)
        
        # build neighborhood indices
        start = center - target_items // 2 # inclusive
        end = center + target_items // 2 # exclusive
        
        # clamp end
        if end > len(self.lines):
            shift = end - len(self.lines)
            start -= shift
            end -= shift
        
        # clamp start
        if start < 0:
            shift = 0 - start
            start += shift
            end += shift

        # squash end
        if end > len(self.lines):
            end = len(self.lines)
        
        # empty
        if end - start <= 0:
            raise Exception("Cannot sample an empty list")
        
        # sample
        index = rng.randint(start, end - 1)
        return self.lines[index]
