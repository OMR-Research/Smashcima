from ._version import __version__

# -----------------------------------------------------------------------------
# import important types that should also be accessible at the top level
from .exporting import *
from .geometry import *
from .scene import *
from .orchestration.Model import Model
from .synthesis.GlyphSynthesizer import GlyphSynthesizer
from .synthesis.LineSynthesizer import LineSynthesizer
from .synthesis.MusicNotationSynthesizer import MusicNotationSynthesizer
from .synthesis.PageSynthesizer import PageSynthesizer
from .synthesis.PaperSynthesizer import PaperSynthesizer
from .synthesis.StafflinesSynthesizer import StafflinesSynthesizer

# -----------------------------------------------------------------------------
# import sub-modules to make them accessible from this module
# TODO: assets
from smashcima import exporting
from smashcima import geometry
# smashcima.jupyter must always be imported explicitly, since it depends
# on jupyter, which is an optional dependency
from smashcima import loading
from smashcima import orchestration
from smashcima import scene
from smashcima import synthesis
from smashcima import config
