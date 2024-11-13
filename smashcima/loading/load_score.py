from pathlib import Path
from typing import Optional, TextIO, Union

from smashcima.scene.semantic.Score import Score

from .MusicXmlLoader import MusicXmlLoader


def load_score(
    file: Union[Path, str, None] = None,
    data: Union[bytes, str, None] = None,
    format: Optional[str] = None,
    soft_errors_output: Optional[TextIO] = None
) -> Score:
    """Loads a file with music notation into a Smashcima Score object.
    
    :param file: Path to a file with musical content (e.g. './my_file.musicxml')
    :param data: Musical contents as a bytes or string (e.g. MusicXML
        file contents)
    :param format: In what format is the musical content (file suffix,
        including the period, i.e. '.musicxml')
    :param soft_errors_output: Optional output for logging soft errors.
    :returns: The parsed score object
    """

    # get format from the suffix
    if file is not None and format is None:
        format = Path(str(file)).suffix or None

    # there must be some annotation format specified
    if format is None:
        raise Exception(
            "Annotation format cannot be deduced. " + \
            "You need to specify it explicitly."
        )
    
    # either file or data must be provided
    if file is None and data is None:
        raise Exception("Either file path or file data must be provided")

    # select parser by format
    if format in [".mxl"]:
        raise Exception("Compressed MusicXML format is not yet supported")
    elif format in [".musicxml"]:
        mxl_loader = MusicXmlLoader(errout=soft_errors_output)
        if data is not None:
            if type(data) is bytes:
                data = data.decode("utf-8")
            return mxl_loader.load_xml(data)
        else:
            return mxl_loader.load_file(file)
    
    raise Exception(f"Format {format} cannot be loaded")
