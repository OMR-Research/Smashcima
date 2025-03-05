from .ImageLayer import ImageLayer
from .LayerSet import LayerSet
from .Postprocessor import Postprocessor


class NullPostprocessor(Postprocessor):
    """Applies no postprocessing filters."""
    
    def process_extracted_layers(
        self,
        layers: LayerSet,
        dpi: float
    ) -> LayerSet:
        return layers
    
    def process_final_layer(
        self,
        final_layer: ImageLayer,
        dpi: float
    ) -> ImageLayer:
        return final_layer
