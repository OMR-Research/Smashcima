from dataclasses import dataclass
from ..SceneObject import SceneObject
from fractions import Fraction
from .TypeDuration import TypeDuration


@dataclass
class Durable(SceneObject):
    """Durable is something that has duration (note or rest)"""
    
    type_duration: TypeDuration
    """The duration type that the note has visually (e.g. an eighth note)"""
    
    augmentation_dots: int
    """How many augmentation (duration) dots are there
    to augment the note's duration"""
    
    fractional_duration: Fraction
    """How many quarter notes does the note actually take up (e.g. an eighth
    note triplet takes up less time than a regular eighth note)"""
