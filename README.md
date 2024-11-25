[![License Apache 2.0](https://badgen.net/badge/license/apache2.0/blue)](https://github.com/OMR-Research/Smashcima/blob/main/LICENSE)
[![PyPI version](https://badge.fury.io/py/smashcima.svg)](https://pypi.org/project/smashcima/)
[![Downloads](https://static.pepy.tech/badge/smashcima)](https://pepy.tech/project/smashcima)
![Python Version](https://badgen.net/badge/python/3.8+/cyan)

<div align="center">
    <br/>
    <img src="docs/assets/smashcima-logo.svg" width="600px">
    <br/>
    <br/>
    <br/>
</div>

A library and a framework for synthesizing images containing handwritten music, intended for the creation of training data for OMR models.

**Try out the demo on [🤗 Huggingface Spaces](https://huggingface.co/spaces/Jirka-Mayer/Smashcima) right now!**<br/>
Example output with MUSCIMA++ writer no. 28 style:

<img src="docs/assets/readme-example.jpg"><br/>

**Install from [pypi](https://pypi.org/project/smashcima/) with:**

```bash
pip install smashcima
```


## Getting started

To quickly learn how to start using Smashcima for your project, start with the tutorials:

1. [Producing music notation images](docs/tutorials/1-producing-music-notation-images.md)
2. [Changing background texture](docs/tutorials/2-changing-background-texture.md)
3. [Using custom glyphs](docs/tutorials/3-using-custom-glyphs.md)


## How it works

Smashcima is primarily a framework and a set of crafted interfaces for building custom visual-data related synthesizers.


- [Introduction](docs/introduction.md)
- Models and service orchestration
- Scene
    - Scene objects
    - Affine spaces and rendering
    - Semantic music scene objects
    - Visual music scene objects
- Synthesis
    - Synthesizer interfaces
    - Glyphs
    - Style control
- Asset bundles
- ...

If you feel like improving the library, take a look at the [TODO List](docs/todo-list.md).


## After cloning

Create a virtual environment and install dependencies:

```bash
python3 -m venv .venv
.venv/bin/pip3 install -e .

# to run jupyter notebooks:
.venv/bin/pip3 install -e .[jupyter]

# to run the gradio demo:
.venv/bin/pip3 install -e .[gradio]
```


## Checklists

- [Before commit](docs/checklists/before-commit.md)
- [Publishing to PyPI](docs/checklists/publishing-to-pypi.md)
- [Deploying Gradio Demo](docs/checklists/deploying-gradio-demo.md)


## Acknowledgement

There's a publication being written. Until then, you can cite the original Mashcima paper:

> Jiří Mayer and Pavel Pecina. Synthesizing Training Data for Handwritten Music Recognition. *16th International Conference on Document Analysis and Recognition, ICDAR 2021.* Lausanne, September 8-10, pp. 626-641, 2021.


## Contact

<img src="https://ufal.mff.cuni.cz/~hajicj/2024/images/logo-large.png" width="600px">

Developed and maintained by [Jiří Mayer](https://ufal.mff.cuni.cz/jiri-mayer) ([mayer@ufal.mff.cuni.cz](mailto:mayer@ufal.mff.cuni.cz)) as part of the [Prague Music Computing Group](https://ufal.mff.cuni.cz/pmcg) lead by [Jan Hajič jr.](https://ufal.mff.cuni.cz/jan-hajic-jr) ([hajicj@ufal.mff.cuni.cz](mailto:hajicj@ufal.mff.cuni.cz)).
