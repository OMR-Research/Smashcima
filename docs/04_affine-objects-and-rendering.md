# Affine spaces and rendering

In the previous documentation section we talked about scene objects and how they can represents arbitrary graph-like data. We used the concepts of a `Note` and a `Notehead` to represent semantic and visual objects. In this documentation section we will describe how the visual portion of a scene is described and rendered (delving into how a `Notehead` visual object might be actually implemented in Smashcima).


## Affine space

Most 2D computer graphics software is built on the concept of a 2D affine space. This mathematical construct is used in both vector and raster computer graphics software, including [Inkscape](https://inkscape.org/), [Krita](https://krita.org/), [Photoshop](https://www.adobe.com/products/photoshop.html), [Illustrator](https://www.adobe.com/products/illustrator.html), [Figma](https://www.figma.com/) and even the [SVG](https://developer.mozilla.org/en-US/docs/Web/SVG/Attribute/transform) vector graphics data format.

In Smashcima I imagine an affine space as a 2D coordinate system, with an origin somewhere in space and coordinates defined by two basis vectors X and Y sitting at the origin. The two basis vectors can have any length and any direction, although in majority of cases they have unit length and are orthogonal.

The affine space lets us put 2D real-valued coordinates on the underlying geometric space.

All visual objects that exist in Smashcima must be situated in some affine space (otherwise the concept of their position (and size and orientation) cannot be defined). These objects include:

- `Sprite` a bitmap image
- `ViewBox` a rectangular viewport into the scene
- `ScenePoint` a 2D point
- `Region` a polygonal area outline in the scene

For example, when you have a `Point` it consists of two coordinates: X and Y. But these coordinates have no meaning on their own. The point has to be placed into an `AffineSpace`, that defines what these numbers mean in spatial terms. Therefore a `ScenePoint` is nothing more than a `Point` combined with an `AffineSpace` reference.


### Space hierarchy

Each affine space can be placed into another existing affine space as a child. Its position within the parent space is defined by an affine `Transform`. An affine transform is just a linear transform (rotation, scale, skew, mirror) that also allows for translational movement (translation).

Another words, in the parent space, the child space's origin can be placed anywhere and the child space can be deformed and rotated in any way that keeps its coordinate grid as straight lines that are evenly spaced.

This nesting of affine spaces lets us take a subset of the scene's visual objects (attached to the child space) and place them anywhere within the parent space as one piece. This means that, for example, a glyph synthesizer can operate in the glyph's local affine space, placing all the glyph strokes properly and then a music notation synthesizer can position the glyph as a whole on a staff.

An affine space that has no parent (is set to `None`) is called the root affine space, and there should only be one such space in a well-defined scene. Existence of a shared root space ensures that for any two scene objects in any two spaces, there exists a nearest ancestor space containing both of them, which allows us to translate between these two object's coordinate spaces.


### Constructing affine spaces

You can create a root affine space like this:

```py
import smashcima as sc

root_space = sc.AffineSpace()
```

Then you can create a child space, with its origin placed at `(10, 20)` like this:

```py
child_space = sc.AffineSpace(
    parent_space=root_space,
    transform=sc.Transform.translate(sc.Vector2(10, 20))
)
```

If no transform is proivded, then `Transform.identity()` is used automatically.

Alternatively, if a child space was constructed before and it has no parent (or we want to change its parent), we can place it under the root space like this:

```py
other_child_space.parent_space = root_space

# optionally, you can modify the transform
other_child_space.transform = sc.Transform.identity()
```


### Understanding transforms

The affine space's transform is fomally defined as a `2x3` matrix that maps from the child's coordinate system into the parent's coordinate system.

Another words, with the parent-child setup from above, with the root space and a child space placed at `(10, 20)`, if we take a point at `(-1, 0)` in the child space, and apply the child's transform to it, we will get `(9, 20)`, which is the point's coordinates in the root space:

```py
point_in_child_coords = sc.Point(-1, 0)
point_in_root_coords = child_space.transform.apply_to(
    point_in_child_coords
)
print(point_in_root_coords) # prints (9, 20)
```

You can chain multiple transforms by using the `.then` method. For example, we could have the child space use the same origin at `(10, 20)` but be rotated 180 degrees. That would put our sample point at `(11, 20)` in the root coordinates:

```py
child_space.transform = sc.Transform.rotateDegCC(180) \
    .then(sc.Transform.translate(sc.Vector2(10, 20)))

# now probing the same point, in a 180deg rotated child space:
point_in_child_coords = sc.Point(-1, 0)
point_in_root_coords = child_space.transform.apply_to(
    point_in_child_coords
)
print(point_in_root_coords) # prints (11, 20)
```

The order of `.then` matters. We are mapping from the child space into the parent space, so we need to first perform the rotation (in the perspective of the child space), and only after that do the translation to the correct position in the parent space.

> **Remember:** Transforms always map from child space coordinates to the parent space coordinates.


### Units are millimeters

So far affine spaces have been defined purely mathematically without any units. While Smashcima does not track any units and you can treat the numeric values however you like, the assumption is that one unit is one millimeter.

This is because we are mostly dealing with scales in the range of a piece of paper, where a millimeter is an appropriate unit (used by many 2D computer graphics software tools).

Smashcima uses physical spatial units, as opposed to pixels, because it aims to harmonize data from various scanned source datasets, which may have been rasterized at various DPIs. Sticking to millimiters is a way to reconcile these differences.

To convert between millimeters and pixels with a given DPI, you can use these utility functions:

```py
print(sc.mm_to_px(1, dpi=300)) # 12.295081967213116
print(sc.px_to_mm(1, dpi=300)) # 0.08133333333333333

# one millimeter is about 12.3 pixels under 300 DPI
```


## Sprites

Now that we have the space itself covered with coordinate systems, we need to place some objects into it. Because most handwritten musical symbol datasets use raster images, I built the Smashcima visual rendering system on raster images as well.

A `Sprite` is a raster image, placed somewhere in an `AffineSpace`, with well-defined scale.

You can create a sprite like this:

```py
import numpy as np

sprite = sc.Sprite(
    space=root_space,
    bitmap=np.array([...]),
    bitmap_origin=sc.Point(0.5, 0.5),
    dpi=300,
    transform=sc.Transform.identity()
)
```

The `space` is the affine space that the sprite is placed into (the parent space).

The `bitmap` is an OpenCV BGRA image with the `uint8` depth (a 3D numpy array).

The `bitmap_origin` is a 2D point in the `0.0 - 1.0` range in each coordinate, specifying where the bitmap should be overlayed with the parent space's origin. Values of `0.5` mean the center of the bitmap. So our bitmap will be centered on the space origin.

The `dpi` controls the physical size of the bitmap in the parent space. At what DPI has the bitmap been scanned.

The `transform` lets you apply an additional transform to the bitmap to position it arbitrarily in the parent space. For example, you can use a rotation transform to rotate the image.

So far I described the `bitmap_origin` and `dpi` as controlling the placement within the parent space. This is not strictly correct. There is a so-called origin space, and these arguments control the placement of the bitmap within the origin space. The `transform` property then controls the placement of the origin space within the parent space. The nesting is as follows:

```
[parent space]
      A
      |    <- controlled by `transform`
      |
[origin space]
      A
      |    <- controlled by `bitmap_origin` and `dpi`
      |
[pixel space]
```

Pixel space is the affine space, where `(0, 0)` is the top-left corner of the bitmap and `(w, h)` is the bottom-right corner of the bitmap, where `w` and `h` are width and height in the number of pixels.

You can get the lower transform by calling `sprite.get_pixels_to_origin_space_transform()` and you can get the upper transform simply by accessing `sprite.transform`. You can also get the joint transform by calling `sprite.get_pixels_to_parent_space_transform()`.

There is also a number of properties you can access about a sprite:

- `.pixel_width` and `.pixel_height` are size in the number of pixels
- `.physical_width` and `.physical_height` are size in millimeters
- `.pixels_bbox` is a helper property that returns a `Rectangle` in pixel space positioned at `(0, 0)` and with size `(pixel_width, pixel_height)`.


## View boxes

Now that we have the coordinate spaces and bitmap images placed in them, we need a rectangular window that will be used as the camera that looks into the scene. This camera-like object is called the `ViewBox`. It's simply a `Rectangle` placed in an `AffineSpace`:

```py
view_box = sc.ViewBox(
    space=root_space,
    rectangle=sc.Rectangle(0, 0, 210, 297) # A4 paper in millimeters
)
```


## Bitmap renderer

With the camera defined, we can now use a `BitmapRenderer` to traverse recursively all the affine spaces, find all sprites, transform them into a blank canvas and layer them on top of each other:

```py
renderer = sc.BitmapRenderer(
    dpi=300, # rasterize the scene at this DPI
    background_color=(0, 0, 0, 0) # BGRA
)
img = renderer.render(view_box)

# img is a np.ndarray OpenCV BGRA uint8 image
```

The renderer is given only the `view_box` but since it links to its affine spaces and affine spaces link to their parents, we can find the root space and iterate from there.

The whole visual scene hangs on the root space and is not garbage collected, because of the double-linking tracked by `SceneObject`s discussed in the previous documetation section.

> **TODO:** View boxes currently assume they are placed in the root affine space. It should be supported that they can be placed in any sub-space. But they must still render the whole scene from its root space. (note it's not view boxes that assume that, it's the BitmapRenderer that assumes that)
