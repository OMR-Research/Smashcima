from typing import Dict
from .ImageLayer import ImageLayer


class LayerSet:
    """A group of layers extracted from the scene by the compositor.
    They can be passed through the postprocessor. It's up the implementation
    of the compositor and postprocessor which layers exist and what meaning
    they have, plus how they should be combined to get the final image."""
    
    def __init__(self, layers: Dict[str, ImageLayer]) -> None:
        self.__layers: Dict[str, ImageLayer] = layers
        """The set of layers and their names"""

    def __getitem__(self, name: str) -> ImageLayer:
        return self.__layers[name]
    
    def __setitem__(self, name: str, layer: ImageLayer):
        self.__layers[name] = layer
    
    def __contains__(self, name: str) -> bool:
        return name in self.__layers
