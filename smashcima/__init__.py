__version__ = "0.2.0dev"


# -----------------------------------------------------------------------------
# import important types that should also be accessible at the top level
from .geometry import *
from .scene import *
from .orchestration.Model import Model
from .synthesis.GlyphSynthesizer import GlyphSynthesizer
from .synthesis.LineSynthesizer import LineSynthesizer

# -----------------------------------------------------------------------------
# import sub-modules to make them accessible from this module
# TODO: assets
from smashcima import geometry
# smashcima.jupyter must always be imported explicitly, since it depends
# on jupyter, which is an optional dependency
from smashcima import loading
from smashcima import orchestration
from smashcima import rendering
from smashcima import scene
from smashcima import synthesis
