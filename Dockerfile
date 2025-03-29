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

# set up environment variables for temporary data
# (smashcima cache data)
ENV MC_HOME=/tmp/smashcima
# (numba jit compiler)
ENV NUMBA_CACHE_DIR=/tmp/numba
# (augraphy renders fonts via imagemagick)
ENV MAGICK_TEMPORARY_PATH=/tmp
# (augraphy also import matplotlib)
ENV MPLCONFIGDIR=/tmp/matplotlib

# configure the assets folder path and
# download and install all necessary demo asset bundles
ENV MC_ASSETS_CACHE=/app/smashcima_assets
# RUN python -m gradio_demo.asset_bundles

# NOPE, instead, copy these over from the local folders,
# since the OmniOMR proto dataset cannot be downloaded
COPY ./smashcima_assets/MuscimaPPGlyphs/bundle.json ./smashcima_assets/MuscimaPPGlyphs/bundle.json
COPY ./smashcima_assets/MuscimaPPGlyphs/symbol_repository.pkl ./smashcima_assets/MuscimaPPGlyphs/symbol_repository.pkl
COPY ./smashcima_assets/OmniOMRGlyphs/bundle.json ./smashcima_assets/OmniOMRGlyphs/bundle.json
COPY ./smashcima_assets/OmniOMRGlyphs/symbol_repository.pkl ./smashcima_assets/OmniOMRGlyphs/symbol_repository.pkl
COPY ./smashcima_assets/MzkPaperPatches ./smashcima_assets/MzkPaperPatches
# fake-install sub-dependencies by only providing the bundle.json:
COPY ./smashcima_assets/MuscimaPP/bundle.json ./smashcima_assets/MuscimaPP/bundle.json
COPY ./smashcima_assets/OmniOMRProto/bundle.json ./smashcima_assets/OmniOMRProto/bundle.json

# configure networking
EXPOSE 7860
ENV GRADIO_SERVER_NAME="0.0.0.0"

# configure startup
ENTRYPOINT ["python", "-m", "gradio_demo"]
CMD []
