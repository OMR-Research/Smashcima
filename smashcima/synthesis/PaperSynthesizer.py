from smashcima.scene.AffineSpace import AffineSpace
from smashcima.geometry.Rectangle import Rectangle
import abc


class PaperSynthesizer(abc.ABC):
    """
    Represents an interface to a synthesizer that produces sprites
    with background paper texture
    """

    @abc.abstractmethod
    def synthesize_paper(
        self,
        page_space: AffineSpace,
        placement: Rectangle
    ):
        """Synthesizes a new paper texture

        :page_space The affine space of the page we are synthesizing
        :placement Where inside the page space should the paper be placed
        """
        raise NotImplementedError
