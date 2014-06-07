#!/usr/bin/env python

import json
import os

def main():
    dirs = ['positive', 'negative']
    for dir in dirs:
        tw_cnt = 0
        ofp = open(dir + '.tweets', 'w')
        h = {}
        for file in os.listdir(dir):
            file = dir + '/' + file
            print 'processing file: %s' % file
            fp = open(file, 'r')
            j = json.load(fp)
            for st in j['statuses']:
                if (len(st['text']) > 30):
                    h[st['text'].replace('\n', ' ').encode("UTF-8")] = '1'
                    tw_cnt += 1

            fp.close()
        print dir + ' tweets: %s' % tw_cnt
        
        tw_cnt = 0
        for text in h.keys():
            ofp.write(text + '\n\n')
            tw_cnt += 1

        print dir + ' wo dup: %s' % tw_cnt

        ofp.close()

if __name__ == "__main__":
    main()
