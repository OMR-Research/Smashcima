# Development Setup


## Setting up

- Clone the repo `git clone git@github.com:OMR-Research/Smashcima.git`
- Create the virtual environment `python3 -m venv .venv`
- Install the `smashcima` package as editable into that venv with all of its dependencies `.venv/bin/pip3 install -e .`

Optionally install also Jupyter and Gradio dependencies:

```bash
.venv/bin/pip3 install -e .[jupyter]
.venv/bin/pip3 install -e .[gradio]
```


## New feature development

- Bump the version in `smashcima/_version.py` and add the `dev` suffix (e.g. `1.2.3dev`)
- Do the feature development (modify the codebase)

Before commit:
- Clear jupyter notebooks `make clear-jupyter-outputs`

Commit and push changes to the Github repository.


## Testing via unit tests

See the `/tests` folder.

- Execute unit tests `.venv/bin/python3 -m tests`
- Inspect the existing tests to see how you can add your own. They are automatically discovered by the `tests/__main__.py` file.


## Testing via Jupyter files

Make sure that Jupyter dependencies are installed:

```bash
.venv/bin/pip3 install -e .[jupyter]
```

All jupyter tests are present in the `/jupyter` folder. They are organized roughly according to the sub-modules of the `smashcima` module, but there are also legacy files present.

- Create a new `.ipynb` file somewhere in the `/jupyter` folder, named according to what it tests.
- The working directory for a jupyter notebook is its parent directory, so specify path to the development assets folder as the first thing in the file's header: `%env MC_ASSETS_CACHE=../../smashcima_assets`
- Add code that does the testing (see other files for inspiration)
- Run the ipynb files directly from inside VS Code
- Restart the kernel before executing (`Restart`)
- Run the whole file (`Run All`)
- Visually inspect the results

> **Note:** The folder `/jupyter/exporting` contains nice visual tests you can read to understand the setup.

Running jupyter notebooks modifies their cached state. Make sure you clear this state before doing a commit:

```bash
make clear-jupyter-outputs
```


## Deploying new version

- Package to PyPI: See the [Publishing to PyPI](checklists/publishing-to-pypi.md) page
- Demo to Huggingface spaces: See the [Deploying Gradio Demo](checklists/deploying-gradio-demo.md) page


## Demo development

- install demo dependencies `.venv/bin/pip3 install -e .[gradio]`
- the demo runs from the `gradio_demo/__main__.py`, can be launched via
    - `make demo-serve`
    - open the demo in the browser (URL is printed to the console)
- when the codebase changes, you must restart the server
