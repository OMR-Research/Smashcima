
<img src="docs/assets/smashcima-logo.png" width="600px">

# Introduction

Smashcima is a library and framework for synthesizing images containing handwritten music for creating synthetic training data for OMR models.

**Try out the demo on [Huggingface Spaces](https://huggingface.co/spaces/Jirka-Mayer/Smashcima) right now!**<br/>
Example output with MUSCIMA++ writer no. 28 style:

<img src="docs/assets/readme-example.jpg"><br/>

**Install from [pypi](https://pypi.org/project/smashcima/) with:**

```bash
pip install smashcima
```

## What is Smashcima, who is it for, and how is it novel?

Smashcima is a Python package primarily intended to be used as part of optical music recognition workflows, esp. with domain adaptation in mind. The target user is therefore a machine-learning, document processing, library sciences, or computational musicology researcher with minimal skills in python programming.

Smashcima is the only tool that simultaneously:

- synthesizes handwritten music notation,
- produces not only raster images but also segmentation masks, classification labels, bounding boxes, and more,
- synthesizes entire pages as well as individual symbols,
- synthesizes background paper textures,
- synthesizes also polyphonic and pianoform music images,
- accepts just [MusicXML](https://www.musicxml.com/) as input,
- is written in Python, which simplifies its adoption and extensibility.

Therefore, Smashcima brings a unique new capability for optical music recognition (OMR): synthesizing a near-realistic image of handwritten sheet music from just a MusicXML file. As opposed to notation editors, which work with a fixed set of fonts and a set of layout rules, it can adapt handwriting styles from existing OMR datasets to arbitrary music (beyond the music encoded in existing OMR datasets), and randomize layout to simulate the imprecisions of handwriting, while guaranteeing the semantic correctness of the output rendering. Crucially, the rendered image is provided also with the positions of all the visual elements of music notation, so that both object detection-based and sequence-to-sequence OMR pipelines can utilize Smashcima as a synthesizer of training data.

(In combination with the [LMX canonical linearization of MusicXML](https://github.com/Jirka-Mayer/lmx), one can imagine the endless possibilities of running Smashcima on inputs from a MusicXML generator.)

## Development

Smashcima is being developed on GitHub: [https://github.com/OMR-Research/Smashcima](https://github.com/OMR-Research/Smashcima).
It is part of the `OMR-Research` organization to maximize reach within the OMR community.

Documentation specific to contributing is available directly in the software's GitHub repository.


## Financing

This work has been done by the OmniOMR project within the 2023-2030 NAKI III programme, supported by the Ministry of Culture of the Czech Republic (DH23P03OVV008).


## How to cite

There's a publication being written. Until then, you can cite the original Mashcima paper:

> Jiří Mayer and Pavel Pecina. Synthesizing Training Data for Handwritten Music Recognition. *16th International Conference on Document Analysis and Recognition, ICDAR 2021.* Lausanne, September 8-10, pp. 626-641, 2021.


## Contact

<img src="assets/logo-large.png" width="600px">

Developed and maintained by [Jiří Mayer](https://ufal.mff.cuni.cz/jiri-mayer) ([mayer@ufal.mff.cuni.cz](mailto:mayer@ufal.mff.cuni.cz)) as part of the [Prague Music Computing Group](https://ufal.mff.cuni.cz/pmcg) lead by [Jan Hajič jr.](https://ufal.mff.cuni.cz/jan-hajic-jr) ([hajicj@ufal.mff.cuni.cz](mailto:hajicj@ufal.mff.cuni.cz)).
