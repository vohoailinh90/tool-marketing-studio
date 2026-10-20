"""sd-11-030: one noisy metric a day, two real incidents, three alert rules."""
import random


def series(seed=3):
    r = random.Random(seed)
    incidents = set(range(400, 420)) | set(range(900, 915))
    return [(95 if t in incidents else 50) + r.gauss(0, 15) for t in range(1440)], incidents


def alerts(s, threshold, k):
    out, run = [], 0
    for t, v in enumerate(s):
        run = run + 1 if v > threshold else 0
        if run == k:
            out.append(t)
    return out


EXPECTED = {1: (38, 32, [2, 0]), 3: (4, 0, [4, 4]), 5: (3, 0, [6, 6])}

if __name__ == "__main__":
    s, inc = series()
    for k, (n, false, delays) in EXPECTED.items():
        a = alerts(s, 80, k)
        got_false = len([t for t in a if t not in inc])
        first = [min([t for t in a if x <= t < x + 20] or [None]) for x in (400, 900)]
        assert (len(a), got_false, [f - x for f, x in zip(first, (400, 900))]) == (n, false, delays), k
    print("sd-11-030 ok")
