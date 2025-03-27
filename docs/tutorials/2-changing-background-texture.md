# Tutorial 2: Changing background texture

This tutorial shows how to modify an existing `Model` class. More specifically, how to change the background texture for the `BaseHandwrittenModel`.


## Standard model use

When using the `BaseHandwrittenModel` as is, you just instantiate and invoke it:

```py
import cv2
import smashcima as sc

model = sc.orchestration.BaseHandwrittenModel()
scene = model("my-input-file.musicxml")

for i, page in enumerate(scene.pages):
    bitmap = scene.render(page)
    cv2.imwrite(f"page_{i}.png", bitmap)
```


## Synthesizers

Internally, a `Model` is a collection of *synthesizers* that are configured and connected together to serve a single purpose. Synthesizers come from the `smashcima.synthesis` module and they are responsible for:

- synthesizing page layout (dimensions and staff placement)
- synthesizing staves (empty stafflines)
- synthesizing music notation (musical content onto empty stafflines)
- synthesizing glyphs (individual musical symbols)
- synthesizing paper texture

As you can see, each synthesizer is like a very narrow model, that is designed to be used in conjunction with the other synthesizers, and synthesizes one tiny piece of the entire puzzle.


## Using different paper synthesizer

We can modify an existing model by changing the configuration of its internal synthesizers. The model is configured inside its constructor, so in order to change it, we need to make a child class and override these methods:

```py
from smashcima.synthesis import PaperSynthesizer, SolidColorPaperSynthesizer

class MyModel(sc.orchestration.BaseHandwrittenModel):
    def register_services(self):
        super().register_services()
        
        # for paper synthesizer use the solid color synth,
        # instead of the texture-quilting default synthesizer
        self.container.type(SolidColorPaperSynthesizer)
        self.container.interface(
            PaperSynthesizer, # when people ask for this
            SolidColorPaperSynthesizer # construct this
        )
    
    def resolve_services(self):
        super().resolve_services()

        # get the paper synthesizer instance
        self.paper_synth: SolidColorPaperSynthesizer \
            = self.container.resolve(PaperSynthesizer)

    def configure_services(self):
        super().configure_services()

        # and configure paper synthesizer's properties
        # (BGRA uint8 format)
        self.paper_synth.color = (187, 221, 234, 255)
```

The model consists of a group of synthesizers and additional classes that together are called services. These services are registered into, and constructed by a [service container](https://www.cosmicpython.com/book/chapter_13_dependency_injection.html), accessible via `self.container`. These services are set up in three methods called by the model constructor:

- `register_services` Registers types into the container, binds them to interfaces.
- `resolve_services` Asks the container to construct services we will use later.
- `configure_services` Configures resolved services instances.

> **Explainer:** The purpose of a service container is to construct services (also known as *resolving services*). You first tell the container what services it should know about (e.g. *When asked about a car, construct a Toyota Corolla.*). Then you resolve services that the model will use later and store them in the model in `self.my_car`. Finally, you adjust the configuration on the constrctued service instances to suit your needs. When the container resolves a service, it recursively resolves all of its dependencies (constructor arguments), which greatly simplifies the service construction process.

> **Note:** If you call `.resolve` on the same type multiple times, you only
get one instance constructed and then returned repeatedly. Another words, all services are registered as singletons.

To learn more, see the documentation on Models.

Now we can use this new model type to do the synthesis:

```py
model = MyModel()
scene = model("my-input-file.musicxml")

for i, page in enumerate(scene.pages):
    bitmap = scene.render(page)
    cv2.imwrite(f"page_{i}.png", bitmap)
```

You can use `(255, 255, 255, 255)` to get white background and `(0, 0, 0, 0)` to get transparent background.


# Replacing the random number generator

Not all services in the model are synthesizers. For example, most synthesizers need a source of randomness. Therefore there is a `random.Random` instance registered as a service in the container. The instance is also stored on the model in the `self.rng` field. You can check they are the same:

```py
import random

model = MyModel()
resolved_rng = model.container.resolve(random.Random)
field_rng = model.rng

assert resolved_rng is field_rng # succeeds!
```

You can replace the random number generator during service registration with your own instance:

```py
my_rng = random.Random(42)

class MyRandomModel(sc.orchestration.BaseHandwrittenModel):
    def register_services(self):
        super().register_services()

        self.container.instance(
            random.Random, # when people ask for this
            my_rng # return this
        )

model = MyRandomModel()
assert model.rng is my_rng # succeeds!
```


## Conclusion

You've learned how to configure model sevices for existing models. To learn more, read the documentation on Models and examine the base model you are overriding to see what services it registers and how, so that you know how to modify them. The next tutorial will teach you how to replace the `GlyphSynthesizer` of a model with your own glyph synthesizer.
