import xml.etree.ElementTree as ET
from ..scene.semantic.Score import Score
from ..scene.semantic.Part import Part
from ..scene.semantic.Measure import Measure
from ..scene.semantic.Note import Note
from ..scene.semantic.RestSemantic import RestSemantic
from ..scene.semantic.MeasureRest import MeasureRest
from ..scene.semantic.TypeDuration import TypeDuration
from ..scene.semantic.Pitch import Pitch
from ..scene.semantic.AttributesChange import AttributesChange
from ..scene.semantic.KeySignature import KeySignature
from ..scene.semantic.Clef import Clef
from ..scene.semantic.ClefSign import ClefSign
from ..scene.semantic.TimeSignature import TimeSignature, TimeSymbol
from ..scene.semantic.Chord import Chord
from ..scene.semantic.StemValue import StemValue
from ..scene.semantic.BeamedGroup import BeamedGroup
from ..scene.semantic.BeamValue import BeamValue
from ..scene.semantic.AccidentalValue import AccidentalValue
from typing import List, TextIO, Optional, Dict, Tuple, Union
from fractions import Fraction
from dataclasses import dataclass, field
from pathlib import Path
import io


@dataclass
class _ScoreState:
    new_system_measures: List[Measure] = field(default_factory=list)
    "Measures that should be placed on new systems (line breaks)"

    new_page_measures: List[Measure] = field(default_factory=list)
    "Measures that should be placed on new pages (page breaks)"


@dataclass
class _PartState:
    part_id: str
    "MusicXML ID of the currently parsed part, used for error localization"

    part: Part
    "The part that is being constructed as it's being parsed"

    measure_number: Optional[str] = None
    "Currently parsed measure number, or None if it was not yet defined/parsed"

    divisions: Optional[int] = None
    "Number of MusicXML duration units per quarter note"

    beats_per_measure: Optional[int] = None
    "How many beats there are in one measure"

    beat_type: Optional[int] = None
    "Type of the beat (inverse of the beat fractional duration)"

    beat_fractional_duration: Optional[Fraction] = None
    "How many quarter notes does a single beat take up"

    measure_fractional_duration: Optional[Fraction] = None
    "How many quarter notes does a whole measure take up"


@dataclass
class _MeasureState:
    part_state: _PartState
    "Reference to the part state"

    measure: Measure
    "The measure that is being constructed as it's being parsed"

    last_chord: Optional[Chord] = None
    """Last chord whose note was constructed. If we hit the <chord/> element,
    then this chord should be extended. Otherwise a new one should be created."""

    fractional_measure_onset: Fraction = Fraction(0, 1) # zero
    """How many quarter notes from the start of the measure are we currently"""

    current_beamed_group: Optional[BeamedGroup] = None
    "The beamed group that is currently being constructed."

    def seek_forward(self, fractional_duration: Fraction):
        self.fractional_measure_onset += fractional_duration

        # we may know measure fractional duration, but we don't check for its
        # overstepping, as measures may contain more notes than their
        # pre-defined duration from the time signature and that's ok
    
    def seek_backup(self, fractional_duration: Fraction):
        self.fractional_measure_onset -= fractional_duration
        
        # we check that we don't have negative onset and clamp to zero
        if self.fractional_measure_onset < 0:
            self.fractional_measure_onset = Fraction(0, 1) # zero


IGNORED_MEASURE_ELEMENTS = set([
    # https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/measure-partwise/
    "direction", "harmony", "figured-bass", "sound", "listening",
    "grouping", "link", "bookmark", "barline"
])


