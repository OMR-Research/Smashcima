import abc


class Column(abc.ABC):
    """Public interface of a layout column"""
    
    # NOTE: The construction of the glyph is not codified, because each one
    # might be constructed in a different manner. What matters here is the
    # methods used by the layout synthesizer to position and space out
    # all the columns.

    def __init__(self):
        self.time_position = 0
        "Where on the staff (staves) is this column placed"
        
        self.width = 0
        "Total width in millimeters of the column"
        
        self.left_width = 0
        "Width left of the origin vertical line"

        self.right_width = 0
        "Width right of the origin vertical line"

        self.flex_grow = 1
        "How much does this column grow when stretched in relation to others"

        self.flex_shrink = 1
        "How much does this column get shrunk when the system is overflowing"

    @abc.abstractmethod
    def position_glyphs(self):
        """Called to place glyphs onto staves based on the current time_position"""
        raise NotImplementedError

    @abc.abstractmethod
    def recalculate_dimensions(self):
        """Should be called at the end of glyph positioning to update width values"""
        raise NotImplementedError

    @abc.abstractmethod
    def detach(self):
        """Removes the column from the scene"""
        raise NotImplementedError
