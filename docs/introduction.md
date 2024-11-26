# Introduction

Smashcima is a python package aimed at synthesizing training data for Optical Music Recognition (OMR). Therefore the ultimate goal is to create synthetic images of music notation, together with the corresponding annotations (textual, visual, or both). The internal structure of Smashcima follows from this goal and is described in this file.


## Synthetic data

Deep learning methods currently yield the best results for tackling OMR and these need training data in order to work. While some training data may be produced manually, this process is costly and synthesis could be used to mix, shuffle, and reuse this small amount of manually annotated data to produce much larger amount of synthetic data. Therefore the goal of data synthesis here is not necessary to create new data out of thin air, but rather to augment existing data to prevent overfitting during model training, making the resulting recognition models more robust.

The training data for supervised methods (which are among the most prominent) comes in pairs of input images and corresponding output annotations. These input images are usually scans or photos of physical music documents, so are available in bitmap formats (JPG, PNG). These images can be individual musical symbols, staves, or whole pages. The annotations are, however, much more diverse and often task-specific. They could be image-classification classes, image-detection bounding boxes, image-segmentation masks, music notation graphs, sequential textual representations (aligned with the image or not), or complex notation formats, such as MusicXML, MEI, Humdrum \*\*kern, Lilypond, ABC, and others.

The purpose of Smashcima is to synthesize these image-annotation aggregates.


## Data model (the scene)

In order for the synthesizer to get a handle on the synthetic data during synthesis, it needs some internal representation of the synthesized music page - a data model. This data model is called the **scene** and it exists as a cluster of python class instances that inherit from the abstract class `SceneObject` and form an interlinked graph.

A scene should contain enough information to produce most desired annotation formats together with the image bitmap.

Scene objects live in the `smashcima.scene` module.


## Exporting (and rendering)

A scene is not the image, nor the annotation. It is more. It contains all the necessary information to produce both. The process of extracting a specific annotation format (say MusicXML) from the scene is called **exporting**.

Similarly, the image bitmap itself can be exported from the scene, but since now we deal with visual data, we call this process **rendering** (terminology borrowed from computer graphics). Another words, rendering is a subset of exporting.

This distinction between the scene and the exported format lets us add exporters for additional output formats on-demand.

Exporters and renderers live in the `smashcima.exporting` module.


## Synthesis

The core of the actual synthesis lies in the process of constructing the scene. If the scene is the data structure, a synthesizer is the algorithm. A synthesizer is some python code, that given some input arguments constructs a piece of the final scene.

> **Note:** APIs of synthesizers vary: It can either create a part of a scene and return it, or it can add something into an existing scene. It depends on the task.

Synthesizers should come in lots of sizes, from small ones synthesizing individual symbols, to large ones putting together the whole page. Smashcima should act as a collection of synthesizers for you to choose and match, given the OMR task you want to solve.

Synthesizers live in the `smashcima.synthesis` module.


## Models

While synthesizers do the heavy lifting, their configuration is complex and they often rely on many other synthesizers (e.g. music notation synthesizer relies on a glyph synthesizer). Asking every single user to build their own synthesis pipeline from scratch would be impractical.

Models act as a ready-to-use wrappers around various synthesis pipelines, being reasonably pre-configured out of the box. While a synthesizer is meant to be as general as possible, a model is built to be as specific as possible. The idea being that you build your own model for your specific task domain - either by bending existing models, or by putting together a custom synthesizer pipeline from scratch.

Models models are meant to orchestrate synthesizers, they live in the `smashcima.orchestration` module.


## Assets

The best synthetic data is partially-real data. Therefore almost all synthesizers need some dataset, some trained generative model, or some set of tuned parameters to work. These real-world input resources are called *assets*. The Smashcima system has an assets layer responsible for their definition, download, preparation and usage.

Assets live in the `smashcima.assets` module.


## Other submodules

Other Smashcima submodules that have not been covered above:

- `smashcima.geometry` Contains types for working with 2D geometry (vectors, points, transforms, polygons).
- `smashcima.loading` Classes that construct the semantic part of a scene by loading it from a music notation format (e.g. MusicXML). They are not synthesizers, because they don't create new data - they just load if from some other format.
- `smashcima.jupyter` Helper methods for working with Smashcima from Jupyter notebooks (mostly scene visualization code). The `smashcima[jupyter]` extra dependencies must be installed in order to use this module.
