import abc

from smashcima.geometry.Transform import Transform


class StaffCoordinateSystem(abc.ABC):
    @abc.abstractmethod
    def get_transform(
        self,
        pitch_position: float,
        time_position: float
    ) -> Transform:
        """Converts stafflines coordinates (pitch position in staffspace/2 units,
        where zero is the middle staffline, 4 is the topmost staffline;
        time position in milimeters from the begining of the staff)
        to a transform to a specific place (and possibly rotation)
        on the staff."""
        # TODO: maybe time position should be in different units than
        # millimeters, this needs to be inspected. How does staffline
        # spacing affect temporal spacing of notes. Are they related? How?
        raise NotImplementedError
