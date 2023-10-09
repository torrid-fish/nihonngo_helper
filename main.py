import requests
from bs4 import BeautifulSoup

# Read in text that need to be processed
openPath = './content.txt'
with open(openPath, "r") as f:
    inputs = f.read()

# Preprocess of input string, chunk it into the form that starts from kanji(漢字)
# For example, we won't send the request like this:
#
#       "文部科学省が公表した審査結果の東北大学の箇所を読むと"
#
# But we will send it like this:
#
#       "文部科学省が\n公表した\n審査結果の\n東北大学の\n箇所を\n読むと"
#
# Then when we try to build back the original sentence, we can know what the kanji read
# (It would be easier to trace than directly send the whole sentence)

# The range of unicode of kanji
def char_is_kanji(c) -> bool:
    return u'\u4E00' <= c <= u'\u9FFF'

indexes = [] # range [l, r) to record the range of orignal content for later update
state = False # Whether had seen a non-kanji char
lastIndex = 0
numNewLine = 0

# Some simple finite state machine to parse kanji
for i in range(len(inputs)):
    state |= not char_is_kanji(inputs[i])
    # Slice
    if (state == True and char_is_kanji(inputs[i])) or inputs[i] == '\n' or (i and inputs[i-1] in "。、？！…」/"): 
        if all([t == '\n' for t in inputs[lastIndex:i]]):
            # There is an empty line
            indexes += [(-1, i)]
            numNewLine += 1
        else:
            # When see next kanji or reach the end of the sentence
            indexes += [(lastIndex, i)]
        lastIndex = i
        state = False
indexes += [(lastIndex, len(inputs))]
print(indexes[-1])

# Create the request to suzukikunn
processedInputs = ''
for i, j in indexes:
    # ignore those newlines
    if i != -1:
        processedInputs += inputs[i:j] + '\n'

# URL to suzukikun(すずきくん)
url = "https://www.gavo.t.u-tokyo.ac.jp/ojad/phrasing/index"

# Data of the POST method
data = {
    "data[Phrasing][text]": processedInputs,
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

# Send a POST and use Beautiful Soup to parse the received html file
content = requests.post(url, data).text
soup = BeautifulSoup(content, "html.parser")

# Fetch the required tags, which are phrasing_text and phrasing_subscript 
phrasingTexts = soup.findAll("div", attrs={"class": "phrasing_text"})
phrasingSubscripts = soup.findAll("div", attrs={"class": "phrasing_subscript"})

# Since suzukikun will parsed into small sentences, we need to merge them back
partialResults = []
for d, s in zip(phrasingTexts, phrasingSubscripts):
    # Fetch subscript text (in the first span tag, final tag is the halt sign)
    phrase = s.find_all("span", recursive= False)
    sentence = ""
    for p in phrase: sentence += p.get_text()

    # Fetch processed data
    temp = d.find_all("span", recursive= False)
    datas = []
    for p in temp:
        # Check accent mark (we don't use unvoiced)
        accent = 0
        if p['class'][0] == 'accent_plain': accent = 1
        elif p['class'][0] == 'accent_top': accent = 2
        datas.append({'text': p.get_text(), 'accent': accent})
    datas = datas[:-1] # Extract last ''
    # Fill back those special signs
    if sentence[-1] in "。、？！…」/":
        datas.append({'text': sentence[-1], 'accent': 0})

    # Here is the syntax we use to mark those accent:
    #
    #           痛める　
    #           {痛|い<b>た</b>}{め|<i>*&emsp;&emsp;*</i>}る
    #
    # We use {|} to represent the use of ruby 
    # This syntax is supported by markdown-it, and can be applyed on hackmd
    #
    # As for accent, we use the css setting written by @OrangeSagoCream based on @Koios's idea
    # The syntax sugar is supported like this:
    #
    #          <b>:  apply the line
    #          <i>:  higher line to match the kanji, type one more character than the marked
    #                content to get proper length
    #   italic(**): apply top accent (right border) 
    #
    # There are some parameters you can set:
    #
    #           :root {
    #               --accent-width: 123rem; 
    #               --accent-color: #000;
    #           }
    #
    # For more details and implementation, please check `./settings.css`
    #
    # To use this css style and syntax, type `{%hackmd @OrangeSagoCream/Accent %}` 
    # at the first line of your hackmd

    def accent_translate(_datas, top = False):
        """
        This function can receive serveral hiraganas and translate into expected form
        """
        result = ''
        for d in _datas:
            t, a = d['text'], d['accent']
            if top:
                if a:
                    result += '<b>%s</b>' % t if a == 1 else '<b>*%s*</b>' % t
                else:
                    result += t
            else:
                if a:
                    result += "{%s|<i>&emsp;</i>}" % t if a == 1 else "{%s|<i>*&emsp;*</i>}" % t
                else:
                    result += t
        return result    
        
    # Find the point where corresponding hiragana ends for Kanji
    i, j = len(sentence)-1, len(datas)-1

    while sentence[i] == datas[j]['text']:
        i -= 1
        j -= 1
        if i < 0 or j < 0: break
    
    partialResult = ''
    # Kanji part
    if i >= 0 and j >= 0:
        partialResult += "{%s|%s}" % (sentence[:i+1], accent_translate(datas[:j+1], True))
    # Non Kanji part
    partialResult += accent_translate(datas[j+1:])

    # Update to partialResults
    partialResults.append(partialResult)
print(len(partialResults), len(indexes)-numNewLine, numNewLine)

# cnt = 0
# for i in range(len(indexes)):
#     if cnt >= len(partialResults): break
#     a, b = indexes[i]
#     if a == -1: continue
#     print("------------")
#     print(inputs[a:b])
#     print(partialResults[cnt])
#     cnt += 1

assert len(partialResults) == len(indexes)-numNewLine, "Length of indexes (len=%d) and partialResults (len=%d) are not aligned" % (len(indexes)-numNewLine, len(partialResults))

# Apply those partialResults back to inputs
result = inputs
cnt = 0
for t in range(len(indexes)-1, 0, -1): # Update backward
    i, j = indexes[t]
    if i == -1:
        result = result [:j] + '\n\n' + result[j:]
    else:
        result = result[:i] + partialResults[cnt] + result[j:]
        cnt += 1

# Write the result to the specified file
writePath = './result.txt'
with open(writePath, "w") as f:
    f.write(result)

print("Translate Finish.")