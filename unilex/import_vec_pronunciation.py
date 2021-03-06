# coding: utf-8

from __future__ import unicode_literals
import codecs, collections, icu, re, unicodedata


PHONEMES = '''
m n ɲ ŋ
p b t d k ɡ
f v ɾ s z h
l ʎ j w
t͡ʃ d͡ʒ d͡z
i u e e̯ o ɛ ɔ a
'''

IPA_TRANSLIT_RULES = '''

# References
# ----------
# [1] Personal communication with Academia de ła Bona Creansa, Venice
# [2] https://en.wikipedia.org/wiki/Venetian_language#Phonology
# [3] https://en.wikipedia.org/wiki/Help:IPA/Venetian (mixed with Ladin)
#
# Output phonemes
# ---------------
#   m n ɲ ŋ
#   p b t d k ɡ
#   f v ɾ s z
#   l ʎ j w
#   t͡ʃ d͡ʒ d͡z
#   i u e e̯ o ɛ ɔ a

$boundary = [^[:L:][:M:][:N:]];
$e = [e é è];
$i = [i í ì];
$ei = [$e $i];
$vowel = [a á à $ei o ó ò u ú ù];
$onset = [
  j w m n ɲ ŋ p b t d k ɡ f v ɾ s z h l ʎ {e̯}
  {t͡ʃ} {d͡ʒ} {d͡z} {mj} {mw} {nj} {nw}
  {ps} {pɾ} {pɾw} {pl} {pj} {pw} {bɾ} {bɾw} {bw} {bj} {bl}
  {ts} {tɾ} {tɾw} {tl} {tj} {tw} {dɾ} {dɾw} {dw} {dj} {dl}
  {kɾ} {kw} {kɾw} {kl} {kj} {kw} {ɡɾ} {ɡɾw} {ɡw} {ɡj} {ɡl}
  {fɾ} {fj} {fl} {fw} {fɾw} {vɾ} {vj} {vw} {ɾw} {ɾj}
  {zm} {zn} {zɲ} {zj} {zl} {zb} {zbɾ} {zbj} {zbw} {zd} {zdɾ} {zdj} {zdw}
  {zɡ} {zɡɾ} {zɡj} {zɡw} {zv} {zvɾ} {zɾ} {zvj} {zd͡ʒ} {zw}
  {sp} {spɾ} {spw} {st} {stɾ} {stw} {sk} {skɾ} {skw}
  {sf} {sfɾ} {sɾ} {st͡ʃ} {sj} {sw} {lj} {lw}
];

::Lower;
::NFC;

([abefjklmoptvw]) → $1;
[á à] → ˈa;
{c [$ei \' ’]} $vowel → t͡ʃ;
cé [\' ’]? → t͡ʃˈe;
cè [\' ’]? → t͡ʃˈɛ;
c e [\' ’]? → t͡ʃe;
c [íì] [\' ’]? → t͡ʃˈi;
c i [\' ’]? → t͡ʃi;
[c {ch} k q {qu}] → k;
é → ˈe;
è → ˈɛ;
{g l $ei} $vowel → ʎ;
g l → ʎ;
ġ → d͡ʒ;
gé [\' ’]? → d͡ʒˈe;
gè [\' ’]? → d͡ʒˈɛ;
g [íì] [\' ’]? → d͡ʒˈi;
{g [$ei \' ’]} $vowel → d͡ʒ;
{g} $ei → d͡ʒ;
gn → ɲ;
[g {gh}] → ɡ;
[í ì] → ˈi;
{i} $vowel → j;
ł → ɰ;
ṅ → ŋ;
ñ → ɲ;
nj → ɲ;
ó → ˈo;
ò → ˈɔ;
r → ɾ;
[ṡ x z] → z;
{s}[bdg] → z;
s → s;
{u} $vowel → w;
[ú ù] → ˈu;
u → u;
y → j;
[ż đ {dh}] → d͡z;
d → d;
[[:P:][:Z:]]+ → ' ';
::NULL;

{n} [p b t d k ɡ f v ɾ s z $boundary] → ŋ;
{ɰ} ˈ? [ei] → ;
eɰ → e;
iɰ → i;
ɰ → e̯;
::NULL;

# Move stress marker before syllable onset: [zɡɾaŋfiɲˈae] → [zɡɾaŋfiˈɲae]
($onset) ˈ → ˈ $1;
::NULL;

'''

LOCALE = icu.Locale('vec')
COLLATOR = icu.Collator.createInstance(LOCALE)

