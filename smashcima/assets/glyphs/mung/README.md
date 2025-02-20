This module contains code that extracts glyphs from MuNG-based datasets into a symbol repository, which can then be used for glyph synthesis by sampling from the repository.

The MUSCIMA++ dataset and the OmniOMR dataset are two examples that rely on this common code.

This module has this structure:

- `repository` Contains code related to the symbol repository - the data model that contains the collection of extracted glyphs. The root object here is the `MungSymbolRepository`, which represents the whole symbol repository.
- `extraction` Contains code that performs the extraction of Smashcima glyphs from the MuNG format. The root object here is the `MungSymbolExtractor` class.
- `utils` Contains utility functions that patch and repair the MuNG graph for datasets which do not follow the standard as designed.
