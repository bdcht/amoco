//toc.c
#include<stdio.h>
#include "include/libtoc.h"

int main (){
  long int max = toc_maximum(2,3);
  printf ("kTOC_MAGICAL_FUN: 0x%lx\n", kTOC_MAGICAL_FUN);
  printf ("toc_extern_export: 0x%x\n", toc_extern_export);
  printf ("===FUNS===\n");
  printf ("toc_XX_unicode: 0x%lu\n", toc_XX_unicode(3, 5));
  printf("toc_maximum: %lu\n", max);

  return 0;
}