class MusicXmlLoader:
    """Loads MusicXML into the scene data model"""

    def __init__(self, errout: Optional[TextIO] = None):
        self._errout = errout or io.StringIO()
        "Print errors and warnings here"

        self._score_state: Optional[_ScoreState] = None
        "Score state, not None when parsing a score"
        
        self._part_state: Optional[_PartState] = None
        "Part state, not None when parsing a part"

        self._measure_state: Optional[_MeasureState] = None
        "Measure state, not None when parsing a measure"

    def _error(self, *values):
        if self._part_state:
            p = self._part_state.part_id
            m = self._part_state.measure_number
            o = self._measure_state.fractional_measure_onset
            header = f"[ERROR][P:{p} M:{m} O:{o}]:"
        else:
            header = f"[ERROR]:"
        print(header, *values, file=self._errout)

    def load_file(self, path: Union[Path, str]) -> Score:
        """Loads a score from a MusicXML file"""
        # TODO: handle .mxl files as well
        with open(str(path), "r") as file:
            return self.load(ET.parse(file))

    def load_xml(self, xml: str) -> Score:
        fake_file = io.StringIO(xml)
        return self.load(ET.parse(fake_file))

    def load(self, tree: ET.ElementTree) -> Score:
        """Loads a score from a MusicXML XML tree"""
        score_partwise_element = tree.getroot()
        if score_partwise_element.tag != "score-partwise":
            raise Exception("The loader expects the <score-partwose> " + \
                            "tag to be the root of the file.")
        
        score = self._load_score_partwise(score_partwise_element)
        score.validate()
        return score
    
    def _load_score_partwise(self, score_partwise_element: ET.Element) -> Score:
        assert score_partwise_element.tag == "score-partwise"

        self._score_state = _ScoreState()

        parts: List[Part] = []

        # go through all the parts
        part_list_element = score_partwise_element.find("part-list")
        for score_part_element in part_list_element.findall("score-part"):
            part_id = score_part_element.attrib.get("id")
            if part_id is None:
                raise Exception("<score-part> element is missing an ID.")

            # find the part element
            part_elements = [
                p for p in score_partwise_element.findall("part")
                if p.attrib.get("id") == part_id
            ]
            if len(part_elements) == 0:
                raise Exception(f"Cannot find <part> with ID '{part_id}'.")
            part_element = part_elements[0]

            # and parse it
            part = self._load_part(score_part_element, part_element, part_id)
            parts.append(part)

        # create the part instance
        score = Score(
            parts=parts,
            new_system_measure_indices=set(
                Part.of_measure(m).measures.index(m)
                for m in self._score_state.new_system_measures
            ),
            new_page_measure_indices=set(
                Part.of_measure(m).measures.index(m)
                for m in self._score_state.new_page_measures
            )
        )

        self._score_state = None

        return score
    
    def _load_part(
        self,
        score_part_element: ET.Element,
        part_element: ET.Element,
        part_id: str
    ) -> Part:
        assert score_part_element.tag == "score-part" # part header
        assert part_element.tag == "part" # part measures
        assert score_part_element.attrib["id"] == part_id
        assert part_element.attrib["id"] == part_id

        self._part_state = _PartState(
            part_id=part_id,
            part=Part()
        )

        for measure_element in part_element:
            measure = self._load_measure(measure_element)
            self._part_state.part.append_measure(measure)
        
        part = self._part_state.part
        self._part_state = None

        # set attributes for each event in the part
        part.compute_event_attributes()
        
        return part
    
    def _load_measure(self, measure_element: ET.Element) -> Measure:
        assert measure_element.tag == "measure"
        assert self._part_state is not None

        self._part_state.measure_number = measure_element.attrib.get("number")
        self._measure_state = _MeasureState(
            part_state=self._part_state,
            measure=Measure()
        )

        for element in measure_element:
            if element.tag in IGNORED_MEASURE_ELEMENTS:
                continue
            elif element.tag == "note":
                self._load_note(element)
            elif element.tag == "attributes":
                self._load_attributes(element)
            elif element.tag == "backup":
                self._load_backup(element)
            elif element.tag == "forward":
                self._load_forward(element)
            elif element.tag == "print":
                self._load_print(element)
            else:
                self._error(
                    "Unexpected <measure> element:",
                    element,
                    element.attrib
                )
        measure = self._measure_state.measure
        self._measure_state = None
            
        # ensure that the measure has all semantic staves,
        # even if there are no durables in some of them
        for i in range(0, self._part_state.part.staff_count):
            measure.get_or_create_staff(i + 1)
        
        return measure

    def _load_note(self, note_element: ET.Element):
        assert note_element.tag == "note"
        assert self._part_state is not None
        assert self._measure_state is not None

        # === decode the context ===

        e = _DecodedNoteElement(
            note_element=note_element,
            _part_state=self._part_state
        )
        
        # determine onset
        onset = self._measure_state.fractional_measure_onset \
            if not e.is_chord else \
            self._measure_state.last_chord.get_event().fractional_measure_onset
        
        # determine the current chord instance
        current_chord: Optional[Chord] = None
        if e.is_measure_rest or e.pitch is None:
            self._measure_state.last_chord = None
        else:
            if e.is_chord: # extend old chord
                current_chord = self._measure_state.last_chord
            else: # start a new chord
                current_chord = Chord()
        self._measure_state.last_chord = current_chord # update state

        # load beam information
        # (only the first note in a chord has this information,
        # others don't repeat it, unlike with stems)
        if len(e.beam_values) > 0:
            assert current_chord is not None, \
                "Rests should not start a beamed group"
            if self._measure_state.current_beamed_group is None:
                self._measure_state.current_beamed_group = BeamedGroup()
            self._measure_state.current_beamed_group.add_chord(
                current_chord, e.beam_values
            )
            if self._measure_state.current_beamed_group.is_complete:
                self._measure_state.current_beamed_group = None

        # === modify state ===

        # advance onset (internal clock)
        if not e.is_chord:
            self._measure_state.seek_forward(e.fractional_duration)

        # === emit proper scene object ===

        # right now just ignore grace notes
        # TODO: decode grace notes
        if e.is_grace_note:
            return None

        # handle measure rests
        if e.is_measure_rest:
            assert onset == 0, "Measure rest should begin at 0 onset"
            self._measure_state.measure.add_durable(
                durable=MeasureRest(
                    fractional_duration=e.fractional_duration,
                    display_pitch=e.display_pitch
                ),
                onset=onset,
                staff_number=e.staff_number,
            )
            return
        
        # handle rests
        if e.pitch is None:
            self._measure_state.measure.add_durable(
                durable=RestSemantic(
                    type_duration=e.type_duration,
                    augmentation_dots=e.duration_dots,
                    fractional_duration=e.fractional_duration,
                    display_pitch=e.display_pitch
                ),
                onset=onset,
                staff_number=e.staff_number
            )
            return
        
        # handle notes
        note = Note(
            pitch=e.pitch,
            type_duration=e.type_duration,
            augmentation_dots=e.duration_dots,
            fractional_duration=e.fractional_duration,
            accidental_value=e.accidental_value,
        )
        self._measure_state.measure.add_durable(
            durable=note,
            onset=onset,
            staff_number=e.staff_number
        )

        assert current_chord is not None
        current_chord.add_note(note, e.stem_value)
    
    def _load_attributes(self, attributes_element: ET.Element):
        # https://www.w3.org/2021/06/musicxml40/musicxml-reference/elements/attributes/
        assert attributes_element.tag == "attributes"

        assert self._part_state is not None, \
            "Part state must be initialized before loading <attributes>"
        assert self._measure_state is not None, \
            "Measure state must be initialized before loading <attributes>"
        
        change = AttributesChange()

        # divisions:
        divisions_element = attributes_element.find("divisions")
        if divisions_element is not None:
            self._load_divisions(divisions_element)
        
        # staves
        staves_element = attributes_element.find("staves")
        if staves_element is not None:
            self._part_state.part.staff_count = int(staves_element.text)
        
        # key signature
        key_element = attributes_element.find("key")
        if key_element is not None:
            staff_number = key_element.attrib.get("number")
            fifths = int(key_element.find("fifths").text)
            if staff_number is None:
                for i in range(1, self._part_state.part.staff_count + 1):
                    change.keys[i] = KeySignature(fifths=fifths)
            else:
                change.keys[int(staff_number)] = KeySignature(fifths=fifths)

        # time signature
        time_element = attributes_element.find("time")
        if time_element is not None:
            change.time_signature = self._load_time_signature(time_element)

        # clef
        clef_elements = attributes_element.findall("clef")
        for clef_element in clef_elements:
            staff_number = int(clef_element.attrib.get("number", "1"))
            after_barline = (clef_element.attrib.get("after-barline", "no") == "yes")
            sign = ClefSign(clef_element.find("sign").text.upper())
            line = int(clef_element.find("line").text)
            change.clefs[staff_number] = Clef(
                sign=sign,
                line=line,
                after_barline=after_barline
            )

        # add the attributes change into the measure
        self._measure_state.measure.add_attributes_change(
            change=change,
            onset=self._measure_state.fractional_measure_onset
        )
    
    def _load_divisions(self, divisions_element: ET.Element):
        assert divisions_element.tag == "divisions"
        assert self._part_state is not None

        assert divisions_element.text is not None
        self._part_state.divisions = int(divisions_element.text)

        assert self._part_state.divisions > 0, \
            "<divisions> should be a positive number"
    
    def _load_time_signature(self, time_element: ET.Element) -> TimeSignature:
        assert time_element.tag == "time"
        
        # parse XML tree
        beats_element = time_element.find("beats")
        assert beats_element is not None, \
            "<beats> must be present in <time> element"
        beat_type_element = time_element.find("beat-type")
        assert beat_type_element is not None, \
            "<beat-type> must be present in <time> element"
        
        assert beats_element.text is not None
        assert beat_type_element.text is not None
        
        # extract time signature values
        beats_per_measure = int(beats_element.text) # typically 4, or 3
        assert beats_per_measure > 0
        beat_type = int(beat_type_element.text) # typically 4
        assert beat_type > 0

        # extract time symbol
        symbol = TimeSymbol(
            time_element.attrib.get("symbol", "normal")
        )

        # compute
        beat_fractional_duration = Fraction(1, beat_type) / Fraction(1, 4)
        measure_fractional_duration = beat_fractional_duration * beats_per_measure

        # modify part state
        self._part_state.beats_per_measure = beats_per_measure
        self._part_state.beat_type = beat_type
        self._part_state.beat_fractional_duration = beat_fractional_duration
        self._part_state.measure_fractional_duration = measure_fractional_duration

        return TimeSignature(
            beats=beats_per_measure,
            beat_type=beat_type,
            symbol=symbol
        )
    
    def _load_backup(self, backup_element: ET.Element):
        assert backup_element.tag == "backup"
        assert self._part_state is not None
        assert self._measure_state is not None

        duration_element = backup_element.find("duration")
        assert duration_element is not None, \
            "The <backup> element lacks the <duration> child element"
        assert duration_element.text is not None

        # get the duration
        backup_duration = int(duration_element.text)
        assert backup_duration > 0

        # number of quarter notes
        fractional_duration = Fraction(
            backup_duration,
            self._part_state.divisions
        )

        # modify measure state
        self._measure_state.seek_backup(fractional_duration)
    
    def _load_forward(self, forward_element: ET.Element):
        assert forward_element.tag == "forward"
        assert self._part_state is not None
        assert self._measure_state is not None

        duration_element = forward_element.find("duration")
        assert duration_element is not None, \
            "The <forward> element lacks the <duration> child element"
        assert duration_element.text is not None

        # get the duration
        forward_duration = int(duration_element.text)
        assert forward_duration > 0

        # number of quarter notes
        fractional_duration = Fraction(
            forward_duration,
            self._part_state.divisions
        )

        # modify measure state
        self._measure_state.seek_forward(fractional_duration)
    
    def _load_print(self, print_element: ET.Element):
        assert print_element.tag == "print"
        assert self._score_state is not None
        assert self._measure_state is not None

        # parse line breaks
        if print_element.attrib.get("new-system") == "yes":
            self._score_state.new_system_measures.append(
                self._measure_state.measure
            )
        
        # parse page breaks
        if print_element.attrib.get("new-page") == "yes":
            self._score_state.new_page_measures.append(
                self._measure_state.measure
            )


