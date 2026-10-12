/* Starch (Alien Images, 1990): what libroger needs to know about the game.
 *
 * The disc boots through !Boot, which reconfigures the machine for the
 * game (the CMOS RAM: no RMA, RAM disc, font or sprite space, ADFS
 * buffers or directory cache, so that 604K is free), marks the CMOS and
 * resets it; on the way back up it restores the CMOS and runs !STARCH,
 * which reads the program from sectors no file owns, decrypts it, and
 * checks that it's the original disc. None of that is done here:
 * tools/unpack.py makes the program as it is in memory once the checks
 * have passed (../unpacked/starch), and it's entered there, at &89454.
 * The game reads no files: everything is in that image. */
#include <roger.h>

extern const struct roger_image recomp_image;      /* gen/entries.c */

/* The slot at &8E18C holds the current level's header, copied there from
 * &8100 + level * &100: its first words are branches to the level's
 * routines (translated: ../analysis/starch.roots), interpreted as they
 * are when called. */
static const uint32_t interpreted[] = {0x8E18C, 0x8E28C, 0, 0};

static const struct roger_config config = {
    .title = "Starch (recompiled)",
    .image_path = "../unpacked/starch",
    .image = &recomp_image,
    .entry = 0x89454,
    .interpreted = interpreted,
    /* the keys (INKEY scans at &89AAC): Harry Q A D F (up down left
     * right) and left Alt to throw, Dave ] ' K L and right Alt; Space
     * starts, P pauses and O resumes, F11/F12 the volume down/up (so the
     * runtime's own keys are Ctrl+F10-F12). A controller each. */
    .pad_map = "up=Q,down=A,left=D,right=F,a=Left Alt,b=Left Alt,start=Space",
    .pad2_map = "up=],down=',left=K,right=L,a=Right Alt,b=Right Alt,start=Space",
    .ctrl_meta_keys = 1,
    .appdir = "../unpacked",
    /* the game selects mode 13 itself, and shows two screen banks
     * (OS_Byte 113): 160K of screen memory */
    .initial_mode = 13,
    .screen_size = 0x28000,
    /* !STARCH sets the stack at the RAM limit, which !Boot required to be
     * at least &9F000 (604K) */
    .wimpslot = 640 * 1024,
};

int main(int argc, char **argv) { roger_main(argc, argv, &config); }
