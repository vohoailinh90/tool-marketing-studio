# Các loại bộ nhớ và lưu trữ: đo khoảng cách giữa các tầng trên một máy

**Điều đáng nhớ nhất về bộ nhớ và lưu trữ không phải tên từng loại mà khoảng cách giữa chúng: mỗi tầng xuống chậm hơn tầng trên hàng chục tới hàng trăm lần.** Nguồn chỉ điểm danh các cặp tên: RAM và ROM, DDR4 và DDR5, firmware và BIOS, SRAM và DRAM, rồi HDD, SSD, USB, thẻ SD. Bài này giải thích ngắn từng cặp, rồi đo trên máy biên soạn một lần đọc mất bao lâu ở từng tầng, từ bộ đệm trong CPU tới đĩa. Đó là lý do cơ sở dữ liệu cố giữ dữ liệu hay dùng trong bộ nhớ, và đọc đĩa theo từng khối lớn.

![Ba khung dọc. Khung một, các loại theo nguồn: RAM là bộ nhớ làm việc, mất khi tắt máy, còn ROM giữ nội dung khi tắt và chứa firmware như BIOS; SRAM nhanh và đắt, làm bộ đệm trong CPU, còn DRAM rẻ hơn, làm bộ nhớ chính, DDR4 và DDR5 là các thế hệ của nó; HDD, SSD, USB và thẻ SD là nơi lưu lâu dài. Khung hai, đo một lần đọc trên máy biên soạn: vùng 16 KiB 1,8 nano giây; vùng 1 MiB khoảng 8 nano giây; vùng 4 đến 16 MiB 26 đến 53 nano giây; vùng từ 64 MiB trở lên 135 đến 217 nano giây. Khung ba, đọc ngẫu nhiên một khối 4 KiB từ đĩa ảo, bỏ qua bộ đệm của hệ điều hành: 31 đến 37 micro giây, gấp khoảng 150 lần một lần đọc bộ nhớ chính.](../../diagrams/sd-04-046-main.svg)

## Từ viết tắt

- **RAM** (Random Access Memory) — bộ nhớ truy cập ngẫu nhiên: bộ nhớ làm việc của máy, đọc ghi nhanh ở bất kỳ vị trí nào, mất sạch khi tắt điện.
- **ROM** (Read-Only Memory) — bộ nhớ chỉ đọc: giữ nội dung khi tắt điện, thường chứa phần mềm khởi động của máy.
- **BIOS** (Basic Input/Output System) — hệ thống vào ra cơ bản: phần mềm nằm sẵn trên bo mạch, chạy đầu tiên khi bật máy để kiểm phần cứng và nạp hệ điều hành.
- **SRAM** (Static Random Access Memory) — bộ nhớ truy cập ngẫu nhiên tĩnh: nhanh, đắt, tốn chỗ, dùng làm các tầng bộ đệm ngay trong CPU.
- **DRAM** (Dynamic Random Access Memory) — bộ nhớ truy cập ngẫu nhiên động: rẻ và dày hơn SRAM nhưng chậm hơn, dùng làm bộ nhớ chính.
- **DDR** (Double Data Rate) — tốc độ dữ liệu kép: chuẩn của thanh DRAM truyền dữ liệu hai lần mỗi nhịp đồng hồ; DDR4 và DDR5 là hai thế hệ.
- **CPU** (Central Processing Unit) — bộ xử lý trung tâm: chip chạy lệnh của máy, có các tầng bộ đệm riêng bên trong.
- **HDD** (Hard Disk Drive) — ổ đĩa cứng: lưu dữ liệu trên đĩa từ quay, có đầu đọc phải di chuyển tới đúng chỗ.
- **SSD** (Solid-State Drive) — ổ thể rắn: lưu trên chip nhớ flash, không có bộ phận chuyển động.
- **USB** (Universal Serial Bus) — chuẩn cổng nối thiết bị ngoài; ổ USB là chip nhớ flash cắm qua cổng này.
- **SD** (Secure Digital) — chuẩn thẻ nhớ flash nhỏ, hay dùng trong điện thoại và máy ảnh.
- **KiB** (Kibibyte) — kibibyte: đơn vị dung lượng bằng 1.024 byte.
- **MiB** (Mebibyte) — mebibyte: đơn vị dung lượng bằng 1.024 KiB, tức 1.048.576 byte.
- **GiB** (Gibibyte) — gibibyte: đơn vị dung lượng bằng 1.024 MiB.
- **GB** (GigaByte) — gigabyte: đơn vị dung lượng cỡ một tỷ byte; ở đây nói lượng bộ nhớ của máy đo.

