# Synthesizer interfaces

Synthesizer is any service that creates or manipulates a scene to produce synthetic data. Its API therefore completely depends on the synthetic data it produces.

Whereas a model comes pre-configured and ready to use to synthesize final data, a synthesizer should have just one narrow responsibility and allow for maximal configuration. The less work it does, the more it can be used as a LEGO piece in a larger synthesis pipeline.

To give some structure to the resulting synthesis pipelines and to allow for intechangebility of synthesizers, Smashcima defines a set of synthesizer interfaces, together with their implementations. This documentation page goes over these interfaces.


## Smashcima synthesizers

This is an overview list of synthesizer interfaces in the order from the most abstract to the most concrete:

- [`ColumnLayoutSynthesizer`](06_column-layout-synthesizer.md) places musical symbols onto empty stafflines
- `PageSynthesizer` produces a sheet of paper with empty stafflines with a given layout
- `StafflinesSynthesizer` produces empty stafflines
- `PaperSynthesizer` produces images of sheets of paper
- `LineSynthesizer` produces line-like music symbols (beams, stems, braces)
- [`GlyphSynthesizer`](07_glyph-synthesizer.md) produces musical symbols (notes, rests, accidentals)


## Using synthesizers

If you look inside `BaseHandwrittenModel.call()` method, you can see that the model uses two synthesizers:

- `PageSynthesizer`
- `MusicNotationSynthesizer`

It loads a music score and then until there are measures remaining, it creates a new page and then fills it with measures from the score.

Looking at it from this top level makes the `BaseHandwrittenModel` a pretty thin and simple class.


## Extensibility

If you're building a synthesizer for a domain not covered by these interfaces, feel free do define your own interfaces and then implement them. Having interfaces explicitly named, documented, and assigned to implementations in models lets other developers to then create alternative implementations to them. Embrace the LEGO piece modularity of Smashcima.
