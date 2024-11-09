# Smashcima

A library and a framework for synthesizing images containing music, intended for the creation of training data for OMR models.

**Try out the demo on [🤗 Huggingface Spaces](https://huggingface.co/spaces/Jirka-Mayer/Smashcima) right now!**

Install with:

```bash
pip3 install smashcima
```


## A tutorial

> **Note:** The tool is under development and does not yet have a fixed public API. The tutorial is being developed and from it the whole tool is being built top-down.

To quickly learn how to start using Smashcima for your project, start with the tutorial.

[Smashcima Tutorial](docs/tutorial.md)


## How it works

Smashcima is not really a single tool, but more like a framework. To fully learn how to leverage its abilities, start by reading its documentation:

[Smashcima Documentation - Introduction](docs/introduction.md)


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

1. Update the version in `smashcima/__init__.py`.
2. Build the package `make build`.
3. Upload to PyPI `make push-prod` or TestPyPI `make push-test`.
4. When asked, use `__token__` for username and paste in the access token for the password (with the `pypi-` prefix).
5. Check the version has been uploaded and try its installation.
6. Submit the version commit and create a release on GitHub.

> **Note:** Don't forget keeping the version at `X.Y.Zdev` when developing version `X.Y.Z`. See the `smashcima/__init__.py` file.

> **Note:** to install from the test pypi, use: `pip3 install --index-url https://test.pypi.org/simple/ --no-deps smashcima`. More info [here](https://packaging.python.org/en/latest/tutorials/packaging-projects/#installing-your-newly-uploaded-package).


## Packaging and development notes

- Read this: https://packaging.python.org/en/latest/tutorials/packaging-projects/
- Package configuration inspired by this: https://github.com/vega/altair/blob/main/pyproject.toml
- For development setup inspiration check out: https://altair-viz.github.io/getting_started/installation.html#development-installation
- jupyter notebooks in git: https://mg.readthedocs.io/git-jupyter.html
- deploying voila: https://voila.readthedocs.io/en/stable/deploy.html