## Đọc hình

1. **Các cặp tên.** RAM là bộ nhớ làm việc và mất khi tắt điện; ROM giữ nội dung khi tắt và chứa firmware (phần mềm gắn với phần cứng) như BIOS. Bên trong RAM lại có hai loại: SRAM làm bộ đệm trong CPU, DRAM làm bộ nhớ chính; DDR4 và DDR5 là các thế hệ thanh DRAM. Dưới cùng là nơi lưu lâu dài: HDD, SSD, ổ USB, thẻ SD. Phần giải nghĩa này là kiến thức chung của người biên soạn; nguồn chỉ nêu tên.
2. **Đo bộ nhớ.** Một chương trình C nhỏ đi theo một chuỗi con trỏ xáo trộn trong một vùng nhớ, nên mỗi lần đọc phải chờ lần trước xong và không đoán trước được địa chỉ. Máy biên soạn (một máy ảo, CPU Intel Xeon 2,1 GHz) báo bộ đệm tầng 1 cỡ 48 KiB, tầng 2 cỡ 2 MiB mỗi nhân, tầng 3 cỡ 260 MiB dùng chung. Đo được: vùng 16 KiB, 1,8 nano giây mỗi lần đọc; 1 MiB, khoảng 8; 4 MiB, 26; 16 MiB, 53; từ 64 MiB trở lên, 135 đến 217. Các bậc không khớp hẳn với cỡ bộ đệm hệ thống báo (tầng 3 dùng chung với máy khác, và vùng lớn còn tốn thêm công tra địa chỉ); bài không tách các nguyên nhân đó.
3. **Đo đĩa.** Đọc ngẫu nhiên từng khối 4 KiB trong một tệp 1 GiB, bỏ qua bộ đệm của hệ điều hành (`O_DIRECT`): 31 đến 37 micro giây mỗi lần. Đó là khoảng 150 lần một lần đọc bộ nhớ chính, và khoảng 20.000 lần một lần đọc trúng bộ đệm tầng 1.

## Giới hạn cần nhớ

Máy biên soạn là máy ảo, đĩa là đĩa ảo của nhà cung cấp; không biết bên dưới là loại ổ nào, nên con số đĩa không đại diện cho HDD hay SSD cụ thể. Một HDD thật phải chờ đĩa quay và đầu đọc dịch chuyển, thường chậm hơn nhiều; bài không đo được. Phép đo dùng một luồng và đọc phụ thuộc nhau; đọc tuần tự hay song song cho số rất khác. Bài không đo ROM, BIOS, DDR4 hay DDR5.

## Nhìn hình thử trả lời

Một truy vấn cần 1.000 dòng nằm rải rác ở 1.000 trang khác nhau. Theo các con số đo trên máy này, nếu mọi trang đã nằm trong bộ nhớ chính thì việc chờ đọc mất cỡ bao lâu, và nếu mọi trang phải đọc từ đĩa thì sao?

<details>
<summary>Xem đáp án</summary>

Trong bộ nhớ chính: 1.000 lần đọc, mỗi lần cỡ 200 nano giây, tổng cỡ 0,2 mili giây (thật ra mỗi trang cần vài lần đọc nữa, nhưng vẫn dưới một mili giây).
Từ đĩa: 1.000 lần đọc ngẫu nhiên, mỗi lần 31 đến 37 micro giây, tổng cỡ 31 đến 37 mili giây, chậm hơn khoảng 150 lần. Đó là lý do cơ sở dữ liệu giữ một bộ đệm lớn trong bộ nhớ, và vì sao lần chạy đầu một câu hỏi sau khi khởi động lại thường chậm hơn các lần sau.

</details>

<details>
<summary>Xem sâu hơn: mã phép đo</summary>

Bộ nhớ (biên dịch `gcc -O2 -o chase chase.c`; thay mảng `sizes` để đo các cỡ khác):

