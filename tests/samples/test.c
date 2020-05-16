// Partial RELRO:
// gcc -m32 -no-pie -g -Wl,-z,relro -o x86/test_partial.elf   test.c
// gcc      -no-pie -g -Wl,-z,relro -o x64/test_partial.elf64 test.c
//
// Full RELRO:
// gcc -m32 -g -Wl,-z,relro,-z,now -o x86/test_full.elf test.c
// gcc      -g -Wl,-z,relro,-z,now -o x64/test_full.elf64 test.c
#include <stdio.h>
#include <stdlib.h>


int main(int argc, int *argv[])
{
size_t *p = (size_t *) strtol(argv[1], NULL, 16);

p[0] = 0xDEADBEEF;

printf("RELRO: %p\n", p);

return 0;
}
