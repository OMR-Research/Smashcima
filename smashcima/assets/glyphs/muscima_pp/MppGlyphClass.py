from enum import Enum


# TODO: this is obsolete,
# use the SMuFL and Smashcima glyph classes instead. Those can be mapped
# to the MUSCIMA++ classes during MuNG rendering.
# Also, this means we can remove the class mapping in MPP synthesizers.
class MppGlyphClass(str, Enum):
    """
    Enum that represents glyphs from the MUSCIMA++ dataset.
    """
    
    # Barlines
    thinBarline = "muscima_pp::thin_barline"
    
    # Clefs
    gClef = "muscima_pp::g-clef"
    fClef = "muscima_pp::f-clef"
    cClef = "muscima_pp::c-clef"
    
    # Noteheads
    noteheadFull = "muscima_pp::notehead-full"
    noteheadEmpty = "muscima_pp::notehead-empty"

    # Ledger Lines
    ledgerLine = "muscima_pp::ledger_line"

    # Stems
    stem = "muscima_pp::stem"

    # Rests
    wholeRest = "muscima_pp::whole_rest"
    halfRest = "muscima_pp::half_rest"
    quarterRest = "muscima_pp::quarter_rest"
    eighthRest = "muscima_pp::8th_rest"
    sixteenthRest = "muscima_pp::16th_rest"

    # Beams
    beam = "muscima_pp::beam"
    beamHook = "muscima_pp::beam_hook"
