# Don't import anything by default
# Especially don't import grandalf, because it imports numpy, which
# leaks memory (the garbage collector is not efficient enough)
