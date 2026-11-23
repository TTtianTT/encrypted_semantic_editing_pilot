"""Post-lock wrapper (not a locked source; DEVIATIONS post-lock #1 and #2): runs the locked analyze.main() unchanged except for
(1) every figure analyze.py saves as .png is also saved as .svg (§13 lists figs/*.png and *.svg);
(2) JSONL shards are split on '\\n' only. symutil.rows uses str.splitlines(), which also splits on U+2028/U+2029/\\x85 etc.; json.dumps
    (ensure_ascii=False) leaves those unescaped inside degenerate decoded text, so one record was cut in two. Records are otherwise
    parsed identically."""
import json
import sys
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
from matplotlib.figure import Figure
import symutil
import analyze

_orig = Figure.savefig


def _both(self, fname, *a, **k):
    _orig(self, fname, *a, **k)
    p = Path(str(fname))
    if p.suffix == '.png':
        k.pop('dpi', None); _orig(self, p.with_suffix('.svg'), *a, **k)


Figure.savefig = _both

_rows0 = symutil.rows


def rows(p): return [json.loads(s) for s in Path(p).read_text().split('\n') if s.strip()]


for m in list(sys.modules.values()):
    if getattr(m, 'rows', None) is _rows0: m.rows = rows

if __name__ == '__main__':
    analyze.main()
