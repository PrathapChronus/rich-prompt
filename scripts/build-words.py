"""Regenerate hooks/words.txt: python3 scripts/build-words.py <bad-words.txt> (needs `pip install wordfreq`)."""
import re
import sys

from wordfreq import top_n_list

bad = {w.strip().lower() for w in open(sys.argv[1]) if w.strip()}
words = [w for w in top_n_list('en', 80000) if re.fullmatch(r'[a-z]{3,}', w) and w not in bad]
open('hooks/words.txt', 'w').write('\n'.join(words[:50000]) + '\n')
