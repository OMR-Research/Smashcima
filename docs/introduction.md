# Introduction

> **WARNING:** This documentation page is outdated. Ignore it. Will be rewritten.

Mashcima 2 is a python package aimed at synthesizing training data for Optical Musci Recognition (OMR). Therefore the ultimate goal is to create synthetic images of music notation, together with the corresponding annotations (textual, visual, or both). The structure of the system follows from this goal and is described in this file.


## Synthetic data

Deep learning methods currently yield the best results for tackling OMR and these need training data in order to work. While some training data may be produced manually, this process is costly and synthesis could be used to mix, shuffle, and reuse this small amount of manual data to produce much larger amount of synthetic data. Therefore the goal of data synthesis here is not necessary to create new data out of thin air, but rather to augment existing data to prevent overfitting in model training, making the resulting models more robust.

The training data for supervised methods (which are among the most prominent) comes in pairs of input images and corresponding output annotations. These input images are usually scans or photos of physical music documents, so are available in bitmap formats (JPG, PNG). These images can be individual musical symbols, staves, or whole pages. The annotations are, however, much more diverse and often task-specific. They could be image-classification classes, image-detection bounding boxes, image-segmentation masks, music notation graphs, sequential textual representations (aligned with the image or not), or complex notation formats, such as MusicXML, MEI, Humdrum \*\*kern, and others.

The purpose of Smashcima is to synthesize these image-annotation aggregates.


## Data model (the Scene)

In order for the synthesizer to get a handle on the synthetic data during synthesis, it needs some internal representation of the synthesized music page - a data model. This data model is called the **scene** and it exists as a cluster of python class instances that extend abstract scene elements (`SceneObject`, `Group`, `Sprite`) and form a hierarchical tree.

A scene should contain enough information to produce most desired annotation formats and the image.


## Rendering

A scene is not the image, nor the annotation. It is more. It contains all the necessary information to produce both. When we want to get hold of the actual image, we need to select and compose the image information from the scene in a process called rendering (terminology borrowed from compuer graphics). The part of the system responsible for this extraction is called the renderer.

Similarly, if we want to extract the annotation (say the MusicXML of the page), we would use another renderer that converts the scene into a MusicXML file. This distinction lets us easily add more renderers for additional output formats.


## Synthesis

The core of the actual synthesis lies in the process of constructing the scene. If the scene is the data structure, a synthesizer is the algorithm. A synthesizer is some python code, that receives a scene (empty or not) and populates it with more content.

Synthesizers should come in lots of sizes, from small ones synthesizing individual symbols, to large ones putting together the whole page. Smashcima should act as a collection of synthesizers for you to choose and match, given the OMR task you want to solve.


## Assets

The best synthetic data is partially-real data. Therefore almost all synthesizers need some dataset, some trained generative model, or some set of tuned parameters to work. These real-world input resources are called *assets*. The Smashcima system has an assets layer responsible for their definition, download, preparation and usage.


## Pipeline synthesis

> **Note:** This area of the system is not fully thought through and settled.

In practise, we don't need to synthesize a single image - we want to train a deep learning model, so we need a whole dataset. And ideally, this dataset is not static - we can make it different for each epoch. Therefore we need orchestration logic to perform:

- Estimate the size of an epoch given the input real-world assets (because at some point they start repeating).
- Synthesize pseudo-randomly (being random, but deterministic, to be repeatable).
- Pipelined synthesis (synthesize on CPU, train on GPU, or another machine).


## Utilities

There is also utility code in the Smashcima system used for:

- 2D geometry
- Music representation format conversions


## The main contribution

While Smashcima is branded as a synthesizer, really, it's a framework of synthesizers and their supporting code. As such, it more resembles a framework, than a single tool. The inspiration here is the [NLTK Natural Language Toolkit](https://www.nltk.org/).

Because of this, the primary contribution of Smashcima is designing a modular structure and good interfaces between these modules. Smashcima will never support all use cases out of the box, but the goal is to make it easily extensible while reusing as much of its existing code as possible. What a game engine is for making games, Smashcima should be for making image synthesizers.
