#!/usr/bin/env python3
"""Starch's program, as its loaders leave it in memory: from the disc image.

    unpack.py DISC.img OUT

The disc's catalogue holds only !Boot, !Starch.!RUN, !SPRITES and
!Starch.!STARCH; the game is in sectors no file owns. !STARCH (208
bytes, run at &8000) decrypts the rest of itself - each word XORed with
a word of its first 64 bytes read unaligned (ARM2 rotation), its own
address, a counter product and the PC - then reads &95FDC bytes from
disc address &5000 (ADFS_DiscOp 1: in a D format image, the byte offset)
to &8100, XORs the words &893D0-&9E2D0 with &F43592A7, overwrites its own
code with &15, &14 ... 1 and jumps to &893D0.

There, the protection: the last break must have been a power-on one,
OS_Byte 247 &AA and OS_Byte 200 3 (as !Boot and !STARCH set them), and
reading the sector at &A0800 must fail (the original disc's odd track).
Passed, it overwrites those checks with &1E ... 1 and goes on at &89454:
that is where the recompilation starts (README.md), so OUT is memory from
&8000 to &9E2D0 at that point. It is checked against the known image."""
import hashlib
import struct
import sys

BASE, END = 0x8000, 0x9E2D0
GAME = '1dd4d2edbcf867e9e83be549a94dbcc91871006dbafa7baf4c17793d31f6c82a'


def word(mem, a):
    return struct.unpack_from('<I', mem, a - BASE)[0]


def put(mem, a, w):
    struct.pack_into('<I', mem, a - BASE, w & 0xffffffff)


def unaligned(mem, a):
    """ldr from a non-word address on an ARM2: the word, rotated"""
    w, r = word(mem, a & ~3), (a & 3) * 8
    return ((w >> r) | (w << (32 - r))) & 0xffffffff if r else w


def unpack(disc):
    if len(disc) < 0x5000 + 0x95FDC:
        sys.exit('unpack: the disc image is too short (%d bytes)' % len(disc))
    mem = bytearray(END - BASE)
    # !STARCH, from the catalogue: the root's second entry, !Starch, at
    # sector &0C; !STARCH is its second entry. Read as ADFS does: the
    # directory's entries are 26 bytes from offset 5.
    sd = int.from_bytes(disc[0x405 + 26 + 22:0x405 + 26 + 25], 'little') * 256
    ent = [disc[sd + 5 + 26 * k:sd + 5 + 26 * (k + 1)] for k in range(3)]
    st = [e for e in ent if e[:7] == b'!STARCH']
    if not st:
        sys.exit('unpack: no !Starch.!STARCH in the disc catalogue')
    e = st[0]
    length, at = struct.unpack_from('<I', e, 18)[0], int.from_bytes(e[22:25], 'little') * 256
    mem[0:length] = disc[at:at + length]

    # !STARCH's first stage: &8054-&80D0 decrypted in place
    r0, r1, r2, r12 = 0x1D, 0x8054, 0x8000, 0x2A
    while True:
        r10 = word(mem, r1)
        r1 += 4
        r11 = unaligned(mem, r2)
        r2 += 2
        r10 ^= r11 ^ r1 ^ (r0 * r12) ^ r2 ^ (0x8044 << 6)    # pc: &803C + 8, user mode, flags out of reach
        put(mem, r1 - 4, r10)
        r0 -= 1
        if r0 < 0:
            break
        r12 -= 1
        if r12 == 0:
            r12 = 0x2A
    # the second: the program off the disc, decrypted
    n, key, start, at, size = word(mem, 0x80BC), word(mem, 0x80C4), word(mem, 0x80C8), 0x5000, 0x95FDC
    mem[0x8100 - BASE:0x8100 - BASE + size] = disc[at:at + size]
    for k in range(n):
        put(mem, start + 4 * k, word(mem, start + 4 * k) ^ key)
    for k, a in enumerate(range(0x8058, 0x80AC, 4)):       # the loader, wiped
        put(mem, a, 0x15 - k)
    for k, a in enumerate(range(0x893D0, 0x89448, 4)):     # the protection, wiped
        put(mem, a, 0x1E - k)
    return mem


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    mem = unpack(open(sys.argv[1], 'rb').read())
    h = hashlib.sha256(mem).hexdigest()
    if h != GAME:
        sys.exit('unpack: the program is not the one this recipe knows (sha256 %s)' % h)
    open(sys.argv[2], 'wb').write(mem)
    print('%s: &%X-&%X, entered at &89454' % (sys.argv[2], BASE, END))


if __name__ == '__main__':
    main()
