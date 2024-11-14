from dataclasses import dataclass, field
from ..SceneObject import SceneObject
from typing import List, Optional
from .Note import Note
from .Event import Event
from .StemValue import StemValue
from .TypeDuration import TypeDuration


@dataclass
class Chord(SceneObject):
    """Chord is a collection of notes that share one stem. Even a single note
    has a chord, since it needs to encode its stem information here. Musically
    a chord is a group of notes with the same onset and duration though.
    A whole note chord is also a chord, despite not having a stem - there the
    stem has value "none". (this is for consistency)"""
    
    notes: List[Note] = field(default_factory=list)
    "Links to all notes within this chord"

    stem_value: Optional[StemValue] = None
    """What orientation does the stem have.
    If StemValue.none, the stem is missing (e.g. whole note).
    If None, the stem orientation is unknown
    and must be inferred during rendering."""

    @classmethod
    def of_note(cls, note: Note):
        return cls.of(note, lambda c: c.notes)
    
    def get_event(self) -> Event:
        """Returns the event that contains notes in this chord"""
        if len(self.notes) == 0:
            raise Exception("The chord is empty, there are no notes.")
        return Event.of_durable(self.notes[0])
    
    def get_type_duration(self) -> TypeDuration:
        """Returns the type duration of all notes in this chord"""
        if len(self.notes) == 0:
            raise Exception("The chord is empty, there are no notes.")
        return self.notes[0].type_duration
    
    def add_note(self, note: Note, stem_value: Optional[StemValue] = None):
        """Adds a note into the chord with a stem value"""
        # store stem value if missing
        if self.stem_value is None:
            self.stem_value = stem_value

        # validate stem value if present
        if self.stem_value is not None and stem_value is not None:
            assert self.stem_value == stem_value, \
                "All notes in a chord must have the same stem value"
        
        # validate that all the notes share the same event (have the same onset)
        if len(self.notes) > 0:
            event = Event.of_durable(self.notes[0])
            inserted_event = Event.of_durable(note)
            assert event is inserted_event, \
                "All notes in a chord must be in the same event (same onset)"
        
        # validate that all the notes have the same type duration
        if len(self.notes) > 0:
            type_duration = self.notes[0].type_duration
            assert type_duration == note.type_duration, \
                "All notes in a chord must have the same type duration"
        
        # update the list of notes
        notes = [*self.notes, note]
        notes.sort(key=lambda n: n.pitch.get_linear_pitch()) # ascending by pitch
        self.notes = notes
