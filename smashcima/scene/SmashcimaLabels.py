from enum import Enum


class SmashcimaLabels(str, Enum):
    """Glyph and region classification labels that are not in SMuFL"""
    
    # Line Glyphs
    #
    # Line glyphs are not really represented in SMuFL,
    # so instead they must be added to the set of classes here.
    ledgerLine = "smashcima::ledgerLine"
    beam = "smashcima::beam"
    beamHook = "smashcima::beamHook"
    slur = "smashcima::slur"

    # Isolated Flags
    #
    # IMPORTANT: For flags as such use the SMuFL class.
    # These are reserved for cases when the flag is split up into individual
    # isolated flag stokes. For example MUSCIMA++ does this.
    isolatedFlag8thUp = "smashcima::flag8thUp"
    isolatedFlag8thDown = "smashcima::flag8thDown"
    isolatedFlag16thUp = "smashcima::flag16thUp"
    isolatedFlag16thDown = "smashcima::flag16thDown"
    isolatedFlag32ndUp = "smashcima::flag32ndUp"
    isolatedFlag32ndDown = "smashcima::flag32ndDown"
    isolatedFlag64thUp = "smashcima::flag64thUp"
    isolatedFlag64thDown = "smashcima::flag64thDown"
    isolatedFlag128thUp = "smashcima::flag128thUp"
    isolatedFlag128thDown = "smashcima::flag128thDown"
    isolatedFlag256thUp = "smashcima::flag256thUp"
    isolatedFlag256thDown = "smashcima::flag256thDown"
    isolatedFlag512thUp = "smashcima::flag512thUp"
    isolatedFlag512thDown = "smashcima::flag512thDown"
    isolatedFlag1024thUp = "smashcima::flag1024thUp"
    isolatedFlag1024thDown = "smashcima::flag1024thDown"
