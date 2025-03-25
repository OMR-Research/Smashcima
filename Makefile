.PHONY: build push-prod push-test demo-serve build-docs clear-jupyter-outputs

build:
	rm -rf dist
	.venv/bin/python3 -m pip install --upgrade build
	.venv/bin/python3 -m build

push-prod:
	.venv/bin/python3 -m pip install --upgrade twine
	.venv/bin/python3 -m twine upload dist/*

push-test:
	.venv/bin/python3 -m pip install --upgrade twine
	.venv/bin/python3 -m twine upload --repository testpypi dist/*

demo-serve:
	MC_ASSETS_CACHE=./smashcima_assets .venv/bin/python3 -m gradio_demo

build-docs:
	.venv/bin/python3 -m docs_builder

clear-jupyter-outputs:
	.venv/bin/jupyter nbconvert --clear-output --inplace jupyter/*.ipynb jupyter/*/*.ipynb jupyter/*/*/*.ipynb jupyter/*/*/*/*.ipynb


######################
# Docker Gradio Demo #
######################

VERSION=$$(grep -oP "__version__\\s*=\\s*\"\K[^\"]+" smashcima/_version.py)
TAG=jirkamayer/smashcima-demo:$(VERSION)

.PHONY: docker-demo-build docker-demo-push docker-demo-run docker-demo-shell

docker-demo-build:
	docker build --tag $(TAG) .

docker-demo-push:
	docker push $(TAG)

docker-demo-run:
	@echo Open the demo at http://localhost:7860/
	docker run --rm -it -p 7860:7860 $(TAG)

docker-demo-shell:
	docker run --rm -it --entrypoint bash $(TAG)
