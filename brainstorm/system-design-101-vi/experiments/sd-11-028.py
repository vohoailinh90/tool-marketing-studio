"""sd-11-028: where a new id lands in an ordered index, birthday estimate, id segments."""
import bisect
import random


def stat(ids):
    s, off_end, behind = [], 0, 0
    for x in ids:
        i = bisect.bisect(s, x)
        behind += len(s) - i
        off_end += (len(s) - i) > 0
        s.insert(i, x)
    return off_end, behind / len(ids)


class Segment:
    def __init__(self, size):
        self.size, self.db, self.cur, self.end, self.calls = size, 0, 0, 0, 0

    def next(self):
        if self.cur >= self.end:
            self.cur = self.db
            self.db += self.size
            self.end = self.db
            self.calls += 1
        self.cur += 1
        return self.cur - 1


def main():
    r = random.Random(7)
    n = 20000
    uuid_like = [r.getrandbits(128) for _ in range(n)]
    off, mean = stat(uuid_like)
    assert off == 19987 and abs(mean - 5005.49135) < 1e-5, (off, mean)
    assert stat(range(n)) == (0, 0.0)
    sf = []
    for t in range(n // 2):
        pair = [(t << 22) | (w << 12) for w in (0, 1)]  # two workers, one id per millisecond each
        r.shuffle(pair)
        sf += pair
    off, mean = stat(sf)
    assert off == 4998 and abs(mean - 0.2499) < 1e-4, (off, mean)
    k = 10**9
    assert abs(k * k / 2 / 2**122 - 9.4039548065783e-20) < 1e-30  # version-4 uuid: 122 random bits
    for size, calls in ((1, 100000), (100, 1000), (1000, 100)):
        g = Segment(size)
        for _ in range(100000):
            g.next()
        assert g.calls == calls
    g = Segment(1000)
    for _ in range(2500):
        g.next()
    assert g.db - g.cur == 500  # a crash leaves the 500 unissued ids of the batch as a gap
    print("sd-11-028 ok")


if __name__ == "__main__":
    main()