```c
/* Đo độ trễ đọc bộ nhớ: đi theo một chuỗi con trỏ xáo trộn trong vùng nhớ cỡ n byte. */
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
static double now(void) { struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t); return t.tv_sec + t.tv_nsec / 1e9; }
int main(void) {
    size_t sizes[] = {16 << 10, 1 << 20, 64 << 20, 1024UL << 20};
    for (int s = 0; s < 4; s++) {
        size_t n = sizes[s] / sizeof(size_t);
        size_t *next = malloc(n * sizeof(size_t)), *order = malloc(n * sizeof(size_t));
        for (size_t i = 0; i < n; i++) order[i] = i;
        srand(46);
        for (size_t i = n - 1; i > 0; i--) { size_t j = ((size_t)rand() * RAND_MAX + rand()) % (i + 1); size_t t = order[i]; order[i] = order[j]; order[j] = t; }
        for (size_t i = 0; i < n; i++) next[order[i]] = order[(i + 1) % n];    /* một vòng duy nhất qua mọi ô */
        size_t p = order[0], steps = 50000000;
        for (size_t i = 0; i < n; i++) p = next[p];                              /* chạy nóng */
        double t = now();
        for (size_t i = 0; i < steps; i++) p = next[p];
        double ns = (now() - t) / steps * 1e9;
        printf("vùng %8zu KiB: %6.1f ns mỗi lần đọc (p=%zu)\n", sizes[s] >> 10, ns, p % 7);
        free(next); free(order);
    }
    return 0;
}
```

Đĩa (biên dịch `gcc -O2 -o disk disk.c`, tạo tệp thử `dd if=/dev/urandom of=big.bin bs=1M count=1024`, chạy `./disk big.bin`):

```c
/* Đọc ngẫu nhiên từng khối 4 KiB từ một tệp 1 GiB, bỏ qua bộ đệm của hệ điều hành (O_DIRECT). */
#define _GNU_SOURCE
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <unistd.h>
static double now(void) { struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t); return t.tv_sec + t.tv_nsec / 1e9; }
int main(int argc, char **argv) {
    int fd = open(argv[1], O_RDONLY | O_DIRECT);
    if (fd < 0) { perror("open O_DIRECT"); return 1; }
    void *buf; if (posix_memalign(&buf, 4096, 4096)) return 1;
    size_t blocks = (1UL << 30) / 4096, reads = 2000; srand(46);
    double t = now();
    for (size_t i = 0; i < reads; i++)
        if (pread(fd, buf, 4096, (off_t)((size_t)rand() % blocks) * 4096) != 4096) { perror("pread"); return 1; }
    printf("đọc ngẫu nhiên 4 KiB, không qua bộ đệm: %.1f µs mỗi lần\n", (now() - t) / reads * 1e6);
    return 0;
}
```

Kết quả hai lần chạy chương trình bộ nhớ: 1,8 và 1,8 nano giây (16 KiB), 8,8 và 7,7 (1 MiB), 134,5 và 138,0 (64 MiB), 216,5 và 204,4 (1 GiB); một lần chạy với các cỡ 4, 16, 32, 128 MiB: 26,1, 52,6, 111,2, 138,2. Chương trình đĩa: 31,5 và 37,1 micro giây.

</details>

## Nguồn đối chiếu

- [ByteByteGo — bài nguồn tại commit cố định](https://github.com/ByteByteGoHq/system-design-101/blob/b28380a4710c5ec9638ec037d4168e288f334cba/data/guides/types-of-memory-and-storage.md): các cặp tên RAM và ROM, DDR4 và DDR5, firmware và BIOS, SRAM và DRAM, HDD, SSD, USB, thẻ SD.

Phép đo chạy ngày 2026-10-18 trên máy biên soạn (máy ảo Linux, 4 nhân Intel Xeon 2,1 GHz, 16 GB bộ nhớ, đĩa ảo), biên dịch bằng gcc; cỡ bộ đệm đọc từ `lscpu` và `/sys/devices/system/cpu/cpu0/cache`. Phần giải nghĩa các loại bộ nhớ là kiến thức chung của người biên soạn, chưa đối chiếu với tài liệu của nhà sản xuất. Bài viết và hình được thiết kế độc lập, không dùng ảnh nguồn.
