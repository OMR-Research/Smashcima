# Publishing to PyPI

Production PyPI at: https://pypi.org/

Testing PyPI at: https://test.pypi.org/

1. Run all Jupyter notebook tests and unit tests and build the demo docker container (to test pip-install of dependencies) and try the demo.
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
