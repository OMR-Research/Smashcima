from .OmniOMRGlyphs import OmniOMRGlyphs
from ...AssetRepository import AssetRepository
from pathlib import Path
import sys


# NOTE: This code re-installs the OmniOMRGlyphs asset bundle.
# It cannot be part of that file in if __name__ == "__main__" idiom,
# because it would cause a double-import, potentially leading to issues:
# https://stackoverflow.com/questions/43393764/python-3-6-project-structure-leads-to-runtimewarning

assets = AssetRepository(Path("smashcima_assets"))

print("Re-installing OmniOMR glyphs...")
bundle = assets.resolve_bundle(OmniOMRGlyphs, force_install=True)

if len(sys.argv) >= 2 and sys.argv[1] == "--debug":
    print("Building the debug folder...")
    bundle.build_debug_folder()

print("Done.")
