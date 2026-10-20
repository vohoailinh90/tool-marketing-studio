"""sd-11-031: a lock with a lease expires while its holder is paused; fencing tokens catch the stale write."""


def simulate(fence):
    lock = {"owner": None, "exp": 0, "tok": 0}
    store = {"val": 0, "tok": 0}
    log = []

    def acquire(who, now):
        if lock["owner"] is None or now >= lock["exp"]:
            lock.update(owner=who, exp=now + 10, tok=lock["tok"] + 1)
            return lock["tok"]

    def write(who, tok, v):
        if fence and tok < store["tok"]:
            log.append((who, "rejected"))
            return
        store["tok"] = max(store["tok"], tok)
        store["val"] = v
        log.append((who, "written", v))

    ta = acquire("A", 0)    # A holds the lock with a lease of 10, then pauses until 15
    tb = acquire("B", 12)   # the lease ran out at 10, so B gets it
    write("B", tb, "B-value")
    write("A", ta, "A-value")  # A wakes at 15 and still believes it holds the lock
    return store, log


if __name__ == "__main__":
    assert simulate(False) == ({"val": "A-value", "tok": 2}, [("B", "written", "B-value"), ("A", "written", "A-value")])
    assert simulate(True) == ({"val": "B-value", "tok": 2}, [("B", "written", "B-value"), ("A", "rejected")])
    print("sd-11-031 ok")
