import abc
import random
from typing import Generic, Optional, TypeVar

from smashcima.assets.AssetRepository import AssetRepository
from smashcima.exporting.compositing.Compositor import Compositor
from smashcima.exporting.compositing.DefaultCompositor import DefaultCompositor
from smashcima.exporting.postprocessing.NullPostprocessor import NullPostprocessor
from smashcima.exporting.postprocessing.Postprocessor import Postprocessor
from smashcima.synthesis.style.Styler import Styler

from .Container import Container


T = TypeVar("T")
"""The scene type the model returns (does NOT need to inherit from `Scene`)"""


class Model(Generic[T], abc.ABC):
    """Base class for a data-generating function used for data synthesis.

    A model is a generating function, that constructs a new scene, whenever
    invoked, based on the constructor and invocation arguments. The goal
    of a model is to wire together and configure synthesizers that together
    construct a new scene, whenever the model is invoked. It differs from a
    synthesizer in that is already comes pre-configured for a singular task
    and requires no configuration to start using. Synthesizer, on the other
    hand, is a LEGO piece that depends on abstract interfaces and must be
    painfully wired together with other synthesizers in order to work
    and it serves some small, abstract task.
    """

    def __init__(self) -> None:
        self.container = Container()
        """IoC container with services used during synthesis"""

        self.scene: Optional[T] = None
        """The scene synthesized during the last invocation of this model"""

        self.register_services()
        self.resolve_services()
        self.configure_services()
    
    def register_services(self):
        """Registers services into the service container.

        Called from the constructor. Override this to customize the behaviour
        of this model at the service level.
        """

        # register the default asset repository into the container,
        # so that synthesizers can resolve asset bundles
        self.container.instance(AssetRepository, AssetRepository.default())

        # register the default RNG to use during randomization
        self.container.instance(random.Random, random.Random())

        # register the styler,
        # with the container reference provided
        self.container.factory(Styler, lambda: Styler(self.container))

        # register default compositor
        self.container.interface(
            Compositor, DefaultCompositor, register_impl=True
        )

        # register null postprocessor
        self.container.interface(
            Postprocessor, NullPostprocessor, register_impl=True
        )

    def resolve_services(self) -> None:
        """Defines model fields that hold specific services.
        
        Called from the constructor in order to resolve the specific
        instances of services that will be used during synthesis.
        These services should then be assigned to a well-named model
        fields so that they can be easily accessed during synthesis.
        Override this to resolve additional services from the container.
        """

        self.rng: random.Random = self.container.resolve(random.Random)
        """The RNG that should be used for all synthesis randomness"""

        self.styler: Styler = self.container.resolve(Styler)
        """Controls the style selection for all the synthesizers"""

        self.compositor: Compositor = self.container.resolve(
            Compositor # type: ignore
        )
        """Defines the pipeline that converts the scene into an ImageLayer"""

        self.postprocessor: Postprocessor = self.container.resolve(
            Postprocessor # type: ignore
        )
        """Applies augmentation filters during the compositing process"""
    
    def configure_services(self):
        """Modifies and configures resolved servies.
        
        Called from the consturctor after services are resolved.
        Here, services should be set-up after their instantiation.
        """
        
        # let the styler pick out all the style domains so that it
        # controls them properly
        self.styler.register_domains_from_container()
    
    def __call__(self, *args, **kwargs) -> T:
        """Synthesizes a new scene based on the arguments and returns it.

        Override this to specify what arguments your model expects
        and perform any pre-synthesis and post-synthesis state changes
        to the model instance (e.g. select styles, remember the scene).
        """

        # select the styles used for synthesis of this sample
        self.styler.pick_style()

        # run the synthesis pipeline and build the scene
        self.scene = self.call(*args, **kwargs)

        # return the new scene
        return self.scene

    @abc.abstractmethod
    def call(self, *args, **kwargs) -> T:
        """Implements the synthesis process, returns a new scene.
        
        Arguments passed to this method should be prepared in the __call__()
        method. This method should not modify the state of the model instance,
        it should only read it.
        """
        raise NotImplementedError(
            f"Model {self.__class__.__name__} does not have the `call()` "
            "method implemented."
        )
