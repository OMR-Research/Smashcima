from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Union


STEP_ORDER = ["C", "D", "E", "F", "G", "A", "B"]


class Octave(int, Enum):
    """Octave number of the scientific picth notation"""
    # https://www.w3.org/2021/06/musicxml40/musicxml-reference/data-types/octave/
    o0 = 0
    o1 = 1
    o2 = 2
    o3 = 3
    o4 = 4
    o5 = 5
    o6 = 6
    o7 = 7
    o8 = 8
    o9 = 9


class Step(str, Enum):
    """Step name of the scientific pitch notation"""
    # https://www.w3.org/2021/06/musicxml40/musicxml-reference/data-types/step/
    C = "C"
    D = "D"
    E = "E"
    F = "F"
    G = "G"
    A = "A"
    B = "B"


class Alter(int, Enum):
    """Semitone alter number (based on MusicXML)"""
    # https://www.w3.org/2021/06/musicxml40/musicxml-reference/data-types/semitones/
    flat = -1
    none = 0
    sharp = 1


@dataclass
class Pitch:
    """Represents an audible pitch in the scientific pitch notation."""
    # https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/pitch/
    octave: Octave
    step: Step
    alter: Alter = field(default=Alter.none)

    @staticmethod
    def parse(octave: str, step: str, alter: Optional[str] = None) -> "Pitch":
        return Pitch(
            octave=Octave(int(octave)),
            step=Step(step),
            alter=Alter.none if alter is None else Alter(int(alter))
        )
    
    def get_linear_pitch(self, with_alters=False) -> Union[int, float]:
        """Converts the pitch object into a number where 0 is A0 note
        and then it increases by one for each tone. If you include alters,
        the returned value is a float with +-0.5 based on the alter."""
        step_index = STEP_ORDER.index(self.step.value)
        linear_pitch = self.octave.value * len(STEP_ORDER) + step_index
        if with_alters:
            if self.alter == Alter.sharp:
                linear_pitch += 0.5
            elif self.alter == Alter.flat:
                linear_pitch -= 0.5
        return linear_pitch
    
    @staticmethod
    def from_linear_pitch(linear_pitch: int) -> "Pitch":
        """Reconstructs a pitch object from an integer linear pitch"""
        assert type(linear_pitch) is int, \
            "Float reconstructions are not supported"
        step_index = linear_pitch % len(STEP_ORDER)
        octave = linear_pitch // len(STEP_ORDER)
        return Pitch(Octave(octave), Step(STEP_ORDER[step_index]))
    
    def __repr__(self) -> str:
        suffix = ""
        if self.alter == Alter.sharp:
            suffix += "+1"
        if self.alter == Alter.flat:
            suffix += "-1"
        return f"Pitch({self.step.value}{self.octave.value}{suffix})"


if __name__ == "__main__":
    # Prints out all the pitches and their linear representation
    # (linear representation is used for staff positioning and conversions)
    print("Pitches and their linear representation:")
    for octave in range(9):
        for step in STEP_ORDER:
            pitch = Pitch.parse(octave, step)
            linear_pitch = pitch.get_linear_pitch()
            assert pitch.octave == Pitch.from_linear_pitch(linear_pitch).octave
            assert pitch.step == Pitch.from_linear_pitch(linear_pitch).step
            print(
                repr(pitch),
                str(linear_pitch).zfill(2),
                end=" | "
            )
        print()
