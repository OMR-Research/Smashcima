import bisect
import random

from .PackedGlyph import PackedGlyph


class LineList(list):
    """Container that keeps a list of line glyphs and provides their sampling"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for glyph in self:
            assert isinstance(glyph, PackedGlyph), "Glyphs must be packed"
            assert glyph.line_length is not None, "Glyphs must be line glyphs"
        
        self.sort(key=lambda pg: pg.line_length)
        self.line_lengths = [pg.line_length for pg in self]
    
    def pick_line(
        self,
        target_length: float,
        rng: random.Random,
        percentile_spread=0.1
    ) -> PackedGlyph:
        center = bisect.bisect_left(
            self.line_lengths,
            target_length,
            0,
            len(self)
        )
        target_items = max(int(len(self) * percentile_spread), 2)
        
        # build neighborhood indices
        start = center - target_items // 2 # inclusive
        end = center + target_items // 2 # exclusive
        
        # clamp end
        if end > len(self):
            shift = end - len(self)
            start -= shift
            end -= shift
        
        # clamp start
        if start < 0:
            shift = 0 - start
            start += shift
            end += shift

        # squash end
        if end > len(self):
            end = len(self)
        
        # empty
        if end - start <= 0:
            raise Exception("Cannot sample an empty list")
        
        # sample
        index = rng.randint(start, end - 1)
        return self[index]
