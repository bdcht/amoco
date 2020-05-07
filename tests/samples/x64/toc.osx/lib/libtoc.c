//libtoc.c
int toc_extern_export = 0xb1b1eb0b;
const long kTOC_MAGICAL_FUN = 0xdeadbeef;

long int toc_maximum(long int x, long int y){
  return x > y ? x : y;
}

long int toc_XX_unicode(long int x, long int y){
  return x * y << 2;
}
