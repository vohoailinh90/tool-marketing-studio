"""sd-11-032: competing consumers, priority queue starvation, saga compensation, claim check size."""
import heapq
import random


def completion_order():
    r = random.Random(5)
    free, done = [0, 0, 0], []
    for m in range(12):
        w = min(range(3), key=lambda i: free[i])
        free[w] += r.randint(1, 9)
        done.append((free[w], m))
    return [m for _, m in sorted(done)]


def priority_run():
    q, low_served = [], 0
    for t in range(100):
        heapq.heappush(q, (0, t, "H"))
        if t % 3 == 0:
            heapq.heappush(q, (0, t, "H2"))
        if t < 10:
            heapq.heappush(q, (1, t, "L"))
        p, _, _ = heapq.heappop(q)   # one item served per tick
        low_served += p == 1
    return low_served, len(q)


def saga(fail_at):
    steps = [("đặt chỗ", "hủy chỗ"), ("trừ tiền", "hoàn tiền"), ("giữ hàng", "trả hàng")]
    done, log = [], []
    for i, (a, c) in enumerate(steps):
        if i == fail_at:
            log.append("lỗi: " + a)
            break
        done.append((a, c))
        log.append("xong: " + a)
    for a, c in reversed(done):
        log.append("bù: " + c)
    return log


if __name__ == "__main__":
    assert completion_order() == [0, 1, 3, 2, 5, 6, 8, 7, 4, 9, 11, 10]
    assert priority_run() == (0, 44)
    assert saga(2) == ["xong: đặt chỗ", "xong: trừ tiền", "lỗi: giữ hàng", "bù: hoàn tiền", "bù: hủy chỗ"]
    assert (5 * 1024 * 1024) // 60 == 87381   # an assumed 60-byte reference
    print("sd-11-032 ok")
