FROM python:3.10

# dependencies for OpenCV
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6 -y

WORKDIR /app

# get the smashcima library (in this current version)
# so that it can be pip installed
COPY ./smashcima ./smashcima
COPY ./pyproject.toml ./pyproject.toml
COPY ./README.md ./README.md
COPY ./LICENSE ./LICENSE

# get the demo
COPY ./gradio_demo ./gradio_demo

# this is here only for the .musicxml files and nothing else,
# once they get moved into the demo folder, you can drop these lines
COPY ./jupyter ./jupyter
COPY ./testing ./testing

# install smashcima and the dependencies for the demo
RUN pip install --no-cache-dir .[gradio]

# configure the assets folder path and
# download and install all necessary demo asset bundles
ENV MC_ASSETS_CACHE=/app/smashcima_assets
RUN python -m gradio_demo.asset_bundles

# configure networking
EXPOSE 7860
ENV GRADIO_SERVER_NAME="0.0.0.0"

# configure startup
ENTRYPOINT ["python", "-m", "gradio_demo"]
CMD []
