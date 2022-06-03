#!/usr/bin/python
# -*- coding:utf-8 -*-
import requests
from word import *
from typing import List

APP_ID = "6ff9cb88"
APP_KEY = "201bcb60cd31df08961b6a0b8d40be74"


class OxfordDic:
    """
    牛津词典API封装，API文档见
    https://developer.oxforddictionaries.com/documentation
    """
    def __init__(self):
        self.root_url = "https://od-api.oxforddictionaries.com/api/v2"
        self.source_lang = "en-gb"
        self.header = {
            "Accept": "application/json",
            "app_id": APP_ID,
            "app_key": APP_KEY}

    @staticmethod
    def _get_word_entries(res_json) -> List[WordEntries]:
        res_total = []

        def _get_word_sense(data) -> WordSense:
            sub_senses = []
            if data.get("subsenses"):
                for sub in data["subsenses"]:
                    sub_data = {
                        "definitions": tuple(def_ for def_ in sub["definitions"]),
                        "examples": tuple(ex["text"] for ex in sub.get("examples", [{"text": None}]))
                    }
                    sub_senses.append(WordSubSense(**sub_data))
            def_s = data.get("definitions", [])
            if def_s:
                definitions = tuple(
                    def_ for def_ in data.get(
                        "definitions", []))
            else:
                definitions = tuple(
                    def_["text"] for def_ in data.get(
                        "translations", []))
            sense_data = {
                "definitions": definitions,
                "examples": tuple(ex["text"] for ex in data.get("examples", [{"text": None}])),
                "synonyms": tuple(sy["text"] for sy in data.get("synonyms", [{"text": None}])),
                "subsenses": tuple(sub_senses),
                "constructions": tuple(co["text"] for co in data.get("constructions", [{"text": None}])),
                "feature": data.get("grammaticalFeatures", None)  # todo 待详细化
            }
            return WordSense(**sense_data)
        for res_data in res_json:
            res_entries = WordEntries(res_data["id"])

            lexical_entries = res_data["lexicalEntries"]
            for entry in lexical_entries:
                word_id = getWordId(entry["lexicalCategory"]["id"])
                derivatives = tuple(de["text"] for de in entry.get(
                    "derivatives", [{"text": None}]))
                phrases = tuple(ph["text"]
                                for ph in entry.get("phrases", [{"text": None}]))

                for sig_entry in entry["entries"]:
                    word_pronunciations = []
                    for pronunciation in sig_entry["pronunciations"]:
                        phoneticSpelling = pronunciation["phoneticSpelling"]
                        audio = pronunciation["audioFile"]
                        detail = pronunciation["dialects"]
                        word_pronunciations.append(
                            {"phoneticSpelling": phoneticSpelling, "audio": audio, "detail": detail})
                    entry_data = {
                        "text": res_data["id"],
                        "wordId": word_id,
                        "senses": tuple(
                            _get_word_sense(se) for se in sig_entry["senses"]),
                        "derivatives": derivatives,
                        "phrases": phrases}
                    word_entry = WordEntry(**entry_data)
                    res_entries.add_data(word_id, word_entry)
            res_total.append(res_entries)
        return res_total

    def fetch_entries(self, word) -> List[WordEntries]:
        """获取单词详情，内容包含例句含义词性"""
        url = self.root_url + f"/entries/{self.source_lang}/{word}"
        res_json = requests.get(url, headers=self.header).json()
        return self._get_word_entries(res_json["results"])

    def fetch_words(self, word) -> List[WordEntries]:
        """通过变形找到原词以及它们的信息"""
        url = self.root_url + f"/words/{self.source_lang}?q={word}"
        res_json = requests.get(url, headers=self.header).json()
        return self._get_word_entries(res_json["results"])

    def fetch_translations(self, word, target_lang) -> List[WordEntries]:
        """获取翻译词信息"""
        url = self.root_url + \
            f"/translations/{self.source_lang}/{target_lang}/{word}?strictMatch=false"
        res_json = requests.get(url, headers=self.header).json()
        return self._get_word_entries(res_json["results"])

    def fetch_sentences(self, word) -> WordEntries:
        url = self.root_url + f"/sentences/{self.source_lang}/{word}"
        res_json = requests.get(url, headers=self.header).json()
        res_data = WordEntries(word)
        # todo "grammaticalFeatures"
        for res in res_json["results"]:
            for entry in res["lexicalEntries"]:
                word_id = getWordId(entry["lexicalCategory"]["id"])
                res_data.add_data(word_id, tuple(sentence["text"] for sentence in entry["sentences"]))
        return res_data

    def fetch_lemmas(self, word) -> WordEntries:
        url = self.root_url + f"/lemmas/{self.source_lang}/{word}"
        res_json = requests.get(url, headers=self.header).json()
        res_data = WordEntries(word)
        for res in res_json["results"]:
            for entry in res["lexicalEntries"]:
                word_id = getWordId(entry["lexicalCategory"]["id"])
                inflectionOf = entry["inflectionOf"][0]["text"]
                if len(entry["inflectionOf"]) > 1:
                    print("error")  # todo
                res_data.add_data(word_id, inflectionOf)
        return res_data

    def fetch_thesaurus(self, word, mode="antonyms") -> WordEntries:
        if mode != "antonyms" and mode != "synonyms":
            raise TypeError("the mode must be 'antonyms' or 'synonyms'")
        url = self.root_url + f"/thesaurus/{self.source_lang}/{word}?fields={mode}"
        res_json = requests.get(url, headers=self.header).json()
        if res_json.get("error"):
            return WordEntries(word)
        res_data = WordEntries(word)
        for res in res_json["results"]:
            for entry in res["lexicalEntries"]:
                word_id = getWordId(entry["lexicalCategory"]["id"])
                for inner_entry in entry.get("entries", []):
                    if not inner_entry.get("senses"):
                        continue
                    for word in inner_entry["senses"]:
                        res_word = tuple(wd["text"] for wd in word["antonyms"])
                        res_data.add_data(word_id, res_word)
        return res_data

    def fetch_inflections(self, word) -> WordEntries:
        """获取单词的其它形式"""
        url = self.root_url + \
            f"/inflections/{self.source_lang}/{word}?strictMatch=false"
        res_json = requests.get(url, headers=self.header).json()
        res_data = WordEntries(word)
        for inflected_data in res_json["results"][0]["lexicalEntries"]:
            word_id = getWordId(inflected_data["lexicalCategory"]["id"])
            inflected_form = tuple(form["inflectedForm"]
                                   for form in inflected_data["inflections"])
            res_data.add_data(word_id, inflected_form)
        return res_data

    def fetch_search(self, word, *, mode="fuzzy", target_lang=None):
        """
        匹配单词
        mode：
        "translations"：查找给定单词的可能翻译
        "fuzzy"：模糊匹配给定的文本字符串
        "thesaurus"：模糊匹配给定的文本字符串(不知道啥区别)
        """
        if mode == "translations":
            if target_lang:
                add_url = "/search/translations/{source_lang}/" + \
                    target_lang + "?q={word}"
            else:
                raise TypeError(f"缺少目标语言target_lang")
        elif mode == "fuzzy":
            add_url = "/search/{source_lang}?q={word}"
        elif mode == "thesaurus":
            add_url = "/search/thesaurus/{source_lang}?q={word}"
        else:
            raise TypeError(f"没有这样的模式{mode}")
        url = self.root_url + \
            add_url.format(source_lang=self.source_lang, word=word)
        res_json = requests.get(url, headers=self.header).json()
        res_data = []
        print(res_json)
        for res_match in res_json["results"]:
            res_data.append({"word": res_match["word"],
                             "score": res_match["score"],
                             "mode": res_match["matchType"]})
        return res_data


if __name__ == "__main__":
    tt = OxfordDic()
    a = tt.fetch_inflections("get")
    print(a)
