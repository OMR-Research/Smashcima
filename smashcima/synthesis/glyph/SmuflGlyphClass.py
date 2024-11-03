from enum import Enum
from smashcima.scene.semantic.TypeDuration import TypeDuration
from smashcima.scene.semantic.StemValue import StemValue
from smashcima.scene.semantic.AccidentalValue import AccidentalValue


class SmuflGlyphClass(str, Enum):
    """
    Enum that represents glyphs from the SMuFL specification.
    https://www.w3.org/2019/03/smufl13/
    """

    # Brackets and dividers
    # https://www.w3.org/2019/03/smufl13/tables/staff-brackets-and-dividers.html
    brace = "smufl::brace"
    bracket = "smufl::bracket"

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

    # Time signatures
    # https://www.w3.org/2019/03/smufl13/tables/time-signatures.html
    timeSig0 = "smufl::timeSig0"
    timeSig1 = "smufl::timeSig1"
    timeSig2 = "smufl::timeSig2"
    timeSig3 = "smufl::timeSig3"
    timeSig4 = "smufl::timeSig4"
    timeSig5 = "smufl::timeSig5"
    timeSig6 = "smufl::timeSig6"
    timeSig7 = "smufl::timeSig7"
    timeSig8 = "smufl::timeSig8"
    timeSig9 = "smufl::timeSig9"
    timeSigCommon = "smufl::timeSigCommon"
    timeSigCutCommon = "smufl::timeSigCutCommon"

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

    # Accidentals
    # https://www.w3.org/2019/03/smufl13/tables/standard-accidentals-12-edo.html
    accidentalFlat = "smufl::accidentalFlat"
    accidentalNatural = "smufl::accidentalNatural"
    accidentalSharp = "smufl::accidentalSharp"
    accidentalDoubleSharp = "smufl::accidentalDoubleSharp"
    accidentalDoubleFlat = "smufl::accidentalDoubleFlat"
    accidentalTripleSharp = "smufl::accidentalTripleSharp"
    accidentalTripleFlat = "smufl::accidentalTripleFlat"
    accidentalNaturalFlat = "smufl::accidentalNaturalFlat"
    accidentalNaturalSharp = "smufl::accidentalNaturalSharp"
    accidentalSharpSharp = "smufl::accidentalSharpSharp"
    accidentalParensLeft = "smufl::accidentalParensLeft"
    accidentalParensRight = "smufl::accidentalParensRight"
    accidentalBracketLeft = "smufl::accidentalBracketLeft"
    accidentalBracketRight = "smufl::accidentalBracketRight"

    # Articulation
    # https://www.w3.org/2019/03/smufl13/tables/articulation.html
    articAccentAbove = "smufl::articAccentAbove"
    articAccentBelow = "smufl::articAccentBelow"
    articStaccatoAbove = "smufl::articStaccatoAbove"
    articStaccatoBelow = "smufl::articStaccatoBelow"
    articTenutoAbove = "smufl::articTenutoAbove"
    articTenutoBelow = "smufl::articTenutoBelow"
    articStaccatissimoAbove = "smufl::articStaccatissimoAbove"
    articStaccatissimoBelow = "smufl::articStaccatissimoBelow"
    articStaccatissimoWedgeAbove = "smufl::articStaccatissimoWedgeAbove"
    articStaccatissimoWedgeBelow = "smufl::articStaccatissimoWedgeBelow"
    articStaccatissimoStrokeAbove = "smufl::articStaccatissimoStrokeAbove"
    articStaccatissimoStrokeBelow = "smufl::articStaccatissimoStrokeBelow"
    articMarcatoAbove = "smufl::articMarcatoAbove"
    articMarcatoBelow = "smufl::articMarcatoBelow"
    articMarcatoStaccatoAbove = "smufl::articMarcatoStaccatoAbove"
    articMarcatoStaccatoBelow = "smufl::articMarcatoStaccatoBelow"
    articAccentStaccatoAbove = "smufl::articAccentStaccatoAbove"
    articAccentStaccatoBelow = "smufl::articAccentStaccatoBelow"
    articTenutoStaccatoAbove = "smufl::articTenutoStaccatoAbove"
    articTenutoStaccatoBelow = "smufl::articTenutoStaccatoBelow"
    articTenutoAccentAbove = "smufl::articTenutoAccentAbove"
    articTenutoAccentBelow = "smufl::articTenutoAccentBelow"
    articStressAbove = "smufl::articStressAbove"
    articStressBelow = "smufl::articStressBelow"
    articUnstressAbove = "smufl::articUnstressAbove"
    articUnstressBelow = "smufl::articUnstressBelow"
    articLaissezVibrerAbove = "smufl::articLaissezVibrerAbove"
    articLaissezVibrerBelow = "smufl::articLaissezVibrerBelow"
    articMarcatoTenutoAbove = "smufl::articMarcatoTenutoAbove"
    articMarcatoTenutoBelow = "smufl::articMarcatoTenutoBelow"

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
            raise Exception(f"Unsupported type duration " + repr(duration))
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
            raise Exception(f"Unsupported type duration " + repr(duration))
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
            raise Exception(f"Unsupported clef " + repr(key))
        return clef

    @staticmethod
    def flag_from_type_duration_and_stem_value(
        type_duration: TypeDuration,
        stem_value: StemValue
    ) -> "SmuflGlyphClass":
        _LOOKUP = {
            ("up", "eighth"): SmuflGlyphClass.flag8thUp,
            ("down", "eighth"): SmuflGlyphClass.flag8thDown,
            ("up", "16th"): SmuflGlyphClass.flag16thUp,
            ("down", "16th"): SmuflGlyphClass.flag16thDown,
            ("up", "32nd"): SmuflGlyphClass.flag32ndUp,
            ("down", "32nd"): SmuflGlyphClass.flag32ndDown,
            ("up", "64th"): SmuflGlyphClass.flag64thUp,
            ("down", "64th"): SmuflGlyphClass.flag64thDown,
            ("up", "128th"): SmuflGlyphClass.flag128thUp,
            ("down", "128th"): SmuflGlyphClass.flag128thDown,
            ("up", "256th"): SmuflGlyphClass.flag256thUp,
            ("down", "256th"): SmuflGlyphClass.flag256thDown,
            ("up", "512th"): SmuflGlyphClass.flag512thUp,
            ("down", "512th"): SmuflGlyphClass.flag512thDown,
            ("up", "1024th"): SmuflGlyphClass.flag1024thUp,
            ("down", "1024th"): SmuflGlyphClass.flag1024thDown,
        }
        key = (stem_value.value, type_duration.value)
        flag = _LOOKUP.get(key)
        if flag is None:
            raise Exception(f"Unsupported flag " + repr(key))
        return flag

    @staticmethod
    def accidental_from_accidental_value(
        accidental_value: AccidentalValue
    ) -> "SmuflGlyphClass":
        _LOOKUP = {
            AccidentalValue.natural: SmuflGlyphClass.accidentalNatural,
            AccidentalValue.flat: SmuflGlyphClass.accidentalFlat,
            AccidentalValue.sharp: SmuflGlyphClass.accidentalSharp,
            AccidentalValue.doubleSharp: SmuflGlyphClass.accidentalDoubleSharp,
        }
        glyph_class = _LOOKUP.get(accidental_value)
        if glyph_class is None:
            raise Exception(f"Unsupported accidental " + repr(accidental_value))
        return glyph_class
