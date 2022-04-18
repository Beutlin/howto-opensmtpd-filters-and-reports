import sys
from io import StringIO
from pathlib import Path

from _pytest.monkeypatch import MonkeyPatch

import afilter


def test_incoming_mail(capsys, monkeypatch):
    Path('out.log').write_text('')
    session_file = 'server1.txt'
    monkeypatch = MonkeyPatch()
    with monkeypatch.context() as m:
        lines = Path(session_file).read_text() + '\nexit'
        m.setattr(sys, 'stdin', StringIO(lines))
        afilter.main()
