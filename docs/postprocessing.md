# Postprocessing

Postprocessing is the process of turning a B/W image back into the colored one that resembles a scan or a photo of a document. It can be understood as the inverse operation to binarization in a traditional document processing pipeline.

Smashcima scene contains sprites, which although can be any RGBA image, are most likely black-on-alpha images, because the source symbol datasets (such as CVC-MUSCIMA) are binarized. Postprocessing aims to re-introduce color and texture into the synthesized image.

Postprocessing also covers the application of geometric distortion filters to the image to simulate camera-related effects.

Postprocessing is a sub-task of compositing, therefore the actions taken by the postprocessor depend on the current compositing pipeline. To learn more about compositing, see the [related documentation page](compositing.md).


## The `Postprocessor` interface

The [Compositing](compositing.md) documentation page contains the description of the `DefaultCompositor`'s compositing pipeline. It consists of the extraction of 3 layers and their subsequent merger. These three layers are given to the `Postprocessor` before they are merged and then once again after they are merged to apply various filters.

Therefore the `Postptocessor` interface defines two methods:

```py
class Postprocessor(abc.ABC):
    
    @abc.abstractmethod
    def process_extracted_layers(
        self,
        layers: LayerSet
    ) -> LayerSet:
        """Processes layers separately right after they are extracted
        from the scene."""
        raise NotImplementedError
    
    @abc.abstractmethod
    def process_final_layer(
        self,
        final_layer: ImageLayer
    ) -> ImageLayer:
        """Processes the final composed layer before it
        exits the compositor."""
        raise NotImplementedError
```

This interface is therefore compatible with any compositor, that first extracts some layers from the scene and then merges them into a final layer.

The first `process_extracted_layers` method receives a `LayerSet`. It's a collection of `ImageLayer`s identified by a string label. It can be manipulated like a `dict` value:

```py
layers: LayerSet

# get a layer
layer: ImageLayer = layers["ink"]

# test presence of a layer
assert "ink" in layers

# set a layer
layers["ink"] = my_new_ink_layer
```

If the `DefaultCompositor` is used, the `LayerSet` will contain the three default layers:

- `ink`
- `stafflines`
- `paper`

Once given layers are processed by the postprocessor, a new `LayerSet` instance should be created and returned from the method:

```py
return LayerSet({
    "ink": postprocessed_ink,
    "stafflines": postprocessed_stafflines,
    "paper": postprocessed_paper
})
```

The second `process_final_layer` method behaves exactly the same, except that it operates only on the one, final, composed layer.


## The `NullPostprocessor` implementation

By default, each `Model` registers the `NullPostprocessor` implementation for the `Postprocessor` interface. This implementation simply does not postprocessing. It returns the exact same layers it gets on input:

```py
class NullPostprocessor(Postprocessor):
    """Applies no postprocessing filters."""
    
    def process_extracted_layers(
        self,
        layers: LayerSet
    ) -> LayerSet:
        return layers
    
    def process_final_layer(
        self,
        final_layer: ImageLayer
    ) -> ImageLayer:
        return final_layer
```


## The `BaseHandwrittenPostprocessor` implementation

In pracise it's good to apply postprocessing, as it acts as image augmentation and makes the trained recognition model more robust.

A reasonable default implementation for (handwritten) music images is the `BaseHandwrittenPostprocessor`. It is built using filters from two image augmentation libraries (which come installed with Smashcima):

- [Augraphy](https://github.com/sparkfish/augraphy)
- [Albumentations](https://albumentations.ai/)

Most of the used filters come from Augraphy, as it's better tuned to augmenting scans of physical documents. Albumentations, on the other hand, provides more filters, but they are more low-level and many are geared towards general-purpose augmentation of photos or medical scan images.

The postprocessor defines 7 filter stacks that apply randomized filters:

- `f_stafflines` Stafflines (dilation, texture, color)
- `f_inkstyle` Scribbles (scribbles and text added on top of the document)
- `f_bleed_through` Bleed through (back-side music notation bleeding through)
- `f_ink_color` Ink color
- `f_scribbles` Ink texture
- `f_folding` Folding (crumpled paper effect)
- `f_camera` Camera effects (rotation, padding, shadow, blur)

These stacks can be toggled in the [gradio demo](https://huggingface.co/spaces/Jirka-Mayer/Smashcima) to see their effects.

For details, please refer to the source code.


## Citing Augraphy and Albumentations

If you use the `BaseHandwrittenPostprocessor` or you build your own using these libraries, don't forget to cite their respective papers:

- [Augraphy citation](https://github.com/sparkfish/augraphy?tab=readme-ov-file#citations)
- [Albumentations citation](https://github.com/albumentations-team/albumentations?tab=readme-ov-file#citing)
