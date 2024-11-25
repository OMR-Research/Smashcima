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
2. Changing image background
3. Using custom glyphs


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


## Publishing new version to PyPI

Production PyPI at: https://pypi.org/

Testing PyPI at: https://test.pypi.org/

1. Run all Jupyter notebook tests and unit tests.
2. Update the version in `smashcima/_version.py`.
3. Build the package `make build`.
4. Upload to PyPI `make push-prod` or TestPyPI `make push-test`.
5. When asked, use `__token__` for username and paste in the access token for the password (with the `pypi-` prefix).
6. Check the version has been uploaded and try its installation.
7. Submit the version commit and create a release on GitHub.

> **Note:** Don't forget keeping the version at `X.Y.Zdev` when developing version `X.Y.Z`. See the `smashcima/_version_.py` file.

> **Note:** to install from the test pypi, use: `pip3 install --index-url https://test.pypi.org/simple/ --no-deps smashcima`. More info [here](https://packaging.python.org/en/latest/tutorials/packaging-projects/#installing-your-newly-uploaded-package).


## Packaging and development notes

- Read this: https://packaging.python.org/en/latest/tutorials/packaging-projects/
- Package configuration inspired by this: https://github.com/vega/altair/blob/main/pyproject.toml
- For development setup inspiration check out: https://altair-viz.github.io/getting_started/installation.html#development-installation
- jupyter notebooks in git: https://mg.readthedocs.io/git-jupyter.html
- deploying voila: https://voila.readthedocs.io/en/stable/deploy.html
