import abc
from ..scene.Scene import Scene
from typing import Optional
from .Container import Container
from smashcima.assets.AssetRepository import AssetRepository
from smashcima.synthesis.style.Styler import Styler
import random


class Model(abc.ABC):
    """
    Model is the container for a specific synthesis pipeline. It:
    - Acts as the public facing API for the data consumer.
    - Constructs and wires together pipeline components (synthesizers,
        loaders, renderers). Acts as an IoC container.
    - Tracks steps, batches, and epochs during the synthesis process.
    """
    
    def __init__(self):
        self.container = Container()
        "IoC container with services used by the synthesis pipeline"

        self.scene: Optional[Scene] = None
        "The scene synthesized during the last invocation of this model"

        self.register_services()
        self.resolve_services()
        self.configure_services()
    
    def register_services(self):
        """Called from the constructor in order to register services into
        the service container. Override this to customize the behaviour
        of this model at the service level."""

        # register the default asset repository into the container,
        # so that synthesizers can resolve asset bundles
        self.container.instance(AssetRepository, AssetRepository.default())

        # register the default RNG to use during randomization
        self.container.instance(random.Random, random.Random())

        # register the styler
        self.container.type(Styler)

    def resolve_services(self):
        """Called from the constructor in order to resolve the specific
        instances of services that will be used during synthesis. Override
        this to resolve additional services from the container."""

        self.rng: random.Random = self.container.resolve(random.Random)
        "The RNG that should be used for all synthesis randomness"

        self.styler: Styler = self.container.resolve(Styler)
        "Controls the style selection for all the synthesizers"
    
    def configure_services(self):
        """Called from the consturctor after services are resolved.
        Here, services should be set-up after their resolution."""
        pass
    
    def __call__(self, *args, **kwargs):
        # create a fresh new scene that will contain the synthesized sample
        self.scene = Scene()

        # select the styles used for synthesis of this sample
        self.styler.pick_style()

        # run the synthesis pipeline
        outputs = self.call(*args, **kwargs)

        # return whatever the model's call method returned
        return outputs

    @abc.abstractmethod
    def call(self, *args, **kwargs):
        raise NotImplementedError(
            f"Model {self.__class__.__name__} does not have the `call()` "
            "method implemented."
        )
