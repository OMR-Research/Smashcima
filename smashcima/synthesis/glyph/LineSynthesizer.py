from smashcima.scene.LineGlyph import LineGlyph
from smashcima.geometry.Point import Point
from typing import Type, TypeVar
import abc


T = TypeVar("T", bound=LineGlyph)


class LineSynthesizer(abc.ABC):
    @abc.abstractmethod
    def synthesize_line(
        self,
        glyph_type: Type[T],
        glyph_class: str,
        start_point: Point,
        end_point: Point,
    ) -> T:
        """Synthesizes a line with the given type, glyph class and endpoints"""
        raise NotImplementedError
