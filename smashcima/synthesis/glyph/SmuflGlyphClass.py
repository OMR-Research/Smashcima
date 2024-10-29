from enum import Enum
from smashcima.scene.semantic.TypeDuration import TypeDuration


class SmuflGlyphClass(str, Enum):
    """
    Enum that represents glyphs from the SMuFL specification.
    https://www.w3.org/2019/03/smufl13/
    """

    # Barlines
    # https://w3c.github.io/smufl/latest/tables/barlines.html
    barlineSingle = "smufl::barlineSingle"

    # Clefs
    # https://w3c.github.io/smufl/latest/tables/clefs.html
    gClef = "smufl::gClef"
    cClef = "smufl::cClef"
    fClef = "smufl::fClef"
    gClefSmall = "smufl::gClefSmall"
    cClefSmall = "smufl::cClefSmall"
    fClefSmall = "smufl::fClefSmall"

    # Noteheads
    # https://w3c.github.io/smufl/latest/tables/noteheads.html
    noteheadDoubleWhole = "smufl::noteheadDoubleWhole"
    noteheadDoubleWholeSquare = "smufl::noteheadDoubleWholeSquare"
    noteheadWhole = "smufl::noteheadWhole"
    noteheadHalf = "smufl::noteheadHalf"
    noteheadBlack = "smufl::noteheadBlack"

    # Individual Notes
    # https://www.w3.org/2019/03/smufl13/tables/individual-notes.html
    # IMPORTANT: This should only be used for ligatures,
    # the default usecase is synthesizing notehead-stem-flag separately.
    noteWhole = "smulf::noteWhole"
    noteHalfUp = "smulf::noteHalfUp"
    noteHalfDown = "smulf::noteHalfDown"
    noteQuarterUp = "smulf::noteQuarterUp"
    noteQuarterDown = "smulf::noteQuarterDown"
    note8thUp = "smulf::note8thUp"
    note8thDown = "smulf::note8thDown"
    note16thUp = "smulf::note16thUp"
    note16thDown = "smulf::note16thDown"
    note32ndUp = "smulf::note32ndUp"
    note32ndDown = "smulf::note32ndDown"
    note64thUp = "smufl::note64thUp"
    note64thDown = "smufl::note64thDown"
    note128thUp = "smufl::note128thUp"
    note128thDown = "smufl::note128thDown"
    note256thUp = "smufl::note256thUp"
    note256thDown = "smufl::note256thDown"
    note512thUp = "smufl::note512thUp"
    note512thDown = "smufl::note512thDown"
    note1024thUp = "smufl::note1024thUp"
    note1024thDown = "smufl::note1024thDown"
    augmentationDot = "smulf::augmentationDot"

    # Stems
    # https://w3c.github.io/smufl/latest/tables/stems.html
    stem = "smufl::stem"

    # Flags
    # https://w3c.github.io/smufl/latest/tables/flags.html
    flag8thUp = "smufl::flag8thUp"
    flag8thDown = "smufl::flag8thDown"
    flag16thUp = "smufl::flag16thUp"
    flag16thDown = "smufl::flag16thDown"
    flag32ndUp = "smufl::flag32ndUp"
    flag32ndDown = "smufl::flag32ndDown"
    flag64thUp = "smufl::flag64thUp"
    flag64thDown = "smufl::flag64thDown"
    flag128thUp = "smufl::flag128thUp"
    flag128thDown = "smufl::flag128thDown"
    flag256thUp = "smufl::flag256thUp"
    flag256thDown = "smufl::flag256thDown"
    flag512thUp = "smufl::flag512thUp"
    flag512thDown = "smufl::flag512thDown"
    flag1024thUp = "smufl::flag1024thUp"
    flag1024thDown = "smufl::flag1024thDown"

    # Rests
    # https://www.w3.org/2019/03/smufl13/tables/rests.html
    restMaxima = "smulf::restMaxima"
    restLonga = "smulf::restLonga"
    restDoubleWhole = "smulf::restDoubleWhole"
    restWhole = "smulf::restWhole"
    restHalf = "smulf::restHalf"
    restQuarter = "smulf::restQuarter"
    rest8th = "smulf::rest8th"
    rest16th = "smulf::rest16th"
    rest32nd = "smulf::rest32nd"
    rest64th = "smulf::rest64th"
    rest128th = "smulf::rest128th"
    rest256th = "smulf::rest256th"
    rest512th = "smulf::rest512th"
    rest1024th = "smulf::rest1024th"

    @staticmethod
    def notehead_from_type_duration(duration: TypeDuration) -> "SmuflGlyphClass":
        # https://www.w3.org/2021/06/musicxml40/musicxml-reference/data-types/note-type-value/
        _LOOKUP = {
            TypeDuration.thousand_twenty_fourth: SmuflGlyphClass.noteheadBlack,
            TypeDuration.five_hundred_twelfth: SmuflGlyphClass.noteheadBlack,
            TypeDuration.two_hundred_fifty_sixth: SmuflGlyphClass.noteheadBlack,
            TypeDuration.hundred_twenty_eighth: SmuflGlyphClass.noteheadBlack,
            TypeDuration.sixty_fourth: SmuflGlyphClass.noteheadBlack,
            TypeDuration.thirty_second: SmuflGlyphClass.noteheadBlack,
            TypeDuration.sixteenth: SmuflGlyphClass.noteheadBlack,
            TypeDuration.eighth: SmuflGlyphClass.noteheadBlack,
            TypeDuration.quarter: SmuflGlyphClass.noteheadBlack,
            TypeDuration.half: SmuflGlyphClass.noteheadHalf,
            TypeDuration.whole: SmuflGlyphClass.noteheadWhole,
            TypeDuration.breve: SmuflGlyphClass.noteheadDoubleWhole,
            TypeDuration.long: SmuflGlyphClass.noteheadDoubleWholeSquare,
            TypeDuration.maxima: SmuflGlyphClass.noteheadDoubleWholeSquare,
        }
        notehead = _LOOKUP.get(duration)
        if notehead is None:
            raise Exception(f"Unsupported type duration " + duration)
        return notehead
    
    @staticmethod
    def rest_from_type_duration(duration: TypeDuration) -> "SmuflGlyphClass":
        # https://www.w3.org/2021/06/musicxml40/musicxml-reference/data-types/note-type-value/
        _LOOKUP = {
            TypeDuration.thousand_twenty_fourth: SmuflGlyphClass.rest1024th,
            TypeDuration.five_hundred_twelfth: SmuflGlyphClass.rest512th,
            TypeDuration.two_hundred_fifty_sixth: SmuflGlyphClass.rest256th,
            TypeDuration.hundred_twenty_eighth: SmuflGlyphClass.rest128th,
            TypeDuration.sixty_fourth: SmuflGlyphClass.rest64th,
            TypeDuration.thirty_second: SmuflGlyphClass.rest32nd,
            TypeDuration.sixteenth: SmuflGlyphClass.rest16th,
            TypeDuration.eighth: SmuflGlyphClass.rest8th,
            TypeDuration.quarter: SmuflGlyphClass.restQuarter,
            TypeDuration.half: SmuflGlyphClass.restHalf,
            TypeDuration.whole: SmuflGlyphClass.restWhole,
            TypeDuration.breve: SmuflGlyphClass.restDoubleWhole,
            TypeDuration.long: SmuflGlyphClass.restLonga,
            TypeDuration.maxima: SmuflGlyphClass.restMaxima,
        }
        notehead = _LOOKUP.get(duration)
        if notehead is None:
            raise Exception(f"Unsupported type duration " + duration)
        return notehead
    
    @staticmethod
    def clef_from_clef_sign(clef_sign: str, small=False) -> "SmuflGlyphClass":
        _LOOKUP = {
            ("G", False): SmuflGlyphClass.gClef,
            ("G", True): SmuflGlyphClass.gClefSmall,
            ("F", False): SmuflGlyphClass.fClef,
            ("F", True): SmuflGlyphClass.fClefSmall,
            ("C", False): SmuflGlyphClass.cClef,
            ("C", True): SmuflGlyphClass.cClefSmall,
        }
        key = (clef_sign, small)
        clef = _LOOKUP.get(key)
        if clef is None:
            raise Exception(f"Unsupported clef " + key)
        return clef