class _DecodedNoteElement:
    """Decodes the contents of a <note> MusicXML element"""

    def __init__(self, note_element: ET.Element, _part_state: _PartState):
        assert note_element.tag == "note"
        
        self.note_element = note_element
        self._part_state = _part_state

        # decode
        self.is_grace_note, self.is_grace_slash = self._grace()
        self.is_chord = self._chord()
        self.pitch, self.is_measure_rest = self._rest_or_pitch() # None pitch for rests
        self.display_pitch = self._display_pitch() # for rests only
        self.voice_name = self._voice()
        self.type_duration = self._type(self.is_measure_rest) # None for measure rests
        self.time_modification = self._time_modification()
        self.duration_dots = self._dot()
        self.accidental_value = self._accidental()
        self.stem_value = self._stem()
        self.staff_number = self._staff()
        self.beam_values = self._beam()

        self.fractional_duration: Fraction = (
            # use the measure length, or 4 beats as a default if not known
            self._part_state.measure_fractional_duration or Fraction(4, 1)
        ) \
            if self.is_measure_rest \
            else self._decode_fractional_duration(
                type_duration=self.type_duration,
                duration_dots=self.duration_dots,
                time_modification=self.time_modification
            )

    # <grace>
    def _grace(self):
        grace_element = self.note_element.find("grace")
        is_grace_note = grace_element is not None
        is_grace_slash = False
        if is_grace_note:
            if grace_element.attrib.get("slash") == "yes":
                is_grace_slash = True
        return is_grace_note, is_grace_slash
    
    # <chord>
    def _chord(self):
        chord_element = self.note_element.find("chord")
        is_chord = chord_element is not None
        return is_chord

    # <rest> or <pitch>
    def _rest_or_pitch(self) -> Tuple[Optional[Pitch], bool]:
        rest_element = self.note_element.find("rest")
        is_measure_rest = False
        pitch: Optional[Pitch] = None

        if rest_element is not None:
            is_measure_rest = rest_element.attrib.get("measure") == "yes"

        else:
            pitch_element = self.note_element.find("pitch")
            assert pitch_element is not None, \
                "The <note> is not a measure rest, yet is missing <pitch>"
            
            step_element = pitch_element.find("step")
            octave_element = pitch_element.find("octave")
            assert step_element is not None
            assert octave_element is not None
            assert step_element.text is not None
            assert octave_element.text is not None

            step = step_element.text
            octave = octave_element.text

            alter = None
            alter_element = pitch_element.find("alter")
            if alter_element is not None:
                alter = alter_element.text
            
            pitch = Pitch.parse(octave, step, alter)
        
        return pitch, is_measure_rest
    
    # <display-step> and <display-octave> for rests
    def _display_pitch(self) -> Optional[Pitch]:
        rest_element = self.note_element.find("rest")
        if rest_element is None:
            return None
        step_element = rest_element.find("display-step")
        octave_element = rest_element.find("display-octave")
        if step_element is None or octave_element is None:
            return None
        return Pitch.parse(
            octave=octave_element.text,
            step=step_element.text
        )
    
    # <voice>
    def _voice(self) -> Optional[str]:
        voice_element = self.note_element.find("voice")
        voice_name: Optional[str] = None
        if voice_element is not None:
            voice_name = voice_element.text
        return voice_name

    # <type>, missing only for rest measures
    def _type(self, is_measure_rest: bool):
        type_element = self.note_element.find("type")
        type_duration: Optional[TypeDuration] = None
        if type_element is not None:
            type_duration = TypeDuration(type_element.text)
        elif is_measure_rest:
            pass # leave type duration at None
        else:
            raise Exception(
                "Note does not have <type>:" +
                ET.tostring(self.note_element).decode("utf-8")
            )
        return type_duration
    
    # <time-modification> (tuplets rhythm-wise)
    def _time_modification(self) -> Optional[Fraction]:
        # triplet is 3in2 (3 actual in 2 normal notes)
        # which translates to 2/3 = 0.66 times the normal duration
        if self.note_element.find("time-modification") is None:
            return None # no time modification
        actual = self.note_element.find("time-modification/actual-notes").text
        normal = self.note_element.find("time-modification/normal-notes").text
        return Fraction(int(normal), int(actual))
    
    # <dot>
    def _dot(self) -> int:
        return len(self.note_element.findall("dot"))
    
    # <accidental>
    def _accidental(self) -> Optional[AccidentalValue]:
        if self.note_element.find("accidental") is None:
            return None # no accidental
        return AccidentalValue(self.note_element.find("accidental").text)
    
    # <stem>
    def _stem(self) -> Optional[StemValue]:
        stem_element = self.note_element.find("stem")
        if stem_element is None:
            return None # stem orientation is unknown
        if stem_element.text not in ["up", "down", "double", "none"]:
            raise Exception(
                f"Unknown stem type '{stem_element.text}'. " +
                ET.tostring(self.note_element).decode("utf-8")
            )
        return StemValue(stem_element.text)

    # <staff>
    def _staff(self) -> int:
        staff_element = self.note_element.find("staff")
        if staff_element is None:
            return 1
        assert staff_element.text is not None
        staff = int(staff_element.text)
        assert staff >= 1, "Staff number must be 1 or more"
        assert staff <= self._part_state.part.staff_count, \
            "Staff number must not exceed the defined staff count"
        return staff

    # <beam>
    def _beam(self) -> Dict[int, BeamValue]:
        values = {}
        for element in self.note_element.findall("beam"):
            v = BeamValue(element.text)
            n = int(element.attrib.get("number"))
            values[n] = v
        return values

    # TODO: <tied>
    # TODO: <tuplet>

    def _decode_fractional_duration(
        self,
        type_duration: TypeDuration,
        duration_dots: int,
        time_modification: Optional[Fraction]
    ) -> Fraction:
        # first get the number of quarter notes
        fractional_duration = type_duration.to_quarter_multiple()

        # now apply duration dots
        dot_duration = fractional_duration / 2
        for _ in range(duration_dots):
            fractional_duration += dot_duration
            dot_duration /= 2
        
        # finally apply time modification
        if time_modification is not None:
            fractional_duration *= time_modification
        
        return fractional_duration
