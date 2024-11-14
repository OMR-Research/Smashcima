import unittest
from dataclasses import dataclass
from typing import List, Optional

from smashcima.scene.SceneObject import (SceneObject,
                                         SceneRelationshipResolutionException)


@dataclass
class Letter(SceneObject):
    character: str


@dataclass
class Word(SceneObject):
    text: str
    letters: List[Letter]

    @staticmethod
    def build(text: str) -> "Word":
        return Word(
            text=text,
            letters=[
                Letter(character) for character in text
            ]
        )

    # NOTE: This is how you should implement explicit query methods:

    @classmethod
    def of_letter(cls, letter: Letter):
        return cls.of(letter, lambda w: w.letters)

    @classmethod
    def of_letter_or_none(cls, letter: Optional[Letter]):
        return cls.of_or_none(letter, lambda w: w.letters)
    
    @classmethod
    def many_of_letter(cls, letter: Letter):
        return cls.many_of(letter, lambda w: w.letters)


class SceneObjectRelationshipQueriesTest(unittest.TestCase):
    def test_standalone_letter_has_no_word(self):
        letter = Letter("A")

        # raw core function
        assert Word._of_impl(letter, lambda w: w.letters) == ([], "letters")

        # genereal query functions
        assert Word.many_of(letter, lambda w: w.letters) == []
        assert Word.of_or_none(letter, lambda w: w.letters) is None
        with self.assertRaises(SceneRelationshipResolutionException):
            Word.of(letter, lambda w: w.letters)

        # explicit child query functions
        assert Word.many_of_letter(letter) == []
        assert Word.of_letter_or_none(letter) is None
        with self.assertRaises(SceneRelationshipResolutionException):
            Word.of_letter(letter)

    def test_word_letter_has_a_word(self):
        word = Word.build("ABCD")
        letter = word.letters[0]

        # raw core function
        assert Word._of_impl(letter, lambda w: w.letters) == ([word], "letters")

        # genereal query functions
        assert Word.many_of(letter, lambda w: w.letters) == [word]
        assert Word.of_or_none(letter, lambda w: w.letters) is word
        assert Word.of(letter, lambda w: w.letters) is word

        # explicit child query functions
        assert Word.many_of_letter(letter) == [word]
        assert Word.of_letter_or_none(letter) is word
        assert Word.of_letter(letter) is word

    def test_letter_in_many_words(self):
        word = Word.build("ABCD")
        word_ab = Word("AB", letters=word.letters[0:2])
        word_bc = Word("BC", letters=word.letters[1:3])
        letter = word.letters[1]
        assert letter.character == "B"

        # the letter "B" is in 3 words: ABCD, AB, BC
        expected_words = [word, word_ab, word_bc]

        # raw core function
        assert Word._of_impl(letter, lambda w: w.letters) \
            == (expected_words, "letters")
        
        # genereal query functions
        assert Word.many_of(letter, lambda w: w.letters) == expected_words
        with self.assertRaises(SceneRelationshipResolutionException):
            Word.of_or_none(letter, lambda w: w.letters)
        with self.assertRaises(SceneRelationshipResolutionException):
            Word.of(letter, lambda w: w.letters)
        
        # explicit child query functions
        assert Word.many_of_letter(letter) == expected_words
        with self.assertRaises(SceneRelationshipResolutionException):
            Word.of_letter_or_none(letter)
        with self.assertRaises(SceneRelationshipResolutionException):
            Word.of_letter(letter)

    def test_null_subject_is_handled(self):
        # This behaviour is useful when chaining multiple steps
        # together since we would like null coalescence if None is allowed.
        # Otherwise throw a ValueError for invalid argument passed in.
        
        # when asking for one existing linker, it makes no sence to accept
        # None even if we chain calls
        with self.assertRaises(ValueError):
            Word.of(None, lambda w: w.letters)
        
        # when asking for one that might exist or not, if we hit None early,
        # then it definitely does not exist and we chain the None along
        assert Word.of_or_none(None, lambda w: w.letters) is None

        # Asking for many cannot be chained, since it returns a list,
        # therefore we fail with an exception.
        with self.assertRaises(ValueError):
            Word.many_of(None, lambda w: w.letters)
