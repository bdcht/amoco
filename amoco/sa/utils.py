import math
from math import log
from collections import Counter

def entropy(data):
    if len(data) <= 1:
        return 0
    counts = Counter()
    for d in data:
        counts[d] += 1
    res = 0
    probs = [float(c) / len(data) for c in counts.values()]
    for p in probs:
        if p > 0.:
            res -= p * log(p, math.exp(1))
    return res
