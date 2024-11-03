from enum import Enum


class AccidentalValue(str, Enum):
    """Presence of an accidental for a note"""
    # https://www.w3.org/2021/06/musicxml40/musicxml-reference/data-types/accidental-value/
    sharp = "sharp"
    natural = "natural"
    flat = "flat"
    doubleSharp = "double-sharp"

    # sharpSharp = "sharp-sharp"
    # flatFlat = "flat-flat"
    # naturalSharp = "natural-sharp"
    # naturalFlat = "natural-flat"
