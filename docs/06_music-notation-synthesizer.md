# `MusicNotationSynthesizer` interface

> **TODO:** The interface is not yet extracted from the class `ColumnLayoutSynthesizer`. The module `layout` should be renamed to `notation` and the class should be renamed to `ColumnMusicNotationSynthesizer` and the interface should be extracted, documented, and used in the `BaseHandwrittenModel`.

This interface represents the (human) writer sitting at a blank piece of paper with stafflines, transcribing a piece of music onto that paper.

To create images of music symbols (glyphs), it uses as a dependency a `GlyphSynthesizer` (and a `LineSynthesizer`). It's responsibility to create these based on the input musical score and position them on the piece of paper according to the rules of common western music notation.


## Public API

It defines two methods: `fill_page` and `synthesize_system`.

They both fill the page with music you give to them, but at two leves of control - at the page level, or at the system level.

The low-level system method has this signature:

```py
def synthesize_system(
    page_space: AffineSpace,
    staves: List[StaffVisual],
    score: Score,
    start_on_measure: int
) -> System:
```

You give it a list of empty staves (stafflines), whose count must match the number of staves in the music score and also the affine space that contains these empty staves. Then you give it the music score and the measure index from which it should start transcribing the music. You get back a system of music notation (system = one line with all instruments).

The high-level method has this signature:

```py
def fill_page(
    page: Page,
    score: Score,
    start_on_measure: int
) -> List[System]:
```

You give it a page with empty stafflines and a music score plus a measure index from which to start transcribing and it fills the page up with music notation.

The interface also defines these public `bool` flags that you can modify after the synthesizer is instantiated to control the music notation flow:

- `.stretch_out_columns` Analogous to text alignment, when true it behaves like "text justify" and when false, it behaves like "text align left".
- `.respect_line_and_page_breaks` When true, systems are terminated at line and page breaks in the music score. When false, these breaks are ignored.
- `.disable_wrapping` When true, music does not wrap to the next system when it starts overflowing. When false, it does. 


## Implementations

- `ColumnLayoutSynthesizer`
