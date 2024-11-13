from smashcima.scene.LineGlyph import LineGlyph
import bisect
import random


def _get_line_length(glyph: LineGlyph) -> float:
    return (
        glyph.end_point.point.vector - glyph.start_point.point.vector
    ).magnitude


class LineList(list):
    """Container that keeps a list of line glyphs and provides their sampling"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for glyph in self:
            assert isinstance(glyph, LineGlyph)
        
        self.sort(key=_get_line_length)
        self.line_lengths = [_get_line_length(g) for g in self]
    
    def pick_line(
        self,
        target_length: float,
        rng: random.Random,
        percentile_spread=0.1
    ) -> LineGlyph:
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
