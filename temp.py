import requests
from bs4 import BeautifulSoup
import MeCab
import jaconv
import suji
######## Path Configuration ########

openPath = "./content.txt"
writePath = "./result.txt"

####################################

# The range of unicode of kanji
def char_is_kanji(c) -> bool:
    return u'\u4E00' <= c <= u'\u9FFF'
def char_is_hira(c) -> bool:
    return u'\u3040' <= c <= u'\u309F'
def char_is_kata(c) -> bool:
    return u'\u30A0' <= c <= u'\u30FF'
def char_is_kata_or_hira(c) -> bool:
    return char_is_hira(c) or char_is_kata(c)

print("Reading contents from", openPath, "...", end=" ", flush=True)

# Read inputs from openPath
with open(openPath, "r") as f:
    inputs = f.read().splitlines()

print("Done!")

print("MeCab analyzing inputs ...", end=" ", flush=True)

# Apply MeCab to do perform Morphological Analyzer
m = MeCab.Tagger()
segments = []
for line in inputs:
    temp = m.parse(line)
    # Extract necessary data
    seg = []
    for l in temp.splitlines()[:-1]: # End with EOS
        s = l.split()
        if any(map(char_is_kanji, s[0])): # If there is kanji
            # seg.append([s[0], jaconv.kata2hira(s[2])])
            seg.append([jaconv.kata2hira(s[2]), s[0]])
            
        else:
            seg.append([s[0], s[0]]) 
    segments.append(seg)

print("Done!")
print("Sending request to 鈴木君 ...", end=" ", flush=True)

# Query to suzukikunn
query = ''
for seg in segments: 
    for s in seg:
        query += s[0]

# URL to suzukikun(すずきくん)
url = "https://www.gavo.t.u-tokyo.ac.jp/ojad/phrasing/index"
# Data of the POST method
data = {
    "data[Phrasing][text]": query,
    "data[Phrasing][curve]": "advanced",
    "data[Phrasing][accent]": "advanced",
    "data[Phrasing][accent_mark]": "all",
    "data[Phrasing][estimation]": "crf",
    "data[Phrasing][analyze]": "true",
    "data[Phrasing][phrase_component]": "invisible",
    "data[Phrasing][param]": "invisible",
    "data[Phrasing][subscript]": "visible",
    "data[Phrasing][jeita]": "invisible"
}

# Send a POST and receive the website html code
website = requests.post(url, data).text

print("Done!")
print("Processing received data ...", end=" ", flush=True)

# Use beautiful soup to parse received html
soup = BeautifulSoup(website, "html.parser")
# Fetch the required tags, which are phrasing_text
phrasingTexts = soup.findAll("div", attrs={"class": "phrasing_text"})

accents = []
# Since suzukikun will parse a sentence into several parts, we need to merge them back
for d in phrasingTexts:
    # Fetch processed data
    temp = d.find_all("span", recursive= False)
    datas = []
    for p in temp:
        # Check accent mark (we don't use unvoiced)
        accent = 0
        if p['class'][0] == 'accent_plain': accent = 1
        elif p['class'][0] == 'accent_top': accent = 2
        datas.append({'text': p.get_text(), 'accent': accent})
    
    accents += datas

print("Done!")

# Segment words (to find number corresponding pairs)
m = MeCab.Tagger("-Owakati")
result = ''
for i in accents: 
    result += i['text']
result = m.parse(result).split()
origin = ''
for seg in segments:
    for s in seg:
        origin += s[0]
origin = m.parse(origin).split()

# Pairing
# pair = [-1] * len(result) # This will record the corresponding chunck of origin
# j = 0
# for i in range(len(result)):
#     if result[i] == origin[j]:
#         pair[i] = j
#         j += 1
#     else:
#         seeKataOrHina = char_is_kata_or_hira(origin[j])
#         temp = j + 1
#         while not seeKataOrHina and temp < len(origin):
#             if result[i] == origin[temp]:
#                 pair[i] = temp
#                 j = temp + 1
#                 break
#             seeKataOrHina = char_is_kata_or_hira(origin[temp])
#             temp += 1

print(origin)
print(result)
# print(pair)
