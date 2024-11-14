from dataclasses import dataclass, field
from fractions import Fraction
from ..SceneObject import SceneObject
from .Durable import Durable
from .Event import Event
from .StaffSemantic import StaffSemantic
from .AttributesChange import AttributesChange
from typing import List


@dataclass
class Measure(SceneObject):
    """A measure of music for a single instrument (a single part)"""

    events: List[Event] = field(default_factory=list)
    "Links to all events within this measure"

    staves: List[StaffSemantic] = field(default_factory=list)
    """Links to all staves within this measure"""

    @property
    def first_event(self) -> Event:
        assert self.events[0].fractional_measure_onset == 0, \
            "The first event in the measure does not have 0 onset"
        return self.events[0]

    @staticmethod
    def of_durable(durable: Durable):
        event = Event.of_durable(durable)
        return Measure.of_event(event)

    @classmethod
    def of_event(cls, event: Event):
        return cls.of(event, lambda m: m.events)
    
    @classmethod
    def of_staff(cls, staff: StaffSemantic):
        return cls.of(staff, lambda m: m.staves)
    
    def add_attributes_change(
        self,
        change: AttributesChange,
        onset: Fraction
    ):
        """Adds an attributes change into the measure"""
        event = self.get_or_create_event(onset)
        event.attributes_change = change

    def add_durable(
        self,
        durable: Durable,
        onset: Fraction,
        staff_number: int
    ):
        """Adds a durable into the measure"""
        event = self.get_or_create_event(onset)
        event.durables = [*event.durables, durable]

        staff = self.get_or_create_staff(staff_number)
        staff.durables = [*staff.durables, durable]

    def get_or_create_event(self, onset: Fraction) -> Event:
        """Returns event with the given onset"""
        matches = [e for e in self.events if e.fractional_measure_onset == onset]
        if len(matches) > 1:
            raise Exception("There are multiple events with the same onset!")
        elif len(matches) == 1:
            return matches[0]
        else:
            event = Event(fractional_measure_onset=onset)
            self.events = [*self.events, event]
            self.sort_events_by_onset()
            return event
    
    def sort_events_by_onset(self):
        """Sorts events by onset, ascending"""
        self.events.sort(key=lambda e: e.fractional_measure_onset)
    
    def get_or_create_staff(self, staff_number: int) -> StaffSemantic:
        """Returns staff with the given staff number"""
        matches = [s for s in self.staves if s.staff_number == staff_number]
        if len(matches) > 1:
            raise Exception("There are multiple staves with the same number!")
        elif len(matches) == 1:
            return matches[0]
        else:
            staff = StaffSemantic(staff_number=staff_number)
            self.staves = [*self.staves, staff]
            self.sort_staves_by_number()
            return staff
    
    def sort_staves_by_number(self):
        """Sorts staves by number, ascending"""
        self.staves.sort(key=lambda e: e.staff_number)
