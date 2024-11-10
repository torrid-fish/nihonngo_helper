import json
from urllib import request

APPID = "dj00aiZpPUlCeUJkTzNRMU1hdSZzPWNvbnN1bWVyc2VjcmV0Jng9NDY-"
URL = "https://jlp.yahooapis.jp/FuriganaService/V2/furigana"


# The range of unicode of kanji
def char_is_kanji(c) -> bool:
    return u'\u4E00' <= c <= u'\u9FFF'
def char_is_hira(c) -> bool:
    return u'\u3040' <= c <= u'\u309F'
def char_is_kata(c) -> bool:
    return u'\u30A0' <= c <= u'\u30FF'
def char_is_kata_or_hira(c) -> bool:
    return char_is_hira(c) or char_is_kata(c)

def yahoo_translate(query):
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Yahoo AppID: {}".format(APPID),
    }
    param_dic = {
      "id": "1234-1",
      "jsonrpc": "2.0",
      "method": "jlp.furiganaservice.furigana",
      "params": {
        "q": query,
        "grade": 1
      }
    }
    params = json.dumps(param_dic).encode()
    req = request.Request(URL, params, headers)
    with request.urlopen(req) as res:
        body = res.read()
    return json.loads(body.decode())


def yahoo_analyze(query):
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Yahoo AppID: {}".format(APPID),
    }
    param_dic = {
      "id": "1234-1",
      "jsonrpc": "2.0",
      "method": "jlp.daservice.parse",
      "params": {
        "q": query
      }
    }
    params = json.dumps(param_dic).encode()
    req = request.Request(URL, params, headers)
    with request.urlopen(req) as res:
        body = res.read()
    return json.loads(body.decode())



def test():
    with open("./content.txt", "r") as f:
        data = f.readlines()

    results = []
    for d in data:
        response = yahoo_analyze(d)
        print(response)
        response = yahoo_translate(d)
        result = ""
        for partial in response["result"]["word"]:
            if partial.get("subword"):
                for subpartial in partial.get("subword"):
                    if all(map(lambda c : char_is_kanji(c), subpartial.get("surface"))):
                        result += "{%s|%s}"%(subpartial.get("surface"),subpartial.get("furigana"))
                    else:
                        result += subpartial.get("surface")
            elif partial.get("furigana"):
                result += "{%s|%s}"%(partial.get("surface"), partial.get("furigana"))
            else:
                result += partial.get("surface")
        results.append(result)

    return results


if __name__ == "__main__":
    results = test()
    for result in results:
        print(result)