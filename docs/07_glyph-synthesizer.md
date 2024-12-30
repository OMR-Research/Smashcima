# `GlyphSynthesizer` interface

Glyph synthesizer represents a service intended to produce glyphs of music notation. These are, for example, noteheads, flags, accidentals, rests, etc.


## `Glyph` scene object

Glyph is a visual scene object that links together other spatial scene objects that together contain information about a music notation symbol.

There are three types of information that a glyph holds:

- appearance (as a list of `Sprite`s)
- classification label (as a `str`)
- semantic segmentation mask (as a `Region`)

It's a set of sprites extended with the information necessary to perform classification, object detection, and semantic segmentation on the symbol.

All of these objects are spatial in its nature, so the glyph instance also carries its owin `AffineSpace` instance, inside of which all of these objects live and which should be used to attach the glyph into the broader scene.

A glyph instance can be created like this:

```py
import smashcima as sc

# new space for the glyph to live in
space = sc.AffineSpace()

# classification label for the glyph
label: str = sc.SmuflLabels.noteheadBlack.value

# dummy sprite to represent the glyph, placed in the space
sprite = Sprite.rectangle(
    space=space,
    rectangle=sc.Rectangle(-1, -1, 2, 2)
)

# create the glyph as a collection of these objects
glyph = sc.Glyph(
    space=space,
    region=sc.Glyph.build_region_from_sprites_alpha_channel(
        label=label,
        sprites=[sprite]
    ),
    sprites=[sprite]
)
```


### Placing a glyph into a scene

The code above creates a glyph that stands outside the greater scene. Its affine space is a root space (has no parent). To place it into another space, just attach the affine space like this:

```py
# some affine space of the whole scene
# (can be a root, can be only a staff or the paper space)
root_space = sc.AffineSpace()

# attach the glyph into the scene space at (10, 20)
glyph.space.parent_space = root_space
glyph.space.transform = sc.Transform.translate(sc.Vector2(10, 20))
```


### Glyph origin point

You can see that placing the glyph into a scene is performed by placing its affine space. More specifically, by placing it's affine space's origin point.

For this reason it's important to be consistent in where exactly this origin point is located for each glyph type (e.g. noteheads have it as their center, whole rests have it as the position of the staffline).

The list of glyph labels and their proper origin points is documented in the [Glyphs](glyphs.md) documentation page.


### Semantics of visual objects

The `Glyph` scene object only represents a visual glyph in the scene, but it carries no semantic information. We would like to have a `Notehead` that will have a link to its semantic `Note` and contain additional links to, for example, the `StaffVisual`.

You should NOT do this via inheritance! The documentation section on scene objects details the complications you'd run into. Instead, you create a `Notehead` scene object and add a reference to the glyph and other scene objects:

```py
from dataclasses import dataclass

@dataclass
class Notehead(sc.SceneObject):
    glyph: Glyph
    notes: List[Note]
    staff: StaffVisual

    @classmethod
    def of_glyph(cls, glyph: Glyph):
        return cls.of(glyph, lambda n: n.glyph)
```

Using the reverse reference queries, you can get the notehead for a glyph (if you know that the glyph is a notehead) and you don't need to inherit or extend the `Glyph` class in any way:

```py
notehead = Notehead.of_glyph(glyph)
```


## Public API

Now that you have an indea of what a `Glyph` is, we can look at how to use a `GlyphSynthesizer` service.

To just simply create a new glyph scene object, you can call the `create_glyph` method:

```py
def create_glyph(label: str) -> Glyph:
```

You just give it the desired glyph class and it will construct a new glyph instance for you in the fashion very similar to the code we've seen at the beginning of this documentation page.

The returned glyph will have its own `AffineSpace`, which will have no parent. You can now do with the `Glyph` whatever you desire.

But since you often want to immediately place the glyph into some parent space, you can directly ask the synthesizer to do that for you using `synthesize_glyph`:

```py
def synthesize_glyph(
    label: str,
    parent_space: AffineSpace,
    transform: Transform
) -> Glyph:
```

You specify the parent space and the transform that specifies the glyph's placement within the parent space. It also performs some additional argument checks that the previous method might not do.

Lastly, since the glyph is usually only translated, but only rarely rotated or scaled, there's the method `synthesize_glyph_at` which takes a `Point` instead of a full `Transform`:

```py
def synthesize_glyph_at(
    label: str,
    parent_space: AffineSpace,
    point: Point
) -> Glyph:
```


### Checking supported glyph labels

Since not all glyph synthesizers support all glyph classification labels, there's a method that you can use to check that the synthesizer you are about to use supports all the labels you will be asking of it:

```py
def supports_label(label: str) -> bool:
```

If you're building a synthesizer that in-turn uses a `GlyphSynthesizer` as a dependency, make sure to call this method before synthesizing. This helps detect compatibility issues before they have a chance to manifest in production after 2 hours of runtime once the input data suddently contains a triple-flat accidental, but the glyph synthesizer you've used so far does not support them.


## Implementing a glyph synthesizer

To implement a custom glyph synthesizer, simply inherit from the `GlyphSynthesizer` abstract base class and override the `supports_label` and `create_glyph` methods. The other two methods are already implemented for you and they internally use the `create_glyph` method you provide:

```py
class MyFancyGlyphSynthesizer(sc.GlyphSynthesizer):
    def supports_label(self, label: str) -> bool:
        return True # yes, we support everything!
    
    def create_glyph(self, label: str) -> Glyph:
        # create a glyph from scratch
        # (or load it from some pickle and deep copy,
        # that's also an option)
        glyph = Glyph(...)
        
        return glyph
```


## Implementations

- `smashcima.synthesis.glyph.MuscimaPPGlyphSynthesizer` Synthesizes glyphs by sampling from the MUSCIMA++ dataset.
