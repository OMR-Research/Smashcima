# Models and service orchestration

When you first start using Smashcima, you will mostly interact with models (extensions of the `Model` abstract class). Model (as in *generative model*) represents a pre-configured synthesis pipeline that produces synthetic data modelling a specific data domain (a specific evaluation dataset / visual style / data type).

Therefore the responsibilities of models are twofold:

1. Provide a polished external interface for synthesizing the modelled data domain
2. Set up and configure internal synthesizers and services to facilitate the data domain modelling, while allowing for at least some re-configuration by the user (i.e. orchestrate its internal services)

Code explored in this documentation section lives in the `smashcima.orchestration` module.


## External model interface

A model is constructed like any other python object:

```py
import smashcima as sc

my_model = sc.BaseHandwrittenModel()
```

Constructor arguments depend on the model used, but the model should always provide default values for all of them to allow for construction without any arguments provided. This is because a model should by default already model some data domain well and customization should only be applied later if needed.

The constructed model instance is callable, so it pretends to be a data-generating function. By calling it, we generate a new sample of data:

```py
new_scene = my_model("input.musicxml")
```

The returned data sample is called a *scene*, because it contains much more information than just an image or an annotation. The actual desired synthetic data must then be exported from the synthesized scene.

Arguments to the model invocation depend completely on the specific model. The `BaseHandwrittenModel` shown in this example expects a MusicXML input, either as a file, or as an XML string. But you might have models that require no arguments, or others that require some random latent vector **z** (e.g. Generative Adversarial Networks), etc.

Similarly, the type of the returned scene instance is also completely controlled by the specific model used. The `BaseHandwrittenModel` returns an instance of `BaseHandwrittenScene`, which contains representation of the music, the synthesized pages, a renderer that will be used for rasterization, and metadata about the chosen MUSCIMA++ writer style.

For this specific scene type, getting the bitmap image is done like this:

```py
# BGRA OpenCV image
img = new_scene.render(new_scene.pages[0])
```

> **Note:** You can imagine how this is very tightly linked to the data domain of handwritten scores of music notation in the MUSCIMA++ dataset. A model designed for synthesis of isolated musical symbols would have a completely different API, accepting a symbol class as an argument and outputting a single symbol image as output, with possible latent space embedding (or similar metadata).

The synthesized scene is also assigned to the model instance under the `.scene` field. This field is `None` before the first invocation. This is for situations when you cannot store the return value from the model invocation immediately:

```py
# an alternative way of getting the scene
# (though the first one is preferred)
my_model("input.musicxml")
new_scene = my_model.scene
```


## Service orchestration

When a model is constructed, it creates a set of synthesizers and auxiliary services, configures them, and connects them to each other. It orchestrates a synthesis pipeline that will be used once the model gets invoked.

These include synthesizers for glyphs, line glyphs, stafflines, page background, page layout, music notation, or stems and beams. The auxiliary services include a random number generator and an assets repository. All of these services depend on one another, for example, the music notation synthesizer uses the glyph synthesizer and both use the random number generator and the assets repository.

Since the manual construction of these services would be tedious and modification of the construction process in this case by the user would be impossible, the model instead uses a service container for the service construction (also known as an IoC container).


### Service container

Each model has its own service container available under the `.container` field.

Service container can be used to construct a dependency graph of service instances in two steps:

1. You register services into the container
2. You resolve the service you want to use

During the registration step, you tell the container what services you wish to be used. This can happen in roughly three ways:

- You give the container an existing instance for a given service type. So, you give it a specific `my_rng` value for the service `random.Random`. When the container is asked to resolve the service `random.Random`, it will return the `my_rng` value.
- Or you tell the container just the service type, e.g. `MuscimaPPStyleDomain`. It will then figure on its own how to construct the type when asked for its instance (by default using the argument-free constructor, or by recursively resolving all the arguments).
- Or you tell the container what specific service type it should construct when asked about an abstract service. For example, you tell the container to construct an instance of `MyFancyGlyphSynthesizer` when the user asks for a `GlyphSynthesizer`.

Once all of these registrations take place, you can that resolve a service from the container (e.g. `GlyphSynthesizer`) and it will recursively construct it, together with all of its dependencies (e.g. `random.Random`) and give it back to you.

These are the methods you can use to register services into the container:

```py
import random
my_rng = random.Random(42)

# register an existing instance
container.instance(random.Random, my_rng)

# register a type
container.type(sc.MuscimaPPStyleDomain)

# register an interface implementation
container.interface(sc.GlyphSynthesizer, MyFancyGlyphSynthesizer)
```

You can then ask the container to give you the glyph synthesizer instance, which will be constructed by the container using the RNG and style domain registered above:

```py
# construct a service based on type registrations
my_glyph_synth = container.resolve(sc.GlyphSynthesizer)

assert type(my_glyph_synth) is MyFancyGlyphSynthesizer # succeeds!
```


#### Singletons

When you resolve a service twice, the container will only construct it once and then return the same instance again:

```py
# every service is constructed only once
first = container.resolve(sc.GlyphSynthesizer)
second = container.resolve(sc.GlyphSynthesizer)

assert first is second # succeeds!
```

This behaviour is called singleton registration - each service always exists only in one instance, i.e. a singleton.

