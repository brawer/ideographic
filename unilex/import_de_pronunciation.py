# coding: utf-8

from __future__ import unicode_literals
import codecs, os, re, unicodedata
import xml.etree.ElementTree as etree


_MARYTTS_LEXICON_DE = '../../marytts-lexicon-de/modules/de/lexicon'


def read_allophones(path):
    mapping = {'-': '.', "'": "ˈ", ",": "ˌ"}
    r = etree.parse(path).getroot()
    for element in (r.findall('./vowel') + r.findall('./consonant')):
        if 'ph' in element.attrib and 'ipa' in element.attrib:
            mapping[element.attrib['ph']] = element.attrib['ipa']
    return mapping


def _build_ipa_regexp(allophones):
    r = '|'.join(sorted(allophones.keys(), key=lambda x:(-len(x), x)))
    r = r.replace('\\', '\\\\').replace('{', '\\{').replace('?', '\\?')
    return re.compile('(%s|.)' % r)


_allophones = read_allophones(_MARYTTS_LEXICON_DE + '/allophones.de.xml')
_ipa_regexp = _build_ipa_regexp(_allophones)



def ipa(xsampa):
    return _ipa_regexp.sub(lambda x: _allophones[x.group(1)], xsampa)


if __name__ == '__main__':
    for line in codecs.open(_MARYTTS_LEXICON_DE + '/de.txt', 'rb', 'utf-8'):
        line = line.strip()
        if not line or line[0] == '#':
            continue
        columns = line.split()
        if len(columns) != 2:
            continue
        word, sampa = [c.strip() for c in columns]
        print '\t'.join([word, ipa(sampa)]).encode('utf-8')





