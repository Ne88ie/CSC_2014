from sys import argv
import codecs

def begins_capital(word):
    return "1" if word[0].isupper() else "0"

def all_capital(word):
    for letter in word:
        if not letter.isupper():
            return "0"
    return "1"

def containsEnglish(word):
    return "1" if any(map(lambda c : 'a' <= c.lower() <= 'z', word)) else "0"

def moreCapitalLetters(word):
    if len(filter((lambda x:x.isupper()), word)) >= 2:
        return "1"
    return "0"

func = [begins_capital, all_capital, containsEnglish, moreCapitalLetters]

def print_features(input_file_name, output_file_name, ifclasses):
    input_file = codecs.open(input_file_name, 'r', encoding="UTF8")
    output_file = codecs.open(output_file_name, 'w', encoding="UTF8")
    for line in input_file:
        line = line.strip()
        if line == "" or line[0] == "#":
            continue
        w, c = line.split()
        res = map(lambda f: f(w), func)
        c = "" if not ifclasses else c
        output_file.write(w + " " + ' '.join(res) + " " + c + "\n")
    output_file.close()
    input_file.close()


if __name__ == "__main__":
    input_file_name = argv[1]
    output_file_name = argv[2]
    ifclasses = argv[3] == "True"
    print_features(input_file_name, output_file_name, ifclasses)