It means that even if `random.Random` is requested by twenty other services, there will only be a single instance created and reused by all of them.

> **Note:** This is a slight simplification from general IoC containers, say in web applications, where the lifetime of services can be configured and there exist scoped and transient services. However, it made little to no sense in our case of constructing synthesis pipelines.


#### No implicit registrations

The service container cannot resolve types that have not been explicitly registered. If that occurs, the resolution raises an exception and you need to provide the registration manually.


#### Complex service constructors

Sometimes, services may require arguments that cannot be automatically resolved by the container during constructions (e.g. having `str` or `int` arguments).

If possible, you can register the service as an instance:

```py
my_rng = random.Random(42)
container.instance(my_rng)
```

But if the service depends on other services that will yet to be constructed by the container, you can register a factory function instead of the true service constructor:

```py
def my_service_factory(dependecy: OtherService) -> MyService:
    return MyService(dependency, some_number=42)

container.factory(MyService, my_service_factory)
```


### Service construction in a model

Now that we know how a service container works, we will look at how it's utilized within a model constructor.

At the end of the `Model.__init__` method, there are these three methods invoked:

```py
self.register_services()
self.resolve_services()
self.configure_services()
```

These are designed for you to override, when you create your own model.

- `register_services` is used to register services into the container via the `.instance`, `.type`, and `.interface` methods on the container.
- `resolve_services` is used to resolve services from the container and assign them to some model fields, so that they can be used later during configuration and synthesis without calling the low-level `container.resolve` method.
- `configure_services` is used to modify services after they are constructed, altering their behaviour.

This is what these methods can look like when implemented:

```py
class MyModel(sc.Model):
    def register_services(self):
        super().register_services()
        
        # register a service
        self.container.interface(
            sc.GlyphSynthesizer,
            MyFancyGlyphSynthesizer
        )
    
    def resolve_services(self):
        super().resolve_services()

        # resolve a service
        self.glyph_synthesizer: MyFancyGlyphSynthesizer \
            = self.container.resolve(sc.GlyphSynthesizer)
        assert type(self.glyph_synthesizer) is MyFancyGlyphSynthesizer
    
    def configure_services(self):
        super().configure_services()

        # configure a constructed service
        self.glyph_synthesizer.level_of_fancy = 999
```


### Pre-defined services

The `Model` base class automatically registers a number of useful services into the service container for you to use. These are:

- `random.Random` instance to generate random numbers
- `sc.AssetRepository` instance to provide access to asset bundles
- `sc.Styler` instance to control style parameters for each synthesized sample

These instances are likely to be needed by almost all models and they are very common synthesizer dependencies.

The random number generator and styler are also exposed via model fields, so that you can access them inside and outside the model:

```py
model.rng     # random.Random
model.styler  # sc.Styler
```


## Re-configuring existing models

There are two ways in which to modify model services:

1. change the way in which they are constructed (e.g. use a different `GlyphSynthesizer` or modify its constructor arguments)
2. change their configuration after they are constructed

The first approach is achieved by overriding container registrations at the end of the `register_services` method.

For example, let's say we want to control the seed of the `random.Random` instance. We could do the following:

```py
import random
import smashcima as sc

class MyModelWithSeed(SomeBaseModel):
    def __init__(self, seed: int):
        # store the seed before we call the super constructor
        self._seed = seed

        # the super constructor will call the `register_services` method
        super().__init__()
    
    def register_services(self):
        super().register_services()

        # override the `random.Random` registration
        self.container.instance(
            random.Random,
            random.Random(self._seed)
        )
```

This works, because registering a type into the service container for the second time replaces the old registration with the new one. This lets us modify the dependency graph of services, what specific service types are used, and what constructor arguments they are given.

The second way of modifying services is after their creation, by modifying their configuration fields.

For example, we could modify the line width in the `NaiveStafflinesSynthesizer`:

```py
class MyModel(sc.BaseHandwrittenModel):
    def configure_services(self):
        super().configure_services()

        # get the naive stafflines synth instance
        synth = self.container.resolve(sc.StafflinesSynthesizer)
        assert type(synth) is NaiveStafflinesSynthesizer, \
            "Just making sure no one changed the registered type we expect"
        
        # modify its configuration
        synth.line_thickness = 0.1 # mm
```

Alternatively, for services that have been resolved in `resolve_services`, you can access them directly via their field:

```py
class MyModel(sc.BaseHandwrittenModel):
    def resolve_services(self):
        super().resolve_services()
        
        # remember service instance in a model field
        self.fancy_glyph_synth: FancyGlyphSynthesizer \
            = self.container.resolve(sc.GlyphSynthesizer)
        assert type(self.fancy_glyph_synth) is FancyGlyphSynthesizer \
            "Checking nobody changed the registered type that we expect"

    def configure_services(self):
        super().configure_services()

        # configure a service
        self.fancy_glyph_synth.level_of_fancy = 999
```

But with these explicitly resolved services, you can modify them post-creation even from outside of the model:

```py
# create a model
model = MyModel()

# configure a service
model.fancy_glyph_synth.level_of_fancy = 999

# use the model
model(...)
```

Note that for most configuration changes to a model, inheriting from the model and making a custom class derivative is necessary.
