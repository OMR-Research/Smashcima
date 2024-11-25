# TODO List

These items are more high-level but there are also more low-level TODO's in the codebase itself.


## Bugs

- [ ] Column layout synthesizer's wrap-on-overflow does not work right now, because the `.detach()` methods do not function properly


## Various

- [ ] MyPy: *Skipping analyzing "smashcima": module is installed, but missing library stubs or py.typed.* - This message is displayed by MyPy to any user of smashcima. I guess I need to export the types with the package somehow.


## Scene

- [ ] SceneObject `__setattr__` should replace lists with modified lists that either prevent `.append`, `.pop`, `+=`, or modify the in/out-links accordingly
- [ ] Voices should be defined and loaded from MusicXML, they should behave similar to `BeamedGroup`s.
- [ ] The `.detach()` method should be standardized and ideally automated.
- [ ] `ScoreMeasure` should be a permanent scene object, not a throw-away view object. Just like `System` and `StaffVisual` and `StaffMeasure` are all permanent.
- [ ] Introduce methods for controlling the inlink/outlink ordering, since that in-turn controls the rasterization order.


## Loading

- [ ] Load compressed MusicXML files (MXL)


## Exporting

- [ ] Rendering layers - compositing. Ink interaction with the paper, etc.
- [ ] Add a MuNG exporter.


## Synthesis

- [ ] Rename "layout synthesis" to "notation synthesis" and formalize relevant interfaces
- [ ] Handle invisible objects (rests in first voice primarily)
- [ ] Learn position distributions (stems, notehead attachments, beam attachments), currently only hard-coded positioning is used.
- [ ] Synthesizer piano brackets
- [ ] Tall measure separators
- [ ] Synthesize layout regions properly (measures, staff measures, grandstaves, systems)
- [ ] Synthesize the vertical line at the system start
- [ ] Synthesize clef changes
- [ ] Synthesize key and time signature changes
- [ ] Synthesize slurs and ties
- [ ] Default display pitch for rests must be modified if there are multiple voices present, otherwise we render multiple rests over each other
- [ ] Add a proper stafflines synthesizer


## Assets

- [ ] Speed-up background synthesis by pre-synthesizing 512x512 base patches
- [ ] `MzkPaperPatches` should be prepackaged as a zip and mirrored to GitHub to prevent excessive usage of the IIIF API
