# Scene

> **WARNING:** This documentation page is outdated. Ignore it. Will be rewritten.

The scene is the data model for the Smashcima synthesizer. It describes the music page constructed during synthesis.

The designing principles are:

- It is data, not logic. It should represent information and allow its querying. It should not do any mutation logic on itself.
- It should not explicitly define concepts that are not universal. Therefore ideally, it is only a collection of cross-referenced python class instances. No explicit hierarchy, no explicit graph edges, just pure python.
- It should be extensible, should someone need to add their own additional information.
- Because the goal it to eventually render the scene to some output image or annotation, it should not contain information that will not be useful for that, on the other hand it should contain precisely that information that could be useful for rendering. (This is to have some guiding principle for what should be included in the data model.) (We could also view the scene as all the concievable annotation formats merged into one datastructure.)


## What data should be included

The output annotations of the synthesizer could be classified into rough categories:

- visual information
    - glyphs, segmentation masks, glyph ligatures, origin points, bounding boxes, lines, splines, offset vectors, bounding hulls, bounding rectangles, coordinate systems
    - foreground / background
- low-level semantic information
    - glyph relationships (notehead-stem, slur-notehead)
    - noteheads and rests (vertical staff position, chords, beamed groups)
    - measures, staves, systems
- mid-level semantic information
    - notes (duration, onset, pitch)
    - time signature, key signature, clef
    - note precedence/simultaneity graph
    - voices
- high-level semantic information
    - kern, MusicXML, MEI, music21, MIDI

The data model should contain enough information to extract all of this data out of it. When I say it should contain the combination of all reasonable annotation formats, I don't mean it should contain both MusicXML and MEI - I mean it should contain some representation, from which either MusicXML or MEI can be deterministically extracted.

Also note that there is a lot of information in the semantic domain. For this reason the data-model is not primarily visual. It is primarily a python class instance graph, where the visual domain has a well defined place, but so does the musical one. You should consider the data model to be a graph (and a highly connected and redundant one).

Music is inherently 2D, which means that trying to impose a tree-like hierarchy onto it necessarily results in awkward edge cases. It is not obvious whether a note belongs to a voice, a chord, a beamed group, a measure, or a staff. It sort of belongs all of them or only some of them in some cases. And all of these frameworks of looking at music are valid and should be supported. That's why Smashcima data model is a graph, not a tree.

This line of thinking has already been employed by [MuNG - Music Notation Graph](https://github.com/OMR-Research/mung). It also makes no assumptions about how the graphical glyphs are grouped together - there are only the atomic glyphs and their relation graph. This is because an eighth note can be a notehead+stem+flag, but it can also be a notehead+stem+beam, where the beam is shared among many notes. Sometimes even the notehead may be shared between two voices. This format, however, only focuses on the visual domain, leaving out the semantics to the user. This means that extracting semantics is difficult and sometimes ambiguous (a voice is something that is not explicitly written in the notation, yet widely used and also built into many high-level formats, such as MusicXML - we need it to be present in the data model).


## The note

At the core of the data model is not a bitmap - that would make it too visual. The core is not even a score - that would make it too semantic. At the core is a note, because that is the elementary unit of music that we can agree upon. A note is not something visual, it is something semantic, but on a very low-level.

A note links to its glyphs, which connects it with the visual domain. And it links to the preceeding and following notes, which puts it into context. It also links to its measure, staff, system, and part, which puts it into the high-level context.

```python
note: Note = ...
notehead: Notehead = ...

queried_note = notehead.note
queried_notehead = Notehead.one_of(note)
queried_notehead = notehead_of(note)

Measure.notes_of(measure)
Staff.notes_of(staff)

class Note:
    staff_onset: Fraction
    base_duration: Fraction
    base_pitch: Fraction

class Notehead:
    glyph: Sprite
    pass

# should I add color to noteheads I extend the graph instead of inheriting:
class NoteheadColor:
    color: str
    notehead: Notehead
    def one_of(notehead: Notehead) -> NoteheadColor: pass
    # all_of(...)
```

The data model is python class instances acting as nodes, linked together by oriented graph edges as python references. These edges, when queried in the forward direction is just a simple python property dereference, but the query in the other direction is via a lookup function. This lookup function queries the entire scene to get the inverse edge. The lookup function always lives on the target of the edge. ~~There are no cycles in the graph, it's a DAG.~~ (well let's see, maybe the precedence graph combined with other edges might form cycles) The direction of edges is from less-fundamental notation elements (e.g. lyrics) to more fundamental (e.g. notes). Notes are the most fundamental elements (because music is primarily in the sound domain), the semantic high-level structure and the visual notation elements both point towards the notes. (WEELL, maybe not? Maybe some relationships are more equal than subordinating, such as note-notehead. I wouldn't say that it's obvious.)

The relationship has a name comming from the name of the field on the parent class instance. If there are multiple and you are doing the inverse lookup, you should be
able to constrain the lookup by the name of the field (in a way that allows python refactoring, say `lambda note: note.notehead`).