def make_transliterator():
    assert unicodedata.normalize(
        'NFC', IPA_TRANSLIT_RULES) == IPA_TRANSLIT_RULES
    return icu.Transliterator.createFromRules(
        'vec-vec_FONIPA', IPA_TRANSLIT_RULES, icu.UTransDirection.FORWARD)


def make_phoneme_set(s):
    pat = [u'\\u0020', "ˈ", '.']
    for phoneme in s.split():
        if len(phoneme) == 1:
            pat.append(phoneme)
        else:
            pat.append('{%s}' % phoneme)
    result = icu.UnicodeSet()
    result.applyPattern('[%s]' % ' '.join(pat))
    return result


def match(s, unicodeset):
    return icu.UnicodeSet.span(
        unicodeset, s, icu.USetSpanCondition.SPAN_CONTAINED) == len(s)


def _build_split_regexps():
    onsets = list('''
        j w
        m n ɲ ŋ
        p b t d k ɡ
        f v ɾ s z h
        l ʎ  t͡ʃ d͡ʒ d͡z
        mj mw nj nw
        ps pɾ pɾw pɾj pl pj pw bɾ bɾw bɾj bw bj bl
        ts tɾ tɾw tɾj tl tj tw dɾ dɾw dɾj dw dj dl
        kɾ kw kɾw kɾj kl kj kw ɡv ɡɾ ɡɾw ɡɾj ɡw ɡj ɡl
        fɾ fj fl fw fɾw fɾj vɾ vj vw ɾw ɾj
        zm zn zɲ zj zl
        zb zbɾ zbj zbw zd zdɾ zdj zdw zɡ zɡɾ zɡj zɡw zv zvɾ zɾ zvj zd͡ʒ zw
        sp spɾ spw spj st stɾ stɾj stj stw sk skɾ skw skj sf sfɾ sfj
        sɾ st͡ʃ sj sw
        lj lw e̯
    '''.split())
    #print ' '.join(['{%s}' % o for o in onsets])
    onsets.sort(key=len, reverse=True)
    vowels = list('i u e o ɛ ɔ a'.split())
    vowels.sort(key=len, reverse=True)
    return re.compile('((%s)?(%s))' % ('|'.join(onsets), '|'.join(vowels)))

_onset_vowel = _build_split_regexps()


def stress(s):
    if len(s) == 1:
        return s
    syll = _onset_vowel.sub(lambda m: "." + m.group(0), s.replace("ˈ", "_"))
    if syll[0] not in '._':
        return s
    syll = syll.replace("_.", "._")
    syll = [t for t in syll.split('.') if t]
    if len(syll) == 1:
        return s.replace("ˈ", "")
    pos = -1
    for i, si in enumerate(syll):
        if '_' in si:
            pos = i
            break
    if pos == -1:
        pos = -2 if s[-1] in 'iueoɛɔa' else -1
    ipa = '.'.join(syll[:pos] + ["ˈ"] + syll[pos:])
    ipa = ipa.replace('_', '')
    ipa = ipa.replace("ˈ.", "ˈ").replace(".ˈ", "ˈ")
    return ipa


def compare_entry(a, b):
    a = '\t'.join(a)
    b = '\t'.join(b)
    if COLLATOR.greater(a, b):
        return 1
    elif COLLATOR.greaterOrEqual(a, b):
        return 0
    else:
        return -1


def main():
    onsets = collections.Counter()
    translit = make_transliterator()
    phonemes = make_phoneme_set(PHONEMES)
    print('Form\tPronunciation\n')
    print('# SPDX-License-Identifier: Unicode-DFS-2016\n')
    entries = []
    for line in codecs.open('data/vec/frequency.txt', 'r', 'utf-8'):
        line = line.split('#')[0].strip()
        if not line:
            continue
        count, form = line.split('\t')
        count = int(count)
        form = unicodedata.normalize('NFC', form)
        ipa = ' '.join(stress(w) for w in translit.transliterate(form).split())
        entries.append((form, ipa))
        assert match(ipa, phonemes), ipa.encode('utf-8')
        onset = re.split(r'i|u|e|o|ɛ|ɔ|a', ipa.split()[-1])[0]
        if onset:
            onsets[onset] += 1
    for entry in sorted(entries, cmp=compare_entry):
        print('\t'.join(entry).encode('utf-8'))
    #for ipa, count in onsets.most_common():
        #print '\t'.join([ipa, str(count)]).encode('utf-8')


if __name__ == '__main__':
    #print stress('ˈɡɛ').encode('utf-8')
    #print stress('zveɾɡoˈi').encode('utf-8')
    #print stress('ˈzveŋtoe').encode('utf-8')
    main()
