# Rendering via `BitmapRenderer`

In the previous documentation page on [Compositing](compositing.md) we described the process of turning a scene into a final `ImageLayer`. Therefore the compositor is actually responsible for the flattening of all of the sprites. After the compositor finishes, there isn't much work left for the `BitmapRenderer` as the final "exporter". It basically just adds a solid background color under the final `ImageLayer` (which by default is transparent):

```py
final_layer: ImageLayer # comes from the compositor

renderer = sc.BitmapRenderer(
    background_color = (255, 0, 0, 255) # solid blue (BGRA)
)

bitmap = renderer.render(final_layer)
```

However, you may want to produce visualizations of scenes (or scene parts) for debugging purposes and for that you don't want to invoke this complex machinery. So the `BitmapRenderer` class provides a static method that uses the `DefaultCompositor` and `NullPostprocessor` to create an image of a scene through a `ViewBox`:

```py
bitmap = BitmapRenderer.default_viewbox_render(
    view_box=view_box,
    dpi=300
)
```

Under the hood, this really just creates all the services and strings them together:

```py
# prepare services
postprocessor = sc.NullPostprocessor()
compositor = sc.DefaultCompositor(postprocessor)
renderer = sc.BitmapRenderer()

# run them
final_layer = compositor.run(view_box, dpi=300)
bitmap = renderer.render(final_layer)
```

In practise, all of this is hidden away from you inside the synthesized scene:

```py
model = sc.BaseHandwrittenModel()

scene = model("input.musicxml")

bitmap = scene.render(scene.pages[0])
```

In this case, the `Compositor` and `Postprocessor` are both taken from the `model`'s service container, and thus appropriate postprocessing filters are applied.
