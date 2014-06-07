from base64 import b64decode
from lxml import etree

__author__ = 'annie'

IN_FILE = "and_good_table.xml"
OUT_FILE = "and_good_table.txt"
NEWS = []
ENTITY = []


def decode_entity():
    print "Decoding entity..."
    global ENTITY
    iparse = etree.iterparse(IN_FILE)
    for event, elem in iparse:
        if elem.tag == '{http://www.romip.ru/common/merged-results-QA-facts-extraction}fact':
            org = elem.get("firstText").encode("utf-8").translate(None, "\"").split(' ')
            pers = elem.get("secondText").encode("utf-8").translate(None, "\"").split(' ')
            ENTITY.append((org, pers))
    print "Entity ready"


def decode_news():
    print "Decoding news..."
    global NEWS
    for f_name in ["news-080404.xml", "news-shevard.xml", "news-vybory.xml"]:
        iparse = etree.iterparse(f_name)
        for event, elem in iparse:
            if elem.tag == "{http://www.romip.ru/data/common}content":
                news = b64decode(elem.text).decode("windows-1251").encode("utf-8")
                news = news.replace(' - ', ' ').replace('\n', ' ').translate(None, ".,?!:;\"()\r").split(' ')
                news = [w for w in news if w != '']
                for org, pers in ENTITY:
                    if all(substring in news for substring in org + pers):
                        NEWS.append([[[w, 'O'] for w in news], False])
                        break
    print "News ready"


def mark_entity():
    print "Mark entities..."
    global NEWS
    count = 0.0
    for ind, (news, used) in enumerate(NEWS):
        count += 1
        for org, pers in ENTITY:
            i = 0
            used_org = False
            used_per = False
            while i < len(news):
                if news[i][0] in org and all(w[1] == 'O' for w in news[i: i + len(org)]):
                    news[i][1] = 'B-ORG'
                    now_used_org = True
                    tmp = i
                    i += 1
                    j = 1
                    while j < len(org) and i < len(news):
                        if news[i][0] in org:
                            news[i][1] = 'I-ORG'
                            i += 1
                            j += 1
                        else:
                            while j > 0:
                                news[i-j][1] = 'O'
                                j -= 1
                            now_used_org = False
                            i = tmp
                            break
                    if now_used_org:
                        used_org = True
                        continue

                if news[i][0] in pers and all(w[1] == 'O' for w in news[i: i + len(pers)]):
                    news[i][1] = 'B-PER'
                    now_used_per = True
                    i += 1
                    tmp = i
                    j = 1
                    while j < len(pers) and i < len(news):
                        if news[i][0] in pers:
                            news[i][1] = 'I-PER'
                            i += 1
                            j += 1
                        else:
                            while j > 0:
                                news[i-j][1] = 'O'
                                j -= 1
                            now_used_per = False
                            i = tmp
                            break
                    if now_used_per:
                        used_per = True
                else:
                    i += 1
            if used_org and used_per:
                NEWS[ind][1] = True
        if count % (len(NEWS)/100) == 0:
            print 'Processed %.0f %s news' % (count * 100.0/len(NEWS), '%')


def out_file():
    print 'Out in file ...'
    count = 0
    with open(OUT_FILE, "w") as out:
        for news, used in NEWS:
            if used:
                count += 1
                for word in news:
                    out.write('%s\t%s\n' % (word[0], word[1]))
    print 'Out %d news from %d ready' % (count, len(NEWS))


if __name__ == "__main__":
    decode_entity()
    decode_news()
    mark_entity()
    out_file()
