from abc import ABC, abstractmethod

from ..image.ImageLayer import ImageLayer
from ..image.LayerSet import LayerSet


class Postprocessor(ABC):
    """Applies postprocessing filters in various stages of the image
    composition process."""
    
    @abstractmethod
    def process_extracted_layers(
        self,
        layers: LayerSet
    ) -> LayerSet:
        """Processes layers separately right after they are extracted
        from the scene."""
        raise NotImplementedError
    
    @abstractmethod
    def process_final_layer(
        self,
        final_layer: ImageLayer
    ) -> ImageLayer:
        """Processes the final composed layer before it exits the compositor."""
        raise NotImplementedError
