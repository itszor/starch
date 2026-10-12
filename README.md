Starch (Alien Images, 1990) - static recompilation
==================================================

A recipe: this repository holds no game data. It rebuilds the game as a
native executable from your own copy of the disc, recognised by content
(recipe.json), so it can be shared without distributing the game.

    ./build.sh "Starch (1990)(Alien Images).zip"    (or the .adf)
    cd recomp && ./starch

build.sh runs recipe.json's steps with SuperSpider's tools/weave.py
(~/stuff/superspider, or $SUPERSPIDER): it recognises the disc, extracts
it (keeping the image itself: extracted/disc1.img), rebuilds the program
from the disc's hidden sectors (tools/unpack.py), analyses and translates
it, and links it with libroger (~/stuff/libroger, or make ROGER=...). It
takes a few seconds. Needs python3, OCaml/dune, gcc and SDL3.

Input: the TOSEC set's `Starch (1990)(Alien Images).zip`, or the .adf in
it. That image is an 800K D format disc cut short after its last used
sector (620K); SuperSpider's ADFSlib pads such images to the size their
map gives.

What it makes:

    extracted/disc1          the catalogue's files (!Boot, !Starch)
    extracted/disc1.img      the disc image (weave.py's "raw": true)
    unpacked/starch          the program as the loaders leave it, &8000-&9E2D0
    analysis/starch.json     SuperSpider's analysis
    recomp/gen/              its C translation
    recomp/starch            the game

Committed: recipe.json, build.sh, tools/unpack.py, analysis/starch.roots,
recomp/ (Makefile, game.c), this file.

How the disc starts the game, and what's skipped
------------------------------------------------

- !Boot reconfigures the machine so the game fits a 1MB Archimedes: it
  saves the CMOS RAM, sets Language, FontSize, RamFsSize, RMASize,
  SpriteSize, SystemSize, ScreenSize, ADFSbuffers and ADFSDirCache to 0,
  marks CMOS bytes 30-32 "MBD" and resets the machine. Coming back up it
  sees the mark, restores the CMOS, checks there's 604K, and loads and
  runs !Starch.!STARCH.
- !STARCH (208 bytes) decrypts the rest of itself (XORs keyed by its own
  bytes, read unaligned, the address and the PC), sets the break action,
  then reads &95FDC bytes from disc address &5000 - sectors no file owns -
  to &8100 with ADFS_DiscOp, XORs &893D0-&9E2D0 with a key, wipes itself
  and jumps to &893D0.
- There, the protection: the last reset must have been a power-on one,
  OS_Byte 247 and 200 must be as !Boot and !STARCH left them, and reading
  the sector at &A0800 (an odd track on the original) must fail. Passed,
  it wipes those checks and starts the game at &89454.

tools/unpack.py does the loaders' work in Python and checks the result
(its sha256), and the recompilation starts at &89454. Nothing of the
CMOS juggling, the reset or the protection runs; the game itself reads no
files and uses no disc (the levels, sprites, samples and tunes are all in
that one image: the developers' own *Key definitions, left in it, list the
layout).

The level code
--------------

The program keeps five 256-byte level headers at &8100-&85FF. The one for
the current level is copied (&89880) into a slot at &8E18C, and the game
calls through the slot: its first words are branches to that level's
routines. SuperSpider now recognises a copy loop into the image from an
unknown source as a slot (calls into it are dispatched at run time, and
assumed to return), which is what made the rest of the program
reachable; the levels' routines are roots (analysis/starch.roots, the
branch targets of each header as placed in the slot), and game.c lists
the slot as interpreted. The analysis then has no unresolved jumps or
problems: 13,669 code words, 341 functions.

Controls
--------

Harry: Q up, A down, D left, F right, left Alt throws. Dave: ] up, ' down,
K left, L right, right Alt. A tap sets the direction: the character keeps
walking. Space starts, P pauses and O resumes, F11/F12 turn the volume
down/up (so libroger's own keys are Ctrl+F10-F12). Two game controllers,
one per player (start = Space).

A headless scenario (start a game, Harry walks left, then down; screenshot-N.bmp):

    ./starch --limit=5e7 --full-os --script=3000:key:99:300,9000:shot,\
    9100:key:51:300,11000:shot,13000:key:66:300,15000:shot

Not done
--------

- Only level 1 has been played in scripted runs. The attract mode goes
  through all five levels (a 1.6e9-instruction --trace-gaps run: no gaps
  outside the slot), but a full game through all five hasn't been played.
  Run with --trace-gaps and `make roots` if anything turns up.
