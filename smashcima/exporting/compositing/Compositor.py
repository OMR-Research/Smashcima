from abc import ABC, abstractmethod

from smashcima.scene.ViewBox import ViewBox

from ..image.ImageLayer import ImageLayer


class Compositor(ABC):
    """Represents the pipeline that extracts layers from the scene,
    calls the postprocessor and combines those layers into one image.
    Implement this interface to define a specific pipeline."""
    
    @abstractmethod
    def run(self, view_box: ViewBox, dpi: float) -> ImageLayer:
        """Composits the entire scene into an image layer from the perspective
        of the provided view box at the requested DPI"""
        raise NotImplementedError
