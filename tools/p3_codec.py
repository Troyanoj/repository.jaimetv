#!/usr/bin/env python3
"""Decode/encode Palantir 3 libs/*.md (b85 + 3-segment rotation)."""
import base64, sys

def decode(data: bytes) -> bytes:
    n = len(data); k = n // 3
    tail = data[n-k:]
    head = data[:n-k]
    return base64.b85decode(tail + head[:k] + head[k:][::-1])

def encode(src: bytes) -> bytes:
    # decode(enc) = C + A + reverse(B), where enc = A+B+C, |A|=|C|=k.
    # b85encode(src) yields exactly C + A + reverse(B); split it and undo.
    b = base64.b85encode(src)
    n = len(b); k = n // 3
    C = b[:k]
    A = b[k:2*k]
    B = b[2*k:][::-1]
    return A + B + C

if __name__ == '__main__':
    mode, path = sys.argv[1], sys.argv[2]
    data = open(path, 'rb').read()
    out = decode(data) if mode == 'decode' else encode(data)
    if mode == 'decode':
        sys.stdout.buffer.write(out)
    else:
        open(path + '.enc', 'wb').write(out)
