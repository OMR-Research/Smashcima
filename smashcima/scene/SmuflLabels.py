from enum import Enum
from .semantic import TypeDuration,StemValue, AccidentalValue


class SmuflLabels(str, Enum):
    """Classification labels from the SMuFL specification.
    
    Learn more at: https://www.w3.org/2019/03/smufl13/
    """

    # Brackets and dividers
    # https://www.w3.org/2019/03/smufl13/tables/staff-brackets-and-dividers.html
    brace = "smufl::brace"
    bracket = "smufl::bracket"

    # Staves
    # https://www.w3.org/2019/03/smufl13/tables/staves.html
    # IMPORTANT: The stafflines and leger lines section in SMuFL is intended
    # only for text-based applications. Use Smashcima label to represent
    # staves and stafflines instead.

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
    noteWhole = "smufl::noteWhole"
    noteHalfUp = "smufl::noteHalfUp"
    noteHalfDown = "smufl::noteHalfDown"
    noteQuarterUp = "smufl::noteQuarterUp"
    noteQuarterDown = "smufl::noteQuarterDown"
    note8thUp = "smufl::note8thUp"
    note8thDown = "smufl::note8thDown"
    note16thUp = "smufl::note16thUp"
    note16thDown = "smufl::note16thDown"
    note32ndUp = "smufl::note32ndUp"
    note32ndDown = "smufl::note32ndDown"
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
    augmentationDot = "smufl::augmentationDot"

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
    restMaxima = "smufl::restMaxima"
    restLonga = "smufl::restLonga"
    restDoubleWhole = "smufl::restDoubleWhole"
    restWhole = "smufl::restWhole"
    restHalf = "smufl::restHalf"
    restQuarter = "smufl::restQuarter"
    rest8th = "smufl::rest8th"
    rest16th = "smufl::rest16th"
    rest32nd = "smufl::rest32nd"
    rest64th = "smufl::rest64th"
    rest128th = "smufl::rest128th"
    rest256th = "smufl::rest256th"
    rest512th = "smufl::rest512th"
    rest1024th = "smufl::rest1024th"

    @staticmethod
    def notehead_from_type_duration(duration: TypeDuration) -> "SmuflLabels":
        # https://www.w3.org/2021/06/musicxml40/musicxml-reference/data-types/note-type-value/
        _LOOKUP = {
            TypeDuration.thousand_twenty_fourth: SmuflLabels.noteheadBlack,
            TypeDuration.five_hundred_twelfth: SmuflLabels.noteheadBlack,
            TypeDuration.two_hundred_fifty_sixth: SmuflLabels.noteheadBlack,
            TypeDuration.hundred_twenty_eighth: SmuflLabels.noteheadBlack,
            TypeDuration.sixty_fourth: SmuflLabels.noteheadBlack,
            TypeDuration.thirty_second: SmuflLabels.noteheadBlack,
            TypeDuration.sixteenth: SmuflLabels.noteheadBlack,
            TypeDuration.eighth: SmuflLabels.noteheadBlack,
            TypeDuration.quarter: SmuflLabels.noteheadBlack,
            TypeDuration.half: SmuflLabels.noteheadHalf,
            TypeDuration.whole: SmuflLabels.noteheadWhole,
            TypeDuration.breve: SmuflLabels.noteheadDoubleWhole,
            TypeDuration.long: SmuflLabels.noteheadDoubleWholeSquare,
            TypeDuration.maxima: SmuflLabels.noteheadDoubleWholeSquare,
        }
        notehead = _LOOKUP.get(duration)
        if notehead is None:
            raise Exception(f"Unsupported type duration " + repr(duration))
        return notehead
    
    @staticmethod
    def rest_from_type_duration(duration: TypeDuration) -> "SmuflLabels":
        # https://www.w3.org/2021/06/musicxml40/musicxml-reference/data-types/note-type-value/
        _LOOKUP = {
            TypeDuration.thousand_twenty_fourth: SmuflLabels.rest1024th,
            TypeDuration.five_hundred_twelfth: SmuflLabels.rest512th,
            TypeDuration.two_hundred_fifty_sixth: SmuflLabels.rest256th,
            TypeDuration.hundred_twenty_eighth: SmuflLabels.rest128th,
            TypeDuration.sixty_fourth: SmuflLabels.rest64th,
            TypeDuration.thirty_second: SmuflLabels.rest32nd,
            TypeDuration.sixteenth: SmuflLabels.rest16th,
            TypeDuration.eighth: SmuflLabels.rest8th,
            TypeDuration.quarter: SmuflLabels.restQuarter,
            TypeDuration.half: SmuflLabels.restHalf,
            TypeDuration.whole: SmuflLabels.restWhole,
            TypeDuration.breve: SmuflLabels.restDoubleWhole,
            TypeDuration.long: SmuflLabels.restLonga,
            TypeDuration.maxima: SmuflLabels.restMaxima,
        }
        notehead = _LOOKUP.get(duration)
        if notehead is None:
            raise Exception(f"Unsupported type duration " + repr(duration))
        return notehead
    
    @staticmethod
    def clef_from_clef_sign(clef_sign: str, small=False) -> "SmuflLabels":
        _LOOKUP = {
            ("G", False): SmuflLabels.gClef,
            ("G", True): SmuflLabels.gClefSmall,
            ("F", False): SmuflLabels.fClef,
            ("F", True): SmuflLabels.fClefSmall,
            ("C", False): SmuflLabels.cClef,
            ("C", True): SmuflLabels.cClefSmall,
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
    ) -> "SmuflLabels":
        _LOOKUP = {
            ("up", "eighth"): SmuflLabels.flag8thUp,
            ("down", "eighth"): SmuflLabels.flag8thDown,
            ("up", "16th"): SmuflLabels.flag16thUp,
            ("down", "16th"): SmuflLabels.flag16thDown,
            ("up", "32nd"): SmuflLabels.flag32ndUp,
            ("down", "32nd"): SmuflLabels.flag32ndDown,
            ("up", "64th"): SmuflLabels.flag64thUp,
            ("down", "64th"): SmuflLabels.flag64thDown,
            ("up", "128th"): SmuflLabels.flag128thUp,
            ("down", "128th"): SmuflLabels.flag128thDown,
            ("up", "256th"): SmuflLabels.flag256thUp,
            ("down", "256th"): SmuflLabels.flag256thDown,
            ("up", "512th"): SmuflLabels.flag512thUp,
            ("down", "512th"): SmuflLabels.flag512thDown,
            ("up", "1024th"): SmuflLabels.flag1024thUp,
            ("down", "1024th"): SmuflLabels.flag1024thDown,
        }
        key = (stem_value.value, type_duration.value)
        flag = _LOOKUP.get(key)
        if flag is None:
            raise Exception(f"Unsupported flag " + repr(key))
        return flag

    @staticmethod
    def accidental_from_accidental_value(
        accidental_value: AccidentalValue
    ) -> "SmuflLabels":
        _LOOKUP = {
            AccidentalValue.natural: SmuflLabels.accidentalNatural,
            AccidentalValue.flat: SmuflLabels.accidentalFlat,
            AccidentalValue.sharp: SmuflLabels.accidentalSharp,
            AccidentalValue.doubleSharp: SmuflLabels.accidentalDoubleSharp,
        }
        label = _LOOKUP.get(accidental_value)
        if label is None:
            raise Exception(f"Unsupported accidental " + repr(accidental_value))
        return label
