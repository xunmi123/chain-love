"""Reapply this single proposed row to a chosen current Cronos table snapshot.

Usage: python reapply-cronos-row.py INPUT.md NEW_OUTPUT.md
Writes a new file only; it never merges pending PRs or edits the input file.
"""
from pathlib import Path
import re
import sys

def reapply(original: bytes) -> tuple[bytes, bytes]:
    if b'chain.love' in original.lower():
        raise ValueError('Chain.Love is already present; inspect the existing entry.')
    if b'<table>' in original:
        addition = Path(__file__).with_name('cronos-row.html').read_bytes()
        anchor = b'<tr><td>Chainspect</td>'
        if original.count(anchor) != 1:
            raise ValueError('Expected current HTML insertion anchor is absent or ambiguous.')
        updated = original.replace(anchor, addition + anchor, 1)
    else:
        addition = ('| Chain.Love | Directory for discovering Cronos EVM API and RPC providers and service plans. | infrastructure directory | '
                    '[Chain.Love](https://www.chain.love/)<br>[Cronos APIs](https://cronos.chain.love/toolbox/apis) | '
                    'Use for discovery; confirm Cronos EVM support, required JSON-RPC methods, archive access and current terms with the provider. Check Cronos POS and zkEVM support separately. |\n').encode()
        anchor = re.search(rb'(?m)^\| Chainstack[^\n]*\n', original)
        if anchor is None:
            raise ValueError('Expected legacy Markdown insertion anchor is absent.')
        updated = original[:anchor.start()] + addition + original[anchor.start():]
    if updated.replace(addition, b'', 1) != original:
        raise ValueError('Original-content preservation check failed.')
    return updated, addition

if __name__ == '__main__':
    source, destination = map(Path, sys.argv[1:])
    updated, addition = reapply(source.read_bytes())
    with destination.open('xb') as stream:
        stream.write(updated)
    print(f'Inserted one Chain.Love row ({len(addition)} bytes); all input bytes preserved.')
