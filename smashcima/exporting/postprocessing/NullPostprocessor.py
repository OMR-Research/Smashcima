from ..image.ImageLayer import ImageLayer
from ..image.LayerSet import LayerSet
from .Postprocessor import Postprocessor


class NullPostprocessor(Postprocessor):
    """Applies no postprocessing filters."""
    
    def process_extracted_layers(
        self,
        layers: LayerSet
    ) -> LayerSet:
        return layers
    
    def process_final_layer(
        self,
        final_layer: ImageLayer
    ) -> ImageLayer:
        return final_layer
