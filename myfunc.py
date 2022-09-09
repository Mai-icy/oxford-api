import oxford
from collections import namedtuple


ox_dic = oxford.OxfordDic()


WordSimpleData = namedtuple(
    "WordSimpleData", [
        "text", "wordId", "phoneticSpelling", "sense"])


class WordSimple(WordSimpleData):
    def __str__(self):
        return f"{self.text}\t{self.wordId.get_abbr()}\t{';'.join(self.sense)}\t/{self.phoneticSpelling}/"


def lookUpWords(word: str):

    words_res_list = ox_dic.fetch_translations(word, "zh")
    for res in words_res_list:
        for id_ in res.keys:
            print(id_)

            for we in res[id_]:
                simple_res = WordSimple(text=word, wordId=id_, phoneticSpelling=we.pronunciations[0].phoneticSpelling,
                                        sense=[','.join(se.definitions) for se in we.senses if se.definitions])
                print(simple_res)


if __name__ == "__main__":
    lookUpWords("test")



