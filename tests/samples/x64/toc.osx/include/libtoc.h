//libtoc.h
#ifndef _LIBTOC_H_
#define _LIBTOC_H_
extern const long kTOC_MAGICAL_FUN;

/*
 a constant definition "exported" by library
 i quote it because it isn't really exported, as it doesn't show up in the exports anywhere
 it basically exists emphemerally in any source code which #includes this header,
 and then disappears after compilation,
 as no symbol is associated with it, and it returns to it's pure anonymous,
 integer brothers and sisters
 of course this has advantages wrt client side speed, since the value can
 typically be used as an immediate, no memory reads are performed,
 and the dynamic linker doesn't have to load the value into the got
*/
#define TOC_MAX_FOO  20

// a global variable exported by library
// if you don't know what extern means you should probably look that up
// .. it helps to think that this file, when you #include it, will pretty much
// be transcluded into your source file, after the c preprocessor runs
extern int toc_extern_export;

// function prototypes for a function exported by library:
extern long int toc_maximum(long int x, long int y);
extern long int toc_XX_unicode(long int x, long int y);

#endif
