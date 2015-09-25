# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import codecs
import icu

from cldr_util import makePhonemeSet, match, check, regtest

GRAPHEMES = icu.UnicodeSet()
GRAPHEMES.applyPattern('[[:Sinh:] [:Cf:]]')

PHONEMES = makePhonemeSet("""
    p b t d c ɟ ʈ ɖ k g
    m n ɲ ŋ b̃ d̃ ɖ̃ ɟ̃ g̃ f s ʃ h
    r l j ʋ ɑ ɑː æ æː i iː
    u uː e eː o oː ə əː ɑ̃ː æ̃ː ə̃ː
    ɑ̯i ɑu iu ei eu æi æu ɑi̯ ɑ̯u oi ou ui ɑːi
    eːi oːi oːu uːi æːi ɑːu æːu iːu w
    .

""")

check('si-si_FONIPA.txt', GRAPHEMES, PHONEMES)
regtest('si-si_FONIPA', GRAPHEMES, PHONEMES)
