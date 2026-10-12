# Static recompilation of Starch: the translated program (gen/, from
# superspider gen) and game.c, linked with libroger (the RISC OS runtime).
ROGER   ?= $(HOME)/stuff/libroger
SS      ?= $(HOME)/stuff/superspider
CC      ?= gcc
CFLAGS  ?= -O2 -g -w -fno-strict-aliasing $(if $(TRACE),-DRECOMP_TRACE)
GEN     := $(wildcard gen/code*.c) gen/entries.c
OBJ     := $(GEN:.c=.o) game.o
LIBS    := $(shell pkg-config --libs sdl3) -lm -lpthread
INC     := -I$(ROGER)/include
IMG     := ../unpacked/starch
SSB     := $(SS)/_build/default/bin/main.exe

starch: $(OBJ) $(ROGER)/libroger.a
	$(CC) $(CFLAGS) -o $@ $(OBJ) $(ROGER)/libroger.a $(LIBS)

$(ROGER)/libroger.a: FORCE
	$(MAKE) -C $(ROGER) libroger.a

gen/%.o: gen/%.c $(ROGER)/include/roger_cpu.h gen/gen.h
	$(CC) $(CFLAGS) $(INC) -c -o $@ $<

game.o: game.c $(ROGER)/include/roger.h
	$(CC) $(CFLAGS) $(INC) -c -o $@ $<

# The program as the loaders leave it (tools/unpack.py, from the disc
# image weave.py keeps as extracted/disc1.img), analysed from &89454, where
# the game starts once the protection has passed.
regen:
	cd $(SS) && dune build
	$(SSB) analyse $(IMG) 8000 --exec 89454 --full --roots ../analysis/starch.roots -o ../analysis/starch.json
	rm -rf gen
	$(SSB) gen $(IMG) 8000 ../analysis/starch.json --c gen

# "make roots" merges the gap entries a --trace-gaps run logged
# (untranslated.log, or LOG=...) into ../analysis/starch.roots.
LOG ?= untranslated.log

roots:
	python3 -I $(SS)/tools/gap_roots.py $(IMG) 8000 ../analysis/starch.roots $(LOG)

clean:
	rm -f gen/*.o game.o starch

.PHONY: FORCE regen roots clean
