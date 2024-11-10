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
results = []
for line in inputs:
    temp = m.parse(line)
    # Extract necessary data
    seg = []
    t = ''
    for l in temp.splitlines()[:-1]: # End with EOS
        jaconv.
        s = l.split()
        if len(s) == 6 and any(map(char_is_kanji, s[0])): # If there is kanji
            seg.append([s[0], jaconv.kata2hira(s[2])])
            # seg.append([jaconv.kata2hira(s[2]), s[0]])
            t += "{%s|%s}" % (s[0],jaconv.kata2hira(s[2]))
        else:
            seg.append([s[0], s[0]]) 
            t += s[0]
    segments.append(seg)
    results.append(t)

result = ''
for l in results:
    if l == '':
        result += '\n'
    else:
        result += l+'\n'

print(result)
writePath = './result.txt'
with open(writePath, "w") as f:
    f.write(result)