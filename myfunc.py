import time

import oxford
from collections import namedtuple
from typing import List

ox_dic = oxford.OxfordDic()

WordSimpleData = namedtuple(
    "WordSimpleData", [
        "text", "wordId", "phoneticSpelling", "sense"])


class WordSimple(WordSimpleData):
    sense_limit = None

    def __str__(self):
        return f"{self.text}\t{self.wordId.get_abbr()}\t{';'.join(self.sense)}\t/{self.phoneticSpelling}/"

    def set_sense_limit(self, max_num: int):
        self.sense_limit = max_num

    def add_sense(self, sense):
        if self.sense_limit and len(self.sense) == self.sense_limit:
            return

        self.sense.extend(sense)

        if self.sense_limit:
            while len(self.sense) > self.sense_limit:
                self.sense.pop()


def lookUpWordsSimple(word: str, *, sense_limit=3):
    """查单词，并获得简单释义和音标以及词性"""
    result_simple_words = []
    lemmas_words = ox_dic.fetch_lemmas(word)

    if not any(word in lemmas_words[key] for key in lemmas_words.keys):
        word = lemmas_words[lemmas_words.keys[0]][0]

    words_res_list = ox_dic.fetch_translations(word, "zh")

    res_entries = words_res_list[0]
    for entry in words_res_list[1:]:
        res_entries += entry

    # print(res.keys)
    for id_ in res_entries.keys:
        # print(id_)
        if not res_entries[id_][0].senses[0].definitions:
            continue

        simple_res_dict = {"text": word, "wordId": id_,
                           "phoneticSpelling": res_entries[id_][0].pronunciations[0].phoneticSpelling, "sense": []}
        simple_res = WordSimple(**simple_res_dict)
        simple_res.set_sense_limit(sense_limit)
        simple_res.add_sense([','.join(se.definitions) for se in res_entries[id_][0].senses if se.definitions])

        if len(res_entries[id_]) == 1:
            # print(simple_res)
            result_simple_words.append(simple_res)
            continue

        for wd in res_entries[id_][1:]:
            if not wd.senses[0].definitions:
                continue

            pronunciation = wd.pronunciations[0].phoneticSpelling
            if pronunciation == simple_res.phoneticSpelling:
                simple_res.add_sense(','.join(se.definitions) for se in wd.senses if se.definitions)
            else:
                # print(simple_res)
                result_simple_words.append(simple_res)
                simple_res_dict = {"text": word, "wordId": id_,
                                   "phoneticSpelling": wd.pronunciations[0].phoneticSpelling, "sense": []}
                simple_res = WordSimple(**simple_res_dict)
                simple_res.set_sense_limit(sense_limit)
                simple_res.add_sense(','.join(se.definitions) for se in wd.senses if se.definitions)
        # print(simple_res)
        result_simple_words.append(simple_res)
    return result_simple_words


def print_to_str(simple_words: List[WordSimple]):
    ps_dict = {}
    word = simple_words[0].text

    for wd in simple_words:
        if wd.phoneticSpelling not in ps_dict:
            ps_dict[wd.phoneticSpelling] = [wd]
        else:
            ps_dict[wd.phoneticSpelling].append(wd)

    res = ""

    for ps in ps_dict:
        res_text_wd = f"{word}\t"

        res_text_wd += "||".join((simple_wd.wordId.get_abbr() + "\t" + ';'.join(simple_wd.sense))
                                 for simple_wd in ps_dict[ps])

        res += res_text_wd + "\t/" + ps + "/ \n"
    return res.strip()


def main(w):
    simple = lookUpWordsSimple(w)
    res_ = print_to_str(simple)
    return res_


if __name__ == "__main__":
    # res1 = lookUpWordsSimple("eat")
    #
    # for i in res1:
    #     print(i)
    #
    # print_to_str(res1)
    print(main("content"))
