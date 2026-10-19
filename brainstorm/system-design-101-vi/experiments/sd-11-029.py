"""sd-11-029: 1000 clients retry against a server that accepts 100 requests per tick."""
import random


def run(policy, clients=1000, cap=100, max_retries=8, seed=1):
    r = random.Random(seed)
    due = {0: [(c, 0) for c in range(clients)]}
    done = gave = peak = total = last = 0
    t = 0
    while due and t < 2000:
        batch = due.pop(t, [])
        if batch:
            r.shuffle(batch)
            if t > 0:
                peak = max(peak, len(batch))
            total += len(batch)
            ok, bad = batch[:cap], batch[cap:]
            done += len(ok)
            if ok:
                last = t
            for c, a in bad:
                if a >= max_retries:
                    gave += 1
                    continue
                due.setdefault(t + max(1, policy(a, r)), []).append((c, a + 1))
        t += 1
    return dict(done=done, gave=gave, peak=peak, total=total, last=last)


BASE, CAP = 2, 64
POLICIES = {
    "linear": lambda a, r: BASE * (a + 1),
    "linear+jitter": lambda a, r: BASE * (a + 1) + r.randint(0, BASE * (a + 1)),
    "exp": lambda a, r: min(CAP, BASE * 2**a),
    "exp+jitter": lambda a, r: min(CAP, BASE * 2**a) + r.randint(0, min(CAP, BASE * 2**a)),
    "exp+full jitter": lambda a, r: r.randint(0, min(CAP, BASE * 2**a)),
}
EXPECTED = {
    "linear": dict(done=900, gave=100, peak=900, total=5400, last=72),
    "linear+jitter": dict(done=1000, gave=0, peak=326, total=2560, last=22),
    "exp": dict(done=900, gave=100, peak=900, total=5400, last=254),
    "exp+jitter": dict(done=1000, gave=0, peak=326, total=2560, last=26),
    "exp+full jitter": dict(done=1000, gave=0, peak=574, total=3128, last=23),
}

if __name__ == "__main__":
    for name, pol in POLICIES.items():
        got = run(pol)
        assert got == EXPECTED[name], (name, got)
    print("sd-11-029 ok")
