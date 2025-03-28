# Asset bundles

When synthesizers create a scene, they usually don't do so out of thin air. They depend on some external static data. This might be datasets of symbol images or pre-trained generative models.

The assets layer of Smashcima is responsible for the downloading and installation of these external resources. It lives in the `smashcima.assets` module.


## Basic usage

Let's say we want to use the MUSCIMA++ dataset during synthesis.

First, we need to get a handle on an `AssetRepository`. It represents a local folder, where the assets are downloaded to. You can get the default one like this:

```py
from smashcima.assets.AssetRepository import AssetRepository

assets = AssetRepository.default()
```

The asset repository manages so-called asset bundles (`AssetBundle`), where an asset bundle is some collection of external resources that are managed as a single object (e.g. a dataset).

You can then use this repository to resolve the `MuscimaPP` dataset asset bundle:

```py
from smashcima.assets.datasets.MuscimaPP import MuscimaPP

muscima_pp = assets.resolve_bundle(MuscimaPP)
```

The `resolve_bundle` method downloads the dataset from the internet if necessary and returns an instance of the `MuscimaPP` asset bundle class that you can then use to access the dataset.

The `MuscimaPP` asset bundle provides the `muscima_pp.cropobjects_directory` field that returns a path to the directory containing the downloaded XML files of the MUSCIMA++ dataset.

You can get the name of the first file in that directory like this:

```py
print("Example file from the MUSCIMA++ dataset:")

for file in muscima_pp.cropobjects_directory.iterdir():
    print(file.name)
    break
```


## Controlling the cache directory

By default, assets bundles are downloaded to the current users's cache directory.

On Linux, this is the `~/.cache/smashcima/assets` directory.

You can override this placement by specifying the `MC_ASSETS_CACHE` environment variable.

This can even be done from within python before any assets are used:

```py
import os

os.environ["MC_ASSETS_CACHE"] = "./smashcima_assets"
```


## Available asset bundles

This is a list of asset bundles provided by Smashcima out of the box:

- `smashcima.assets.datasets.MuscimaPP`
- `smashcima.assets.datasets.OmniOMRProto`
- `smashcima.assets.glyphs.muscima_pp.MuscimaPPGlyphs`
- `smashcima.assets.glyphs.omni_omr.OmniOMRGlyphs`
- `smashcima.assets.textures.MzkPaperPatches`
