#!/usr/bin/python
# -*- coding:utf-8 -*-
from enum import Enum
from collections import namedtuple

__all__ = [
    "WordId",
    "getWordId",
    "WordEntries",
    "WordEntry",
    "WordSense",
    "WordSubSense",
    "WordPronounce",
    "showWordEntries"]


class WordId(Enum):
    NULL = -1
    NOUN = 0
    PRONOUN = 1
    ADJECTIVE = 2
    ADVERB = 3
    VERB = 4
    NUMERAL = 5
    ARTICLE = 6
    PREPOSITION = 7
    CONJUNCTION = 8
    INTERJECTION = 9
    OTHER = 10

    def get_abbr(self):
        abbrs = ["n.", "pron.", "adj.", "adv.", "v.", "num.", "art.", "prep.", "conj.", "int.", "other"]
        return abbrs[self.value]


def getWordId(id_text: str):
    try:
        res_id = getattr(WordId, id_text.upper())
    except AttributeError:
        res_id = WordId(10)
    return res_id


class WordEntries:
    def __init__(self, word_text: str):
        self.word = word_text
        self.keys = []

    def __setitem__(self, key, value):
        if isinstance(key, int):
            setattr(self, str(WordId(key)), value)
            self.keys.append(WordId(key))
        elif isinstance(key, WordId):
            setattr(self, str(key), value)
            self.keys.append(key)
        else:
            raise TypeError("The key's type must be 'WordId' or 'int'")

    def __getitem__(self, item):
        if isinstance(item, int):
            return getattr(self, str(WordId(item)))
        elif isinstance(item, WordId):
            return getattr(self, str(item))
        else:
            raise TypeError("The key's type must be 'WordId' or 'int'")

    def __str__(self):
        def cut_down_length(text):
            return text[:150] + " ..." if len(text) > 200 else text
        res_txt = "<WordEntries(\n"
        for id_ in self.keys:
            res_txt += str(id_) + ":\n"

            res_txt += "\n".join([cut_down_length(str(i)) for i in self[id_]]) + "\n"
        res_txt += ")>"
        return res_txt

    def __add__(self, other):
        if isinstance(other, WordEntries):
            if not self.word == other.word:
                raise ValueError("The words must be the same")
        res_entries = WordEntries(self.word)
        for key in self.keys:
            for data_ in self[key]:
                res_entries.add_data(key, data_)
        for key in other.keys:
            for data_ in other[key]:
                res_entries.add_data(key, data_)
        return res_entries

    def add_data(self, word_id, data):
        if not hasattr(self, str(word_id)):
            self[word_id] = []
        self[word_id].append(data)


WordSenseData = namedtuple(
    "WordSense", [
        "definitions", "feature", "examples", "constructions", "subsenses", "synonyms"])

WordPronounceData = namedtuple(
    "WordPronounce", [
        "phoneticSpelling", "audio", "detail"])

WordEntryData = namedtuple(
    "WordEntry", [
        "text", "wordId", "senses", "derivatives", "phrases", "pronunciations"])

WordSubSenseData = namedtuple("WordSubSense", ["definitions", "examples"])


class WordEntry(WordEntryData):
    def __str__(self):
        return f"<WordEntry(text='{self.text}', wordId={self.wordId}, senses=[{len(self.senses)}])>"

    def __add__(self, other):
        if isinstance(other, WordEntry):
            if not self.text == other.text:
                raise ValueError("The words must be the same")
            res_entries = WordEntries(self.text)
            res_entries.add_data(other.wordId, other)
            res_entries.add_data(self.wordId, self)
            return res_entries
        else:
            raise ValueError("WordEntry can only add to WordEntry")


class WordSense(WordSenseData):
    def __str__(self):
        return f"<WordSense(definitions=({len(self.definitions)}), examples=({len(self.examples)}))>"


class WordSubSense(WordSubSenseData):
    def __str__(self):
        # def_text = self.definitions[0] if self.definitions else None
        return f"<WordSubSense(definitions=({len(self.definitions)}), examples=({len(self.examples)}))>"


class WordPronounce(WordPronounceData):
    def __str__(self):
        return f"<WordPronounce(phoneticSpelling=('{self.phoneticSpelling}'), audio=('{self.audio.split('/')[-1]}')" \
               f", detail=({self.detail[0]}))>"


def showWordEntries(entries: WordEntries):
    for key in entries.keys:
        print(entries[key])


if __name__ == "__main__":
    pass
